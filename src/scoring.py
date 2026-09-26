"""
Opción 7: entrena el modelo de reglas en dos etapas (src/modelo_reglas.py)
con las reseñas vectorizadas y la Verdad Base, y lo guarda para la opción 8.

También conserva la regresión lineal anterior (entrenar_lineal), que la
opción 9 usa como comparación.
"""

from collections import defaultdict

import chromadb
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity

from src import pooling as resumen_resenias
from src.config import DIR_CHROMA, POOLING_RESENIAS, RUTA_GT, RUTA_MODELO
from src.metricas import K_RANKING
from src.modelo_reglas import MODO_FRASES_POR_DEFECTO, evaluar, subconjunto_rasgos
from src.normalizacion import (
    canonicalizar_film_id,
    obtener_filtros_del_perfil,
    seleccionar_perfil,
)

ETIQUETAS_TIPO = {"restrictivos": "filtro", "afinidad": "afinidad", "excepcion": "excepción"}
N_PARTICIONES = 5
MINIMO_PELICULAS = 10


def agrupar_embeddings_por_pelicula(review_ids, review_embeddings, pooling: str = POOLING_RESENIAS):
    # Cada reseña se guardó en varios chunks (y puede haber más de una
    # reseña por película). Resumimos todos los vectores de la misma
    # película en uno solo por film_id, comparable contra la Verdad Base
    # (que también es por película): con el promedio, o con un percentil de
    # cada dimensión si pooling es "pXX".
    acumulador = defaultdict(list)
    for id_compuesto, vector in zip(review_ids, review_embeddings):
        film_id = canonicalizar_film_id(id_compuesto.split("::")[0])
        acumulador[film_id].append(vector)

    if pooling == "media":
        return {film_id: np.mean(vectores, axis=0) for film_id, vectores in acumulador.items()}
    return {film_id: np.percentile(vectores, int(pooling[1:]), axis=0) for film_id, vectores in acumulador.items()}


def construir_estructura(perfil: dict) -> dict:
    # Términos a vectorizar y relaciones afinidad <- filtro <- excepción que define el perfil.
    afinidades = set(perfil.get("afinidad", {}))
    restrictivos = perfil.get("restrictivos", {})

    excepciones = [filtro for filtro, datos in restrictivos.items() if datos.get("excepcion")]
    corrupciones = [
        (afinidad, filtro)
        for filtro, datos in restrictivos.items()
        for afinidad in datos.get("corrupcion_directa") or []
        if afinidad in afinidades
    ]
    terminos = obtener_filtros_del_perfil(perfil) + [("excepcion", filtro) for filtro in excepciones]
    return {"terminos": terminos, "corrupciones": corrupciones, "excepciones": excepciones}


def obtener_embeddings_perfil(coleccion_perfiles, nombre_perfil, terminos):
    # Filtra por persona: distintos perfiles pueden compartir nombres de filtro.
    datos_perfil = coleccion_perfiles.get(where={"persona": nombre_perfil}, include=['embeddings', 'metadatas'])
    if len(datos_perfil['ids']) == 0:
        raise ValueError(
            f"No hay embeddings del perfil '{nombre_perfil}'. Ejecuta el módulo 3 primero."
        )

    por_termino = {
        (meta['tipo'], meta['filtro']): emb
        for meta, emb in zip(datos_perfil['metadatas'], datos_perfil['embeddings'])
    }
    dimension = len(datos_perfil['embeddings'][0])

    faltantes = [f"{ETIQUETAS_TIPO[tipo]} '{nombre}'" for tipo, nombre in terminos if (tipo, nombre) not in por_termino]
    if faltantes:
        print(f"[!] Aviso: sin embedding para {', '.join(faltantes)}; se usa un vector nulo. "
              "Vuelve a ejecutar el módulo 3 si editaste el perfil.")

    # vector nulo (ortogonal) si el término no tiene embedding
    return np.array([por_termino.get(tuple(termino), np.zeros(dimension)) for termino in terminos])


def construir_features(similitudes, estructura, escala=None):
    # Similitud con cada término, más un producto por cada relación del perfil:
    # afinidad x filtro (el filtro corrompe la afinidad) y filtro x excepción
    # (la excepción neutraliza el filtro). Las similitudes se estandarizan con
    # la media y desviación de entrenamiento (escala): varían muy poco entre
    # películas, y sin estandarizar los productos quedan diminutos y la
    # regresión les asigna pesos gigantes e inestables.
    if escala is None:
        desviaciones = similitudes.std(axis=0)
        escala = (similitudes.mean(axis=0), np.where(desviaciones > 0, desviaciones, 1.0))
    medias, desviaciones = escala
    z = (similitudes - medias) / desviaciones
    indice = {tuple(termino): i for i, termino in enumerate(estructura["terminos"])}

    columnas = [z[:, i] for i in range(z.shape[1])]
    nombres = [f"{ETIQUETAS_TIPO[tipo]} · {nombre}" for tipo, nombre in estructura["terminos"]]

    for afinidad, filtro in estructura["corrupciones"]:
        columnas.append(z[:, indice[("afinidad", afinidad)]] * z[:, indice[("restrictivos", filtro)]])
        nombres.append(f"{afinidad} × {filtro}")

    for filtro in estructura["excepciones"]:
        columnas.append(z[:, indice[("restrictivos", filtro)]] * z[:, indice[("excepcion", filtro)]])
        nombres.append(f"{filtro} × excepción")

    return np.column_stack(columnas), nombres, escala


def cargar_embeddings_peliculas(cliente, pooling: str = POOLING_RESENIAS):
    datos_resenias = cliente.get_collection(name="resenias").get(include=['embeddings'])
    return agrupar_embeddings_por_pelicula(datos_resenias['ids'], datos_resenias['embeddings'], pooling)


def entrenar_lineal(nombre_perfil: str, perfil: dict) -> dict:
    # Regresión lineal sobre la similitud con cada término del perfil (el
    # modelo de las versiones anteriores; la opción 9 la usa como comparación).
    # Cruza las películas con reseñas vectorizadas contra la Verdad Base.
    # Lanza ValueError si faltan datos.
    if not RUTA_GT.exists():
        raise ValueError("No se encontró matriz_perdida.csv. Ejecuta el módulo 5 primero.")

    estructura = construir_estructura(perfil)

    print("Conectando con la base de datos vectorial ChromaDB...")
    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))
    embeddings_perfil = obtener_embeddings_perfil(
        cliente.get_collection(name="perfiles"), nombre_perfil, estructura["terminos"]
    )
    embeddings_por_pelicula = cargar_embeddings_peliculas(cliente)

    df_gt = pd.read_csv(RUTA_GT)
    df_gt['canon_id'] = df_gt['film_id'].apply(canonicalizar_film_id)

    film_ids, embeddings_entrenamiento, y_entrenamiento = [], [], []
    for _, fila in df_gt.iterrows():
        canon_id = fila['canon_id']
        if canon_id in embeddings_por_pelicula and pd.notna(fila['gt_nota_global']):
            film_ids.append(canon_id)
            embeddings_entrenamiento.append(embeddings_por_pelicula[canon_id])
            y_entrenamiento.append(fila['gt_nota_global'])

    if len(y_entrenamiento) < 2:
        raise ValueError("No se lograron cruzar suficientes reseñas vectorizadas con el Ground Truth "
                         f"({len(y_entrenamiento)} película(s)). Se necesitan al menos 2.")

    y_array = np.array(y_entrenamiento)

    # cálculo de la Similitud del Coseno (Matriz X)
    print("Calculando distancias semánticas (Matriz X)...")
    similitudes = cosine_similarity(np.array(embeddings_entrenamiento), embeddings_perfil)
    matriz_x, columnas, escala = construir_features(similitudes, estructura)

    print("Entrenando Regresión Lineal...")
    modelo = LinearRegression()
    modelo.fit(matriz_x, y_array)
    predicciones = modelo.predict(matriz_x)

    return {
        "perfil": nombre_perfil, "estructura": estructura, "modelo": modelo, "escala": escala,
        "columnas": columnas, "film_ids": film_ids, "similitudes": similitudes, "matriz_x": matriz_x,
        "y": y_array, "predicciones": predicciones, "embeddings_perfil": embeddings_perfil,
        "embeddings_por_pelicula": embeddings_por_pelicula,
        "mse": mean_squared_error(y_array, predicciones), "r2": r2_score(y_array, predicciones),
    }


def textos_del_perfil(cliente, nombre_perfil: str, perfil: dict) -> dict:
    # Descripción y frases de reseña de los criterios que tienen frases (vacío si no hay).
    if not any(datos.get("frases_resenia") for tipo in ("restrictivos", "afinidad")
               for datos in perfil.get(tipo, {}).values()):
        return {}
    try:
        coleccion = cliente.get_collection(name="perfiles")
    except Exception:
        print("[!] Aviso: no hay embeddings del perfil; se entrena sin frases de reseña. Ejecuta el módulo 3.")
        return {}
    return resumen_resenias.textos_de_criterios(coleccion, nombre_perfil, perfil)


def entradas_peliculas(cliente, textos: dict, pooling: str, umbrales=None) -> dict:
    # Embedding resumido de cada película con reseñas vectorizadas y, si el
    # perfil tiene frases de reseña, sus rasgos de frases. Con umbrales=None se
    # calculan con los chunks actuales (al entrenar); al recomendar se usan los
    # guardados con el modelo.
    print("Cargando los chunks de reseñas vectorizadas...")
    chunks = resumen_resenias.cargar_chunks(cliente)
    if not chunks:
        raise ValueError("No hay reseñas vectorizadas todavía. Ejecuta el módulo 4 primero.")
    film_ids = sorted(chunks)
    X = resumen_resenias.representar(chunks, film_ids, pooling)
    rasgos = None
    if textos:
        if umbrales is None:
            umbrales = resumen_resenias.umbrales_frases(chunks, textos)
        rasgos = resumen_resenias.rasgos_frases(chunks, film_ids, textos, umbrales=umbrales)
    return {"chunks": chunks, "film_ids": film_ids, "X": X, "rasgos": rasgos, "umbrales": umbrales}


def entrenar_reglas(nombre_perfil: str, perfil: dict) -> dict:
    # Valida con validación cruzada y entrena con todas las películas evaluadas
    # el modelo de reglas. Lanza ValueError si faltan datos.
    if not RUTA_GT.exists():
        raise ValueError("No se encontró matriz_perdida.csv. Ejecuta el módulo 5 primero.")

    print("Conectando con la base de datos vectorial ChromaDB...")
    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))
    textos = textos_del_perfil(cliente, nombre_perfil, perfil)
    entradas = entradas_peliculas(cliente, textos, POOLING_RESENIAS)

    df_gt = pd.read_csv(RUTA_GT)
    df_gt["canon_id"] = df_gt["film_id"].apply(canonicalizar_film_id)
    # En el orden de la Verdad Base, el mismo que usan las comparaciones de la opción 9.
    posicion = {film_id: i for i, film_id in enumerate(entradas["film_ids"])}
    evaluadas = df_gt.loc[df_gt["gt_nota_global"].notna(), "canon_id"]
    indices = [posicion[film_id] for film_id in dict.fromkeys(evaluadas) if film_id in posicion]
    if len(indices) < MINIMO_PELICULAS:
        raise ValueError(f"Solo {len(indices)} películas tienen reseñas vectorizadas y nota de Gemini; "
                         f"se necesitan al menos {MINIMO_PELICULAS}. Evalúa más películas (módulo 6).")

    film_ids = [entradas["film_ids"][i] for i in indices]
    print(f"Entrenando el modelo de reglas con {len(film_ids)} películas "
          f"({'con' if textos else 'sin'} frases de reseña, pooling {POOLING_RESENIAS})...")
    evaluacion = evaluar(perfil, df_gt, film_ids, entradas["X"][indices], N_PARTICIONES,
                         rasgos=subconjunto_rasgos(entradas["rasgos"], indices), modo_frases=MODO_FRASES_POR_DEFECTO)
    return {"perfil": nombre_perfil, "film_ids": film_ids, "textos": textos, "entradas": entradas,
            "evaluacion": evaluacion}


def main(perfil_elegido: str | None = None):
    try:
        nombre_perfil, perfil = seleccionar_perfil(perfil_elegido)
        resultado = entrenar_reglas(nombre_perfil, perfil)
    except (FileNotFoundError, ValueError) as error:
        print(f"[!] Error: {error}")
        return None

    evaluacion, textos = resultado["evaluacion"], resultado["textos"]
    modelo = evaluacion["modelo"]
    # Se guarda todo lo necesario para que la opción 8 prepare las películas
    # igual que al entrenar: pooling, frases y sus umbrales de similitud.
    joblib.dump({
        "tipo": "reglas", "modelo": modelo, "perfil": nombre_perfil, "pooling": POOLING_RESENIAS,
        "textos": textos, "umbrales": resultado["entradas"]["umbrales"],
    }, RUTA_MODELO)

    cv = evaluacion["metricas"]["completo"]
    print("\n| -- Modelo de reglas: validación cruzada (películas que el modelo no vio) -- |")
    print(f"Perfil: {nombre_perfil} | películas evaluadas: {len(resultado['film_ids'])}")
    desviacion = evaluacion["metricas"]["completo_desviacion"]
    print(f"Promedio de {evaluacion['metricas']['repeticiones']} repeticiones con particiones distintas.")
    print(f"ρ de Spearman (orden de las películas contra el de Gemini): {cv['spearman']:.3f} ± {desviacion['spearman']:.3f}")
    print(f"NDCG@{K_RANKING}: {cv[f'ndcg@{K_RANKING}']:.3f} | Precisión@{K_RANKING}: {cv[f'precision@{K_RANKING}']:.3f}")
    print(f"Error absoluto medio de la nota (MAE): {cv['mae']:.3f} | R²: {cv['r2']:.3f}")
    if textos:
        con_frases = [nombre for tipo in ("restrictivos", "afinidad")
                      for nombre, datos in perfil.get(tipo, {}).items() if datos.get("frases_resenia")]
        print(f"Frases de reseña usadas en: {', '.join(con_frases)}.")

    print("\n| -- Reglas aprendidas -- |")
    for linea in modelo.regla.describir():
        print(f" - {linea}")
    print(f"\nParámetros: {modelo.regla.n_parametros()} en la regla (etapa 2) y "
          f"{modelo.n_parametros_etapa_1()} en las regresiones Ridge de la etapa 1.")
    print(f"\nModelo guardado en: {RUTA_MODELO}")
    return resultado


if __name__ == '__main__':
    main()

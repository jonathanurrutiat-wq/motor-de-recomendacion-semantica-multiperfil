from collections import defaultdict

import chromadb
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity

from src.config import DIR_CHROMA, POOLING_RESENIAS, RUTA_GT, RUTA_MODELO
from src.normalizacion import (
    canonicalizar_film_id,
    obtener_filtros_del_perfil,
    seleccionar_perfil,
)

ETIQUETAS_TIPO = {"restrictivos": "filtro", "afinidad": "afinidad", "excepcion": "excepción"}


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


def entrenar(nombre_perfil: str, perfil: dict) -> dict:
    # Cruza las películas con reseñas vectorizadas contra la Verdad Base y
    # entrena la regresión. Lanza ValueError si faltan datos.
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


def main(perfil_elegido: str | None = None):
    try:
        nombre_perfil, perfil = seleccionar_perfil(perfil_elegido)
        resultado = entrenar(nombre_perfil, perfil)
    except (FileNotFoundError, ValueError) as error:
        print(f"[!] Error: {error}")
        return None

    # Se guarda el pooling para que la opción 8 resuma las reseñas igual que al entrenar.
    joblib.dump(
        {**{key: resultado[key] for key in ("modelo", "perfil", "estructura", "escala")}, "pooling": POOLING_RESENIAS},
        RUTA_MODELO,
    )

    n_peliculas, columnas, modelo = len(resultado["y"]), resultado["columnas"], resultado["modelo"]
    print("\n| -- Métricas Finales de Entrenamiento -- |")
    print(f"Perfil: {nombre_perfil}")
    print(f"Películas evaluadas con éxito (Cruce Vectorial): {n_peliculas}")
    print(f"Error Cuadrático Medio (MSE): {resultado['mse']:.4f}")
    print(f"Varianza Explicada (R^2): {resultado['r2']:.4f}")
    if n_peliculas <= len(columnas):
        print(f"[!] Aviso: hay {n_peliculas} películas para {len(columnas)} variables; el modelo está "
              "sobreajustado y estas métricas no son confiables. Evalúa más películas (módulo 6).")

    print("\n| -- Pesos Sinápticos (Impacto semántico de cada término y relación) -- |")
    for columna, peso in zip(columnas, modelo.coef_):
        print(f" {columna}: {peso:.4f}")

    print(f"\nSesgo Base (Bias): {modelo.intercept_:.4f}")
    print(f"\nModelo guardado en: {RUTA_MODELO}")
    return resultado


if __name__ == '__main__':
    main()

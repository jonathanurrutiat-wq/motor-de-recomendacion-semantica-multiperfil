from collections import defaultdict

import chromadb
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity

from src.config import DIR_CHROMA, RUTA_GT, RUTA_MODELO
from src.normalizacion import (
    canonicalizar_film_id,
    nombre_columna_gt,
    obtener_filtros_del_perfil,
    seleccionar_perfil,
)


def agrupar_embeddings_por_pelicula(review_ids, review_embeddings):
    # Cada reseña se guardó en varios chunks (y puede haber más de una
    # reseña por película). Promediamos todos los vectores de la misma
    # película para tener un solo embedding por film_id, comparable contra
    # la Verdad Base (que también es por película).
    acumulador = defaultdict(list)
    for id_compuesto, vector in zip(review_ids, review_embeddings):
        film_id = canonicalizar_film_id(id_compuesto.split("::")[0])
        acumulador[film_id].append(vector)

    return {film_id: np.mean(vectores, axis=0) for film_id, vectores in acumulador.items()}


def obtener_embeddings_filtros(coleccion_perfiles, nombre_perfil, nombres_filtros):
    # Filtra por persona: distintos perfiles pueden compartir nombres de filtro.
    datos_perfil = coleccion_perfiles.get(where={"persona": nombre_perfil}, include=['embeddings', 'metadatas'])
    if len(datos_perfil['ids']) == 0:
        raise ValueError(
            f"No hay embeddings del perfil '{nombre_perfil}'. Ejecuta el módulo 3 primero."
        )

    por_filtro = {meta['filtro']: emb for meta, emb in zip(datos_perfil['metadatas'], datos_perfil['embeddings'])}
    dimension = len(datos_perfil['embeddings'][0])

    faltantes = [nombre for nombre in nombres_filtros if nombre not in por_filtro]
    if faltantes:
        print(f"[!] Aviso: sin embedding para {', '.join(faltantes)}; se usa un vector nulo. "
              "Vuelve a ejecutar el módulo 3 si editaste el perfil.")

    # vector nulo (ortogonal) si el filtro no tiene embedding
    return np.array([por_filtro.get(nombre, np.zeros(dimension)) for nombre in nombres_filtros])


def cargar_embeddings_peliculas(cliente):
    datos_resenias = cliente.get_collection(name="resenias").get(include=['embeddings'])
    return agrupar_embeddings_por_pelicula(datos_resenias['ids'], datos_resenias['embeddings'])


def main():
    if not RUTA_GT.exists():
        print("[!] Error: No se encontró matriz_perdida.csv. Ejecuta el módulo 5 primero.")
        return

    try:
        nombre_perfil, perfil = seleccionar_perfil()
    except (FileNotFoundError, ValueError) as error:
        print(f"[!] Error: {error}")
        return

    filtros_perfil = obtener_filtros_del_perfil(perfil)
    nombres_filtros = [nombre for _, nombre in filtros_perfil]
    columnas = [nombre_columna_gt(tipo, nombre) for tipo, nombre in filtros_perfil]

    print("Conectando con la base de datos vectorial ChromaDB...")
    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))

    try:
        embeddings_filtros = obtener_embeddings_filtros(
            cliente.get_collection(name="perfiles"), nombre_perfil, nombres_filtros
        )
    except ValueError as error:
        print(f"[!] Error: {error}")
        return

    embeddings_por_pelicula = cargar_embeddings_peliculas(cliente)

    df_gt = pd.read_csv(RUTA_GT)
    df_gt['canon_id'] = df_gt['film_id'].apply(canonicalizar_film_id)

    embeddings_entrenamiento, y_entrenamiento = [], []
    for _, fila in df_gt.iterrows():
        canon_id = fila['canon_id']
        if canon_id in embeddings_por_pelicula and pd.notna(fila['gt_nota_global']):
            embeddings_entrenamiento.append(embeddings_por_pelicula[canon_id])
            y_entrenamiento.append(fila['gt_nota_global'])

    if len(y_entrenamiento) < 2:
        print("[!] Error: No se lograron cruzar suficientes reseñas vectorizadas con el Ground Truth "
              f"({len(y_entrenamiento)} película(s)). Se necesitan al menos 2.")
        return

    embeddings_reviews = np.array(embeddings_entrenamiento)
    y_array = np.array(y_entrenamiento)

    # cálculo de la Similitud del Coseno (Matriz X)
    print("Calculando distancias semánticas (Matriz X)...")
    matriz_x = cosine_similarity(embeddings_reviews, embeddings_filtros)

    print("Entrenando Regresión Lineal...")
    modelo = LinearRegression()
    modelo.fit(matriz_x, y_array)

    predicciones = modelo.predict(matriz_x)
    mse = mean_squared_error(y_array, predicciones)
    r2 = r2_score(y_array, predicciones)

    joblib.dump(
        {"modelo": modelo, "perfil": nombre_perfil, "filtros": nombres_filtros},
        RUTA_MODELO,
    )

    print("\n| -- Métricas Finales de Entrenamiento -- |")
    print(f"Perfil: {nombre_perfil}")
    print(f"Películas evaluadas con éxito (Cruce Vectorial): {len(matriz_x)}")
    print(f"Error Cuadrático Medio (MSE): {mse:.4f}")
    print(f"Varianza Explicada (R^2): {r2:.4f}")
    if len(matriz_x) <= len(nombres_filtros):
        print(f"[!] Aviso: hay {len(matriz_x)} películas para {len(nombres_filtros)} filtros; el modelo está "
              "sobreajustado y estas métricas no son confiables. Evalúa más películas (módulo 6).")

    print("\n| -- Pesos Sinápticos (Impacto semántico de cada filtro) -- |")
    for columna, peso in zip(columnas, modelo.coef_):
        print(f" {columna}: {peso:.4f}")

    print(f"\nSesgo Base (Bias): {modelo.intercept_:.4f}")
    print(f"\nModelo guardado en: {RUTA_MODELO}")


if __name__ == '__main__':
    main()

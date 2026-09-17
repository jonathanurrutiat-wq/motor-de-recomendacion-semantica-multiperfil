"""
Genera un ranking de películas candidatas a gustarle a un perfil.

Usa el mismo enfoque de scoring.py (similitud de coseno entre embeddings de
reseñas y embeddings de los filtros/afinidades del perfil + regresión lineal
entrenada contra la Verdad Base), pero en vez de solo medir qué tan bien el
modelo reproduce las notas ya conocidas, lo aplica sobre las películas que
tienen reseña procesada pero todavía NO tienen nota de Gemini cargada, y
las ordena de mayor a menor nota estimada.
"""

from collections import defaultdict
from pathlib import Path

import chromadb
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics.pairwise import cosine_similarity

from src.normalizacion import (
    canonicalizar_film_id,
    cargar_perfil_actual,
    obtener_filtros_del_perfil,
)


def agrupar_embeddings_por_pelicula(review_ids, review_embeddings):
    # Cada reseña se guardó en varios chunks (y puede haber más de una
    # reseña por película). Acá promediamos todos los vectores que
    # pertenecen a la misma película para tener un solo embedding por
    # film_id, comparable contra la Verdad Base (que también es por película).
    acumulador = defaultdict(list)
    for id_compuesto, vector in zip(review_ids, review_embeddings):
        film_id = canonicalizar_film_id(id_compuesto.split("::")[0])
        acumulador[film_id].append(vector)

    return {film_id: np.mean(vectores, axis=0) for film_id, vectores in acumulador.items()}


def obtener_embeddings_filtros(coleccion_perfiles, nombres_filtros):
    datos_perfil = coleccion_perfiles.get(include=['embeddings', 'metadatas'])

    embeddings_filtros = []
    for nombre_filtro in nombres_filtros:
        indice = None
        for i, meta in enumerate(datos_perfil['metadatas']):
            if meta['filtro'] == nombre_filtro:
                indice = i
                break

        if indice is not None:
            embeddings_filtros.append(datos_perfil['embeddings'][indice])
        else:
            # vector nulo (ortogonal) si el filtro fue eliminado del perfil
            embeddings_filtros.append([0.0] * 384)

    return np.array(embeddings_filtros)


def main():
    root_dir = Path.cwd()
    chroma_dir = root_dir / "src" / "db" / "embeddings" / "chroma"
    gt_path = root_dir / "src" / "loss" / "matriz_perdida.csv"

    if not gt_path.exists():
        print("[!] Error: No se encontró matriz_perdida.csv. Ejecuta el módulo 5 primero.")
        return

    print("Conectando con la base de datos vectorial ChromaDB...")
    cliente = chromadb.PersistentClient(path=str(chroma_dir))
    coleccion_perfiles = cliente.get_collection(name="perfiles")
    coleccion_resenias = cliente.get_collection(name="resenias")

    # Se arma dinámicamente a partir del perfil activo en perfiles.json,
    # igual que en scoring.py (ver src/normalizacion.py).
    perfil_actual = cargar_perfil_actual()
    nombres_filtros = [nombre for _, nombre in obtener_filtros_del_perfil(perfil_actual)]
    embeddings_filtros = obtener_embeddings_filtros(coleccion_perfiles, nombres_filtros)

    print("Agrupando embeddings de reseñas por película...")
    datos_resenias = coleccion_resenias.get(include=['embeddings'])
    embeddings_por_pelicula = agrupar_embeddings_por_pelicula(
        datos_resenias['ids'], datos_resenias['embeddings']
    )

    if not embeddings_por_pelicula:
        print("[!] Error: No hay reseñas vectorizadas todavía. Ejecuta el módulo 4 primero.")
        return

    print("Entrenando modelo con las películas que ya tienen Verdad Base...")
    df_gt = pd.read_csv(gt_path)
    df_gt['canon_id'] = df_gt['film_id'].apply(canonicalizar_film_id)

    embeddings_entrenamiento, y_entrenamiento, film_ids_entrenamiento = [], [], []
    peliculas_evaluadas = set(df_gt['canon_id'])

    for _, fila in df_gt.iterrows():
        canon_id = fila['canon_id']
        if canon_id in embeddings_por_pelicula:
            embeddings_entrenamiento.append(embeddings_por_pelicula[canon_id])
            y_entrenamiento.append(fila['gt_nota_global'])
            film_ids_entrenamiento.append(canon_id)

    if not y_entrenamiento:
        print("[!] Error: No se lograron cruzar las reseñas vectorizadas con el Ground Truth.")
        return

    matriz_x_entrenamiento = cosine_similarity(np.array(embeddings_entrenamiento), embeddings_filtros)

    modelo = LinearRegression()
    modelo.fit(matriz_x_entrenamiento, y_entrenamiento)

    # Predicción del modelo también sobre las que ya tienen nota de Gemini,
    # para poder comparar ambas notas en la misma lista.
    predicciones_entrenamiento = modelo.predict(matriz_x_entrenamiento)

    peliculas_candidatas = {
        film_id: vector
        for film_id, vector in embeddings_por_pelicula.items()
        if film_id not in peliculas_evaluadas
    }

    film_ids_candidatos = list(peliculas_candidatas.keys())
    if film_ids_candidatos:
        matriz_x_candidatos = cosine_similarity(np.array(list(peliculas_candidatas.values())), embeddings_filtros)
        predicciones_candidatos = modelo.predict(matriz_x_candidatos)
    else:
        predicciones_candidatos = []

    # Una sola lista con todas las películas (evaluadas + candidatas),
    # ordenada por la nota que le dio el modelo. Para las candidatas no
    # hay nota de Gemini, así que se muestra como NaN.
    resultados = list(zip(film_ids_entrenamiento, predicciones_entrenamiento, y_entrenamiento))
    resultados += [
        (film_id, nota_modelo, float('nan'))
        for film_id, nota_modelo in zip(film_ids_candidatos, predicciones_candidatos)
    ]
    resultados.sort(key=lambda fila: fila[1], reverse=True)

    print(f"\n| -- Ranking de recomendaciones ({len(resultados)} películas) -- |")
    print(f"{'Película':<30}{'Nota Modelo':>14}{'Nota de Gemini':>16}")
    for film_id, nota_modelo, nota_gemini in resultados:
        nota_gemini_str = "NaN" if np.isnan(nota_gemini) else f"{nota_gemini:.2f}"
        print(f"{film_id:<30}{nota_modelo:>14.2f}{nota_gemini_str:>16}")

    print(
        "\n* 'NaN' en 'Nota de Gemini' significa que esa película todavía no "
        "tiene una nota cargada por Gemini (no hay Verdad Base para ella)."
    )


if __name__ == '__main__':
    main()

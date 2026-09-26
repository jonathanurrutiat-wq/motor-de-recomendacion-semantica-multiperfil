"""
Genera un ranking de películas candidatas a gustarle a un perfil.

Carga el modelo entrenado y guardado por scoring.py (opción 7) y lo aplica
sobre todas las películas con reseña procesada: las que ya tienen nota de
Gemini (para comparar) y las que todavía no la tienen, ordenadas de mayor a
menor nota estimada.
"""

import chromadb
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.config import DIR_CHROMA, RUTA_GT, RUTA_MODELO
from src.normalizacion import canonicalizar_film_id
from src.scoring import cargar_embeddings_peliculas, construir_features, obtener_embeddings_perfil


def calcular_ranking() -> pd.DataFrame:
    # Aplica el modelo guardado a todas las películas con reseñas vectorizadas.
    # Lanza ValueError si falta algún paso previo.
    if not RUTA_MODELO.exists():
        raise ValueError("No hay un modelo entrenado. Ejecuta el módulo 7 primero.")

    guardado = joblib.load(RUTA_MODELO)
    if "escala" not in guardado:
        raise ValueError("El modelo guardado es de una versión anterior. Ejecuta el módulo 7 de nuevo.")

    nombre_perfil, estructura = guardado["perfil"], guardado["estructura"]
    print(f"Usando el modelo entrenado para el perfil: {nombre_perfil}")

    print("Conectando con la base de datos vectorial ChromaDB...")
    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))
    embeddings_perfil = obtener_embeddings_perfil(
        cliente.get_collection(name="perfiles"), nombre_perfil, estructura["terminos"]
    )

    # Modelos guardados antes de que se pudiera elegir el pooling usaban el promedio.
    pooling = guardado.get("pooling", "media")
    print(f"Agrupando embeddings de reseñas por película ({pooling})...")
    embeddings_por_pelicula = cargar_embeddings_peliculas(cliente, pooling)
    if not embeddings_por_pelicula:
        raise ValueError("No hay reseñas vectorizadas todavía. Ejecuta el módulo 4 primero.")

    notas_gemini = {}
    if RUTA_GT.exists():
        df_gt = pd.read_csv(RUTA_GT)
        notas_gemini = dict(zip(df_gt['film_id'].apply(canonicalizar_film_id), df_gt['gt_nota_global']))

    film_ids = list(embeddings_por_pelicula.keys())
    similitudes = cosine_similarity(np.array(list(embeddings_por_pelicula.values())), embeddings_perfil)
    matriz_x, _, _ = construir_features(similitudes, estructura, guardado["escala"])

    ranking = pd.DataFrame({
        "film_id": film_ids,
        "nota_modelo": guardado["modelo"].predict(matriz_x),
        # Para las candidatas no hay nota de Gemini, así que queda como NaN.
        "nota_gemini": [notas_gemini.get(film_id, float('nan')) for film_id in film_ids],
    })
    ranking["evaluada"] = ranking["nota_gemini"].notna()
    return ranking.sort_values("nota_modelo", ascending=False, ignore_index=True)


def main():
    try:
        ranking = calcular_ranking()
    except ValueError as error:
        print(f"[!] Error: {error}")
        return None

    print(f"\n| -- Ranking de recomendaciones ({len(ranking)} películas) -- |")
    print(f"{'Película':<30}{'Nota Modelo':>14}{'Nota de Gemini':>16}")
    for fila in ranking.itertuples():
        nota_gemini_str = "NaN" if pd.isna(fila.nota_gemini) else f"{fila.nota_gemini:.2f}"
        print(f"{fila.film_id:<30}{fila.nota_modelo:>14.2f}{nota_gemini_str:>16}")

    print(
        "\n* 'NaN' en 'Nota de Gemini' significa que esa película todavía no "
        "tiene una nota cargada por Gemini (no hay Verdad Base para ella)."
    )
    return ranking


if __name__ == '__main__':
    main()

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


def main():
    if not RUTA_MODELO.exists():
        print("[!] Error: No hay un modelo entrenado. Ejecuta el módulo 7 primero.")
        return

    guardado = joblib.load(RUTA_MODELO)
    if "estructura" not in guardado:
        print("[!] Error: El modelo guardado es de una versión anterior. Ejecuta el módulo 7 de nuevo.")
        return

    modelo = guardado["modelo"]
    nombre_perfil = guardado["perfil"]
    estructura = guardado["estructura"]
    print(f"Usando el modelo entrenado para el perfil: {nombre_perfil}")

    print("Conectando con la base de datos vectorial ChromaDB...")
    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))

    try:
        embeddings_perfil = obtener_embeddings_perfil(
            cliente.get_collection(name="perfiles"), nombre_perfil, estructura["terminos"]
        )
    except ValueError as error:
        print(f"[!] Error: {error}")
        return

    print("Agrupando embeddings de reseñas por película...")
    embeddings_por_pelicula = cargar_embeddings_peliculas(cliente)

    if not embeddings_por_pelicula:
        print("[!] Error: No hay reseñas vectorizadas todavía. Ejecuta el módulo 4 primero.")
        return

    notas_gemini = {}
    if RUTA_GT.exists():
        df_gt = pd.read_csv(RUTA_GT)
        notas_gemini = dict(zip(df_gt['film_id'].apply(canonicalizar_film_id), df_gt['gt_nota_global']))

    film_ids = list(embeddings_por_pelicula.keys())
    similitudes = cosine_similarity(np.array(list(embeddings_por_pelicula.values())), embeddings_perfil)
    matriz_x, _, _ = construir_features(similitudes, estructura, guardado["medias"])
    predicciones = modelo.predict(matriz_x)

    # Para las candidatas no hay nota de Gemini, así que se muestra como NaN.
    resultados = [
        (film_id, nota_modelo, notas_gemini.get(film_id, float('nan')))
        for film_id, nota_modelo in zip(film_ids, predicciones)
    ]
    resultados.sort(key=lambda fila: fila[1], reverse=True)

    print(f"\n| -- Ranking de recomendaciones ({len(resultados)} películas) -- |")
    print(f"{'Película':<30}{'Nota Modelo':>14}{'Nota de Gemini':>16}")
    for film_id, nota_modelo, nota_gemini in resultados:
        nota_gemini_str = "NaN" if pd.isna(nota_gemini) else f"{nota_gemini:.2f}"
        print(f"{film_id:<30}{nota_modelo:>14.2f}{nota_gemini_str:>16}")

    print(
        "\n* 'NaN' en 'Nota de Gemini' significa que esa película todavía no "
        "tiene una nota cargada por Gemini (no hay Verdad Base para ella)."
    )


if __name__ == '__main__':
    main()

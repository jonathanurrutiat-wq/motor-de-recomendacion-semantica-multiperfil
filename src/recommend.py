"""
Genera un ranking de películas candidatas a gustarle a un perfil.

Carga el modelo de reglas entrenado y guardado por scoring.py (opción 7) y lo
aplica sobre todas las películas con reseña procesada: las que ya tienen nota
de Gemini (para comparar) y las que todavía no la tienen, ordenadas de mayor
a menor nota estimada.
"""

import chromadb
import joblib
import pandas as pd

from src.config import DIR_CHROMA, rutas_perfil
from src.normalizacion import canonicalizar_film_id, seleccionar_perfil
from src.scoring import entradas_peliculas


def calcular_ranking(nombre_perfil: str) -> pd.DataFrame:
    # Aplica el modelo guardado del perfil a todas las películas con reseñas vectorizadas.
    # Lanza ValueError si falta algún paso previo.
    rutas = rutas_perfil(nombre_perfil)
    if not rutas.modelo.exists():
        raise ValueError(f"No hay un modelo entrenado para {nombre_perfil} ({rutas.modelo}). Ejecuta el módulo 7 primero.")

    guardado = joblib.load(rutas.modelo)
    if guardado.get("tipo") != "reglas":
        raise ValueError("El modelo guardado es de una versión anterior (regresión lineal). Ejecuta el módulo 7 de nuevo.")
    if guardado.get("perfil") != nombre_perfil:
        raise ValueError(f"El modelo guardado en {rutas.modelo} es del perfil '{guardado.get('perfil')}', no de "
                         f"'{nombre_perfil}'. Ejecuta el módulo 7 con este perfil.")

    modelo = guardado["modelo"]
    print(f"Usando el modelo de reglas entrenado para el perfil: {guardado['perfil']}")

    print("Conectando con la base de datos vectorial ChromaDB...")
    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))
    # Mismo pooling, frases y umbrales que al entrenar.
    entradas = entradas_peliculas(cliente, guardado["textos"], guardado["pooling"], guardado["umbrales"])

    notas_gemini = {}
    if rutas.gt.exists():
        df_gt = pd.read_csv(rutas.gt)
        notas_gemini = dict(zip(df_gt['film_id'].apply(canonicalizar_film_id), df_gt['gt_nota_global']))

    ranking = pd.DataFrame({
        "film_id": entradas["film_ids"],
        "nota_modelo": modelo.predict(entradas["X"], entradas["rasgos"]),
        # Para las candidatas no hay nota de Gemini, así que queda como NaN.
        "nota_gemini": [notas_gemini.get(film_id, float('nan')) for film_id in entradas["film_ids"]],
    })
    ranking["evaluada"] = ranking["nota_gemini"].notna()
    return ranking.sort_values("nota_modelo", ascending=False, ignore_index=True)


def main(perfil_elegido: str | None = None):
    try:
        nombre_perfil, _ = seleccionar_perfil(perfil_elegido)
        ranking = calcular_ranking(nombre_perfil)
    except (FileNotFoundError, ValueError) as error:
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

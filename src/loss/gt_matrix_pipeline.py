from pathlib import Path

import pandas as pd

from src.config import DIR_FILTRADOS, RUTA_GT, RUTA_INSTRUCCIONES, RUTA_PENDIENTES
from src.loss.ingest_maestro import filas_evaluadas, leer_csv_editado
from src.loss.instrucciones import generar_instrucciones
from src.loss.matrix import generar_matriz_vacia
from src.normalizacion import canonicalizar_film_id, seleccionar_perfil


def obtener_peliculas_con_resenias(directorio_filtrados: Path) -> set:
    # Recorre todos los csv filtrados (todos los lotes, no solo el último)
    # y arma el set de películas que ya tienen reseñas procesadas.
    archivos = list(directorio_filtrados.glob("filtrado_*.csv"))
    if not archivos:
        return set()

    peliculas = set()
    for archivo in archivos:
        df = pd.read_csv(archivo)
        if "film_id" not in df.columns:
            continue
        peliculas.update(canonicalizar_film_id(fid) for fid in df["film_id"].dropna())

    return peliculas


def obtener_peliculas_evaluadas(gt_path: Path) -> set:
    # Lee la Verdad Base ya procesada (si existe) y arma el set de
    # películas que ya fueron evaluadas a mano.
    if not gt_path.exists():
        return set()

    df_gt = pd.read_csv(gt_path)
    if "film_id" not in df_gt.columns:
        return set()

    return {canonicalizar_film_id(fid) for fid in df_gt["film_id"].dropna()}


def main(perfil_elegido=None):
    dir_filtrados = DIR_FILTRADOS
    gt_path = RUTA_GT

    print("Recolectando películas con reseñas procesadas...")
    peliculas_con_resenias = obtener_peliculas_con_resenias(dir_filtrados)

    if not peliculas_con_resenias:
        print(f"[!] No se encontraron csv 'filtrado_*.csv' en {dir_filtrados}")
        print("Ejecuta primero el pipeline ETL (opción 2) y genera reseñas filtradas.")
        return

    print("Cruzando contra la Verdad Base actual...")
    peliculas_evaluadas = obtener_peliculas_evaluadas(gt_path)

    # Álgebra de conjuntos: reseñas procesadas menos las ya evaluadas = pendientes.
    # canonicalizar_film_id() ya se aplicó a ambos lados, así que una misma
    # película nunca queda contada dos veces por culpa del sufijo de año.
    peliculas_pendientes = peliculas_con_resenias - peliculas_evaluadas

    print("\n| -- Estado de evaluación -- |")
    print(f"Películas con reseñas procesadas: {len(peliculas_con_resenias)}")
    print(f"Películas ya evaluadas (Verdad Base): {len(peliculas_evaluadas)}")
    print(f"Películas pendientes de evaluar: {len(peliculas_pendientes)}")

    if not peliculas_pendientes:
        print("\nNo hay películas pendientes. La Verdad Base está al día.")
        return

    print("\nPelículas pendientes:")
    for film_id in sorted(peliculas_pendientes):
        print(f"  - {film_id}")

    if RUTA_PENDIENTES.exists():
        sin_importar = int(filas_evaluadas(leer_csv_editado(RUTA_PENDIENTES)).sum())
        if sin_importar:
            print(f"\n[!] {RUTA_PENDIENTES.name} tiene {sin_importar} película(s) ya evaluadas que aún no se "
                  "importan. No se sobrescribe: ejecuta primero el módulo 5 para importarlas.")
            return

    try:
        nombre_perfil, perfil = seleccionar_perfil(perfil_elegido)
    except (FileNotFoundError, ValueError) as error:
        print(f"[!] Error: {error}")
        return

    # Plantilla con las columnas correctas (según los filtros/afinidades
    # del perfil elegido) para facilitar la evaluación de lo pendiente.
    plantilla = generar_matriz_vacia(perfil)
    plantilla_pendientes = pd.DataFrame({"film_id": sorted(peliculas_pendientes)})
    for columna in plantilla.columns:
        if columna != "film_id":
            plantilla_pendientes[columna] = pd.NA

    plantilla_pendientes.to_csv(RUTA_PENDIENTES, index=False, encoding="utf-8")
    RUTA_INSTRUCCIONES.write_text(
        generar_instrucciones(nombre_perfil, perfil, sorted(peliculas_pendientes)), encoding="utf-8"
    )
    print(f"\nPlantilla para evaluación guardada en: {RUTA_PENDIENTES}")
    print(f"Instrucciones para evaluar con Gemini guardadas en: {RUTA_INSTRUCCIONES}")
    print("Pega su respuesta en la plantilla (al menos gt_nota_global) y ejecuta el módulo 5 "
          "para sumarla a la Verdad Base.")


if __name__ == '__main__':
    main()

import pandas as pd
import os
from pathlib import Path
from src.loss.matrix import generar_matriz_vacia

def parse_filtered(db_folder):
    if not db_folder.exists():
        print(f"Error. No se encontró la ruta {db_folder}.")
        return
    
    csv_files = list(db_folder.glob("*.csv"))
    if not csv_files:
        print("No hay archivos filtrados pendientes en el directorio.")
        return
    
    for file in csv_files:
        # Utilizamos yield para pausar el script con cada archivo entregado
        # a matrix.py y así tanto no desperdiciar memoria como también para
        # mantener la pipeline limpia y protegida en caso de cualquier eventualidad.
        yield file

def main():
    root_dir = Path.cwd()
    db_dir = root_dir / "src" / "db" / "filtered" / "result"
    
    loss_dir = root_dir / "src" / "loss"
    matriz_csv_path = loss_dir / "matriz_perdida.csv"

    if matriz_csv_path.exists():
        matriz_perdida = pd.read_csv(matriz_csv_path)
    else:
        matriz_perdida = generar_matriz_vacia()

    file_generator = parse_filtered(db_dir)

    for file_path in file_generator:
        print(f"\nProcesando lote: {file_path.name}")

        df_lote = pd.read_csv(file_path)

        # Aquí se extraen los valores de 'film_id' únicos e ignorando nulos.

        set_lote = set(df_lote['film_id'].unique())
        set_matriz = set(matriz_perdida['film_id'].dropna().unique())

        pendientes = set_lote - set_matriz

        print(f"Encontradas {len(set_lote)} películas en el lote.")
        print(f"Películas nuevas a evaluar (ignorando ya evaluadas): {len(pendientes)}.")

        if not pendientes:
            print("Lote completamente evaluado. Pasando al siguiente...")
            continue
        
        print(f"Generando plantilla CSV para {len(pendientes)} películas pendientes...")
        # Filtramos el lote para quedarnos solo con las películas pendientes
        df_pendientes = df_lote[df_lote['film_id'].isin(pendientes)].copy()

        # Nos quedamos solo con las columnas de contexto para que el usuario sepa qué evalúa
        columnas_contexto = ['film_id', 'film_title', 'director']
        df_plantilla = df_pendientes[columnas_contexto].drop_duplicates()

        # Añadimos las columnas matemáticas vacías desde la matriz de pérdida generada
        columnas_gt = [col for col in matriz_perdida.columns if col.startswith('gt_')]
        for col in columnas_gt:
            df_plantilla[col] = pd.NA # Dejamos la celda como nula / vacía

        nombre_plantilla = f"por_evaluar_{file_path.name}.csv"
        ruta_plantilla = loss_dir / nombre_plantilla

        df_plantilla.to_csv(ruta_plantilla, index=False, encoding='utf-8')
        print(f"Plantilla creada exitósamente en: {ruta_plantilla.name}")
        print("-> Ábrela en Excel/Sheets, rellena las columnas 'gt_' y guárdala con el prefijo 'evaluado_'.")


if __name__ == '__main__':
    main()
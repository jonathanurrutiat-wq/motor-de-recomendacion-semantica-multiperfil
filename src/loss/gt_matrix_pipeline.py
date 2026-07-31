import pandas as pd
from pathlib import Path
from matrix import generar_matriz_vacia

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
    curr_dir = Path(__file__).resolve().parent
    db_dir = curr_dir.parent / "db" / "filtered" / "result"
    matriz_csv_path = curr_dir / "matriz_perdida.csv"

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
        
        # ... Código del oráculo para evaluar pendientes...

if __name__ == '__main__':
    main()
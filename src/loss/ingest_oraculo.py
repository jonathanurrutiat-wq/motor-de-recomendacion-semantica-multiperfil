import pandas as pd
import sqlite3
import os
from pathlib import Path

def main():
    root_dir = Path.cwd()
    loss_dir = root_dir / "src" / "loss"

    archivos_evaluados = list(loss_dir.glob("evaluado_*.csv"))
    if not archivos_evaluados:
        print("No se encontraron planillas evaluadas para ingestar.")
        return

    db_path = loss_dir / "ground_truth.db"
    conexion_sql = sqlite3.connect(db_path)

    for archivo in archivos_evaluados:
        print(f"Ingestando archivos en SQL: {archivo.name}...")

        # Leemos el CSV relleno
        df_evaluado = pd.read_csv(archivo)

        # Escribimos los datos en una tabla SQL donde
        # if_exists='append' añade nuevas filas sin borrar las anteriores.
        df_evaluado.to_sql('matriz_perdida', con=conexion_sql, if_exists='append', index=False)
        print(f"-> Datos evaluados de {len(df_evaluado)} películas insertados en la tabla 'matriz_perdida'.")

        archivo.rename(loss_dir / f"procesado_{archivo.name}")

    print("\n| -- Verificación de integridad SQL -- |")
    query = "SELECT film_id, film_title, gt_nota_global FROM matriz_perdida LIMIT 5;"
    df_verificacion = pd.read_sql_query(query, con=conexion_sql)
    print(df_verificacion)

    conexion_sql.close()

if __name__ == '__main__':
    main()
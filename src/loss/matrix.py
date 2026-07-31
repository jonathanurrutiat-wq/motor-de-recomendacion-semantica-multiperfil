import pandas as pd
from pathlib import Path
import json

def generar_matriz_vacia():
    curr_dir = Path(__file__).resolve().parent
    prfs_file = curr_dir.parent.parent / "perfiles.json"

    with open(prfs_file, "r", encoding="utf-8") as file:
        prfs_data = json.load(file)

    get_cols = ["film_id"]

    prf_name = next(iter(prfs_data))
    prf_curr = prfs_data[prf_name]
    
    if "restrictivos" in prf_curr:
        for nombre_filtro in prf_curr["restrictivos"].keys():
            col_name = f"gt_cols_{nombre_filtro.lower().replace(' ', '_')}"
            get_cols.append(col_name)
    
    if "afinidad" in prf_curr:
        for nombre_afinidad in prf_curr["afinidad"].keys():
            col_name = f"gt_afinidad_{nombre_afinidad.lower().replace(' ', '_')}"
            get_cols.append(col_name)

    get_cols.append("gt_nota_global")
    return pd.DataFrame(columns=get_cols)

def main():
    # Únicamente para testear si se ejecuta el código correctamente.
    matriz_prueba = generar_matriz_vacia()
    print("Matriz generada con las siguientes columnas:")
    for col in matriz_prueba.columns:
        print(f"| - {col}")

if __name__ == '__main__':
    main()
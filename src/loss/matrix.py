import pandas as pd
from pathlib import Path
import json

def generar_matriz_vacia():
    prfs_file = Path.cwd() / "perfiles.json"

    # Guarda de seguridad por si el JSON aún no ha sido creado
    if not prfs_file.exists():
        print(f"\n[!] Error crítico: No se encontró el archivo en {prfs_file}")
        print("Por favor, asegúrate de crear un perfil (Opción 1) antes de evaluar películas.")
        return pd.DataFrame(columns=["film_id", "gt_nota_global"])

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
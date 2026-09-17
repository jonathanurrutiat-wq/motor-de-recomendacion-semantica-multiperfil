import pandas as pd
from pathlib import Path
import json

from src.normalizacion import nombre_columna_gt, obtener_filtros_del_perfil

def generar_matriz_vacia():
    prfs_file = Path.cwd() / "src" / "db" / "profiles" / "perfiles.json"

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

    for tipo_categoria, nombre_filtro in obtener_filtros_del_perfil(prf_curr):
        get_cols.append(nombre_columna_gt(tipo_categoria, nombre_filtro))

    get_cols.append("gt_nota_global")
    return pd.DataFrame(columns=get_cols)
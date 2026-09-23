import pandas as pd

from src.normalizacion import nombre_columna_gt, obtener_filtros_del_perfil, seleccionar_perfil


def generar_matriz_vacia():
    try:
        _, prf_curr = seleccionar_perfil()
    except (FileNotFoundError, ValueError) as error:
        print(f"\n[!] Error crítico: {error}")
        return pd.DataFrame(columns=["film_id", "gt_nota_global"])

    get_cols = ["film_id"]
    for tipo_categoria, nombre_filtro in obtener_filtros_del_perfil(prf_curr):
        get_cols.append(nombre_columna_gt(tipo_categoria, nombre_filtro))

    get_cols.append("gt_nota_global")
    return pd.DataFrame(columns=get_cols)

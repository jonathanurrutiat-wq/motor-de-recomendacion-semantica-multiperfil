import pandas as pd

from src.normalizacion import columnas_evaluacion


def generar_matriz_vacia(perfil: dict) -> pd.DataFrame:
    return pd.DataFrame(columns=["film_id"] + columnas_evaluacion(perfil))

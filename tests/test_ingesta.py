import pandas as pd

from src.loss.ingest_maestro import a_numerico, mapear_encabezados


def test_mapear_encabezados_usa_el_encabezado_o_el_nombre():
    perfil = {"restrictivos": {"Insoportabilidad Prolongada": {"encabezado": "Insoport."}},
              "afinidad": {"Ternura": {}}}
    mapeo, excepciones, faltantes = mapear_encabezados(perfil, ["Película", "Insoport.", "Ternura", "Global"])
    assert mapeo["Insoport."] == "gt_cols_insoportabilidad_prolongada"
    assert mapeo["Ternura"] == "gt_afinidad_ternura"
    assert mapeo["Global"] == "gt_nota_global"
    assert excepciones == {"Insoport.": "gt_excepcion_insoportabilidad_prolongada"}
    assert faltantes == []


def test_mapear_encabezados_informa_faltantes():
    perfil = {"restrictivos": {"Caos": {"encabezado": "Caos*"}}, "afinidad": {}}
    _, _, faltantes = mapear_encabezados(perfil, ["Global"])
    assert faltantes == ["'Caos*' (Caos)"]


def test_a_numerico_acepta_asterisco_y_coma():
    assert a_numerico(pd.Series(["8,5", "3*", "x"])).tolist()[:2] == [8.5, 3.0]

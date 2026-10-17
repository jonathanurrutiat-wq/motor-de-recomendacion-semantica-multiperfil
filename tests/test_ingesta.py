import pandas as pd

from src.loss.ingest_maestro import NOTA_REPROBADA, a_numerico, mapear_encabezados


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


def test_a_numerico_convierte_reprobada():
    assert a_numerico(pd.Series(["REPROBADA", "reprobada ", "2.5"])).tolist() == [NOTA_REPROBADA, NOTA_REPROBADA, 2.5]


def test_lista_evaluadas_sin_resenias(tmp_path, monkeypatch):
    from src.loss import gt_matrix_pipeline as opcion_6
    gt = tmp_path / "matriz.csv"
    pd.DataFrame({"film_id": ["elvis-2022", "persona", "toy-story-3"],
                  "film_title": ["Elvis (2022)", "Persona", "Toy Story 3 (2010)"]}).to_csv(gt, index=False)
    salida = tmp_path / "pendientes_resenias.csv"
    monkeypatch.setattr(opcion_6, "RUTA_SIN_RESENIAS", salida)
    # Las reseñas de Elvis vienen con otro sufijo de año: igual cuenta como con reseñas.
    assert opcion_6.guardar_evaluadas_sin_resenias(gt, {"elvis", "persona"}) == 1
    assert pd.read_csv(salida)["film_slug"].tolist() == ["toy-story-3"]

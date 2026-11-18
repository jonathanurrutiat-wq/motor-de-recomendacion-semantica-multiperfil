import json

import pandas as pd
import pytest

from src import config
from src.config import rutas_perfil, slug_perfil


def test_slug_quita_tildes_y_separa_con_guion_bajo():
    assert slug_perfil("Ignacio Araya") == "ignacio_araya"
    assert slug_perfil("Matías Fuentes") == "matias_fuentes"
    assert slug_perfil("  Ñandú Pérez-López ") == "nandu_perez_lopez"


def test_rutas_viven_en_la_carpeta_perfil_nombre():
    rutas = rutas_perfil("Camila Rojas")
    assert rutas.carpeta == config.LOSS_DIR / "perfil_camila_rojas"
    for ruta in (rutas.dataset_maestro, rutas.adicionales, rutas.pendientes, rutas.instrucciones,
                 rutas.sin_resenias, rutas.gt, rutas.modelo):
        assert ruta.parent == rutas.carpeta
    assert rutas.gt.name == "matriz_perdida.csv"
    assert rutas.sin_resenias.name == "pendientes_resenias.csv"
    assert rutas.modelo.name.startswith("modelo_reglas") and rutas.modelo.suffix == ".joblib"


def test_perfiles_distintos_no_comparten_ningun_archivo():
    a, b = rutas_perfil("Ignacio Araya"), rutas_perfil("Matías Fuentes")
    assert not set(a) & set(b)


def test_nombre_sin_letras_ni_numeros_se_rechaza():
    with pytest.raises(ValueError):
        rutas_perfil("¡¿?!")


# --- Opción 5 con varios perfiles: cada uno trabaja solo en su carpeta -----------------

PERFILES = {
    "Perfil Uno": {"restrictivos": {"Rancia": {"encabezado": "Rancia"}}, "afinidad": {"Ternura": {}}},
    "Perfil Dos": {"restrictivos": {"Rancia": {"encabezado": "Rancia"}}, "afinidad": {"Ternura": {}}},
}
COLUMNAS = ["film_id", "gt_cols_rancia", "gt_excepcion_rancia", "gt_afinidad_ternura", "gt_nota_global"]


@pytest.fixture
def proyecto(tmp_path, monkeypatch):
    # Una carpeta src/loss y un perfiles.json de mentira, para no tocar los reales.
    json_perfiles = tmp_path / "perfiles.json"
    json_perfiles.write_text(json.dumps(PERFILES), encoding="utf-8")
    monkeypatch.setattr(config, "LOSS_DIR", tmp_path / "loss")
    monkeypatch.setattr("src.normalizacion.RUTA_PERFILES", json_perfiles)
    return tmp_path


def test_opcion_5_con_planilla_y_evaluaciones_adicionales(proyecto):
    from src.loss.ingest_maestro import main
    rutas = rutas_perfil("Perfil Uno")
    rutas.carpeta.mkdir(parents=True)
    pd.DataFrame({"Película": ["1. Persona (1966)", "Elvis (2022)"], "film_slug": ["persona", "elvis"],
                  "Rancia": ["0", "3*"], "Ternura": ["8", "5"], "Global": ["9", "6"]}).to_csv(rutas.dataset_maestro, index=False)
    pd.DataFrame([["toy-story-3", 1, 0, 7, 8]], columns=COLUMNAS).to_csv(rutas.adicionales, index=False)

    main("Perfil Uno")

    gt = pd.read_csv(rutas.gt)
    assert gt["film_id"].tolist() == ["persona", "elvis", "toy-story-3"]
    assert gt["gt_nota_global"].tolist() == [9, 6, 8]
    # El asterisco de la planilla marca que la excepción del filtro aplica a esa película.
    assert gt["gt_excepcion_rancia"].tolist()[:2] == [0.0, 1.0]


def test_opcion_5_sin_planilla_usa_solo_las_evaluaciones_adicionales(proyecto):
    from src.loss.ingest_maestro import main
    rutas = rutas_perfil("Perfil Dos")
    rutas.carpeta.mkdir(parents=True)
    pd.DataFrame([["persona", 0, 0, 8, 9], ["elvis-2022", 3, 1, 5, 6]], columns=COLUMNAS).to_csv(rutas.adicionales, index=False)

    main("Perfil Dos")

    gt = pd.read_csv(rutas.gt)
    assert gt["film_id"].tolist() == ["persona", "elvis-2022"]
    assert gt.columns[:2].tolist() == ["film_id", "film_title"]
    assert gt["gt_nota_global"].tolist() == [9, 6]


def test_opcion_5_importa_las_evaluadas_de_la_plantilla(proyecto):
    from src.loss.ingest_maestro import main
    rutas = rutas_perfil("Perfil Dos")
    rutas.carpeta.mkdir(parents=True)
    pd.DataFrame([["persona", 0, 0, 8, 9]], columns=COLUMNAS).to_csv(rutas.adicionales, index=False)
    plantilla = pd.DataFrame([["elvis", 3, 1, 5, 6], ["toy-story-3", None, None, None, None]], columns=COLUMNAS)
    plantilla.to_csv(rutas.pendientes, index=False)

    main("Perfil Dos")

    assert pd.read_csv(rutas.gt)["film_id"].tolist() == ["persona", "elvis"]
    # La no evaluada sigue pendiente; la evaluada pasó a las adicionales.
    assert pd.read_csv(rutas.pendientes)["film_id"].tolist() == ["toy-story-3"]
    assert pd.read_csv(rutas.adicionales)["film_id"].tolist() == ["persona", "elvis"]


def test_opcion_5_de_un_perfil_no_toca_los_archivos_de_otro(proyecto):
    from src.loss.ingest_maestro import main
    uno, dos = rutas_perfil("Perfil Uno"), rutas_perfil("Perfil Dos")
    for rutas, film in ((uno, "persona"), (dos, "elvis")):
        rutas.carpeta.mkdir(parents=True)
        pd.DataFrame([[film, 0, 0, 8, 9]], columns=COLUMNAS).to_csv(rutas.adicionales, index=False)

    main("Perfil Uno")
    assert uno.gt.exists() and not dos.gt.exists()
    gt_uno = uno.gt.read_bytes()

    main("Perfil Dos")
    assert pd.read_csv(dos.gt)["film_id"].tolist() == ["elvis"]
    assert uno.gt.read_bytes() == gt_uno


def test_opcion_5_sin_datos_del_perfil_avisa_y_no_crea_nada(proyecto, capsys):
    from src.loss.ingest_maestro import main
    rutas = rutas_perfil("Perfil Uno")

    main("Perfil Uno")

    assert "no se encontró" in capsys.readouterr().out
    assert not rutas.carpeta.exists()


def test_opcion_6_guarda_sus_archivos_en_la_carpeta_del_perfil(proyecto, monkeypatch):
    from src.loss import gt_matrix_pipeline as opcion_6
    filtrados = proyecto / "filtrados"
    filtrados.mkdir()
    pd.DataFrame({"film_id": ["persona", "elvis", "toy-story-3"]}).to_csv(filtrados / "filtrado_reviews_x.csv", index=False)
    monkeypatch.setattr(opcion_6, "DIR_FILTRADOS", filtrados)
    uno = rutas_perfil("Perfil Uno")
    uno.carpeta.mkdir(parents=True)
    # Verdad Base de Perfil Uno: "persona" tiene reseñas; "nickel-boys" está evaluada pero no tiene.
    pd.DataFrame([["persona", 0, 0, 8, 9], ["nickel-boys", 0, 0, 7, 8]], columns=COLUMNAS).to_csv(uno.gt, index=False)

    opcion_6.main("Perfil Uno")

    assert pd.read_csv(uno.pendientes)["film_id"].tolist() == ["elvis", "toy-story-3"]
    assert uno.instrucciones.read_text(encoding="utf-8").startswith("# Instrucciones de evaluación — perfil Perfil Uno")
    assert pd.read_csv(uno.sin_resenias)["film_slug"].tolist() == ["nickel-boys"]
    # Otro perfil, que aún no tiene datos, no recibe archivos ajenos.
    assert not rutas_perfil("Perfil Dos").carpeta.exists()


def test_opcion_6_de_un_perfil_nuevo_deja_todas_las_peliculas_pendientes(proyecto, monkeypatch):
    from src.loss import gt_matrix_pipeline as opcion_6
    filtrados = proyecto / "filtrados"
    filtrados.mkdir()
    pd.DataFrame({"film_id": ["persona", "elvis"]}).to_csv(filtrados / "filtrado_reviews_x.csv", index=False)
    monkeypatch.setattr(opcion_6, "DIR_FILTRADOS", filtrados)

    opcion_6.main("Perfil Dos")

    assert pd.read_csv(rutas_perfil("Perfil Dos").pendientes)["film_id"].tolist() == ["elvis", "persona"]

from src.normalizacion import (canonicalizar_film_id, columnas_evaluacion, nombre_columna_excepcion,
                               nombre_columna_gt, parse_film_id)


def test_parse_film_id():
    assert parse_film_id("1. In the Mood for Love (2000)") == "in-the-mood-for-love"
    assert parse_film_id("Kiki's Delivery Service") == "kikis-delivery-service"


def test_canonicalizar_quita_solo_el_anio_final():
    assert canonicalizar_film_id("sinners-2025") == "sinners"
    assert canonicalizar_film_id("2046") == "2046"
    assert canonicalizar_film_id("blade-runner-2049") == "blade-runner"  # el año se confunde con el título


def test_nombres_de_columnas():
    assert nombre_columna_gt("afinidad", "Humanismo Social") == "gt_afinidad_humanismo_social"
    assert nombre_columna_gt("restrictivos", "Caos Asfixiante") == "gt_cols_caos_asfixiante"
    assert nombre_columna_excepcion("Caos Asfixiante") == "gt_excepcion_caos_asfixiante"


def test_columnas_evaluacion_pone_la_excepcion_junto_a_su_filtro():
    perfil = {"restrictivos": {"Caos": {"descripcion": "x"}}, "afinidad": {"Ternura": {"descripcion": "y"}}}
    columnas = columnas_evaluacion(perfil)
    assert columnas.index("gt_excepcion_caos") == columnas.index("gt_cols_caos") + 1
    assert columnas[-1] == "gt_nota_global"

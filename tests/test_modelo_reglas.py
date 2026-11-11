import numpy as np
import pandas as pd
import pytest

from src.modelo_reglas import ModeloDosEtapas, ReglaGlobal, evaluar, sigmoide, subconjunto_rasgos


def datos_regla(n=300, semilla=0):
    rng = np.random.default_rng(semilla)
    A = rng.uniform(0, 10, (n, 2))
    F = rng.uniform(0, 10, (n, 1))
    E = (rng.random((n, 1)) < 0.2).astype(float)
    y = 2 + 0.3 * A[:, 0] + 0.2 * A[:, 1] - 3 * sigmoide(1.5 * (F[:, 0] - 6)) * (1 - E[:, 0])
    return A, F, E, y + rng.normal(0, 0.05, n)


def test_regla_recupera_umbral_y_desplome():
    A, F, E, y = datos_regla()
    regla = ReglaGlobal(["a1", "a2"], ["f1"], []).fit(A, F, E, y)
    assert np.mean(np.abs(regla.predict(A, F, E) - y)) < 0.1
    filtro = regla.parametros()["filtros"]["f1"]
    assert filtro["umbral"] == pytest.approx(6, abs=0.5)
    assert filtro["desplome"] == pytest.approx(3, abs=0.5)


@pytest.mark.parametrize("n_a, n_f", [(1, 0), (3, 2), (6, 5)])
def test_regla_generica_en_cantidad_de_criterios(n_a, n_f):
    rng = np.random.default_rng(1)
    A, F, E = rng.uniform(0, 10, (80, n_a)), rng.uniform(0, 10, (80, n_f)), np.zeros((80, n_f))
    regla = ReglaGlobal([f"a{i}" for i in range(n_a)], [f"f{i}" for i in range(n_f)], []).fit(A, F, E, rng.uniform(5, 9, 80))
    assert regla.n_parametros() == 1 + n_a + 2 * n_f
    assert regla.predict(A, F, E).shape == (80,)


def perfil_y_verdad_base(n=60, semilla=0):
    rng = np.random.default_rng(semilla)
    perfil = {"afinidad": {"Ternura": {"descripcion": "x"}}, "restrictivos": {"Caos": {"descripcion": "y", "excepcion": "z"}}}
    embeddings = rng.normal(size=(n, 12))
    gt = pd.DataFrame({
        "film_id": [f"peli-{i}" for i in range(n)],
        "gt_afinidad_ternura": np.clip(6 + 2 * embeddings[:, 0], 0, 10),
        "gt_cols_caos": np.clip(3 + 3 * embeddings[:, 1], 0, 10),
        "gt_excepcion_caos": (embeddings[:, 2] > 1).astype(float),
    })
    gt["gt_nota_global"] = 3 + 0.6 * gt["gt_afinidad_ternura"] - 2 * sigmoide(1.5 * (gt["gt_cols_caos"] - 5)) * (1 - gt["gt_excepcion_caos"])
    gt["canon_id"] = gt["film_id"]
    return perfil, gt, embeddings


@pytest.mark.parametrize("modo", ["concatenar", "ponderar", "solo_frases"])
def test_modelo_dos_etapas_con_rasgos(modo):
    perfil, gt, X = perfil_y_verdad_base()
    rasgos = {"gt_cols_caos": np.column_stack([X[:, 1], X[:, 1] ** 2])}
    modelo = ModeloDosEtapas(["Ternura"], ["Caos"], [], modo).fit(X, gt, gt, gt["gt_nota_global"].to_numpy(), rasgos)
    pred = modelo.predict(X, rasgos)
    assert pred.shape == (60,)
    puntajes = modelo.predecir_puntajes(X, rasgos)
    assert puntajes["gt_excepcion_caos"].between(0, 1).all()
    assert puntajes["gt_cols_caos"].between(0, 10).all()


def test_modo_desconocido():
    with pytest.raises(ValueError):
        ModeloDosEtapas(["a"], ["f"], [], "otro")


def test_subconjunto_rasgos():
    rasgos = {"c": np.arange(10).reshape(5, 2)}
    assert subconjunto_rasgos(None, [0]) is None
    np.testing.assert_array_equal(subconjunto_rasgos(rasgos, [1, 3])["c"], [[2, 3], [6, 7]])


def test_evaluar_promedia_repeticiones():
    perfil, gt, X = perfil_y_verdad_base()
    resultado = evaluar(perfil, gt, list(gt["film_id"]), X, 5, semillas=(0, 1))
    metricas = resultado["metricas"]
    assert metricas["repeticiones"] == 2
    assert {"spearman", "mae", "ndcg@10", "precision@10"} <= set(metricas["completo"])
    # Las notas dependen de los embeddings, así que el modelo debe ordenar mejor que el azar.
    assert metricas["completo"]["spearman"] > 0.3
    assert resultado["pred_cv"].shape == (60,)

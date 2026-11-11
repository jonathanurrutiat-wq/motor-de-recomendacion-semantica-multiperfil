import numpy as np
import pytest

from src.metricas import K_RANKING, al_azar, metricas, metricas_linea_base, ndcg, precision_top

NDCG, PRECISION = f"ndcg@{K_RANKING}", f"precision@{K_RANKING}"


@pytest.fixture
def notas():
    return np.round(np.random.default_rng(0).uniform(4, 10, 60) * 2) / 2


def test_orden_perfecto(notas):
    m = metricas(notas, notas + 0.1)
    assert m["spearman"] == pytest.approx(1)
    assert m[NDCG] == pytest.approx(1)
    assert m[PRECISION] == pytest.approx(1)


def test_orden_invertido(notas):
    assert metricas(notas, -notas)["spearman"] == pytest.approx(-1)


def test_prediccion_constante_equivale_al_azar(notas):
    m = metricas(notas, np.full(len(notas), 7.0))
    assert m["spearman"] == 0
    assert m[NDCG] == pytest.approx(al_azar(notas)[NDCG])


def test_al_azar_coincide_con_simulacion(notas):
    rng = np.random.default_rng(1)
    simulado = np.mean([ndcg(notas, rng.random(len(notas))) for _ in range(3000)])
    assert simulado == pytest.approx(al_azar(notas)[NDCG], abs=0.01)
    simulado = np.mean([precision_top(notas, rng.random(len(notas))) for _ in range(3000)])
    assert simulado == pytest.approx(al_azar(notas)[PRECISION], abs=0.01)


def test_precision_con_empates_en_el_corte():
    y = np.array([10, 9, 9, 9, 1, 1, 1, 1, 1, 1, 1, 1], float)
    # Las 4 mejores son relevantes (tres empatadas en el corte con k=2).
    # Primeras según la predicción: una empatada en el corte (relevante) y una irrelevante.
    assert precision_top(y, np.array([0, 9, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0], float), k=2) == 0.5
    assert precision_top(y, np.array([9, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0], float), k=2) == 1.0


def test_linea_base_usa_valores_al_azar(notas):
    # Promedios por partición distintos no deben contar como un orden.
    pred = np.where(np.arange(len(notas)) < 30, 8.0, 8.1)
    assert metricas_linea_base(notas, pred)["spearman"] == 0

"""
Métricas para comparar modelos: error de la nota predicha y calidad del
ranking que produce. Para recomendar importa sobre todo el orden, y en
particular qué películas quedan arriba.
"""

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

K_RANKING = 10


def _ganancias(y_real):
    # La peor película evaluada aporta 0: con notas entre 5 y 9, usar la nota
    # tal cual haría que cualquier orden pareciera casi perfecto.
    return y_real - y_real.min()


def _pesos(k):
    return 1.0 / np.log2(np.arange(2, k + 2))


def ndcg(y_real, y_pred, k: int = K_RANKING) -> float:
    # 1 si las k primeras según la predicción son las k mejores según Gemini,
    # en ese orden; pesa más acertar arriba de la lista.
    y_real, y_pred = np.asarray(y_real, float), np.asarray(y_pred, float)
    k = min(k, len(y_real))
    ganancias, pesos = _ganancias(y_real), _pesos(k)
    ideal = np.sort(ganancias)[::-1][:k] @ pesos
    if ideal == 0:
        return float("nan")
    return float(ganancias[np.argsort(-y_pred, kind="stable")[:k]] @ pesos / ideal)


def precision_top(y_real, y_pred, k: int = K_RANKING) -> float:
    # Fracción de las k primeras según la predicción que están entre las k
    # mejores según Gemini (con empates en el corte, entran todas las empatadas).
    y_real, y_pred = np.asarray(y_real, float), np.asarray(y_pred, float)
    k = min(k, len(y_real))
    relevantes = y_real >= np.sort(y_real)[::-1][k - 1]
    return float(relevantes[np.argsort(-y_pred, kind="stable")[:k]].mean())


def al_azar(y_real, k: int = K_RANKING) -> dict:
    # Valor esperado de las métricas de ranking con un orden al azar.
    y_real = np.asarray(y_real, float)
    k = min(k, len(y_real))
    ganancias, pesos = _ganancias(y_real), _pesos(k)
    ideal = np.sort(ganancias)[::-1][:k] @ pesos
    relevantes = y_real >= np.sort(y_real)[::-1][k - 1]
    return {"spearman": 0.0, f"ndcg@{K_RANKING}": float(ganancias.mean() * pesos.sum() / ideal) if ideal else float("nan"),
            f"precision@{K_RANKING}": float(relevantes.mean())}


def metricas(y_real, y_pred) -> dict:
    y_real, y_pred = np.asarray(y_real, float), np.asarray(y_pred, float)
    resultado = {
        "mse": float(mean_squared_error(y_real, y_pred)),
        "mae": float(mean_absolute_error(y_real, y_pred)),
        "r2": float(r2_score(y_real, y_pred)),
    }
    if np.ptp(y_pred) == 0:
        # Una predicción constante (la línea base) no ordena: equivale al azar.
        return {**resultado, **al_azar(y_real)}
    return {
        **resultado,
        "spearman": float(spearmanr(y_real, y_pred)[0]),
        f"ndcg@{K_RANKING}": ndcg(y_real, y_pred),
        f"precision@{K_RANKING}": precision_top(y_real, y_pred),
    }


def metricas_linea_base(y_real, y_pred) -> dict:
    # La línea base predice el promedio de cada partición de entrenamiento: el
    # orden que eso genera entre particiones es arbitrario, así que sus métricas
    # de ranking son las de un orden al azar.
    return {**metricas(y_real, y_pred), **al_azar(y_real)}

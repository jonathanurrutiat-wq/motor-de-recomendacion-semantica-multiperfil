"""
Cálculos del informe que necesitan la base de embeddings de reseñas: las
predicciones de validación cruzada por película, el ejemplo guiado y la curva
de aprendizaje. Solo escribe datos agregados (ids de películas, puntajes y
métricas, ningún texto de reseñas), igual que la opción 9.

El workflow de análisis lo corre con e5 después de la opción 9 y publica la
salida junto al análisis en la rama resultados-analisis; esos archivos se
copian a docs/informe/datos/ antes de correr tablas.py y figuras.py.

Uso, desde la raíz del repositorio y con la opción 9 ya ejecutada:
    python docs/informe/calculos.py <carpeta de salida>
"""

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ)]

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.model_selection import KFold  # noqa: E402

from src.modelo_reglas import (PENDIENTE, ModeloDosEtapas, criterios_del_perfil,  # noqa: E402
                               matrices_puntajes, sigmoide, subconjunto_rasgos)
from src.normalizacion import canonicalizar_film_id, nombre_columna_gt  # noqa: E402
from src.scoring import entrenar_reglas  # noqa: E402

NOMBRE_PERFIL = "Ignacio Araya"
PELICULA_EJEMPLO = "manhattan"
FRACCIONES_CURVA = (0.25, 0.5, 0.75, 1.0)
SEMILLAS_CURVA = range(10)


def main(salida: Path):
    salida.mkdir(parents=True, exist_ok=True)
    perfil = json.load(open(RAIZ / "src" / "db" / "profiles" / "perfiles.json"))[NOMBRE_PERFIL]
    inicio = time.time()
    res = entrenar_reglas(NOMBRE_PERFIL, perfil)
    ev, e = res["evaluacion"], res["entradas"]
    pos = {f: i for i, f in enumerate(e["film_ids"])}
    idx = [pos[f] for f in res["film_ids"]]
    X, rasgos = e["X"][idx], subconjunto_rasgos(e["rasgos"], idx)
    gt = pd.read_csv(RAIZ / "src" / "loss" / "matriz_perdida.csv")
    gt["canon_id"] = gt["film_id"].apply(canonicalizar_film_id)
    ig = {c: i for i, c in enumerate(gt["canon_id"])}
    punt = gt.iloc[[ig[f] for f in res["film_ids"]]].reset_index(drop=True)
    y = punt["gt_nota_global"].to_numpy(float)
    print("Evaluación lista", round(time.time() - inicio), "s")

    # 1) Predicciones de validación cruzada (promedio de las repeticiones) por película.
    pd.DataFrame({"film_id": res["film_ids"], "nota_gemini": y, "nota_cv": ev["pred_cv"]}).to_csv(salida / "cv_e5.csv", index=False)

    # 2) Ejemplo guiado, con un modelo entrenado sin la película.
    afin, filt, corr, _ = criterios_del_perfil(perfil, gt.columns)
    A, F, E = matrices_puntajes(gt, afin, filt)
    comp = ~(np.isnan(A).any(1) | np.isnan(F).any(1) | gt["gt_nota_global"].isna().to_numpy())
    gc = gt[comp].reset_index(drop=True)
    y2 = gc["gt_nota_global"].to_numpy(float)
    k = res["film_ids"].index(PELICULA_EJEMPLO)
    resto = np.array([i for i in range(len(y)) if i != k])
    sin_ejemplo = (gc["canon_id"] != PELICULA_EJEMPLO).to_numpy()
    modelo = ModeloDosEtapas(afin, filt, corr, "ponderar").fit(
        X[resto], punt.iloc[resto], gc[sin_ejemplo], y2[sin_ejemplo], subconjunto_rasgos(rasgos, resto))
    pred_punt = modelo.predecir_puntajes(X[[k]], subconjunto_rasgos(rasgos, [k])).iloc[0]
    nota = float(modelo.predict(X[[k]], subconjunto_rasgos(rasgos, [k]))[0])
    p = modelo.regla.parametros()
    Ap, Fp, Ep = matrices_puntajes(pred_punt.to_frame().T, afin, filt)
    detalle = {"sesgo": p["sesgo"], "afinidades": [], "filtros": []}
    for i, n in enumerate(afin):
        detalle["afinidades"].append({"criterio": n, "gemini": float(punt.loc[k, nombre_columna_gt("afinidad", n)]),
                                      "predicho": float(Ap[0, i]), "peso": p["afinidades"][n]["peso"],
                                      "aporte": float(Ap[0, i] * p["afinidades"][n]["peso"])})
    for i, n in enumerate(filt):
        q = p["filtros"][n]
        activo = float(sigmoide(PENDIENTE * (Fp[0, i] - q["umbral"])) * (1 - Ep[0, i]))
        col_e = f"gt_excepcion_{nombre_columna_gt('restrictivos', n).replace('gt_cols_', '')}"
        detalle["filtros"].append({"criterio": n, "gemini": float(punt.loc[k, nombre_columna_gt("restrictivos", n)]),
                                   "gemini_excepcion": float(punt[col_e].iloc[k]) if col_e in punt else None,
                                   "predicho": float(Fp[0, i]), "excepcion_predicha": float(Ep[0, i]),
                                   "umbral": q["umbral"], "desplome": q["desplome"], "activacion": activo,
                                   "descuento": activo * q["desplome"]})
    detalle.update(nota_modelo=nota, nota_gemini=float(y[k]), n_chunks=int(len(e["chunks"][PELICULA_EJEMPLO][1])),
                   n_resenias=int(len(set(e["chunks"][PELICULA_EJEMPLO][0]))))
    # Rasgos de frases de Insoportabilidad de la película contra la mediana de las películas.
    col = nombre_columna_gt("restrictivos", "Insoportabilidad Prolongada")
    nombres, m = res["textos"][col][0], rasgos[col]
    detalle["frases_insoportabilidad"] = [{"texto": t, "fraccion_manhattan": float(m[k, j]), "fraccion_mediana": float(np.median(m[:, j])),
                                           "percentil_manhattan": float((m[:, j] < m[k, j]).mean() * 100)} for j, t in enumerate(nombres)]
    detalle["cv_nota"] = float(ev["pred_cv"][k])
    json.dump(detalle, open(salida / "ejemplo_manhattan.json", "w"), indent=1, ensure_ascii=False)
    print("Ejemplo listo", round(time.time() - inicio), "s")

    # 3) Curva de aprendizaje: fracción de las particiones de entrenamiento.
    filas = []
    for frac in FRACCIONES_CURVA:
        for semilla in SEMILLAS_CURVA:
            rng = np.random.default_rng(100 + semilla)
            pred = np.empty(len(y))
            for tr, te in KFold(5, shuffle=True, random_state=semilla).split(X):
                sub = np.sort(rng.choice(tr, max(10, int(round(frac * len(tr)))), replace=False))
                en2 = gc["canon_id"].isin(set(np.asarray(res["film_ids"])[sub])).to_numpy()
                mod = ModeloDosEtapas(afin, filt, corr, "ponderar").fit(
                    X[sub], punt.iloc[sub], gc[en2], y2[en2], subconjunto_rasgos(rasgos, sub))
                pred[te] = mod.predict(X[te], subconjunto_rasgos(rasgos, te))
            filas.append({"fraccion": frac, "n_entrenamiento": int(round(frac * len(y) * 0.8)), "semilla": semilla,
                          "rho": float(spearmanr(y, pred)[0]), "mae": float(np.mean(np.abs(y - pred)))})
        print("Curva", frac, round(time.time() - inicio), "s")
    pd.DataFrame(filas).to_csv(salida / "curva_aprendizaje.csv", index=False)
    print("Cálculos del informe listos", round(time.time() - inicio), "s")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python docs/informe/calculos.py <carpeta de salida>")
    main(Path(sys.argv[1]))

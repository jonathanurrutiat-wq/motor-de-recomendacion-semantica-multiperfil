"""
Genera las figuras del informe (docs/informe/figuras/*.pdf) a partir de los
datos agregados de docs/informe/datos/ y de la Verdad Base del repositorio.

Uso, desde la raíz del repositorio:
    python docs/informe/figuras.py
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "docs" / "informe" / "datos"
SALIDA = RAIZ / "docs" / "informe" / "figuras"

# Paleta categórica (3 primeros tonos, validados para daltonismo) y tinta neutra.
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA_2, REFERENCIA, GRILLA = "#0b0b0b", "#52514e", "#8a8983", "#e4e3de"
MODELOS = [("minilm", "MiniLM"), ("mpnet", "mpnet-base"), ("e5", "e5-base")]

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9,
    "axes.edgecolor": TINTA_2, "axes.labelcolor": TINTA, "xtick.color": TINTA_2, "ytick.color": TINTA_2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRILLA,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "figure.dpi": 150,
})


def guardar(figura, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    figura.savefig(SALIDA / f"{nombre}.pdf", bbox_inches="tight")
    plt.close(figura)


def distribucion_verdad_base():
    gt = pd.read_csv(RAIZ / "src" / "loss" / "matriz_perdida.csv")
    figura, (izq, der) = plt.subplots(1, 2, figsize=(6.4, 2.4), gridspec_kw={"width_ratios": [1.1, 1]})
    izq.hist(gt["gt_nota_global"], bins=np.arange(2.75, 10.5, 0.5), color=AZUL, edgecolor="white", linewidth=1)
    izq.axvline(gt["gt_nota_global"].mean(), color=TINTA_2, linewidth=1, linestyle="--")
    izq.text(gt["gt_nota_global"].mean() - 0.15, izq.get_ylim()[1] * 0.92, f"media {gt['gt_nota_global'].mean():.2f}",
             ha="right", color=TINTA_2, fontsize=8)
    izq.set(xlabel="Nota global de Gemini", ylabel="Películas", title="Nota global (110 películas)")
    izq.grid(axis="x", visible=False)
    filtros = [c for c in gt.columns if c.startswith("gt_cols_")]
    nombres = [c.replace("gt_cols_", "").replace("_", " ").capitalize() for c in filtros]
    cantidad = [(gt[c] >= 6).sum() for c in filtros]
    orden = np.argsort(cantidad)
    der.barh(np.array(nombres)[orden], np.array(cantidad)[orden], color=NARANJA, height=0.6)
    for i, v in enumerate(np.array(cantidad)[orden]):
        der.text(v + 0.4, i, str(v), va="center", fontsize=8, color=TINTA)
    der.set(xlabel="Películas con puntaje de Gemini ≥ 6", ylabel="Filtro del perfil", title="Filtros que aplican con fuerza")
    der.grid(axis="y", visible=False)
    figura.tight_layout()
    guardar(figura, "distribucion_verdad_base")


def modelos():
    filas = []
    for clave, nombre in MODELOS:
        resumen = json.load(open(DATOS / f"{clave}_resumen.json"))["metricas"]
        reglas = json.load(open(DATOS / f"{clave}_reglas.json"))["metricas"]
        filas.append((nombre, resumen["reglas_dos_etapas_5_particiones"]["spearman"],
                      reglas.get("completo_desviacion", {}).get("spearman", 0),
                      resumen["validacion_cruzada_5_particiones"]["spearman"]))
    figura, eje = plt.subplots(figsize=(4.6, 2.3))
    y = np.arange(len(filas))
    eje.barh(y + 0.18, [f[1] for f in filas], height=0.34, color=AZUL, xerr=[f[2] for f in filas],
             error_kw={"ecolor": TINTA_2, "elinewidth": 0.8, "capsize": 2},
             label="Modelo de reglas + frases (opciones 7 y 8), ± desv. de 10 repeticiones")
    eje.barh(y - 0.18, [f[3] for f in filas], height=0.34, color=NARANJA, label="Regresión lineal anterior")
    for i, f in enumerate(filas):
        eje.text(f[1] + f[2] + 0.01, i + 0.18, f"{f[1]:.3f}", va="center", fontsize=8, color=TINTA)
        eje.text(f[3] + 0.01, i - 0.18, f"{f[3]:.3f}", va="center", fontsize=8, color=TINTA)
    eje.set_yticks(y, [f[0] for f in filas])
    eje.set(xlim=(0, 0.8), xlabel="ρ de Spearman con el orden de Gemini (validación cruzada)", ylabel="Modelo de embeddings")
    eje.grid(axis="y", visible=False)
    eje.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=1, fontsize=8)
    guardar(figura, "modelos")


def deltas(clave_archivo, referencia, titulo, nombre, etiquetas=None, limite=None, eje_y=""):
    # Misma escala en los tres paneles para poder compararlos.
    figura, ejes = plt.subplots(1, 3, figsize=(6.6, 2.9 if limite is None else 2.3), sharey=True, sharex=True)
    signos = set()
    for eje, (clave, modelo) in zip(ejes, MODELOS):
        tabla = pd.read_csv(DATOS / f"{clave}_{clave_archivo}.csv")
        tabla = tabla[tabla["representacion"] != referencia]
        if etiquetas:
            tabla = tabla[tabla["representacion"].isin(etiquetas)]
            tabla = tabla.set_index("representacion").loc[list(etiquetas)].reset_index()
        y = np.arange(len(tabla))
        colores = [AZUL if d > 0 else NARANJA for d in tabla["Δ ρ"]]
        signos.update(tabla["Δ ρ"] > 0)
        eje.barh(y, tabla["Δ ρ"], xerr=tabla["desv. Δ ρ"], color=colores, height=0.6,
                 error_kw={"ecolor": TINTA_2, "elinewidth": 0.7, "capsize": 1.5})
        eje.axvline(0, color=REFERENCIA, linewidth=0.8)
        eje.set_title(modelo)
        eje.grid(axis="y", visible=False)
        nombres = [etiquetas[r] for r in tabla["representacion"]] if etiquetas else list(tabla["representacion"])
        eje.set_yticks(y, nombres)
        eje.invert_yaxis()
        if limite:
            eje.set_xlim(*limite)
    # Eje x compartido por los tres paneles.
    figura.supxlabel(f"Δ ρ de Spearman contra «{titulo}» (media ± desv. de 10 repeticiones)", fontsize=9,
                     y=0.02 if limite is None else 0.06)
    ejes[0].set_ylabel(eje_y)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    # Solo los colores que aparecen en el gráfico.
    entradas = [Patch(color=AZUL, label=f"ordena mejor que «{titulo}»")] if True in signos else []
    entradas += [Patch(color=NARANJA, label=f"ordena peor que «{titulo}»")] if False in signos else []
    entradas.append(Line2D([], [], color=TINTA_2, linewidth=0.8, marker="|", markersize=6,
                           label="± desviación entre repeticiones"))
    figura.legend(handles=entradas, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=len(entradas),
                  fontsize=7.5, frameon=False)
    figura.tight_layout()
    guardar(figura, nombre)


def pooling():
    etiquetas = {}
    for estrategia, corto in [("promedio", "promedio"), ("percentil 50 por dimensión", "p50"),
                              ("percentil 75 por dimensión", "p75"), ("percentil 90 por dimensión", "p90"),
                              ("percentil 95 por dimensión", "p95"), ("promedio + percentiles de similitud", "prom.+sim.")]:
        for cantidad, sufijo in [("todas las reseñas", "todas"), ("hasta 100 reseñas", "100"), ("hasta 50 reseñas", "50")]:
            etiquetas[f"{estrategia}, {cantidad}"] = f"{corto}, {sufijo}"
    etiquetas.pop("promedio, todas las reseñas")
    deltas("pooling", "promedio, todas las reseñas", "promedio, todas", "pooling", etiquetas,
           eje_y="Pooling, reseñas por película")


def frases():
    etiquetas = {"promedio + frases de reseña, ponderadas": "frases ponderadas (elegida)",
                 "promedio + frases de reseña": "frases concatenadas",
                 "solo frases de reseña": "solo frases",
                 "promedio + descripción (control)": "descripción concatenada",
                 "solo descripción (control)": "solo descripción"}
    deltas("frases_resenia", "promedio (sin frases)", "sin frases", "frases", etiquetas, limite=(-0.025, 0.03),
           eje_y="Uso de las frases")


def etapa_1():
    reglas = json.load(open(DATOS / "e5_reglas.json"))["metricas"]["etapa_1_por_criterio"]
    sin = pd.read_csv(DATOS / "e5_frases_resenia_por_criterio.csv").set_index("criterio")["promedio (sin frases)"]
    filas = []
    for columna, m in reglas.items():
        if columna.startswith("gt_excepcion_"):
            continue
        tipo = "filtro" if columna.startswith("gt_cols_") else "afinidad"
        corto = columna.replace("gt_cols_", "").replace("gt_afinidad_", "")
        filas.append((corto.replace("_", " ").capitalize(), tipo, m["r2"], sin.get(corto, np.nan)))
    filas.sort(key=lambda f: (f[1], f[2]))
    figura, eje = plt.subplots(figsize=(5.2, 2.9))
    y = np.arange(len(filas))
    eje.barh(y, [f[2] for f in filas], color=[AZUL if f[1] == "afinidad" else NARANJA for f in filas], height=0.6)
    for i, f in enumerate(filas):
        if not np.isnan(f[3]):
            eje.plot(f[3], i, marker="|", markersize=10, color=TINTA, markeredgewidth=1.5)
        eje.text(max(f[2], 0) + 0.012, i, f"{f[2]:.2f}", va="center", fontsize=7.5, color=TINTA)
    eje.set_yticks(y, [f[0] for f in filas])
    eje.axvline(0, color=REFERENCIA, linewidth=0.8)
    eje.set(xlabel="R² de la etapa 1: puntaje predicho desde reseñas vs. Gemini (validación cruzada, e5)",
            ylabel="Criterio del perfil", xlim=(-0.05, 0.7))
    eje.grid(axis="y", visible=False)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    eje.legend(handles=[Patch(color=AZUL, label="afinidad"), Patch(color=NARANJA, label="filtro (con frases)"),
                        Line2D([], [], marker="|", color=TINTA, linestyle="", markersize=10, markeredgewidth=1.5,
                               label="filtro sin frases")], loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7.5)
    guardar(figura, "etapa_1")


def dispersion():
    cv = pd.read_csv(DATOS / "cv_e5.csv")
    figura, eje = plt.subplots(figsize=(3.6, 3.2))
    eje.plot([3, 10], [3, 10], color=REFERENCIA, linewidth=0.8, linestyle="--", label="predicción = nota de Gemini")
    eje.scatter(cv["nota_gemini"], cv["nota_cv"], s=18, color=AZUL, edgecolor="white", linewidth=0.6, zorder=3,
                label="película evaluada")
    # Películas comentadas en el ejemplo guiado, con la etiqueta en una posición fija.
    for film, tx, ty in [("manhattan", 5.3, 8.95), ("amelie", 4.1, 9.4), ("marty-supreme", 5.8, 6.35)]:
        fila = cv[cv["film_id"] == film]
        if len(fila):
            x, y = fila.iloc[0]["nota_gemini"], fila.iloc[0]["nota_cv"]
            eje.scatter([x], [y], s=26, color=NARANJA, edgecolor="white", linewidth=0.6, zorder=4,
                        label="comentada en el ejemplo guiado" if film == "manhattan" else None)
            eje.annotate(film, (x, y), xytext=(tx, ty), fontsize=7.5, color=TINTA,
                         arrowprops={"arrowstyle": "-", "color": TINTA_2, "linewidth": 0.6})
    eje.set(xlabel="Nota de Gemini", ylabel="Nota predicha (validación cruzada)", xlim=(4, 10.3), ylim=(4, 10.3),
            title="e5 + frases, predicción promedio de 10 repeticiones")
    eje.legend(loc="lower right", fontsize=7, handletextpad=0.4, borderaxespad=0.3)
    guardar(figura, "dispersion")


def curva():
    tabla = pd.read_csv(DATOS / "curva_aprendizaje.csv")
    resumen = tabla.groupby("n_entrenamiento")["rho"].agg(["mean", "std"]).reset_index()
    figura, eje = plt.subplots(figsize=(3.8, 2.5))
    eje.fill_between(resumen["n_entrenamiento"], resumen["mean"] - resumen["std"], resumen["mean"] + resumen["std"],
                     color=AZUL, alpha=0.15, linewidth=0, label="± 1 desviación (10 repeticiones)")
    eje.plot(resumen["n_entrenamiento"], resumen["mean"], color=AZUL, linewidth=2, marker="o", markersize=5,
             label="ρ medio")
    for _, f in resumen.iterrows():
        eje.text(f["n_entrenamiento"], f["mean"] + 0.035, f"{f['mean']:.2f}", ha="center", fontsize=8, color=TINTA)
    eje.set(xlabel="Películas de entrenamiento", ylabel="ρ de Spearman", ylim=(0, 0.85),
            title="Curva de aprendizaje (e5 + frases)")
    eje.legend(loc="lower right", fontsize=7.5)
    guardar(figura, "curva_aprendizaje")


def sondas():
    tabla = pd.read_csv(DATOS / "sondas.csv")
    if "chunks" in tabla:
        tabla = tabla[tabla["chunks"] == "todos"]
    filas = []
    for filtro, grupo in tabla.groupby("filtro", sort=False):
        descripcion = grupo[grupo["texto"] == "descripción del perfil"]["rho"].max()
        mejor = grupo[grupo["texto"].str.startswith("sonda")]["rho"].max()
        filas.append((filtro, descripcion, mejor))
    figura, eje = plt.subplots(figsize=(4.8, 2.3))
    y = np.arange(len(filas))
    eje.barh(y + 0.18, [f[1] for f in filas], height=0.34, color=NARANJA, label="descripción del perfil")
    eje.barh(y - 0.18, [f[2] for f in filas], height=0.34, color=AZUL, label="mejor frase de reseña")
    for i, f in enumerate(filas):
        for valor, dy in ((f[1], 0.18), (f[2], -0.18)):
            eje.text(max(valor, 0) + 0.01, i + dy, f"{valor:.2f}", va="center", fontsize=7.5, color=TINTA)
    eje.set_yticks(y, [f[0] for f in filas])
    eje.invert_yaxis()
    eje.axvline(0, color=REFERENCIA, linewidth=0.8)
    eje.set(xlabel="ρ de Spearman con el puntaje de Gemini del filtro", ylabel="Filtro del perfil", xlim=(-0.1, 0.65))
    eje.grid(axis="y", visible=False)
    eje.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=7.5)
    guardar(figura, "sondas")


if __name__ == "__main__":
    for funcion in (distribucion_verdad_base, modelos, pooling, frases, etapa_1, sondas, dispersion, curva):
        try:
            funcion()
            print(f"ok  {funcion.__name__}")
        except FileNotFoundError as error:
            print(f"--  {funcion.__name__}: falta {Path(error.filename).name}")

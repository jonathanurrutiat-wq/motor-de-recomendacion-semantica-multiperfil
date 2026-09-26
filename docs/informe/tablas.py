"""
Genera las tablas y valores del informe (docs/informe/generado/*.tex) a partir
de los datos agregados de docs/informe/datos/, para que el texto, las tablas y
las figuras usen siempre los mismos números.

Uso, desde la raíz del repositorio:
    python docs/informe/tablas.py
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "docs" / "informe" / "datos"
SALIDA = RAIZ / "docs" / "informe" / "generado"
MODELOS = [("minilm", "MiniLM"), ("mpnet", "mpnet-base"), ("e5", "e5-base")]


def escribir(nombre, texto):
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / f"{nombre}.tex").write_text(texto + "\n", encoding="utf-8")


def tex(texto: str) -> str:
    return str(texto).replace("_", r"\_").replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")


def f3(valor) -> str:
    return f"{valor:.3f}"


def tabla_modelos():
    filas = []
    for clave, nombre in MODELOS:
        m = json.load(open(DATOS / f"{clave}_resumen.json"))["metricas"]
        d = json.load(open(DATOS / f"{clave}_reglas.json"))["metricas"]["completo_desviacion"]
        r, lin, rid = m["reglas_dos_etapas_5_particiones"], m["validacion_cruzada_5_particiones"], m["validacion_cruzada_ridge_5_particiones"]
        filas.append(rf"\multirow{{3}}{{*}}{{{nombre}}} & \textbf{{Reglas + frases (op.~7 y 8)}} & "
                     rf"\textbf{{{f3(r['spearman'])}}} $\pm$ {d['spearman']:.3f} & {f3(r['ndcg@10'])} & {f3(r['precision@10'])} & {f3(r['mae'])} \\")
        filas.append(rf" & Regresión lineal anterior & {f3(lin['spearman'])} & {f3(lin['ndcg@10'])} & {f3(lin['precision@10'])} & {f3(lin['mae'])} \\")
        filas.append(rf" & Regresión lineal con Ridge & {f3(rid['spearman'])} & {f3(rid['ndcg@10'])} & {f3(rid['precision@10'])} & {f3(rid['mae'])} \\ \midrule")
    b = m["linea_base_promedio"]
    filas.append(rf"\multicolumn{{2}}{{l}}{{Orden al azar / predecir el promedio}} & 0 & {f3(b['ndcg@10'])} & {f3(b['precision@10'])} & {f3(b['mae'])} \\")
    escribir("tabla_modelos", "\n".join([
        r"\begin{tabular}{llcccc}", r"\toprule",
        r"Embeddings & Modelo & $\rho$ Spearman & NDCG@10 & Precisión@10 & MAE \\", r"\midrule", *filas,
        r"\bottomrule", r"\end{tabular}"]))


def tabla_etapa_2():
    m = json.load(open(DATOS / "e5_reglas.json"))["metricas"]
    filas = []
    for clave, nombre in [("etapa_2_regla", "Regla con condiciones (16 parámetros)"),
                          ("etapa_2_lineal", "Regresión lineal sobre los puntajes"), ("etapa_2_linea_base", "Predecir el promedio")]:
        x = m[clave]
        filas.append(rf"{nombre} & {f3(x['spearman'])} & {f3(x['r2'])} & {f3(x['mae'])} \\")
    completo = json.load(open(DATOS / "e5_resumen.json"))["metricas"]["reglas_dos_etapas_5_particiones"]
    filas.append(r"\midrule")
    filas.append(rf"Modelo completo (etapa 1 desde reseñas + regla), e5 & {f3(completo['spearman'])} & {f3(completo['r2'])} & {f3(completo['mae'])} \\")
    escribir("tabla_etapa_2", "\n".join([
        r"\begin{tabular}{lccc}", r"\toprule", r"Entrada de la etapa 2 & $\rho$ Spearman & $R^2$ & MAE \\", r"\midrule",
        r"\multicolumn{4}{l}{\emph{Puntajes reales de Gemini (110 películas)}} \\", *filas, r"\bottomrule", r"\end{tabular}"]))


def tabla_comparacion(archivo, referencia, nombres, etiqueta_ref):
    tablas = {clave: pd.read_csv(DATOS / f"{clave}_{archivo}.csv").set_index("representacion") for clave, _ in MODELOS}
    filas = []
    for representacion, nombre in nombres.items():
        celdas = []
        for clave, _ in MODELOS:
            fila = tablas[clave].loc[representacion]
            if representacion == referencia:
                celdas.append(rf"\multicolumn{{2}}{{c}}{{$\rho$ = {f3(fila['ρ Spearman'])} ({etiqueta_ref})}}")
            else:
                delta = f"{fila['Δ ρ']:+.3f}"
                if fila["Δ ρ"] > 0 and str(fila["mejora ρ"]).startswith(("9/", "10/")):
                    delta = rf"\textbf{{{delta}}}"
                celdas.append(rf"{delta} $\pm$ {fila['desv. Δ ρ']:.3f} & {fila['mejora ρ']}")
        filas.append(rf"{nombre} & " + " & ".join(celdas) + r" \\")
    cabecera = " & ".join(rf"\multicolumn{{2}}{{c}}{{{nombre}}}" for _, nombre in MODELOS)
    return "\n".join([
        r"\begin{tabular}{l" + "rc" * len(MODELOS) + "}", r"\toprule", rf"Variante & {cabecera} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}",
        " & " + " & ".join([r"$\Delta\rho$ & mejora"] * len(MODELOS)) + r" \\", r"\midrule", *filas, r"\bottomrule", r"\end{tabular}"])


def tabla_pooling():
    nombres = {"promedio, todas las reseñas": "promedio, todas (elegida)"}
    for estrategia, corto in [("promedio", "promedio"), ("percentil 50 por dimensión", "percentil 50"),
                              ("percentil 75 por dimensión", "percentil 75"), ("percentil 90 por dimensión", "percentil 90"),
                              ("percentil 95 por dimensión", "percentil 95"), ("promedio + percentiles de similitud", "promedio + sim.")]:
        for cantidad, sufijo in [("todas las reseñas", "todas"), ("hasta 100 reseñas", "100"), ("hasta 50 reseñas", "50")]:
            clave = f"{estrategia}, {cantidad}"
            if clave not in nombres:
                nombres[clave] = f"{corto}, {sufijo}"
    escribir("tabla_pooling", tabla_comparacion("pooling", "promedio, todas las reseñas", nombres, "ref."))


def tabla_frases():
    nombres = {"promedio (sin frases)": "sin frases (referencia)",
               "promedio + frases de reseña, ponderadas": "frases ponderadas (elegida)",
               "promedio + frases de reseña": "frases concatenadas",
               "solo frases de reseña": "solo frases",
               "promedio + descripción (control)": "descripción concat. (control)",
               "solo descripción (control)": "solo descripción (control)"}
    escribir("tabla_frases", tabla_comparacion("frases_resenia", "promedio (sin frases)", nombres, "ref."))


def tabla_sondas():
    tabla = pd.read_csv(DATOS / "sondas.csv")
    if "chunks" in tabla:
        tabla = tabla[tabla["chunks"] == "todos"]
    lexico = {"Camaradería Masculina Rancia": -0.03, "Insoportabilidad Prolongada": 0.55,
              "Control Emocional Artificial": 0.16, "Personajes Diorama": 0.17, "Caos Asfixiante": 0.34}
    filas = []
    for filtro, grupo in tabla.groupby("filtro", sort=False):
        descripcion = grupo[grupo["texto"] == "descripción del perfil"]["rho"].max()
        sondas = grupo[grupo["texto"].str.startswith("sonda")]
        mejor = sondas.loc[sondas["rho"].idxmax()]
        texto = mejor["texto"].split(": ", 1)[1]
        filas.append(rf"{filtro} & {descripcion:.2f} & {mejor['rho']:.2f} & {lexico[filtro]:.2f} & \emph{{``{tex(texto)}''}} \\")
    escribir("tabla_sondas", "\n".join([
        r"\begin{tabular}{lcccp{4.6cm}}", r"\toprule",
        r"Filtro & Descripción & Mejor frase & Léxico & Frase con mejor $\rho$ \\", r"\midrule", *filas,
        r"\bottomrule", r"\end{tabular}"]))


def tabla_candidatas():
    ranking = pd.read_csv(DATOS / "e5_ranking.csv")
    candidatas = ranking[~ranking["evaluada"]].head(10)
    filas = [rf"{i} & \texttt{{{tex(f.film_id)}}} & {f.nota_modelo:.2f} & {f.nota_lineal:.2f} \\"
             for i, f in enumerate(candidatas.itertuples(), 1)]
    escribir("tabla_candidatas", "\n".join([
        r"\begin{tabular}{rlcc}", r"\toprule", r"\# & Película & Nota del modelo & Nota lineal anterior \\", r"\midrule",
        *filas, r"\bottomrule", r"\end{tabular}"]))
    evaluadas = ranking[ranking["evaluada"]]
    escribir("valores_ranking", "\n".join([
        rf"\newcommand{{\NPeliculasRanking}}{{{len(ranking)}}}",
        rf"\newcommand{{\NCandidatas}}{{{int((~ranking['evaluada']).sum())}}}",
        rf"\newcommand{{\NEvaluadasRanking}}{{{len(evaluadas)}}}"]))


def reglas():
    datos = json.load(open(DATOS / "e5_reglas.json"))
    lineas = [rf"\item {tex(linea)}" for linea in datos["reglas"]]
    escribir("reglas_e5", "\n".join([r"\begin{itemize}", *lineas, r"\end{itemize}"]))


def ejemplo():
    ruta = DATOS / "ejemplo_manhattan.json"
    if not ruta.exists():
        return
    e = json.load(open(ruta))
    valores = [
        rf"\newcommand{{\EjNotaGemini}}{{{e['nota_gemini']:.1f}}}",
        rf"\newcommand{{\EjNotaModelo}}{{{e['nota_modelo']:.2f}}}",
        rf"\newcommand{{\EjNotaCV}}{{{e['cv_nota']:.2f}}}",
        rf"\newcommand{{\EjChunks}}{{{e['n_chunks']}}}",
        rf"\newcommand{{\EjResenias}}{{{e['n_resenias']}}}",
        rf"\newcommand{{\EjSesgo}}{{{e['sesgo']:.2f}}}",
        rf"\newcommand{{\EjBase}}{{{e['sesgo'] + sum(a['aporte'] for a in e['afinidades']):.2f}}}",
        rf"\newcommand{{\EjDescuento}}{{{sum(f['descuento'] for f in e['filtros']):.2f}}}",
    ]
    # Puesto de algunas películas en el orden del modelo (validación cruzada) y en el de Gemini.
    cv = pd.read_csv(DATOS / "cv_e5.csv")
    cv["puesto_modelo"] = cv["nota_cv"].rank(ascending=False).astype(int)
    cv["puesto_gemini"] = cv["nota_gemini"].rank(ascending=False, method="min").astype(int)
    for film, macro in [("manhattan", "Manhattan"), ("marty-supreme", "Marty"), ("amelie", "Amelie")]:
        fila = cv[cv["film_id"] == film].iloc[0]
        valores += [rf"\newcommand{{\Puesto{macro}}}{{{fila['puesto_modelo']}}}",
                    rf"\newcommand{{\PuestoGemini{macro}}}{{{fila['puesto_gemini']}}}",
                    rf"\newcommand{{\NotaCV{macro}}}{{{fila['nota_cv']:.2f}}}",
                    rf"\newcommand{{\NotaGemini{macro}}}{{{fila['nota_gemini']:.1f}}}"]
    valores.append(rf"\newcommand{{\NPeliculasCV}}{{{len(cv)}}}")
    ins = next(f for f in e["filtros"] if f["criterio"] == "Insoportabilidad Prolongada")
    frase = max(e["frases_insoportabilidad"], key=lambda t: t["percentil_manhattan"])
    descripcion = e["frases_insoportabilidad"][0]
    valores += [rf"\newcommand{{\EjInsGemini}}{{{ins['gemini']:.0f}}}",
                rf"\newcommand{{\EjInsPredicho}}{{{ins['predicho']:.1f}}}",
                rf"\newcommand{{\EjInsUmbral}}{{{ins['umbral']:.1f}}}",
                rf"\newcommand{{\EjFrasePercentil}}{{{frase['percentil_manhattan']:.0f}}}",
                rf"\newcommand{{\EjFraseManhattan}}{{{100 * frase['fraccion_manhattan']:.1f}}}",
                rf"\newcommand{{\EjFraseMediana}}{{{100 * frase['fraccion_mediana']:.1f}}}",
                rf"\newcommand{{\EjDescPercentil}}{{{descripcion['percentil_manhattan']:.0f}}}"]
    escribir("valores_ejemplo", "\n".join(valores))
    filas = [rf"{a['criterio']} & {a['gemini']:.1f} & {a['predicho']:.1f} & $w$ = {a['peso']:.2f} & +{a['aporte']:.2f} \\"
             for a in e["afinidades"]]
    filas.append(r"\midrule")
    for f in e["filtros"]:
        exc = "" if f["gemini_excepcion"] is None else f" (exc. {f['gemini_excepcion']:.0f})"
        filas.append(rf"{f['criterio']} & {f['gemini']:.1f}{exc} & {f['predicho']:.1f} (exc. {f['excepcion_predicha']:.2f}) & "
                     rf"$u$ = {f['umbral']:.1f}, $d$ = {f['desplome']:.2f}, act. {f['activacion']:.2f} & "
                     + (rf"$-${f['descuento']:.2f}" if f["descuento"] >= 0.005 else "0.00") + r" \\")
    escribir("tabla_ejemplo", "\n".join([
        r"\begin{tabular}{lcccr}", r"\toprule",
        r"Criterio & Gemini & Etapa 1 (predicho) & Parámetros de la regla & Aporte \\", r"\midrule",
        rf"Sesgo & & & & {e['sesgo']:.2f} \\", *filas, r"\midrule",
        rf"\multicolumn{{4}}{{l}}{{\textbf{{Nota predicha}} (Gemini: {e['nota_gemini']:.1f})}} & \textbf{{{e['nota_modelo']:.2f}}} \\",
        r"\bottomrule", r"\end{tabular}"]))
    filas = [rf"\emph{{{tex(t['texto'])}}} & {100 * t['fraccion_manhattan']:.1f}\,\% & {100 * t['fraccion_mediana']:.1f}\,\% & {t['percentil_manhattan']:.0f} \\"
             for t in e["frases_insoportabilidad"]]
    escribir("tabla_ejemplo_frases", "\n".join([
        r"\begin{tabular}{>{\raggedright\arraybackslash}p{7.2cm}ccc}", r"\toprule",
        r"Texto & Manhattan & Mediana & Percentil \\", r"\midrule", *filas, r"\bottomrule", r"\end{tabular}"]))


def curva():
    ruta = DATOS / "curva_aprendizaje.csv"
    if not ruta.exists():
        return
    resumen = pd.read_csv(ruta).groupby("n_entrenamiento")["rho"].agg(["mean", "std"]).reset_index()
    filas = [rf"{int(f.n_entrenamiento)} & {f.mean:.3f} $\pm$ {f.std:.3f} \\" for f in resumen.itertuples()]
    escribir("tabla_curva", "\n".join([
        r"\begin{tabular}{cc}", r"\toprule", r"Películas & $\rho$ Spearman \\", r"\midrule",
        *filas, r"\bottomrule", r"\end{tabular}"]))


if __name__ == "__main__":
    for funcion in (tabla_modelos, tabla_etapa_2, tabla_pooling, tabla_frases, tabla_sondas, tabla_candidatas,
                    reglas, ejemplo, curva):
        funcion()
        print(f"ok  {funcion.__name__}")

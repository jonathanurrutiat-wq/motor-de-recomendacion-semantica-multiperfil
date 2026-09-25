"""
Ejecuta el pipeline completo (opciones 2 a 8) sin preguntas y guarda en
analisis/<fecha_hora>/ los datos para analizar el modelo: métricas con
validación cruzada, datos por película, pesos, ranking y similitud entre
los términos del perfil.
"""

import json
import time
from collections import Counter
from datetime import datetime

import chromadb
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import KFold

import src.procesing_profiles as procesamiento_perfiles
import src.procesing_reviews as procesamiento_resenias
from src.config import DIR_ANALISIS, DIR_CHROMA, RUTA_GT
from src.db.filtered import filter as filtro
from src.loss.gt_matrix_pipeline import main as revisar_pendientes
from src.loss.ingest_maestro import main as cargar_verdad_base
from src.modelo_reglas import evaluar as evaluar_reglas
from src.normalizacion import canonicalizar_film_id, seleccionar_perfil
from src.recommend import calcular_ranking
from src.scoring import ETIQUETAS_TIPO, construir_features
from src.scoring import main as entrenar_y_guardar

N_PARTICIONES = 5
# Intensidades de regularización que prueba Ridge (se elige la mejor en cada partición).
ALFAS_RIDGE = np.logspace(-2, 3, 30)


def encabezado(numero: int, total: int, titulo: str):
    print("\n" + "=" * 72)
    print(f"[{numero}/{total}] {titulo}")
    print("=" * 72)


def metricas(y_real, y_pred) -> dict:
    return {
        "mse": float(mean_squared_error(y_real, y_pred)),
        "mae": float(mean_absolute_error(y_real, y_pred)),
        "r2": float(r2_score(y_real, y_pred)),
    }


def validacion_cruzada(similitudes, y, estructura):
    # Predice cada película con un modelo que no la vio al entrenar. Las
    # media y desviación para estandarizar se calculan solo con la parte de
    # entrenamiento de cada partición, para no filtrar información.
    n_particiones = min(N_PARTICIONES, len(y))
    pred_modelo, pred_ridge, pred_base = np.empty(len(y)), np.empty(len(y)), np.empty(len(y))
    particiones = KFold(n_particiones, shuffle=True, random_state=0).split(similitudes)
    for numero, (entrenamiento, prueba) in enumerate(particiones, 1):
        x_entrenamiento, _, escala = construir_features(similitudes[entrenamiento], estructura)
        x_prueba, _, _ = construir_features(similitudes[prueba], estructura, escala)
        modelo = LinearRegression().fit(x_entrenamiento, y[entrenamiento])
        pred_modelo[prueba] = modelo.predict(x_prueba)
        pred_ridge[prueba] = RidgeCV(alphas=ALFAS_RIDGE).fit(x_entrenamiento, y[entrenamiento]).predict(x_prueba)
        pred_base[prueba] = y[entrenamiento].mean()
        print(f"  Partición {numero}/{n_particiones}: entrena con {len(entrenamiento)}, prueba con {len(prueba)} "
              f"| MAE modelo {mean_absolute_error(y[prueba], pred_modelo[prueba]):.3f} "
              f"| MAE Ridge {mean_absolute_error(y[prueba], pred_ridge[prueba]):.3f} "
              f"| MAE promedio {mean_absolute_error(y[prueba], pred_base[prueba]):.3f}")
    return pred_modelo, pred_ridge, pred_base, n_particiones


def contar_chunks_por_pelicula() -> Counter:
    ids = chromadb.PersistentClient(path=str(DIR_CHROMA)).get_collection("resenias").get(include=[])["ids"]
    return Counter(canonicalizar_film_id(i.split("::")[0]) for i in ids)


def tabla_markdown(df: pd.DataFrame, decimales: int = 2) -> str:
    filas = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for fila in df.itertuples(index=False):
        filas.append("| " + " | ".join(f"{v:.{decimales}f}" if isinstance(v, float) else str(v) for v in fila) + " |")
    return "\n".join(filas)


def guardar_analisis(nombre_perfil, resultado, pred_cv, pred_ridge, pred_base, n_particiones, ranking, reglas, tiempos):
    carpeta = DIR_ANALISIS / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta.mkdir(parents=True, exist_ok=True)

    estructura, modelo = resultado["estructura"], resultado["modelo"]
    etiquetas = [f"{ETIQUETAS_TIPO[tipo]} · {nombre}" for tipo, nombre in estructura["terminos"]]
    y = resultado["y"]

    # Por película: similitudes con cada término, notas y errores.
    por_pelicula = resultado["embeddings_por_pelicula"]
    film_ids = list(por_pelicula)
    similitudes = cosine_similarity(np.array(list(por_pelicula.values())), resultado["embeddings_perfil"])
    peliculas = pd.DataFrame(similitudes, columns=[f"sim · {e}" for e in etiquetas])
    peliculas.insert(0, "film_id", film_ids)
    chunks = contar_chunks_por_pelicula()
    peliculas.insert(1, "n_chunks", [chunks.get(f, 0) for f in film_ids])

    modelo_reglas = reglas["modelo"]
    todas = np.array(list(por_pelicula.values()))
    puntajes_reglas = modelo_reglas.predecir_puntajes(todas).add_prefix("pred · ")
    peliculas = pd.concat([peliculas, puntajes_reglas], axis=1)
    peliculas["nota_reglas"] = modelo_reglas.predict(todas)
    ranking = ranking.merge(peliculas[["film_id", "nota_reglas"]], on="film_id", how="left")

    entrenamiento = pd.DataFrame({
        "film_id": resultado["film_ids"], "nota_gemini": y,
        "nota_modelo_entrenamiento": resultado["predicciones"], "nota_modelo_cv": pred_cv,
        "error_cv": pred_cv - y, "nota_reglas_cv": reglas["pred_cv"], "error_reglas_cv": reglas["pred_cv"] - y,
    })
    peliculas = (peliculas
                 .merge(entrenamiento, on="film_id", how="left")
                 .merge(ranking[["film_id", "nota_modelo"]], on="film_id", how="left"))
    peliculas.insert(2, "evaluada", peliculas["nota_gemini"].notna())
    peliculas.to_csv(carpeta / "peliculas.csv", index=False, encoding="utf-8")

    pesos = pd.DataFrame({"variable": resultado["columnas"], "peso": modelo.coef_})
    pesos = pesos.reindex(pesos["peso"].abs().sort_values(ascending=False).index)
    pd.concat([pesos, pd.DataFrame({"variable": ["(sesgo)"], "peso": [modelo.intercept_]})]).to_csv(
        carpeta / "pesos.csv", index=False, encoding="utf-8")

    vectores = resultado["embeddings_perfil"]
    pd.DataFrame(cosine_similarity(vectores, vectores), index=etiquetas, columns=etiquetas).round(4).to_csv(
        carpeta / "similitud_perfil.csv", encoding="utf-8")

    ranking.to_csv(carpeta / "ranking.csv", index=False, encoding="utf-8")
    (carpeta / "reglas.json").write_text(json.dumps({
        "reglas": modelo_reglas.regla.describir(), "parametros": modelo_reglas.regla.parametros(),
        "metricas": reglas["metricas"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    df_gt = pd.read_csv(RUTA_GT)
    sin_resenias = sorted(set(df_gt["film_id"].apply(canonicalizar_film_id)) - set(resultado["film_ids"]))
    resumen = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "perfil": nombre_perfil,
        "parametros_filtrado": {
            "min_caracteres_resenia": filtro.MIN_CARACTERES_RESENIA,
            "max_resenias_por_pelicula": filtro.MAX_RESENIAS_POR_PELICULA,
            "min_resenias_por_pelicula": filtro.MIN_RESENIAS_POR_PELICULA,
        },
        "datos": {
            "peliculas_con_embeddings": len(film_ids),
            "chunks_de_resenias": int(sum(chunks.values())),
            "peliculas_en_verdad_base": int(len(df_gt)),
            "peliculas_para_entrenar": int(len(y)),
            "peliculas_candidatas": int((~ranking["evaluada"]).sum()),
            "variables_del_modelo": len(resultado["columnas"]),
            "evaluadas_sin_resenias": sin_resenias,
        },
        "metricas": {
            "entrenamiento": metricas(y, resultado["predicciones"]),
            f"validacion_cruzada_{n_particiones}_particiones": metricas(y, pred_cv),
            f"validacion_cruzada_ridge_{n_particiones}_particiones": metricas(y, pred_ridge),
            "linea_base_promedio": metricas(y, pred_base),
            f"reglas_dos_etapas_{n_particiones}_particiones": reglas["metricas"]["completo"],
        },
        "tiempos_segundos": {paso: round(segundos, 1) for paso, segundos in tiempos.items()},
    }
    (carpeta / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

    m = resumen["metricas"]
    cv = m[f"validacion_cruzada_{n_particiones}_particiones"]
    ridge = m[f"validacion_cruzada_ridge_{n_particiones}_particiones"]
    mr = reglas["metricas"]
    completo = mr["completo"]
    fila = lambda nombre, x: f"| {nombre} | {x['mse']:.3f} | {x['mae']:.3f} | {x['r2']:.3f} |"
    etapa_1 = pd.DataFrame([{"criterio": c, "MAE": v["mae"], "R²": v["r2"]} for c, v in mr["etapa_1_por_criterio"].items()])
    peores = entrenamiento.reindex(entrenamiento["error_cv"].abs().sort_values(ascending=False).index).head(10)
    candidatas = ranking[~ranking["evaluada"]].head(10)
    lineas = [
        f"# Análisis del modelo — perfil {nombre_perfil}",
        "",
        f"Generado el {resumen['fecha']}.",
        "",
        "## Datos",
        "",
        f"- Películas con embeddings: {len(film_ids)} ({resumen['datos']['chunks_de_resenias']} chunks de reseñas).",
        f"- Películas para entrenar (con reseñas y nota de Gemini): {len(y)} de {len(df_gt)} en la Verdad Base.",
        f"- Evaluadas sin reseñas: {', '.join(sin_resenias) or 'ninguna'}.",
        f"- Candidatas a recomendar (sin nota de Gemini): {resumen['datos']['peliculas_candidatas']}.",
        f"- Variables del modelo: {len(resultado['columnas'])}.",
        "",
        "## Métricas",
        "",
        "La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. "
        "La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. "
        "Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.",
        "",
        "| Evaluación | MSE | MAE | R² |",
        "|---|---|---|---|",
        f"| Entrenamiento (optimista) | {m['entrenamiento']['mse']:.3f} | {m['entrenamiento']['mae']:.3f} | {m['entrenamiento']['r2']:.3f} |",
        f"| Validación cruzada ({n_particiones} particiones) | {cv['mse']:.3f} | {cv['mae']:.3f} | {cv['r2']:.3f} |",
        f"| Validación cruzada con Ridge (comparación) | {ridge['mse']:.3f} | {ridge['mae']:.3f} | {ridge['r2']:.3f} |",
        fila("Validación cruzada, modelo de reglas en dos etapas", completo),
        f"| Línea base (promedio) | {m['linea_base_promedio']['mse']:.3f} | {m['linea_base_promedio']['mae']:.3f} | {m['linea_base_promedio']['r2']:.3f} |",
        "",
        "## Modelo de reglas en dos etapas",
        "",
        "Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas. "
        "Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.",
        "",
        "### Reglas aprendidas (modelo final)",
        "",
        *[f"- {linea}" for linea in modelo_reglas.regla.describir()],
        "",
        "### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?",
        "",
        "| Modelo | MSE | MAE | R² |",
        "|---|---|---|---|",
        fila("Regla con condiciones", mr["etapa_2_regla"]),
        fila("Regresión lineal sobre los puntajes", mr["etapa_2_lineal"]),
        fila("Línea base (promedio)", mr["etapa_2_linea_base"]),
        "",
        "### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)",
        "",
        tabla_markdown(etapa_1, 3) if len(etapa_1) else "Sin datos.",
        "",
        "## Variables con más peso (regresión lineal)",
        "",
        tabla_markdown(pesos.head(10), 3),
        "",
        "## Películas peor predichas (validación cruzada)",
        "",
        tabla_markdown(peores[["film_id", "nota_gemini", "nota_modelo_cv", "error_cv"]]),
        "",
        "## Mejores candidatas a recomendar",
        "",
        tabla_markdown(candidatas[["film_id", "nota_modelo", "nota_reglas"]]) if len(candidatas) else "No hay películas candidatas.",
        "",
        "## Archivos",
        "",
        "- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas y errores.",
        "- `pesos.csv`: peso de cada variable de la regresión lineal.",
        "- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.",
        "- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).",
        "- `ranking.csv`: ranking completo de recomendaciones.",
        "- `resumen.json`: estos datos en formato legible por programas.",
        "",
    ]
    (carpeta / "resumen.md").write_text("\n".join(lineas), encoding="utf-8")
    return carpeta, resumen, ranking


def main():
    try:
        nombre_perfil, perfil = seleccionar_perfil()
    except (FileNotFoundError, ValueError) as error:
        print(f"[!] Error: {error}")
        return

    print(f"\nPerfil: {nombre_perfil}. El pipeline corre sin más preguntas y no borra datos: "
          "los chunks antiguos o perfiles huérfanos solo se informan.")

    pasos = [
        ("Filtrado de reseñas crudas (opción 2)", filtro.main),
        ("Embeddings del perfil (opción 3)", lambda: procesamiento_perfiles.main(nombre_perfil, eliminar_huerfanos=False)),
        ("Embeddings de reseñas (opción 4)", lambda: procesamiento_resenias.main(eliminar_ids_antiguos=False)),
        ("Verdad Base (opción 5)", lambda: cargar_verdad_base(nombre_perfil)),
        ("Películas pendientes de evaluar (opción 6)", lambda: revisar_pendientes(nombre_perfil)),
        ("Entrenamiento del modelo (opción 7)", lambda: entrenar_y_guardar(nombre_perfil)),
    ]
    total = len(pasos) + 3
    tiempos, inicio_total, resultado = {}, time.time(), None

    for numero, (titulo, paso) in enumerate(pasos, 1):
        encabezado(numero, total, titulo)
        inicio = time.time()
        resultado = paso()
        tiempos[titulo] = time.time() - inicio
        print(f"\n--> {titulo}: {tiempos[titulo]:.1f} s")

    if resultado is None:
        print("\n[!] El entrenamiento no se completó; revisa los mensajes anteriores. No se generó el análisis.")
        return

    encabezado(total - 2, total, f"Validación cruzada de la regresión lineal ({N_PARTICIONES} particiones)")
    inicio = time.time()
    pred_cv, pred_ridge, pred_base, n_particiones = validacion_cruzada(resultado["similitudes"], resultado["y"], resultado["estructura"])
    tiempos["Validación cruzada"] = time.time() - inicio

    encabezado(total - 1, total, "Modelo de reglas en dos etapas")
    inicio = time.time()
    df_gt = pd.read_csv(RUTA_GT)
    df_gt["canon_id"] = df_gt["film_id"].apply(canonicalizar_film_id)
    embeddings = np.array([resultado["embeddings_por_pelicula"][f] for f in resultado["film_ids"]])
    reglas = evaluar_reglas(perfil, df_gt, resultado["film_ids"], embeddings, N_PARTICIONES)
    tiempos["Modelo de reglas"] = time.time() - inicio

    encabezado(total, total, "Ranking (opción 8) y datos de análisis")
    inicio = time.time()
    try:
        ranking = calcular_ranking()
    except ValueError as error:
        print(f"[!] Error: {error}")
        return
    carpeta, resumen, ranking = guardar_analisis(
        nombre_perfil, resultado, pred_cv, pred_ridge, pred_base, n_particiones, ranking, reglas, tiempos)
    tiempos["Ranking y análisis"] = time.time() - inicio

    m = resumen["metricas"]
    cv = m[f"validacion_cruzada_{n_particiones}_particiones"]
    print("\n| -- Resumen -- |")
    print(f"Películas para entrenar: {resumen['datos']['peliculas_para_entrenar']} "
          f"| candidatas: {resumen['datos']['peliculas_candidatas']}")
    print(f"MAE entrenamiento: {m['entrenamiento']['mae']:.3f} | MAE validación cruzada: {cv['mae']:.3f} "
          f"| MAE línea base: {m['linea_base_promedio']['mae']:.3f}")
    ridge = m[f"validacion_cruzada_ridge_{n_particiones}_particiones"]
    print(f"R² validación cruzada: {cv['r2']:.3f} | con Ridge: {ridge['r2']:.3f} (MAE {ridge['mae']:.3f})")
    completo = m[f"reglas_dos_etapas_{n_particiones}_particiones"]
    print(f"Modelo de reglas en dos etapas: MAE {completo['mae']:.3f} | R² {completo['r2']:.3f}")
    print(f"Tiempo total: {time.time() - inicio_total:.1f} s")
    print(f"\nDatos de análisis guardados en: {carpeta}")
    for archivo in sorted(carpeta.iterdir()):
        print(f"  - {archivo.name}")


if __name__ == '__main__':
    main()

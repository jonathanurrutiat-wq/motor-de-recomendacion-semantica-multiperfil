"""
Modelo de notas ponderadas con condiciones, con la forma de la regla global.
Se arma a partir de cualquier perfil, sin importar cuántos filtros y
afinidades tenga.

Etapa 1: predice el puntaje 0-10 de cada filtro y afinidad, y si aplica la
excepción de cada filtro, a partir del embedding promedio de las reseñas.
Los criterios con frases_resenia en el perfil pueden usar además (o en vez
del embedding) rasgos de cuántas reseñas se parecen a esas frases.

Etapa 2: calcula la nota global con una regla simple cuyos pesos y umbrales
se aprenden de la Verdad Base:
  nota = base + suma(peso * afinidad) - suma(desplome * [filtro > umbral y su excepción no aplica])
Opcionalmente (usar_corrupcion, usar_pisos) un filtro activo puede además
reducir las afinidades que corrompe, y una afinidad alta asegurar una nota
mínima. Los umbrales son suaves (sigmoides) para poder ajustarlos por
optimización.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.metricas import K_RANKING, metricas, metricas_linea_base
from src.normalizacion import nombre_columna_excepcion, nombre_columna_gt

PENDIENTE = 1.5          # qué tan abrupto es cada umbral, por punto de la escala 0-10
SUAVIDAD_MAXIMO = 2.0    # aproximación suave del máximo entre la base y los pisos
PENALIZACION = 1e-3      # evita penalizaciones y pisos grandes que no mejoran el ajuste
ALFAS_ETAPA_1 = np.logspace(-1, 4, 30)
MINIMO_EJEMPLOS_ETAPA_1 = 5
INICIOS_UMBRALES = [(8.0, 5.0), (9.0, 3.0), (6.5, 7.0)]  # (umbral afinidades, umbral filtros)
# Cómo usa la etapa 1 los rasgos de frases de reseña de un criterio:
# "concatenar" los agrega al embedding, "ponderar" también pero con la misma
# varianza total que el embedding (si no, Ridge los penaliza como a una
# dimensión más entre cientos) y "solo_frases" usa solo esos rasgos.
MODOS_FRASES = ("concatenar", "ponderar", "solo_frases")


def sigmoide(x):
    return 1.0 / (1.0 + np.exp(-x))


def criterios_del_perfil(perfil: dict, columnas_disponibles) -> tuple[list, list, list, list]:
    # Filtros y afinidades del perfil que tienen columna en la Verdad Base, y
    # las relaciones de corrupción entre ellos.
    columnas = set(columnas_disponibles)
    afinidades = [n for n in perfil.get("afinidad", {}) if nombre_columna_gt("afinidad", n) in columnas]
    filtros = [n for n in perfil.get("restrictivos", {}) if nombre_columna_gt("restrictivos", n) in columnas]
    faltantes = [n for tipo in ("restrictivos", "afinidad") for n in perfil.get(tipo, {})
                 if n not in afinidades + filtros]
    corrupciones = [
        (afinidad, filtro)
        for filtro in filtros
        for afinidad in perfil["restrictivos"][filtro].get("corrupcion_directa") or []
        if afinidad in afinidades
    ]
    return afinidades, filtros, corrupciones, faltantes


def matrices_puntajes(df, afinidades, filtros):
    # A: afinidades, F: filtros, E: excepción aplicada (0 si no hay columna).
    A = df[[nombre_columna_gt("afinidad", n) for n in afinidades]].to_numpy(float)
    F = df[[nombre_columna_gt("restrictivos", n) for n in filtros]].to_numpy(float)
    E = np.column_stack([
        df[nombre_columna_excepcion(n)].to_numpy(float) if nombre_columna_excepcion(n) in df else np.zeros(len(df))
        for n in filtros
    ]) if filtros else np.zeros((len(df), 0))
    return A, F, np.nan_to_num(E)


class ReglaGlobal:
    """Etapa 2: de los puntajes por criterio a la nota global."""

    def __init__(self, afinidades, filtros, corrupciones, usar_pisos=False, usar_corrupcion=False):
        # Por defecto la regla es simple (pesos + desplomes): en validación
        # cruzada con la Verdad Base, pisos y corrupción no mejoraron la
        # precisión y casi duplican los parámetros. Se pueden activar.
        self.usar_pisos, self.usar_corrupcion = usar_pisos, usar_corrupcion
        self.afinidades, self.filtros = list(afinidades), list(filtros)
        self.pares = [(self.afinidades.index(a), self.filtros.index(f)) for a, f in corrupciones]
        n_a, n_f = len(self.afinidades), len(self.filtros)
        # Orden de los parámetros: sesgo | pesos, umbrales y pisos de afinidades | umbrales, desplomes y corrupción de filtros
        self.tamanos = [1, n_a, n_a, n_a, n_f, n_f, n_f]
        self.theta = None

    def _separar(self, theta):
        return np.split(theta, np.cumsum(self.tamanos)[:-1])

    def _predecir(self, theta, A, F, E):
        sesgo, pesos, umbral_a, piso, umbral_f, desplome, corrupcion = self._separar(theta)
        activo = sigmoide(PENDIENTE * (F - umbral_f)) * (1 - E)
        efectivas = A.copy()
        for i_a, i_f in self.pares:
            efectivas[:, i_a] *= 1 - corrupcion[i_f] * activo[:, i_f]
        base = sesgo[0] + efectivas @ pesos - activo @ desplome
        pisos = sigmoide(PENDIENTE * (A - umbral_a)) * piso
        candidatos = np.column_stack([base, pisos]) * SUAVIDAD_MAXIMO
        maximo = candidatos.max(axis=1, keepdims=True)
        return (maximo[:, 0] + np.log(np.exp(candidatos - maximo).sum(axis=1))) / SUAVIDAD_MAXIMO

    def fit(self, A, F, E, y):
        n_a, n_f = len(self.afinidades), len(self.filtros)
        pesos0 = np.full(n_a, 1.0 / n_a) if n_a else np.zeros(0)
        sesgo0 = float(y.mean() - (A @ pesos0).mean()) if n_a else float(y.mean())
        limite_piso = (0, 10) if self.usar_pisos else (0, 0)
        limite_corrupcion = (0, 1) if self.usar_corrupcion and self.pares else (0, 0)
        limites = ([(-10, 10)] + [(0, 2)] * n_a + [(0, 10)] * n_a + [limite_piso] * n_a
                   + [(0, 10)] * n_f + [(0, 10)] * n_f + [limite_corrupcion] * n_f)

        def perdida(theta):
            _, _, _, piso, _, desplome, corrupcion = self._separar(theta)
            error = np.mean((self._predecir(theta, A, F, E) - y) ** 2)
            return error + PENALIZACION * (np.sum(piso ** 2) + np.sum(desplome ** 2) + np.sum(corrupcion ** 2))

        mejor = None
        for umbral_a0, umbral_f0 in INICIOS_UMBRALES:
            theta0 = np.concatenate([[sesgo0], pesos0, np.full(n_a, umbral_a0), np.zeros(n_a),
                                     np.full(n_f, umbral_f0), np.zeros(n_f), np.zeros(n_f)])
            intento = minimize(perdida, theta0, method="L-BFGS-B", bounds=limites)
            if mejor is None or intento.fun < mejor.fun:
                mejor = intento
        self.theta = mejor.x
        return self

    def n_parametros(self) -> int:
        # Parámetros que realmente se ajustan: sesgo, peso por afinidad, umbral y
        # desplome por filtro, más los de pisos y corrupción si están activos.
        n_a, n_f = len(self.afinidades), len(self.filtros)
        return (1 + n_a + 2 * n_f + (2 * n_a if self.usar_pisos else 0)
                + (n_f if self.usar_corrupcion and self.pares else 0))

    def predict(self, A, F, E):
        return self._predecir(self.theta, A, F, E)

    def describir(self) -> list:
        sesgo, pesos, umbral_a, piso, umbral_f, desplome, corrupcion = self._separar(self.theta)
        lineas = ["Nota base = {:.2f} + {}".format(
            sesgo[0], " + ".join(f"{p:.2f}·{n}" for p, n in zip(pesos, self.afinidades)) or "0")]
        for i, filtro in enumerate(self.filtros):
            efectos = []
            if desplome[i] >= 0.05:
                efectos.append(f"resta hasta {desplome[i]:.2f} puntos")
            afectadas = [self.afinidades[i_a] for i_a, i_f in self.pares if i_f == i]
            if afectadas and corrupcion[i] >= 0.05:
                efectos.append(f"reduce {', '.join(afectadas)} en {corrupcion[i]:.0%}")
            if efectos:
                lineas.append(f"Si {filtro} supera {umbral_f[i]:.1f} y su excepción no aplica: {'; '.join(efectos)}.")
        for i, afinidad in enumerate(self.afinidades):
            if piso[i] >= 0.5:
                lineas.append(f"Si {afinidad} supera {umbral_a[i]:.1f}: la nota global queda en al menos ~{piso[i]:.1f}.")
        return lineas

    def parametros(self) -> dict:
        sesgo, pesos, umbral_a, piso, umbral_f, desplome, corrupcion = self._separar(self.theta)
        return {
            "sesgo": float(sesgo[0]),
            "afinidades": {n: {"peso": float(pesos[i]), "umbral_piso": float(umbral_a[i]), "piso": float(piso[i])}
                           for i, n in enumerate(self.afinidades)},
            "filtros": {n: {"umbral": float(umbral_f[i]), "desplome": float(desplome[i]), "corrupcion": float(corrupcion[i])}
                        for i, n in enumerate(self.filtros)},
        }


def escalar_columnas(X, pesos):
    return X * pesos


def subconjunto_rasgos(rasgos: dict | None, indices) -> dict | None:
    # Subconjunto de películas de los rasgos de frases (columna -> matriz).
    return None if rasgos is None else {columna: matriz[indices] for columna, matriz in rasgos.items()}


class ModeloDosEtapas:
    """Etapa 1 (embedding -> puntaje de cada criterio) + etapa 2 (ReglaGlobal)."""

    def __init__(self, afinidades, filtros, corrupciones, modo_frases: str = "concatenar"):
        # modo_frases: ver MODOS_FRASES.
        if modo_frases not in MODOS_FRASES:
            raise ValueError(f"modo_frases debe ser uno de {MODOS_FRASES}")
        self.modo_frases = modo_frases
        self.afinidades, self.filtros = afinidades, filtros
        self.regla = ReglaGlobal(afinidades, filtros, corrupciones)
        self.columnas = ([nombre_columna_gt("afinidad", n) for n in afinidades]
                         + [nombre_columna_gt("restrictivos", n) for n in filtros]
                         + [nombre_columna_excepcion(n) for n in filtros])
        self.predictores, self.constantes = {}, {}

    def _entrada(self, columna, embeddings, rasgos):
        if not rasgos or columna not in rasgos:
            return embeddings
        if self.modo_frases == "solo_frases":
            return rasgos[columna]
        return np.hstack([embeddings, rasgos[columna]])

    def fit(self, embeddings, puntajes, puntajes_etapa_2, y_etapa_2, rasgos=None):
        # Etapa 1 con las películas que tienen embedding; etapa 2 con todas las
        # que tienen puntajes completos en la Verdad Base (no necesita reseñas).
        self.fit_etapa_1(embeddings, puntajes, rasgos)
        self.regla.fit(*matrices_puntajes(puntajes_etapa_2, self.afinidades, self.filtros), y_etapa_2)
        return self

    def fit_etapa_1(self, embeddings, puntajes, rasgos=None):
        for columna in self.columnas:
            if columna not in puntajes:
                self.constantes[columna] = 0.0
                continue
            valores = puntajes[columna].to_numpy(float)
            con_dato = ~np.isnan(valores)
            if con_dato.sum() >= MINIMO_EJEMPLOS_ETAPA_1:
                entrada = self._entrada(columna, embeddings, rasgos)
                pasos = [StandardScaler()]
                if self.modo_frases == "ponderar" and rasgos and columna in rasgos:
                    n_rasgos = rasgos[columna].shape[1]
                    pesos = np.ones(entrada.shape[1])
                    pesos[-n_rasgos:] = np.sqrt(embeddings.shape[1] / n_rasgos)
                    pasos.append(FunctionTransformer(escalar_columnas, kw_args={"pesos": pesos}))
                self.predictores[columna] = make_pipeline(*pasos, RidgeCV(alphas=ALFAS_ETAPA_1)).fit(
                    entrada[con_dato], valores[con_dato])
            else:
                self.constantes[columna] = float(np.nanmean(valores)) if con_dato.any() else 0.0
        return self

    def n_parametros_etapa_1(self) -> int:
        # Un coeficiente por variable de entrada (dimensiones del embedding y
        # rasgos de frases) más el sesgo, por cada criterio predicho (regularizados con Ridge).
        return sum(len(p[-1].coef_) + 1 for p in self.predictores.values())

    def predecir_puntajes(self, embeddings, rasgos=None):
        puntajes = {}
        for columna in self.columnas:
            if columna in self.predictores:
                valores = self.predictores[columna].predict(self._entrada(columna, embeddings, rasgos))
            else:
                valores = np.full(len(embeddings), self.constantes[columna])
            limite = 1.0 if columna.startswith("gt_excepcion_") else 10.0
            puntajes[columna] = np.clip(valores, 0.0, limite)
        return pd.DataFrame(puntajes)

    def predict(self, embeddings, rasgos=None):
        return self.regla.predict(*matrices_puntajes(self.predecir_puntajes(embeddings, rasgos), self.afinidades, self.filtros))


def evaluar(perfil: dict, df_gt, film_ids, embeddings, n_particiones: int, semilla: int = 0) -> dict:
    # Validación cruzada del modelo en dos etapas y de la etapa 2 por separado,
    # y modelo final entrenado con todos los datos. film_ids y embeddings son las
    # películas con reseñas y nota global; df_gt debe tener la columna canon_id.
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error
    from sklearn.model_selection import KFold

    afinidades, filtros, corrupciones, faltantes = criterios_del_perfil(perfil, df_gt.columns)
    if faltantes:
        print(f"[!] Aviso: sin columna en la Verdad Base, se omiten del modelo de reglas: {', '.join(faltantes)}")

    A, F, E = matrices_puntajes(df_gt, afinidades, filtros)
    completas = ~(np.isnan(A).any(axis=1) | np.isnan(F).any(axis=1) | df_gt["gt_nota_global"].isna().to_numpy())
    gt_completa = df_gt[completas].reset_index(drop=True)
    A, F, E = A[completas], F[completas], E[completas]
    y2 = gt_completa["gt_nota_global"].to_numpy(float)
    print(f"Criterios: {len(afinidades)} afinidades, {len(filtros)} filtros, {len(corrupciones)} relaciones de corrupción.")
    print(f"Etapa 2 con {len(y2)} películas con todos sus puntajes en la Verdad Base.")

    # Etapa 2 sola: ¿cuánto de la nota global explican los puntajes de Gemini?
    print("\nEtapa 2 por separado (puntajes reales de Gemini -> nota global):")
    pred_regla, pred_lineal, pred_base = np.empty(len(y2)), np.empty(len(y2)), np.empty(len(y2))
    X = np.column_stack([A, F, E])
    k2 = min(n_particiones, len(y2))
    for numero, (tr, te) in enumerate(KFold(k2, shuffle=True, random_state=semilla).split(X), 1):
        pred_regla[te] = ReglaGlobal(afinidades, filtros, corrupciones).fit(A[tr], F[tr], E[tr], y2[tr]).predict(A[te], F[te], E[te])
        pred_lineal[te] = LinearRegression().fit(X[tr], y2[tr]).predict(X[te])
        pred_base[te] = y2[tr].mean()
        print(f"  Partición {numero}/{k2}: MAE regla {mean_absolute_error(y2[te], pred_regla[te]):.3f} "
              f"| MAE lineal sobre puntajes {mean_absolute_error(y2[te], pred_lineal[te]):.3f}")

    # Modelo completo: etapa 1 + etapa 2, sobre películas que no vio.
    print("\nModelo completo (reseñas -> puntajes -> nota global):")
    indice_gt = {canon: i for i, canon in enumerate(df_gt["canon_id"])}
    puntajes = df_gt.iloc[[indice_gt[f] for f in film_ids]].reset_index(drop=True)
    y = puntajes["gt_nota_global"].to_numpy(float)
    modelo_vacio = ModeloDosEtapas(afinidades, filtros, corrupciones)
    pred_completo = np.empty(len(y))
    pred_puntajes = pd.DataFrame(index=range(len(y)), columns=modelo_vacio.columnas, dtype=float)
    k = min(n_particiones, len(y))
    for numero, (tr, te) in enumerate(KFold(k, shuffle=True, random_state=semilla).split(embeddings), 1):
        prueba = set(np.asarray(film_ids)[te])
        entrenamiento_2 = ~gt_completa["canon_id"].isin(prueba).to_numpy()
        modelo = ModeloDosEtapas(afinidades, filtros, corrupciones).fit(
            embeddings[tr], puntajes.iloc[tr], gt_completa[entrenamiento_2], y2[entrenamiento_2])
        pred_completo[te] = modelo.predict(embeddings[te])
        pred_puntajes.iloc[te] = modelo.predecir_puntajes(embeddings[te]).to_numpy()
        print(f"  Partición {numero}/{k}: MAE {mean_absolute_error(y[te], pred_completo[te]):.3f}")

    etapa_1 = {}
    for columna in modelo_vacio.columnas:
        if columna in puntajes:
            reales = puntajes[columna].to_numpy(float)
            con_dato = ~np.isnan(reales)
            # Una columna constante (ej. una excepción que nunca aplica) no dice nada.
            if con_dato.sum() >= 2 and np.std(reales[con_dato]) > 0:
                etapa_1[columna] = metricas(reales[con_dato], pred_puntajes[columna].to_numpy(float)[con_dato])

    print("\nEntrenando el modelo de reglas final con todos los datos...")
    final = ModeloDosEtapas(afinidades, filtros, corrupciones).fit(embeddings, puntajes, gt_completa, y2)
    return {
        "modelo": final,
        "pred_cv": pred_completo,
        "metricas": {
            "completo": metricas(y, pred_completo),
            "etapa_2_regla": metricas(y2, pred_regla),
            "etapa_2_lineal": metricas(y2, pred_lineal),
            "etapa_2_linea_base": metricas_linea_base(y2, pred_base),
            "etapa_1_por_criterio": etapa_1,
        },
    }


def comparar_representaciones(perfil: dict, df_gt, film_ids, representaciones: dict, n_particiones: int,
                              semilla: int = 0) -> pd.DataFrame:
    # Evalúa el modelo en dos etapas con distintas formas de resumir las reseñas
    # de cada película (representaciones: nombre -> matriz alineada con film_ids,
    # o tupla (matriz, rasgos de frases, modo_frases)). La columna r2_por_criterio
    # trae el R² de la etapa 1 de cada criterio.
    # Todas usan las mismas particiones, y la etapa 2 (que no depende de las
    # reseñas) se entrena una sola vez por partición. Se ordenan por NDCG: para
    # recomendar importa sobre todo qué películas quedan arriba.
    from sklearn.metrics import r2_score
    from sklearn.model_selection import KFold

    afinidades, filtros, corrupciones, _ = criterios_del_perfil(perfil, df_gt.columns)
    A, F, E = matrices_puntajes(df_gt, afinidades, filtros)
    completas = ~(np.isnan(A).any(axis=1) | np.isnan(F).any(axis=1) | df_gt["gt_nota_global"].isna().to_numpy())
    gt_completa = df_gt[completas].reset_index(drop=True)
    A, F, E = A[completas], F[completas], E[completas]
    y2 = gt_completa["gt_nota_global"].to_numpy(float)

    indice_gt = {canon: i for i, canon in enumerate(df_gt["canon_id"])}
    puntajes = df_gt.iloc[[indice_gt[f] for f in film_ids]].reset_index(drop=True)
    y = puntajes["gt_nota_global"].to_numpy(float)
    particiones = list(KFold(min(n_particiones, len(y)), shuffle=True, random_state=semilla).split(np.zeros(len(y))))

    print(f"Entrenando la etapa 2 una vez por partición ({len(particiones)})...")
    reglas = []
    for _, te in particiones:
        fuera = ~gt_completa["canon_id"].isin(set(np.asarray(film_ids)[te])).to_numpy()
        reglas.append(ReglaGlobal(afinidades, filtros, corrupciones).fit(A[fuera], F[fuera], E[fuera], y2[fuera]))

    columnas_a = [nombre_columna_gt("afinidad", n) for n in afinidades]
    columnas_f = [nombre_columna_gt("restrictivos", n) for n in filtros]
    resultados = []
    for nombre, representacion in representaciones.items():
        X, rasgos, modo = representacion if isinstance(representacion, tuple) else (representacion, None, "concatenar")
        pred = np.empty(len(y))
        pred_puntajes = pd.DataFrame(index=range(len(y)), columns=columnas_a + columnas_f, dtype=float)
        for (tr, te), regla in zip(particiones, reglas):
            modelo = ModeloDosEtapas(afinidades, filtros, corrupciones, modo).fit_etapa_1(
                X[tr], puntajes.iloc[tr], subconjunto_rasgos(rasgos, tr))
            modelo.regla = regla
            pred[te] = modelo.predict(X[te], subconjunto_rasgos(rasgos, te))
            pred_puntajes.iloc[te] = modelo.predecir_puntajes(X[te], subconjunto_rasgos(rasgos, te))[columnas_a + columnas_f].to_numpy()

        r2_por_criterio = {}
        for c in columnas_a + columnas_f:
            reales = puntajes[c].to_numpy(float)
            ok = ~np.isnan(reales)
            if ok.sum() >= 2 and np.std(reales[ok]) > 0:
                r2_por_criterio[c] = float(r2_score(reales[ok], pred_puntajes[c].to_numpy(float)[ok]))

        def r2_medio(columnas):
            valores = [r2_por_criterio[c] for c in columnas if c in r2_por_criterio]
            return float(np.mean(valores)) if valores else float("nan")

        # Variables de entrada por criterio: el embedding y/o los rasgos de frases de ese criterio.
        anchos = sorted({modelo._entrada(c, X[:1], subconjunto_rasgos(rasgos, [0])).shape[1] for c in columnas_a + columnas_f})
        resultados.append({"representacion": nombre,
                           "dimensiones": str(anchos[0]) if len(anchos) == 1 else f"{anchos[0]}-{anchos[-1]}",
                           **columnas_metricas(metricas(y, pred)),
                           "R² etapa 1 afinidades": r2_medio(columnas_a), "R² etapa 1 filtros": r2_medio(columnas_f),
                           "r2_por_criterio": r2_por_criterio})
        fila = resultados[-1]
        print(f"  {nombre:45} MAE {fila['MAE']:.3f} | ρ {fila['ρ Spearman']:.3f} | NDCG@{K_RANKING} {fila[f'NDCG@{K_RANKING}']:.3f} "
              f"| etapa 1: afinidades {fila['R² etapa 1 afinidades']:.3f}, filtros {fila['R² etapa 1 filtros']:.3f}")
    return pd.DataFrame(resultados).sort_values(f"NDCG@{K_RANKING}", ascending=False, ignore_index=True)


def columnas_metricas(m: dict) -> dict:
    # Nombres de columna para las tablas de comparación.
    return {"MAE": m["mae"], "R²": m["r2"], "ρ Spearman": m["spearman"],
            f"NDCG@{K_RANKING}": m[f"ndcg@{K_RANKING}"], f"Precisión@{K_RANKING}": m[f"precision@{K_RANKING}"]}

"""
Experimento: ¿detectan mejor los filtros unas frases sonda escritas con el
vocabulario de las reseñas que la descripción del filtro en el perfil?

Para cada película y cada texto (descripción o sonda) se calcula la similitud
de todos sus chunks con el texto, resumida como promedio, percentil 90 y
fracción de chunks por sobre el percentil 95 global, y se correlaciona
(Spearman) con el puntaje de Gemini para ese filtro. Se repite usando solo los
chunks de reseñas en inglés, porque los de otros idiomas aparecen de más entre
los más similares. Solo guarda números e identificadores de chunks, nunca
texto de reseñas.

Uso (desde la raíz del repo, con embeddings de reseñas ya generados):
    python -m src.experimentos.sondas_filtros
"""

import json
from datetime import datetime

import chromadb
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sentence_transformers import SentenceTransformer

from src.config import DIR_ANALISIS, DIR_CHROMA, DIR_FILTRADOS, EMBEDDING_MODEL_NAME, PREFIJO_EMBEDDINGS, RUTA_GT, SRC_DIR
from src.normalizacion import canonicalizar_film_id, nombre_columna_gt

SONDAS = {
    "Camaradería Masculina Rancia": [
        "sexist humor where women are only objects or jokes",
        "the women are just props for the men and their friendship",
        "humor machista y sexista, las mujeres son un chiste",
    ],
    "Insoportabilidad Prolongada": [
        "the main character is insufferable, arrogant and smug",
        "I couldn't stand the protagonist, he is a pretentious narcissist and a creep",
        "an unlikable, annoying character you have to spend the whole movie with",
        "un protagonista insoportable, arrogante y pedante",
    ],
    "Control Emocional Artificial": [
        "emotionally manipulative, the music tells you exactly what to feel",
        "so sweet, whimsical and quirky that it becomes saccharine and twee",
        "technically perfect but cold, calculated and polished",
        "Oscar bait designed to make you cry",
    ],
    "Personajes Diorama": [
        "beautiful and symmetrical but emotionally hollow",
        "style over substance, the characters feel like dolls in a dollhouse",
        "the characters have no personality beyond their job or quirk",
    ],
    "Caos Asfixiante": [
        "chaotic, frantic and exhausting, it never lets you breathe",
        "overstimulating, loud and relentless, too much happening at once",
        "caótica y agotadora, no da respiro",
    ],
}
CASOS = ["manhattan", "amelie", "la-la-land"]
TAMANO_PAGINA = 5000


def cargar_chunks_con_ids(cliente):
    coleccion = cliente.get_collection("resenias")
    ids, vectores = [], []
    for inicio in range(0, coleccion.count(), TAMANO_PAGINA):
        datos = coleccion.get(include=["embeddings"], limit=TAMANO_PAGINA, offset=inicio)
        ids.extend(datos["ids"])
        vectores.append(np.asarray(datos["embeddings"], dtype=np.float32))
    matriz = np.vstack(vectores)
    matriz /= np.maximum(np.linalg.norm(matriz, axis=1, keepdims=True), 1e-12)
    peliculas = np.array([canonicalizar_film_id(i.split("::")[0]) for i in ids])
    return np.array(ids), peliculas, matriz


def idiomas_de_chunks(ids):
    # El idioma está en el csv filtrado de cada lote; review_N es la fila en ese csv.
    lotes = {}
    idiomas = []
    for i in ids:
        _, lote, resenia, _ = i.split("::")
        if lote not in lotes:
            ruta = DIR_FILTRADOS / f"{lote}.csv"
            # Los lotes de los csv antiguos no tienen idioma: quedan como desconocido.
            tabla = pd.read_csv(ruta) if ruta.exists() else None
            lotes[lote] = tabla["lang"].to_numpy() if tabla is not None and "lang" in tabla else None
        idiomas.append(lotes[lote][int(resenia.split("_")[1])] if lotes[lote] is not None else None)
    return np.array(idiomas, dtype=object)


def main():
    perfil = json.loads((SRC_DIR / "db" / "profiles" / "perfiles.ejemplo.json").read_text(encoding="utf-8"))
    perfil = next(iter(perfil.values()))
    gt = pd.read_csv(RUTA_GT)
    gt["canon"] = gt["film_id"].apply(canonicalizar_film_id)

    print(f"Cargando chunks de {DIR_CHROMA}...")
    ids, peliculas, matriz = cargar_chunks_con_ids(chromadb.PersistentClient(path=str(DIR_CHROMA)))
    evaluadas = [f for f in gt["canon"] if f in set(peliculas)]
    indices = {f: np.flatnonzero(peliculas == f) for f in evaluadas + [c for c in CASOS if c not in evaluadas]}
    idiomas = idiomas_de_chunks(ids)
    en_ingles = idiomas == "en"
    print(f"{len(ids)} chunks ({en_ingles.mean():.0%} en inglés, {pd.isna(idiomas).mean():.0%} sin idioma conocido); "
          f"{len(evaluadas)} películas evaluadas con reseñas.")
    rng = np.random.default_rng(0)
    variantes = {"todos": np.ones(len(ids), bool), "solo inglés": en_ingles}
    muestras = {v: matriz[rng.choice(np.flatnonzero(m), min(20000, m.sum()), replace=False)] for v, m in variantes.items()}

    modelo = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cpu")
    filas, top = [], {}
    for filtro, sondas in SONDAS.items():
        descripcion = f"{filtro}. {perfil['restrictivos'][filtro]['descripcion']}"
        textos = {"descripción del perfil": descripcion, **{f"sonda {i + 1}: {s}": s for i, s in enumerate(sondas)}}
        vectores = modelo.encode([PREFIJO_EMBEDDINGS + t for t in textos.values()], normalize_embeddings=True)
        puntajes = gt.set_index("canon").loc[evaluadas, nombre_columna_gt("restrictivos", filtro)].to_numpy(float)

        fracciones_sondas = {v: [] for v in variantes}
        for (nombre, _), vector in zip(textos.items(), vectores):
            for variante, mascara in variantes.items():
                umbral = np.percentile(muestras[variante] @ vector, 95)
                metricas = {"promedio": [], "percentil 90": [], "fracción sobre p95": []}
                for f in evaluadas:
                    s = matriz[indices[f][mascara[indices[f]]]] @ vector
                    if not len(s):  # película sin chunks en esta variante
                        for valores in metricas.values():
                            valores.append(np.nan)
                        continue
                    metricas["promedio"].append(s.mean())
                    metricas["percentil 90"].append(np.percentile(s, 90))
                    metricas["fracción sobre p95"].append((s > umbral).mean())
                for metrica, valores in metricas.items():
                    rho, p = spearmanr(valores, puntajes, nan_policy="omit")
                    filas.append({"filtro": filtro, "chunks": variante, "texto": nombre, "métrica": metrica, "rho": round(float(rho), 3), "p": round(float(p), 4)})
                if nombre != "descripción del perfil":
                    fracciones_sondas[variante].append(metricas["fracción sobre p95"])
            for caso in CASOS:
                if caso in indices:
                    s = matriz[indices[caso]] @ vector
                    orden = np.argsort(-s)[:5]
                    top.setdefault(caso, {}).setdefault(filtro, {})[nombre] = [
                        {"id": str(ids[indices[caso][k]]), "similitud": round(float(s[k]), 3)} for k in orden]
        for variante, fracciones in fracciones_sondas.items():
            rho, p = spearmanr(np.nanmean(fracciones, axis=0), puntajes, nan_policy="omit")
            filas.append({"filtro": filtro, "chunks": variante, "texto": "sondas combinadas", "métrica": "fracción sobre p95", "rho": round(float(rho), 3), "p": round(float(p), 4)})
        mejor = max((f for f in filas if f["filtro"] == filtro), key=lambda f: f["rho"])
        print(f"{filtro}: mejor ρ = {mejor['rho']:.2f} ({mejor['texto'][:50]}, {mejor['métrica']})")

    tabla = pd.DataFrame(filas)
    carpeta = DIR_ANALISIS / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_sondas"
    carpeta.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(carpeta / "sondas.csv", index=False, encoding="utf-8")
    (carpeta / "top_chunks.json").write_text(json.dumps(top, indent=1, ensure_ascii=False), encoding="utf-8")

    lineas = [f"# Frases sonda para los filtros ({EMBEDDING_MODEL_NAME})", "",
              f"{len(evaluadas)} películas evaluadas. ρ de Spearman entre la métrica y el puntaje de Gemini del filtro.", ""]
    for filtro in SONDAS:
        sub = tabla[tabla.filtro == filtro].sort_values("rho", ascending=False)
        lineas += [f"## {filtro}", "", "| chunks | texto | métrica | ρ | p |", "|---|---|---|---|---|"]
        lineas += [f"| {r.chunks} | {r.texto} | {r.métrica} | {r.rho:.3f} | {r.p:.4f} |" for r in sub.itertuples()]
        lineas.append("")
    (carpeta / "resumen.md").write_text("\n".join(lineas), encoding="utf-8")
    print(f"Resultados en {carpeta}")


if __name__ == "__main__":
    main()

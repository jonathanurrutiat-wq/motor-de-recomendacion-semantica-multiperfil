"""
Formas de resumir los chunks de reseñas de una película en un solo vector
(pooling), para comparar cuál predice mejor en la opción 9.
"""

from collections import defaultdict

import numpy as np

from src.normalizacion import canonicalizar_film_id

PERCENTILES_SIMILITUD = (50, 75, 90, 100)
TAMANO_PAGINA = 5000


def cargar_chunks(cliente) -> dict:
    # film_id -> (rango de la reseña dentro de la película, matriz de embeddings
    # de sus chunks). Las reseñas de cada lote están ordenadas por likes, así que
    # el rango 0 es la reseña con más likes.
    coleccion = cliente.get_collection("resenias")
    por_pelicula = defaultdict(list)
    # Por páginas: con decenas de miles de chunks, una sola consulta con
    # metadatos supera el límite de variables de SQLite.
    for inicio in range(0, coleccion.count(), TAMANO_PAGINA):
        datos = coleccion.get(include=["embeddings", "metadatas"], limit=TAMANO_PAGINA, offset=inicio)
        for id_chunk, vector, meta in zip(datos["ids"], datos["embeddings"], datos["metadatas"]):
            film_id = canonicalizar_film_id(id_chunk.split("::")[0])
            por_pelicula[film_id].append(((meta.get("lote", ""), meta.get("review_idx", 0)), vector))

    chunks = {}
    for film_id, filas in por_pelicula.items():
        orden = {resenia: rango for rango, resenia in enumerate(sorted({clave for clave, _ in filas}))}
        rangos = np.array([orden[clave] for clave, _ in filas])
        chunks[film_id] = (rangos, np.array([vector for _, vector in filas], dtype=np.float32))
    return chunks


def representar(chunks: dict, film_ids, estrategia: str, max_resenias: int | None = None,
                embeddings_perfil=None) -> np.ndarray:
    # estrategia: "media", "pXX" (percentil XX de cada dimensión del embedding) o
    # "media+similitud" (media + percentiles de la similitud de los chunks con
    # cada término del perfil).
    if estrategia == "media+similitud":
        perfil = embeddings_perfil / np.maximum(np.linalg.norm(embeddings_perfil, axis=1, keepdims=True), 1e-12)

    filas = []
    for film_id in film_ids:
        rangos, matriz = chunks[film_id]
        if max_resenias is not None:
            matriz = matriz[rangos < max_resenias]
        if estrategia == "media":
            filas.append(matriz.mean(axis=0))
        elif estrategia.startswith("p") and estrategia[1:].isdigit():
            filas.append(np.percentile(matriz, int(estrategia[1:]), axis=0))
        elif estrategia == "media+similitud":
            normalizada = matriz / np.maximum(np.linalg.norm(matriz, axis=1, keepdims=True), 1e-12)
            similitudes = normalizada @ perfil.T
            filas.append(np.concatenate([matriz.mean(axis=0),
                                         np.percentile(similitudes, PERCENTILES_SIMILITUD, axis=0).ravel()]))
        else:
            raise ValueError(f"Estrategia de pooling desconocida: {estrategia}")
    return np.array(filas)


def nombre(estrategia: str, max_resenias: int | None) -> str:
    descripcion = {"media": "promedio", "media+similitud": "promedio + percentiles de similitud"}.get(
        estrategia, f"percentil {estrategia[1:]} por dimensión")
    return f"{descripcion}, {'todas las' if max_resenias is None else f'hasta {max_resenias}'} reseñas"

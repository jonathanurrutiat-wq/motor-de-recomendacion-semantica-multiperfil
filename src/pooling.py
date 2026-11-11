"""
Formas de resumir los chunks de reseñas de una película en un solo vector
(pooling), para comparar cuál predice mejor en la opción 9.
"""

from collections import defaultdict

import numpy as np

from src.normalizacion import canonicalizar_film_id, nombre_columna_gt

PERCENTILES_SIMILITUD = (50, 75, 90, 100)
TAMANO_PAGINA = 5000
# Rasgos de frases de reseña: un chunk "habla" de un texto si su similitud con
# él supera este percentil entre todos los chunks.
PERCENTIL_UMBRAL_FRASES = 95
MUESTRA_UMBRAL_FRASES = 20000


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


def textos_de_criterios(coleccion_perfiles, nombre_perfil: str, perfil: dict) -> dict:
    # Para cada criterio con frases_resenia en el perfil: columna de la Verdad
    # Base -> (nombres de los textos, embeddings). El primer texto es la
    # descripción del perfil y los demás, sus frases de reseña.
    datos = coleccion_perfiles.get(where={"persona": nombre_perfil}, include=["embeddings", "metadatas"])
    descripciones, frases = {}, {}
    for meta, vector in zip(datos["metadatas"], datos["embeddings"]):
        if meta["tipo"] in ("restrictivos", "afinidad"):
            descripciones[(meta["tipo"], meta["filtro"])] = vector
        elif meta["tipo"] == "frase_resenia":
            frases.setdefault((meta["categoria"], meta["filtro"]), []).append((meta["indice"], vector))

    textos = {}
    for tipo in ("restrictivos", "afinidad"):
        for nombre_criterio, datos_criterio in perfil.get(tipo, {}).items():
            clave = (tipo, nombre_criterio)
            if not datos_criterio.get("frases_resenia"):
                continue
            if clave not in descripciones or len(frases.get(clave, [])) != len(datos_criterio["frases_resenia"]):
                print(f"[!] Aviso: faltan embeddings de las frases de reseña de '{nombre_criterio}'; se omiten. "
                      "Vuelve a ejecutar el módulo 3 si editaste el perfil.")
                continue
            vectores = [descripciones[clave]] + [v for _, v in sorted(frases[clave], key=lambda par: par[0])]
            nombres = ["descripción"] + list(datos_criterio["frases_resenia"])
            textos[nombre_columna_gt(tipo, nombre_criterio)] = (nombres, np.array(vectores, dtype=np.float32))
    return textos


def _textos_normalizados(textos: dict, solo_descripcion: bool):
    columnas = list(textos)
    bloques = [textos[c][1][:1] if solo_descripcion else textos[c][1] for c in columnas]
    todos = np.vstack(bloques)
    return columnas, bloques, todos / np.maximum(np.linalg.norm(todos, axis=1, keepdims=True), 1e-12)


def _similitudes(matriz, textos_normalizados):
    normalizada = matriz / np.maximum(np.linalg.norm(matriz, axis=1, keepdims=True), 1e-12)
    return normalizada @ textos_normalizados.T


def umbrales_frases(chunks: dict, textos: dict, solo_descripcion: bool = False) -> np.ndarray:
    # Umbral de similitud por texto, con una muestra de chunks de todas las
    # películas (no usa notas). El modelo guardado conserva los suyos para
    # medir igual a las películas que se recomiendan después.
    _, _, todos = _textos_normalizados(textos, solo_descripcion)
    rng = np.random.default_rng(0)
    peliculas = list(chunks)
    tamanos = np.array([len(chunks[f][1]) for f in peliculas])
    elegidos = np.sort(rng.choice(tamanos.sum(), min(MUESTRA_UMBRAL_FRASES, tamanos.sum()), replace=False))
    # Sin juntar todos los chunks en una sola matriz (con e5 pesaría cientos de MB).
    inicios = np.concatenate([[0], np.cumsum(tamanos)])
    muestra = np.vstack([chunks[f][1][elegidos[(elegidos >= a) & (elegidos < b)] - a]
                         for f, a, b in zip(peliculas, inicios[:-1], inicios[1:])])
    return np.percentile(_similitudes(muestra, todos), PERCENTIL_UMBRAL_FRASES, axis=0)


def rasgos_frases(chunks: dict, film_ids, textos: dict, max_resenias: int | None = None,
                  solo_descripcion: bool = False, umbrales=None) -> dict:
    # Para cada criterio de textos: matriz (películas x 2 por texto) con la
    # fracción de chunks de la película que superan el umbral de similitud con
    # el texto y el percentil 90 de esa similitud. Resume cuántas reseñas
    # hablan del rasgo, en vez de diluirlo en el promedio de todas.
    if not textos:
        return {}
    columnas, bloques, todos = _textos_normalizados(textos, solo_descripcion)
    if umbrales is None:
        umbrales = umbrales_frases(chunks, textos, solo_descripcion)
    similitudes = lambda matriz: _similitudes(matriz, todos)

    filas = []
    for film_id in film_ids:
        rangos, matriz = chunks[film_id]
        if max_resenias is not None:
            matriz = matriz[rangos < max_resenias]
        s = similitudes(matriz)
        filas.append(np.concatenate([(s > umbrales).mean(axis=0), np.percentile(s, 90, axis=0)]))
    filas = np.array(filas)

    n_textos = len(todos)
    rasgos, inicio = {}, 0
    for columna, bloque in zip(columnas, bloques):
        indices = np.arange(inicio, inicio + len(bloque))
        rasgos[columna] = np.column_stack([filas[:, indices], filas[:, n_textos + indices]])
        inicio += len(bloque)
    return rasgos

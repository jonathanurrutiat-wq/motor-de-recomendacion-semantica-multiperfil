"""
Reutilización de embeddings de reseñas ya calculados. Cada lote filtrado de una
fuente (ej. reviews.db) trae todas sus reseñas, así que cuando llega una versión
nueva de la base casi todos sus chunks ya están vectorizados en el lote
anterior: solo se codifican los chunks cuyo texto no está en la colección, y
el lote anterior se elimina para no duplicar chunks.
"""

import re
from pathlib import Path

import numpy as np

TAMANO_PAGINA = 5000
# Nombre que da filter.py a cada lote: filtrado_<fuente>_<fecha>_<hora>.
_PATRON_LOTE = re.compile(r"^filtrado_(?P<fuente>.+)_(?P<fecha>\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$")


def fuente_del_lote(lote: str) -> str:
    # "filtrado_reviews_2026-10-18_23-15-02" -> "reviews"
    coincidencia = _PATRON_LOTE.match(lote)
    return coincidencia["fuente"] if coincidencia else lote


def _fecha_del_lote(lote: str) -> str:
    coincidencia = _PATRON_LOTE.match(lote)
    return coincidencia["fecha"] if coincidencia else ""


def ultimos_por_fuente(archivos) -> list[Path]:
    # Solo el filtrado más reciente de cada fuente: los anteriores quedaron reemplazados.
    ultimos = {}
    for archivo in archivos:
        fuente = fuente_del_lote(archivo.stem)
        if fuente not in ultimos or _fecha_del_lote(archivo.stem) > _fecha_del_lote(ultimos[fuente].stem):
            ultimos[fuente] = archivo
    return sorted(ultimos.values(), key=lambda p: _fecha_del_lote(p.stem))


def lotes_reemplazados(lotes) -> list[str]:
    # Lotes de los que hay uno más reciente de la misma fuente.
    vigentes = {}
    for lote in lotes:
        fuente = fuente_del_lote(lote)
        if fuente not in vigentes or _fecha_del_lote(lote) > _fecha_del_lote(vigentes[fuente]):
            vigentes[fuente] = lote
    return sorted(set(lotes) - set(vigentes.values()))


def lotes_de_coleccion(coleccion) -> set[str]:
    lotes = set()
    for inicio in range(0, coleccion.count(), TAMANO_PAGINA):
        datos = coleccion.get(include=["metadatas"], limit=TAMANO_PAGINA, offset=inicio)
        lotes.update(meta.get("lote", "") for meta in datos["metadatas"])
    return lotes - {""}


def vectores_previos(coleccion, textos: set[str]) -> dict:
    # Texto del chunk -> embedding ya guardado, solo para los textos pedidos. El
    # vector depende solo del texto (y del modelo, que tiene su propia base).
    previos = {}
    for inicio in range(0, coleccion.count(), TAMANO_PAGINA):
        datos = coleccion.get(include=["documents", "embeddings"], limit=TAMANO_PAGINA, offset=inicio)
        for texto, vector in zip(datos["documents"], datos["embeddings"]):
            if texto in textos and texto not in previos:
                previos[texto] = np.asarray(vector, dtype="float32")
    return previos


def codificar_reutilizando(textos: list[str], previos: dict, codificar) -> tuple[np.ndarray, int]:
    # codificar(lista de textos) -> matriz de embeddings; se llama solo con los
    # textos sin vector previo (sin repetir). Devuelve los vectores en el orden
    # de textos y cuántos se calcularon.
    nuevos = list(dict.fromkeys(texto for texto in textos if texto not in previos))
    calculados = dict(zip(nuevos, np.asarray(codificar(nuevos), dtype="float32"))) if nuevos else {}
    vectores = np.asarray([previos[texto] if texto in previos else calculados[texto] for texto in textos], dtype="float32")
    return vectores, len(nuevos)

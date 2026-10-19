"""
Compacta la base de ChromaDB del modelo de embeddings actual. Chroma no libera
espacio en disco al eliminar chunks (ej. el lote de reseñas que reemplaza uno
nuevo): la base queda del tamaño de ambos lotes. Este script copia cada
colección a una base nueva y reemplaza la anterior.

Correr con el programa cerrado, en un proceso aparte:
    python src/compactar_chroma.py
"""

import shutil
import subprocess
from pathlib import Path

import chromadb

from config import DIR_CHROMA

TAMANO_PAGINA = 5000


def tamano_mb(ruta: Path) -> float:
    return int(subprocess.run(["du", "-sk", str(ruta)], capture_output=True, text=True).stdout.split()[0]) / 1024


def compactar(ruta: Path) -> tuple[float, float]:
    nueva = ruta.with_name(ruta.name + "_compacta")
    shutil.rmtree(nueva, ignore_errors=True)
    origen = chromadb.PersistentClient(path=str(ruta))
    destino = chromadb.PersistentClient(path=str(nueva))

    # Según la versión de chromadb, list_collections devuelve colecciones o nombres.
    for nombre in [getattr(c, "name", c) for c in origen.list_collections()]:
        coleccion = origen.get_collection(nombre)
        copia = destino.create_collection(nombre, metadata=coleccion.metadata)
        for inicio in range(0, coleccion.count(), TAMANO_PAGINA):
            datos = coleccion.get(include=["embeddings", "documents", "metadatas"], limit=TAMANO_PAGINA, offset=inicio)
            copia.add(ids=datos["ids"], embeddings=datos["embeddings"], documents=datos["documents"],
                      metadatas=datos["metadatas"])
        if copia.count() != coleccion.count():
            raise RuntimeError(f"La copia de '{nombre}' tiene {copia.count()} registros en vez de {coleccion.count()}.")
        print(f"Colección '{nombre}': {copia.count()} registros copiados.")

    antes, despues = tamano_mb(ruta), tamano_mb(nueva)
    shutil.rmtree(ruta)
    nueva.rename(ruta)
    return antes, despues


if __name__ == '__main__':
    if not DIR_CHROMA.exists():
        raise SystemExit(f"No existe la base {DIR_CHROMA}.")
    antes, despues = compactar(DIR_CHROMA)
    print(f"{DIR_CHROMA.name}: {antes:.0f} MB -> {despues:.0f} MB.")

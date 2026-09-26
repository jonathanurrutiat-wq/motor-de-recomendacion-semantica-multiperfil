from pathlib import Path

import chromadb
import numpy as np
import pandas as pd
import semchunk
import torch
from sentence_transformers import SentenceTransformer

from config import DIR_CHROMA, DIR_FILTRADOS, EMBEDDING_MODEL_NAME, PREFIJO_EMBEDDINGS

NOMBRE_COLECCION = "resenias"
TAMANO_TANDA_CHROMA = 5000

COLUMNAS_REQUERIDAS = {"film_id", "review_text"}


"""Selección de lotes filtrados pendientes"""

def obtener_lotes_pendientes(directorio: Path, coleccion) -> list[Path]:
    # Un lote está pendiente si ninguno de sus chunks está en la colección.
    if not directorio.exists():
        raise FileNotFoundError(f"No existe el directorio {directorio}")

    archivos = sorted(directorio.glob("filtrado_*.csv"), key=lambda p: p.stat().st_mtime)
    if not archivos:
        raise FileNotFoundError(f"No se encontraron csv 'filtrado_*.csv' en {directorio}")

    return [
        archivo for archivo in archivos
        if not coleccion.get(where={"lote": archivo.stem}, limit=1, include=[])['ids']
    ]


def limpiar_ids_antiguos(coleccion, eliminar: bool | None = None):
    # Antes el id no incluía el lote ("pelicula::review_N::chunk_M") y
    # reseñas de lotes distintos se pisaban entre sí. Si no se indica qué
    # hacer, se pregunta.
    ids_antiguos = [i for i in coleccion.get(include=[])['ids'] if len(i.split("::")) == 3]
    if not ids_antiguos:
        return

    print(f"\n[!] Hay {len(ids_antiguos)} chunks guardados con el formato de id antiguo (sin lote).")
    print("    Si no se eliminan, quedarán duplicados al volver a vectorizar sus lotes.")
    print(f"    Elimínalos solo si todavía tienes los csv filtrados en {DIR_FILTRADOS}: se vectorizarán de nuevo desde ahí.")
    if eliminar is None:
        eliminar = input("¿Eliminarlos? (s/n): ").strip().lower() == "s"
    if eliminar:
        coleccion.delete(ids=ids_antiguos)
        print(f"Eliminados {len(ids_antiguos)} chunks antiguos.")
    else:
        print("    Se mantienen; se pueden eliminar desde la opción 4 del menú principal.")


def cargar_resenias(csv_path: Path) -> pd.DataFrame:
    resenias = pd.read_csv(csv_path)

    faltantes = COLUMNAS_REQUERIDAS - set(resenias.columns)
    if faltantes:
        raise ValueError(
            f"Al csv '{csv_path.name}' le faltan columnas requeridas: {faltantes}"
        )

    return resenias


"""Proceso de chunking de las reseñas"""

def chunking_resenias(resenias: pd.DataFrame) -> list[dict]:
    chunker = semchunk.chunkerify(EMBEDDING_MODEL_NAME, 128)
    resenias_chunkeadas = []

    for idx, fila in resenias.iterrows():
        texto = fila["review_text"]

        if pd.isna(texto) or not str(texto).strip():
            print(f"[!] Reseña vacía en la fila {idx} (film_id={fila.get('film_id')}), se omite.")
            continue

        chunks = chunker(str(texto))
        resenias_chunkeadas.append({
            "film_id": fila["film_id"],
            "review_idx": idx,
            "chunks": chunks,
        })

    return resenias_chunkeadas


"""Construccion de embeddings"""

def crear_embeddings_resenias(resenias_chunkeadas: list[dict], model: SentenceTransformer) -> list[dict]:
    # Todos los chunks se codifican en una sola pasada por tandas: llamar al
    # modelo una vez por reseña es mucho más lento con lotes grandes.
    entradas = [entrada for entrada in resenias_chunkeadas if entrada["chunks"]]
    todos_los_chunks = [chunk for entrada in entradas for chunk in entrada["chunks"]]
    if not todos_los_chunks:
        return []
    print(f"Codificando {len(todos_los_chunks)} chunks de {len(entradas)} reseñas...")
    vectores = np.asarray(model.encode([PREFIJO_EMBEDDINGS + chunk for chunk in todos_los_chunks], batch_size=64, show_progress_bar=True), dtype="float32")

    resultado, inicio = [], 0
    for entrada in entradas:
        fin = inicio + len(entrada["chunks"])
        resultado.append({
            "film_id": entrada["film_id"],
            "review_idx": entrada["review_idx"],
            "chunks": entrada["chunks"],
            "embeddings": vectores[inicio:fin],
        })
        inicio = fin

    return resultado


"""Persistencia en ChromaDB"""

def guardar_lote(coleccion, lote: str, resenias_embebidas: list[dict]):
    ids, embeddings, documentos, metadatas = [], [], [], []

    for entrada in resenias_embebidas:
        film_id = entrada["film_id"]
        review_idx = entrada["review_idx"]

        for i, (chunk_texto, vector) in enumerate(zip(entrada["chunks"], entrada["embeddings"])):
            ids.append(f"{film_id}::{lote}::review_{review_idx}::chunk_{i}")
            embeddings.append(vector.tolist())
            documentos.append(chunk_texto)
            metadatas.append({
                "film_id": str(film_id),
                "lote": lote,
                "review_idx": int(review_idx),
                "chunk_idx": i,
            })

    if not ids:
        print(f"El lote {lote} no tiene chunks para guardar.")
        return

    # Chroma limita la cantidad de registros por llamada (~5.400).
    for inicio in range(0, len(ids), TAMANO_TANDA_CHROMA):
        fin = inicio + TAMANO_TANDA_CHROMA
        coleccion.upsert(
            ids=ids[inicio:fin],
            embeddings=embeddings[inicio:fin],
            documents=documentos[inicio:fin],
            metadatas=metadatas[inicio:fin],
        )

    print(f"Lote {lote}: {len(ids)} chunks guardados en la colección '{NOMBRE_COLECCION}'.")


def main(eliminar_ids_antiguos: bool | None = None):
    DIR_CHROMA.mkdir(parents=True, exist_ok=True)
    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))
    coleccion = cliente.get_or_create_collection(name=NOMBRE_COLECCION)

    limpiar_ids_antiguos(coleccion, eliminar_ids_antiguos)

    lotes = obtener_lotes_pendientes(DIR_FILTRADOS, coleccion)
    if not lotes:
        print("Todos los lotes filtrados ya están vectorizados. No hay nada nuevo que procesar.")
        return

    print(f"Lotes pendientes de vectorizar: {', '.join(lote.name for lote in lotes)}")

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Cargando nuevo modelo neuronal en memoria ({dispositivo.upper()}). Por favor espere...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=dispositivo)

    for csv_path in lotes:
        print(f"\nLeyendo lote: {csv_path.name}")
        resenias = cargar_resenias(csv_path)

        print("Chunkeando reseñas...")
        resenias_chunkeadas = chunking_resenias(resenias)

        print("Generando embeddings...")
        resenias_embebidas = crear_embeddings_resenias(resenias_chunkeadas, model)

        guardar_lote(coleccion, csv_path.stem, resenias_embebidas)


if __name__ == '__main__':
    main()

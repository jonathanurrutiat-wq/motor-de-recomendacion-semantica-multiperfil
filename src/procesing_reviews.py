from pathlib import Path

import chromadb
import numpy as np
import pandas as pd
import semchunk
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME

DIR_FILTRADOS = Path.cwd() / "src" / "db" / "filtered" / "result"
DIR_CHROMA = Path.cwd() / "src" / "db" / "embeddings" / "chroma"
NOMBRE_COLECCION = "resenias"

COLUMNAS_REQUERIDAS = {"film_id", "review_text"}


"""Selección del lote filtrado más reciente"""

def obtener_csv_mas_reciente(directorio: Path) -> Path:
    if not directorio.exists():
        raise FileNotFoundError(f"No existe el directorio {directorio}")

    archivos = list(directorio.glob("filtrado_*.csv"))
    if not archivos:
        raise FileNotFoundError(f"No se encontraron csv 'filtrado_*.csv' en {directorio}")

    # Por fecha real de modificación, no por el nombre del archivo.
    return max(archivos, key=lambda p: p.stat().st_mtime)


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
    resultado = []

    for entrada in resenias_chunkeadas:
        chunks = entrada["chunks"]
        if not chunks:
            continue

        vectores = model.encode(chunks)
        resultado.append({
            "film_id": entrada["film_id"],
            "review_idx": entrada["review_idx"],
            "chunks": chunks,
            "embeddings": np.asarray(vectores, dtype="float32"),
        })

    return resultado


"""Persistencia en ChromaDB"""

def guardar_coleccion(resenias_embebidas: list[dict]) -> chromadb.api.models.Collection.Collection:
    DIR_CHROMA.mkdir(parents=True, exist_ok=True)

    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))
    coleccion = cliente.get_or_create_collection(name=NOMBRE_COLECCION)

    ids, embeddings, documentos, metadatas = [], [], [], []

    for entrada in resenias_embebidas:
        film_id = entrada["film_id"]
        review_idx = entrada["review_idx"]

        for i, (chunk_texto, vector) in enumerate(zip(entrada["chunks"], entrada["embeddings"])):
            ids.append(f"{film_id}::review_{review_idx}::chunk_{i}")
            embeddings.append(vector.tolist())
            documentos.append(chunk_texto)
            metadatas.append({
                "film_id": str(film_id),
                "review_idx": int(review_idx),
                "chunk_idx": i,
            })

    if not ids:
        print("No hay chunks nuevos para guardar.")
        return coleccion

    # upsert: si vuelves a correr esto sobre el mismo lote, actualiza en vez
    # de duplicar (mismo id = misma película, misma reseña, mismo chunk).
    coleccion.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documentos,
        metadatas=metadatas,
    )

    print(f"Colección '{NOMBRE_COLECCION}' actualizada en: {DIR_CHROMA}")
    print(f"Chunks guardados/actualizados: {len(ids)}")

    return coleccion


def main():
    print("Cargando nuevo modelo neuronal en memoria CUDA. Por favor espere...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cuda")

    csv_path = obtener_csv_mas_reciente(DIR_FILTRADOS)
    print(f"Leyendo lote más reciente: {csv_path.name}")
    resenias = cargar_resenias(csv_path)

    print("Chunkeando reseñas...")
    resenias_chunkeadas = chunking_resenias(resenias)

    print("Generando embeddings...")
    resenias_embebidas = crear_embeddings_resenias(resenias_chunkeadas, model)

    guardar_coleccion(resenias_embebidas)


if __name__ == '__main__':
    main()
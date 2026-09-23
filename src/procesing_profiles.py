import json

import chromadb
import numpy as np
import torch
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from config import DIR_CHROMA, EMBEDDING_MODEL_NAME
from config import RUTA_PERFILES as ARCHIVO_PERFILES

NOMBRE_COLECCION = "perfiles"


"""Carga del perfil desde perfiles.json"""

def obtener_todos_los_perfiles() -> dict:
    if not ARCHIVO_PERFILES.exists():
        raise FileNotFoundError(
            f"No se encontró {ARCHIVO_PERFILES}. Crea uno primero desde la opción 1 del menú principal."
        )
    try:
        with open(ARCHIVO_PERFILES, "r", encoding="utf-8") as archivo:
            todos_los_perfiles = json.load(archivo)
            return todos_los_perfiles if todos_los_perfiles else {}
    except json.JSONDecodeError:
        return {}

def cargar_perfil(nombre_perfil: str) -> dict:
    if not ARCHIVO_PERFILES.exists():
        raise FileNotFoundError(
            f"No se encontró {ARCHIVO_PERFILES}. Crea uno primero desde la opción 1 del menú principal."
        )

    with open(ARCHIVO_PERFILES, "r", encoding="utf-8") as archivo:
        todos_los_perfiles = json.load(archivo)
    
    if not todos_los_perfiles:
        raise ValueError(f"No hay perfiles disponibles en {ARCHIVO_PERFILES}. Crea uno primero desde la opción 1 del menú principal.")

    if nombre_perfil not in todos_los_perfiles:
        disponibles = ", ".join(todos_los_perfiles.keys()) or "ninguno"
        raise KeyError(
            f"El perfil '{nombre_perfil}' no existe en {ARCHIVO_PERFILES}. "
            f"Perfiles disponibles: {disponibles}."
        )

    return {nombre_perfil: todos_los_perfiles[nombre_perfil]}


"""Proceso de chunking del perfil"""

def construir_chunk(perfiles: dict) -> list[Document]:
    documentos = []

    for perfil, categoria in perfiles.items():
        for tipo_categoria, filtros in categoria.items():

            for nombre_filtro, datos in filtros.items():
                partes = [f"Filtro: {nombre_filtro}"]
                partes.append(f"Descripcion: {datos.get('descripcion', '  ')}")

                metadata = {
                    "persona": perfil,
                    "tipo": tipo_categoria,
                    "filtro": nombre_filtro,
                }

                if tipo_categoria == "restrictivos":
                    partes.append(f"Nivel : {datos.get('nivel')}")
                    partes.append(f"Severidad : {datos.get('severidad')}")

                    if datos.get("corrupcion_directa"):
                        partes.append(f"Corrupcion Directa : {datos.get('corrupcion_directa')}")

                    if datos.get("excepcion"):
                        partes.append(f"Excepciones: {datos.get('excepcion')}")

                    metadata["nivel"] = datos.get("nivel")
                    metadata["severidad"] = datos.get("severidad")
                    metadata["corrupcion_directa"] = datos.get("corrupcion_directa", [])
                    metadata["tiene_excepcion"] = bool(datos.get("excepcion"))
                else:
                    partes.append(f"Importancia Base  {datos.get('importancia_base')}")
                    metadata["importancia_base"] = datos.get("importancia_base")

                texto_chunk = "\n".join(partes)
                documentos.append(Document(page_content=texto_chunk, metadata=metadata))

    return documentos


# esto retorna una lista de documentos por perfil chunkeados


"""Construccion de embeddings"""

def extraer_textos(documentos: list[Document]) -> list[str]:
    return [documento.page_content for documento in documentos]


def crear_embeddings(textos: list[str], model: SentenceTransformer) -> np.ndarray:
    embeddings = model.encode(textos)
    return np.asarray(embeddings, dtype="float32")


"""Persistencia en ChromaDB"""

def sanitizar_metadata(metadata: dict) -> dict:
    # Chroma solo acepta str/int/float/bool en metadata: nada de None ni listas.
    limpio = {}
    for clave, valor in metadata.items():
        if valor is None:
            continue
        if isinstance(valor, list):
            limpio[clave] = ", ".join(str(v) for v in valor)
        else:
            limpio[clave] = valor
    return limpio


def construir_id(documento: Document) -> str:
    meta = documento.metadata
    return f"{meta['persona']}::{meta['tipo']}::{meta['filtro']}"


def guardar_coleccion(documentos: list[Document], embeddings: np.ndarray) -> chromadb.api.models.Collection.Collection:
    DIR_CHROMA.mkdir(parents=True, exist_ok=True)

    cliente = chromadb.PersistentClient(path=str(DIR_CHROMA))
    coleccion = cliente.get_or_create_collection(name=NOMBRE_COLECCION)

    ids = [construir_id(doc) for doc in documentos]
    textos = extraer_textos(documentos)
    metadatas = [sanitizar_metadata(doc.metadata) for doc in documentos]

    # upsert en vez de add: si vuelves a generar embeddings para el mismo
    # perfil (porque lo editaste), esto actualiza los documentos existentes
    # en vez de duplicarlos o fallar por ids repetidos.
    coleccion.upsert(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=textos,
        metadatas=metadatas,
    )

    print(f"Colección '{NOMBRE_COLECCION}' actualizada en: {DIR_CHROMA}")
    print(f"Documentos guardados/actualizados: {len(ids)}")

    return coleccion


def main():
    perfiles = obtener_todos_los_perfiles()
    
    if not perfiles:
        print("No hay perfiles disponibles para generar embeddings. Crea uno primero desde la opción 1 del menú principal.")
        return

    print("\nPerfiles disponibles:")
    for perfil in perfiles.keys():
        print(f"- {perfil}")
    
    nombre_perfil = input("Ingrese el nombre del perfil a embeddear: ").strip().title()
    
    if nombre_perfil not in perfiles:
        print(f"El perfil '{nombre_perfil}' no existe.")
        return
    
    perfil_a_procesar = {nombre_perfil: perfiles[nombre_perfil]}
    
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Cargando nuevo modelo neuronal en memoria ({dispositivo.upper()}). Por favor espere...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=dispositivo)

    print("Construyendo chunks...")
    documentos = construir_chunk(perfil_a_procesar)
    textos_extraidos = extraer_textos(documentos)

    print("Generando embeddings...")
    embeddings = crear_embeddings(textos_extraidos, model)
    print(f"Embeddings generados con éxito. Forma del tensor: {embeddings.shape}")

    guardar_coleccion(documentos, embeddings)


if __name__ == '__main__':
    main()
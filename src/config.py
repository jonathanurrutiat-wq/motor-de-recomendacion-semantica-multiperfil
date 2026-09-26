import os
import re
from pathlib import Path

# e5-base predice y ordena mejor que MiniLM (ver el changelog 1.2.0 del README),
# a cambio de embeddings unas 3 veces más lentos de generar.
MODELO_POR_DEFECTO = "intfloat/multilingual-e5-base"
# Modelo usado hasta la versión 1.2.0; su base de embeddings está en chroma/.
MODELO_ANTERIOR = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# Se puede cambiar con la variable de entorno MODELO_EMBEDDINGS para comparar modelos.
EMBEDDING_MODEL_NAME = os.environ.get("MODELO_EMBEDDINGS", MODELO_POR_DEFECTO)
# Los modelos e5 esperan un prefijo en cada texto; "query: " es el indicado para similitud simétrica.
PREFIJO_EMBEDDINGS = "query: " if "-e5-" in EMBEDDING_MODEL_NAME.lower() else ""
SLUG_MODELO = re.sub(r"[^a-z0-9]+", "-", EMBEDDING_MODEL_NAME.split("/")[-1].lower()).strip("-")

# Rutas relativas a este archivo, no al directorio desde donde se ejecuta el programa.
SRC_DIR = Path(__file__).resolve().parent
DB_DIR = SRC_DIR / "db"
LOSS_DIR = SRC_DIR / "loss"

RUTA_PERFILES = DB_DIR / "profiles" / "perfiles.json"
DIR_RAW = DB_DIR / "raw"
DIR_FILTRADOS = DB_DIR / "filtered" / "result"
# Cada modelo guarda sus embeddings aparte: tienen dimensiones distintas y no se
# pueden mezclar. MiniLM conserva la carpeta chroma/ de las versiones anteriores.
_SUFIJO = "" if EMBEDDING_MODEL_NAME == MODELO_ANTERIOR else f"_{SLUG_MODELO}"
DIR_CHROMA = DB_DIR / "embeddings" / f"chroma{_SUFIJO}"

RUTA_DATASET_MAESTRO = LOSS_DIR / "dataset_maestro.csv"
RUTA_GT = LOSS_DIR / "matriz_perdida.csv"
RUTA_PENDIENTES = LOSS_DIR / "pendientes_evaluar.csv"
RUTA_ADICIONALES = LOSS_DIR / "evaluaciones_adicionales.csv"
RUTA_INSTRUCCIONES = LOSS_DIR / "instrucciones_evaluacion.md"

DIR_ANALISIS = SRC_DIR.parent / "analisis"

# Cómo se resumen los chunks de reseñas de cada película en un solo vector:
# "media" (promedio, por defecto) o "pXX", el percentil XX de cada dimensión
# (ej. "p90"). La opción 9 compara ambas; con 5 repeticiones, ningún percentil
# superó al promedio de forma consistente.
POOLING_RESENIAS = os.environ.get("POOLING_RESENIAS", "media").strip().lower()
if not (POOLING_RESENIAS == "media" or (POOLING_RESENIAS[:1] == "p" and POOLING_RESENIAS[1:].isdigit()
                                         and 0 <= int(POOLING_RESENIAS[1:]) <= 100)):
    raise ValueError(f"POOLING_RESENIAS debe ser 'media' o 'pXX' (percentil 0-100), no '{POOLING_RESENIAS}'.")
RUTA_MODELO = LOSS_DIR / f"modelo_regresion{_SUFIJO}.joblib"

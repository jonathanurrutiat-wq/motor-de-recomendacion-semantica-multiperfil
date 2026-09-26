import os
import re
from pathlib import Path

MODELO_POR_DEFECTO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
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
# Cada modelo guarda sus embeddings aparte: tienen dimensiones distintas y no se pueden mezclar.
_SUFIJO = "" if EMBEDDING_MODEL_NAME == MODELO_POR_DEFECTO else f"_{SLUG_MODELO}"
DIR_CHROMA = DB_DIR / "embeddings" / f"chroma{_SUFIJO}"

RUTA_DATASET_MAESTRO = LOSS_DIR / "dataset_maestro.csv"
RUTA_GT = LOSS_DIR / "matriz_perdida.csv"
RUTA_PENDIENTES = LOSS_DIR / "pendientes_evaluar.csv"
RUTA_ADICIONALES = LOSS_DIR / "evaluaciones_adicionales.csv"
RUTA_INSTRUCCIONES = LOSS_DIR / "instrucciones_evaluacion.md"

DIR_ANALISIS = SRC_DIR.parent / "analisis"
RUTA_MODELO = LOSS_DIR / f"modelo_regresion{_SUFIJO}.joblib"

from pathlib import Path

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Rutas relativas a este archivo, no al directorio desde donde se ejecuta el programa.
SRC_DIR = Path(__file__).resolve().parent
DB_DIR = SRC_DIR / "db"
LOSS_DIR = SRC_DIR / "loss"

RUTA_PERFILES = DB_DIR / "profiles" / "perfiles.json"
DIR_RAW = DB_DIR / "raw"
DIR_FILTRADOS = DB_DIR / "filtered" / "result"
DIR_CHROMA = DB_DIR / "embeddings" / "chroma"

RUTA_DATASET_MAESTRO = LOSS_DIR / "dataset_maestro.csv"
RUTA_GT = LOSS_DIR / "matriz_perdida.csv"
RUTA_PENDIENTES = LOSS_DIR / "pendientes_evaluar.csv"
RUTA_MODELO = LOSS_DIR / "modelo_regresion.joblib"

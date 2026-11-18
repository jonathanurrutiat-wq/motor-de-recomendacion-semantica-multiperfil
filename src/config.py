import os
import re
import unicodedata
from pathlib import Path
from typing import NamedTuple

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



# Cada perfil guarda su Verdad Base y su modelo en su propia carpeta,
# src/loss/perfil_<nombre>/ (ej. perfil_ignacio_araya). El programa deduce las
# rutas desde el nombre del perfil elegido, así que cambiar de perfil no obliga
# a mover archivos.
class RutasPerfil(NamedTuple):
    carpeta: Path
    # Planilla con las notas de Gemini. Es opcional: un perfil puede tener toda
    # su Verdad Base en evaluaciones_adicionales.csv.
    dataset_maestro: Path
    # Evaluaciones importadas con la opción 5 (se suman a la planilla).
    adicionales: Path
    # Plantilla de la opción 6 con las películas pendientes de evaluar y las
    # instrucciones para Gemini que genera.
    pendientes: Path
    instrucciones: Path
    # Películas de la Verdad Base sin reseñas suficientes: hay que descargarlas con el scraper.
    sin_resenias: Path
    # Verdad Base ligera que arma la opción 5 y usan las opciones 7, 8 y 9.
    gt: Path
    # Modelo entrenado por la opción 7, que usa la opción 8.
    modelo: Path


def slug_perfil(nombre_perfil: str) -> str:
    # "Matías Fuentes" -> "matias_fuentes": sin tildes, en minúsculas y con "_" entre palabras.
    sin_tildes = unicodedata.normalize("NFKD", nombre_perfil).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", sin_tildes.lower()).strip("_")


def rutas_perfil(nombre_perfil: str) -> RutasPerfil:
    slug = slug_perfil(nombre_perfil)
    if not slug:
        raise ValueError(f"No se puede armar la carpeta del perfil '{nombre_perfil}': su nombre no tiene letras ni números.")
    carpeta = LOSS_DIR / f"perfil_{slug}"
    return RutasPerfil(
        carpeta=carpeta,
        dataset_maestro=carpeta / "dataset_maestro.csv",
        adicionales=carpeta / "evaluaciones_adicionales.csv",
        pendientes=carpeta / "pendientes_evaluar.csv",
        instrucciones=carpeta / "instrucciones_evaluacion.md",
        sin_resenias=carpeta / "pendientes_resenias.csv",
        gt=carpeta / "matriz_perdida.csv",
        modelo=carpeta / f"modelo_reglas{_SUFIJO}.joblib",
    )


DIR_ANALISIS = SRC_DIR.parent / "analisis"

# Cómo se resumen los chunks de reseñas de cada película en un solo vector:
# "media" (promedio, por defecto) o "pXX", el percentil XX de cada dimensión
# (ej. "p90"). La opción 9 compara ambas; con 5 repeticiones, ningún percentil
# superó al promedio de forma consistente.
POOLING_RESENIAS = os.environ.get("POOLING_RESENIAS", "media").strip().lower()
if not (POOLING_RESENIAS == "media" or (POOLING_RESENIAS[:1] == "p" and POOLING_RESENIAS[1:].isdigit()
                                         and 0 <= int(POOLING_RESENIAS[1:]) <= 100)):
    raise ValueError(f"POOLING_RESENIAS debe ser 'media' o 'pXX' (percentil 0-100), no '{POOLING_RESENIAS}'.")
# Rasgos de similitud (pooling.rasgos_frases): para cada película, qué fracción de
# los chunks de sus reseñas se parece mucho a un criterio del perfil y cuánto
# vale el percentil 90 de esa similitud. Con "1" (por defecto) se calculan para
# todos los filtros y afinidades, con su descripción y, si las tienen, sus
# frases_resenia; con "0", solo para los criterios que tienen frases_resenia.
RASGOS_DESCRIPCION = os.environ.get("RASGOS_DESCRIPCION", "1").strip() != "0"

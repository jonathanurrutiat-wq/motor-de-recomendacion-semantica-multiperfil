"""
Normalización compartida de film_id.

Hay dos fuentes de film_id en el proyecto que no siempre coinciden:

- El de las reseñas (viene de Letterboxd, vía filter.py): solo incluye el
  año al final ("-2025") cuando Letterboxd necesitó desambiguar el título
  de otra película con el mismo nombre. La mayoría de las veces NO lo trae.

- El del ground truth (generado a mano en dataset_maestro.csv y normalizado
  acá con parse_film_id): el año SIEMPRE se elimina del título original,
  sin importar si la película lo necesitaba para desambiguarse o no.

Esto significa que para una película que en Letterboxd sí necesitó el año
(ej. "sinners-2025"), el ground truth generaría "sinners" (sin año) y el
cruce entre ambos fallaría en silencio. canonicalizar_film_id() resuelve
esto normalizando ambos lados a una forma común SOLO para comparar, sin
alterar el film_id real que se usa para guardar o mostrar datos.
"""

import json
import re
from pathlib import Path


def parse_film_id(raw_title: str) -> str:
    # Normalizamos "1. In the Mood for Love" y similares a "in-the-mood-for-love"

    # Eliminar números y puntos iniciales
    text = re.sub(r'^\d+\.\s*', '', str(raw_title))
    # Eliminar el año entre paréntesis al final
    text = re.sub(r'\s*\(\d{4}\)', '', text)
    # Eliminar comillas u otros caracteres extraños
    text = text.replace('"', '').replace("'", "")

    # Pasar a minúsculas
    text = text.lower().strip()

    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)

    return text


def canonicalizar_film_id(film_id: str) -> str:
    # Quita un sufijo de año final ("-2025") de un film_id ya generado,
    # para poder comparar contra un film_id que nunca lo tuvo.
    return re.sub(r'-\d{4}$', '', str(film_id))


"""
Utilidades compartidas para leer el perfil activo y nombrar sus columnas
de Verdad Base de forma dinámica (matrix.py, scoring.py, recommend.py).

Antes cada módulo tenía escrito a mano un diccionario con los nombres de
los filtros/afinidades del perfil. Si se agregaba un perfil nuevo o se le
cambiaban los filtros a uno existente, había que salir a editar ese
diccionario en cada archivo. Estas funciones leen esa información
directamente desde perfiles.json, así que siempre están al día.
"""

RUTA_PERFILES = Path.cwd() / "src" / "db" / "profiles" / "perfiles.json"


def cargar_perfil_actual() -> dict:
    # Carga el primer (y hoy único) perfil guardado en perfiles.json.
    if not RUTA_PERFILES.exists():
        raise FileNotFoundError(
            f"No se encontró {RUTA_PERFILES}. Crea un perfil primero desde profiles.py."
        )

    with open(RUTA_PERFILES, "r", encoding="utf-8") as archivo:
        perfiles = json.load(archivo)

    nombre_perfil = next(iter(perfiles))
    return perfiles[nombre_perfil]


def obtener_filtros_del_perfil(perfil: dict) -> list:
    # Devuelve [(tipo_categoria, nombre_filtro), ...]: primero los filtros
    # restrictivos y después las afinidades, en el orden en que aparecen
    # en perfiles.json.
    filtros = []
    for tipo_categoria in ("restrictivos", "afinidad"):
        if tipo_categoria in perfil:
            filtros.extend((tipo_categoria, nombre) for nombre in perfil[tipo_categoria].keys())
    return filtros


def nombre_columna_gt(tipo_categoria: str, nombre_filtro: str) -> str:
    # Nombre de columna de la Verdad Base para un filtro/afinidad,
    # siguiendo siempre la misma regla de armado.
    slug = nombre_filtro.lower().replace(' ', '_')
    prefijo = "gt_cols" if tipo_categoria == "restrictivos" else "gt_afinidad"
    return f"{prefijo}_{slug}"
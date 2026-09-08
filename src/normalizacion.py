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

import re


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
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pandas as pd

DEFAULT_VALUE = float(0.0)

MIN_CARACTERES_RESENIA = 100
# Reseñas con más likes que se toman de cada película: con 100 o 200 los modelos
# rinden igual, y 100 reduce a la mitad el tiempo de generar embeddings. Se
# puede cambiar con la variable de entorno MAX_RESENIAS_POR_PELICULA.
MAX_RESENIAS_POR_PELICULA = int(os.environ.get("MAX_RESENIAS_POR_PELICULA", 100))
# Con pocas reseñas, el embedding promedio de la película es demasiado ruidoso.
MIN_RESENIAS_POR_PELICULA = 20

def mostrar_data(df, mensaje=""):
  print(f"| ---------------- {mensaje} ---------------- |")
  df.info()
  print("\n|" + "="*56 + "|\n\n")

def parse_rating(rating_str):
  # Verificar integridad del token
  if not isinstance(rating_str, str):
    # Si es un valor nulo, asignar por defecto un decimal 0.0
    if pd.isnull(rating_str):
      return DEFAULT_VALUE
    # Caso excepcional de seguridad
    return rating_str

  score = float(rating_str.count("★"))

  if "½" in rating_str:
    score+=0.5

  return score


def parse_review(serie_review):
  serie_limpia = serie_review.fillna("").astype(str).str.replace(
      r"[^\w\s.,!?¿¡()\-áéíóúÁÉÍÓÚñÑüÜ]", "", regex=True
  )
  return serie_limpia

def filtrar_data(df):
  # Pasos a seguir:
  # 1. Eliminar columna de usernames -> no es necesaria.
  # 2. Transformar calificaciones de estrellas a flotantes.
  # 3. Filtrar los emojis y todos los carácteres especiales en las reviews.

  df = df.drop('user_name', axis=1)

  df['rating'] = df['rating'].apply(parse_rating)

  if 'review_text' in df.columns:
    df['review_text'] = parse_review(df['review_text'])

    # Nuevo: filtro semántico (v0.0.1.2)

    # Eliminar reseñas completamente vacías
    df = df[df['review_text'].str.strip() != ""]
    # Eliminar reseñas que son única y exclusivamente números (no aportan contexto significativo)
    df = df[~df['review_text'].str.match(r'^\s*\d+\s*$', na=False)]

  return df

def leer_resenias_db(ruta_db):
  # Base SQLite del scraper de Letterboxd (tablas films/reviews). Se toman las
  # reseñas con más likes de cada película, descartando las muy cortas, que
  # suelen ser chistes de una línea que no describen la película.
  consulta = """
    SELECT film_slug AS film_id, film_title, director, rating, lang, likes, review_text
    FROM (
      SELECT r.*, f.title AS film_title, f.director,
             ROW_NUMBER() OVER (PARTITION BY r.film_slug ORDER BY r.likes DESC, r.review_id) AS posicion,
             COUNT(*) OVER (PARTITION BY r.film_slug) AS total_pelicula
      FROM reviews r JOIN films f USING (film_slug)
      WHERE length(trim(r.review_text)) >= ?
    )
    WHERE posicion <= ? AND total_pelicula >= ?
    ORDER BY film_id, posicion
  """
  with closing(sqlite3.connect(f"file:{ruta_db}?mode=ro", uri=True)) as conexion:
    tablas = {nombre for (nombre,) in conexion.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    if not {"reviews", "films"} <= tablas:
      return None
    df = pd.read_sql(consulta, conexion, params=(MIN_CARACTERES_RESENIA, MAX_RESENIAS_POR_PELICULA, MIN_RESENIAS_POR_PELICULA))

  df['review_text'] = parse_review(df['review_text'])
  return df[df['review_text'].str.strip() != ""]

def main():

  curr_dir = Path(__file__).resolve().parent
  raw_dir = curr_dir.parent / "raw"
  target_dir = curr_dir / "result"

  if not raw_dir.exists():
    print(f"Error: la carpeta {raw_dir} no existe.")
    return

  fuentes = list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.db"))
  if not fuentes:
    print(f"No se encontraron archivos .csv ni .db en la carpeta {raw_dir}.")
    return
  # Crear carpeta result puesto que no existe -> no hay archivos filtrados
  target_dir.mkdir(parents=True, exist_ok=True)

  for csv_file in fuentes:
    # Se omite si ya existe un filtrado de este crudo más nuevo que el propio crudo.
    previos = list(target_dir.glob(f"filtrado_{csv_file.stem}_*.csv"))
    if any(p.stat().st_mtime >= csv_file.stat().st_mtime for p in previos):
      print(f"Omitiendo {csv_file.name}: ya fue filtrado y no ha cambiado.\n")
      continue

    print(f"Procesando archivo: {csv_file.name}\n")

    if csv_file.suffix == ".db":
      try:
        df = leer_resenias_db(csv_file)
      except (sqlite3.DatabaseError, pd.errors.DatabaseError) as error:
        detalle = str(error).splitlines()[-1].strip(" ':")
        print(f"[!] Error: {csv_file.name} está dañada ({detalle}). Suele pasar cuando se copia mientras el "
              "scraper sigue escribiendo: vuelve a copiarla con el scraper detenido.\n")
        continue
      if df is None:
        print(f"Omitiendo {csv_file.name}: no tiene las tablas 'reviews' y 'films'.\n")
        continue
      print(f"Reseñas de al menos {MIN_CARACTERES_RESENIA} caracteres, hasta {MAX_RESENIAS_POR_PELICULA} por película, "
            f"en películas con al menos {MIN_RESENIAS_POR_PELICULA}: {len(df)} reseñas de {df['film_id'].nunique()} películas.\n")
    else:
      df = pd.read_csv(csv_file)
      mostrar_data(df, f"Inspección inicial: {csv_file.name}")
      df = filtrar_data(df)

    # Si el resultado es idéntico al último filtrado de esta fuente (ej. el crudo
    # se volvió a copiar sin cambios), no se crea otro: con otro nombre, la
    # opción 4 lo tomaría como un lote nuevo y duplicaría sus embeddings.
    contenido = df.to_csv(index=False)
    ultimo = max(previos, key=lambda p: p.stat().st_mtime, default=None)
    if ultimo is not None and ultimo.read_text(encoding='utf-8') == contenido:
      print(f"Omitiendo {csv_file.name}: el resultado es idéntico a {ultimo.name}.\n")
      continue

    # ==== Crear nuevo nombre para archivo filtrado resultante ====

    # Extraer hora actual
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Crear nuevo nombre
    new_filename = f"filtrado_{csv_file.stem}_{timestamp}.csv"
    output_path = target_dir / new_filename

    # Mostrar data del dataframe final
    mostrar_data(df, f"Datos limpios: {new_filename}")

    # Serializar a archivo .csv
    output_path.write_text(contenido, encoding='utf-8')
    print(f"Archivo {new_filename} guardado exitosamente en:\n{output_path}.\n")

if __name__ == '__main__':
  main()
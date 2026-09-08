import pandas as pd
# import os
from pathlib import Path
from datetime import datetime

DEFAULT_VALUE = float(0.0)

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

import re

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

def main():

  curr_dir = Path(__file__).resolve().parent
  raw_dir = curr_dir.parent / "raw"
  target_dir = curr_dir / "result"

  if not raw_dir.exists():
    print(f"Error: la carpeta {raw_dir} no existe.")
    return

  csv_files = list(raw_dir.glob("*.csv"))
  if not csv_files:
    print(f"No se encontraron archivos .csv en la carpeta {raw_dir}.")
    return
  # Crear carpeta result puesto que no existe -> no hay archivos filtrados
  target_dir.mkdir(parents=True, exist_ok=True)

  for csv_file in csv_files:
    print(f"Procesando archivo: {csv_file.name}\n")

    df = pd.read_csv(csv_file)
    mostrar_data(df, f"Inspección inicial: {csv_file.name}")

    df = filtrar_data(df)

    # ==== Crear nuevo nombre para archivo filtrado resultante ====

    # Extraer hora actual
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Crear nuevo nombre
    new_filename = f"filtrado_{timestamp}.csv"
    output_path = target_dir / new_filename

    # Mostrar data del dataframe final
    mostrar_data(df, f"Datos limpios: {new_filename}")

    # Serializar a archivo .csv
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Archivo {new_filename} guardado exitosamente en:\n{output_path}.\n")

if __name__ == '__main__':
  main()
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

def parse_rating(ratingStr):
    if not isinstance(ratingStr, str):
        if pd.isnull(ratingStr):
            return 0.0
        return ratingStr
    
    score = float(ratingStr.count("★"))
    if "½" in ratingStr:
        score += 0.5

    return score

def parse_review(serieReview):
    serieLimpia = serieReview.fillna("").astype(str).str.replace(
        r"[^\w\s.,!?¿¡()\-áéíóúÁÉÍÓÚñÑüÜ]", "", regex=True
    )
    return serieLimpia

def procesar_csv(csvFile, target_dir):
    df = pd.read_csv(csvFile)
    if 'user_name' in df.columns:
        df = df.drop('user_name', axis=1)

    if 'rating' in df.columns:
        df['rating'] = df['rating'].apply(parse_rating)

    if 'review_text' in df.columns:
        df['review_text'] = parse_review(df['review_text'])
        df = df[df['review_text'].str.strip() != ""]
        df = df[~df['review_text'].str.match(r'^\s*\d+\s*$', na=False)]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_filename = f"filtrado_{timestamp}.csv"
    output_path = target_dir / new_filename

    df.to_csv(output_path, index=False, encoding='utf-8')

def procesar_json(jsonFile, target_dir):
    with open(jsonFile, 'r', encoding='utf-8') as file:
        data = json.load(file)
    filas = []
    for slug, info in data.items():
        textos = []
        if "overview" in info and info["overview"]:
            textos.append(info["overview"])

        if "genres" in info and isinstance(info["genres"], list):
            textos.append(" ".join(info["genres"]))

        if "keywords" in info and isinstance(info["keywords"], list):
            textos.append(" ".join(info["keywords"]))

        reviewText = " ".join(textos)
        filas.append({
            'film_id': slug,
            'film_title': info.get('title', ''),
            'rating': info.get('tmdb_rating', 0.0),
            'review_text': reviewText
        })

    df = pd.DataFrame(filas)
    df['review_text'] = parse_review(df['review_text'])
    df = df[df['review_text'].str.strip() != ""]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_filename = f"filtrado_json_{timestamp}.csv"
    output_path = target_dir / new_filename

    df.to_csv(output_path, index=False, encoding='utf-8')

def main():
    curr_dir = Path(__file__).resolve().parent
    raw_dir = curr_dir.parent / "raw"
    target_dir = curr_dir / "result"
    target_dir.mkdir(parents=True, exist_ok=True)

    print("\n========================================")
    print("1) Filtrar CSVs crudos")
    print("2) Filtrar JSON crudo")

    opcion = input("< ")
    match opcion:
        case "1":
            csv_files = list(raw_dir.glob("*.csv"))
            for f in csv_files:
                procesar_csv(f, target_dir)
        case "2":
            json_files = list(raw_dir.glob("*.json"))
            for f in json_files:
                procesar_json(f, target_dir)
        case _:
            pass

if __name__ == '__main__':
    main()
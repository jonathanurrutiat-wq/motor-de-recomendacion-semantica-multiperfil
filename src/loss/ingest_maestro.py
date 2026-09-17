import pandas as pd
import json
import re
from pathlib import Path

def parse_film_id(rawTitle):

    text = re.sub(r'^\d+\.\s*', '', str(rawTitle))
    text = re.sub(r'\s*\(\d{4}\)', '', text)
    text = text.replace('"', '').replace("'", "")
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)

    return text

def procesar_csv(loss_dir):
    ds_master = loss_dir / "dataset_maestro.csv"
    if not ds_master.exists():
        return
    
    df = pd.read_csv(ds_master)
    if "Película" in df.columns:
        df = df.rename(columns={"Película": "Pelicula"})

    df['film_id'] = df['Pelicula'].apply(parse_film_id)
    df['film_title'] = df['Pelicula']

    mapeo_columnas = {
        "Rancia": "gt_cols_camaradería_masculina_rancia",
        "Insoport.": "gt_cols_insoportabilidad_prolongada",
        "Control": "gt_cols_control_emocional_artificial",
        "Diorama": "gt_cols_personajes_diorama",
        "Caos": "gt_cols_caos_asfixiante",
        "Resist. Fem.": "gt_afinidad_resistencia_femenina",
        "Contemp.": "gt_afinidad_contemplación_inmersiva",
        "Ternura": "gt_afinidad_ternura_y_empatía_radical",
        "Humanismo": "gt_afinidad_humanismo_social",
        "Vanguardia": "gt_afinidad_vanguardia_y_simbolismo",
        "Global": "gt_nota_global"
    }

    for col_original, col_nueva in mapeo_columnas.items():
        if col_original in df.columns:
            df[col_nueva] = df[col_original].astype(str).str.replace(r'\*', '', regex=True)
            df[col_nueva] = pd.to_numeric(df[col_nueva], errors='coerce')

    columnasFinales = ['film_id', 'film_title'] + list(mapeo_columnas.values())
    df_final = df[columnasFinales]
    csv_path = loss_dir / "matriz_perdida.csv"
    df_final.to_csv(csv_path, index=False, encoding='utf-8')

def procesar_json(loss_dir):
    # definir el único ground-truth apuntando directamente a raw en módulo db
    root_dir = Path.cwd()
    json_master = root_dir / "src" / "db" / "raw" / "movies_slug_clean.json"
    
    if not json_master.exists():
        print(f"[!] Error: No se encontró el archivo en {json_master}")
        return
        
    with open(json_master, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    filas = []
    for slug, info in data.items():
        filas.append({
            'film_id': slug,
            'film_title': info.get('title', ''),
            # relleno para compatibilidad con la regresión lineal
            'gt_cols_camaradería_masculina_rancia': pd.NA,
            'gt_cols_insoportabilidad_prolongada': pd.NA,
            'gt_cols_control_emocional_artificial': pd.NA,
            'gt_cols_personajes_diorama': pd.NA,
            'gt_cols_caos_asfixiante': pd.NA,
            'gt_afinidad_resistencia_femenina': pd.NA,
            'gt_afinidad_contemplación_inmersiva': pd.NA,
            'gt_afinidad_ternura_y_empatía_radical': pd.NA,
            'gt_afinidad_humanismo_social': pd.NA,
            'gt_afinidad_vanguardia_y_simbolismo': pd.NA,
            'gt_nota_global': info.get('tmdb_rating', 0.0)
        })
        
    df_final = pd.DataFrame(filas)
    csv_path = loss_dir / "matriz_perdida.csv"
    df_final.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Éxito. {len(df_final)} películas procesadas desde JSON y guardadas en {csv_path.name}.")

def main():
    root_dir = Path.cwd()
    loss_dir = root_dir / "src" / "loss"

    print("\n========================================")
    print("1) Cargar CSV (dataset_maestro.csv)")
    print("2) Cargar JSON (movies_slug_clean.json)")

    opcion = input("< ")
    match opcion:
        case "1":
            procesar_csv(loss_dir)
        case "2":
            procesar_json(loss_dir)
        case _:
            pass

if __name__ == '__main__':
    main()
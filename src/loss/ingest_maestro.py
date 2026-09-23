import pandas as pd

from src.config import RUTA_DATASET_MAESTRO, RUTA_GT
from src.normalizacion import parse_film_id

# Traducción de los encabezados abreviados de la planilla evaluada por Gemini
# a los nombres de columna de la Verdad Base. Si la planilla cambia de
# columnas (o se evalúa con otro perfil), hay que actualizar este mapeo.
MAPEO_ENCABEZADOS = {
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
    "Global": "gt_nota_global",
}


def main():
    if not RUTA_DATASET_MAESTRO.exists():
        print(f"[!] Error: No se encontró el dataset en {RUTA_DATASET_MAESTRO}")
        print("Por favor, renombra el CSV de ground-truth a 'dataset_maestro.csv' y colócalo en src/loss/")
        return

    print("Leyendo el dataset maestro...")
    df = pd.read_csv(RUTA_DATASET_MAESTRO)

    # Quitar tilde en la palabra Pelicula para hacer más cómodo de trabajar en el futuro
    if "Película" in df.columns:
        df = df.rename(columns={"Película": "Pelicula"})

    if "Pelicula" not in df.columns:
        print("[!] Error: El dataset maestro no tiene la columna 'Película'.")
        return

    if "Global" not in df.columns:
        print("[!] Error: El dataset maestro no tiene la columna 'Global' (nota global), necesaria para entrenar.")
        return

    df['film_id'] = df['Pelicula'].apply(parse_film_id)
    df['film_title'] = df['Pelicula']  # Conservamos el original por si acaso

    columnas_gt = []
    for col_original, col_nueva in MAPEO_ENCABEZADOS.items():
        if col_original not in df.columns:
            print(f"[!] Aviso: falta la columna '{col_original}' en el dataset maestro, se omite.")
            continue
        # Reemplazamos el asterisco por nada y forzamos a float
        df[col_nueva] = df[col_original].astype(str).str.replace(r'\*', '', regex=True)
        df[col_nueva] = pd.to_numeric(df[col_nueva], errors='coerce')
        columnas_gt.append(col_nueva)

    no_mapeadas = set(df.columns) - set(MAPEO_ENCABEZADOS) - set(columnas_gt) - {"Pelicula", "film_id", "film_title"}
    if no_mapeadas:
        print(f"[!] Aviso: columnas sin mapeo en MAPEO_ENCABEZADOS, se ignoran: {', '.join(sorted(no_mapeadas))}")

    df_final = df[['film_id', 'film_title'] + columnas_gt]

    print(f"Guardando Verdad Base en formato ligero: {RUTA_GT.name}...")

    # guardar el DataFrame sobrescribiendo cualquier versión anterior
    df_final.to_csv(RUTA_GT, index=False, encoding='utf-8')

    print(f"Éxito. {len(df_final)} películas ingestadas y normalizadas.")

    print("\n| -- Verificación de integridad matemática -- |")
    print(df_final[['film_id'] + columnas_gt].head())


if __name__ == '__main__':
    main()

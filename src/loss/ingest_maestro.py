from pathlib import Path

import pandas as pd

from src.normalizacion import parse_film_id


def main():
    root_dir = Path.cwd()
    loss_dir = root_dir / "src" / "loss"

    ds_master = loss_dir / "dataset_maestro.csv"
    if not ds_master.exists():
        print(f"[!] Error: No se encontró el dataset en {ds_master}")
        print("Por favor, renombra el CSV de ground-truth a 'dataset_maestro.csv' y colócalo en src/loss/")
        return

    print("Leyendo el dataset maestro...")
    df = pd.read_csv(ds_master)

    # Quitar tilde en la palabra Pelicula para hacer más cómodo de trabajar en el futuro
    if "Película" in df.columns:
        df = df.rename(columns={"Película": "Pelicula"})

    df['film_id'] = df['Pelicula'].apply(parse_film_id)
    df['film_title'] = df['Pelicula']  # Conservamos el original por si acaso

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

    # Limpieza de Asteriscos y conversión a numérico
    for col_original, col_nueva in mapeo_columnas.items():
        if col_original in df.columns:
            # Reemplazamos el asterisco por nada y forzamos a float
            df[col_nueva] = df[col_original].astype(str).str.replace(r'\*', '', regex=True)
            df[col_nueva] = pd.to_numeric(df[col_nueva], errors='coerce')

    # Seleccionar las columnas finales
    columnas_finales = ['film_id', 'film_title'] + list(mapeo_columnas.values())
    df_final = df[columnas_finales]

    csv_path = loss_dir / "matriz_perdida.csv"
    print(f"Guardando Verdad Base en formato ligero: {csv_path.name}...")

    # guardar el DataFrame sobrescribiendo cualquier versión anterior
    df_final.to_csv(csv_path, index=False, encoding='utf-8')

    print(f"Éxito. {len(df_final)} películas ingestadas y normalizadas.")

    # verificación directa desde Pandas
    columnas_verificacion = ['film_id', 'gt_cols_insoportabilidad_prolongada', 'gt_nota_global']
    print("\n| -- Verificación de integridad matemática -- |")
    print(df_final[columnas_verificacion].head())


if __name__ == '__main__':
    main()
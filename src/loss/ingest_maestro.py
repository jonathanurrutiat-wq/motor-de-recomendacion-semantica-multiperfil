import pandas as pd

from src.config import RUTA_ADICIONALES, RUTA_DATASET_MAESTRO, RUTA_GT, RUTA_PENDIENTES
from src.normalizacion import canonicalizar_film_id, parse_film_id

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


def a_numerico(serie: pd.Series) -> pd.Series:
    # Acepta asteriscos y coma decimal ("8,5").
    texto = serie.astype(str).str.strip().str.replace('*', '', regex=False).str.replace(',', '.', regex=False)
    return pd.to_numeric(texto, errors='coerce')


def leer_csv_editado(ruta) -> pd.DataFrame:
    # La plantilla se completa a mano (a veces en Excel): se toleran ';' como
    # separador y archivos guardados en latin-1.
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(ruta, sep=None, engine="python", encoding=encoding, dtype=str)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo leer {ruta}: codificación no reconocida.")


def filas_evaluadas(df: pd.DataFrame) -> pd.Series:
    if "gt_nota_global" not in df.columns:
        return pd.Series(False, index=df.index)
    return a_numerico(df["gt_nota_global"]).notna()


def importar_pendientes_evaluadas():
    # Mueve las filas ya evaluadas de pendientes_evaluar.csv a
    # evaluaciones_adicionales.csv, que persiste entre ejecuciones.
    if not RUTA_PENDIENTES.exists():
        return

    df = leer_csv_editado(RUTA_PENDIENTES)
    if "film_id" not in df.columns:
        print(f"[!] Aviso: {RUTA_PENDIENTES.name} no tiene la columna 'film_id', se omite.")
        return

    evaluadas = filas_evaluadas(df)
    if not evaluadas.any():
        return

    nuevas = df[evaluadas].copy()
    for columna in nuevas.columns:
        if columna.startswith("gt_"):
            nuevas[columna] = a_numerico(nuevas[columna])

    if RUTA_ADICIONALES.exists():
        nuevas = pd.concat([pd.read_csv(RUTA_ADICIONALES), nuevas], ignore_index=True)
    nuevas = nuevas.drop_duplicates(subset="film_id", keep="last")

    # Primero se guardan las evaluaciones y recién después se quitan de la plantilla.
    nuevas.to_csv(RUTA_ADICIONALES, index=False, encoding="utf-8")
    df[~evaluadas].to_csv(RUTA_PENDIENTES, index=False, encoding="utf-8")

    print(f"Importadas {int(evaluadas.sum())} evaluaciones desde {RUTA_PENDIENTES.name} "
          f"a {RUTA_ADICIONALES.name}.")


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
        df[col_nueva] = a_numerico(df[col_original])
        columnas_gt.append(col_nueva)

    no_mapeadas = set(df.columns) - set(MAPEO_ENCABEZADOS) - set(columnas_gt) - {"Pelicula", "film_id", "film_title"}
    if no_mapeadas:
        print(f"[!] Aviso: columnas sin mapeo en MAPEO_ENCABEZADOS, se ignoran: {', '.join(sorted(no_mapeadas))}")

    df_final = df[['film_id', 'film_title'] + columnas_gt]

    importar_pendientes_evaluadas()

    if RUTA_ADICIONALES.exists():
        adicionales = pd.read_csv(RUTA_ADICIONALES)
        adicionales['film_title'] = adicionales['film_id']

        en_maestro = set(df_final['film_id'].apply(canonicalizar_film_id))
        repetidas = adicionales['film_id'].apply(canonicalizar_film_id).isin(en_maestro)
        if repetidas.any():
            print(f"[!] Aviso: se ignoran evaluaciones adicionales ya presentes en el dataset maestro: "
                  f"{', '.join(adicionales.loc[repetidas, 'film_id'])}")

        df_final = pd.concat([df_final, adicionales[~repetidas]], ignore_index=True)
        print(f"Sumadas {int((~repetidas).sum())} evaluaciones adicionales desde {RUTA_ADICIONALES.name}.")

    print(f"Guardando Verdad Base en formato ligero: {RUTA_GT.name}...")

    # guardar el DataFrame sobrescribiendo cualquier versión anterior
    df_final.to_csv(RUTA_GT, index=False, encoding='utf-8')

    print(f"Éxito. {len(df_final)} películas ingestadas y normalizadas.")

    print("\n| -- Verificación de integridad matemática -- |")
    print(df_final[['film_id'] + columnas_gt].head())


if __name__ == '__main__':
    main()

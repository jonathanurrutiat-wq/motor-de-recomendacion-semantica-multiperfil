import pandas as pd

from src.config import RUTA_ADICIONALES, RUTA_DATASET_MAESTRO, RUTA_GT, RUTA_PENDIENTES
from src.normalizacion import (
    canonicalizar_film_id,
    columnas_evaluacion,
    nombre_columna_excepcion,
    nombre_columna_gt,
    obtener_filtros_del_perfil,
    parse_film_id,
    seleccionar_perfil,
)

ENCABEZADO_NOTA_GLOBAL = "Global"


def mapear_encabezados(perfil: dict, columnas_planilla) -> tuple[dict, dict, list]:
    # Cada filtro/afinidad se busca en la planilla por su "encabezado" (la
    # abreviatura usada al evaluar, ej. "Insoport.") o, si no tiene, por su nombre.
    mapeo, excepciones, faltantes = {}, {}, []
    for tipo, nombre in obtener_filtros_del_perfil(perfil):
        encabezado = perfil[tipo][nombre].get("encabezado") or nombre
        if encabezado in columnas_planilla:
            mapeo[encabezado] = nombre_columna_gt(tipo, nombre)
            if tipo == "restrictivos":
                excepciones[encabezado] = nombre_columna_excepcion(nombre)
        else:
            faltantes.append(f"'{encabezado}'" + (f" ({nombre})" if encabezado != nombre else ""))

    mapeo[ENCABEZADO_NOTA_GLOBAL] = "gt_nota_global"
    return mapeo, excepciones, faltantes


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


def main(perfil_elegido=None):
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

    if ENCABEZADO_NOTA_GLOBAL not in df.columns:
        print(f"[!] Error: El dataset maestro no tiene la columna '{ENCABEZADO_NOTA_GLOBAL}' (nota global), necesaria para entrenar.")
        return

    try:
        nombre_perfil, perfil = seleccionar_perfil(perfil_elegido)
    except (FileNotFoundError, ValueError) as error:
        print(f"[!] Error: {error}")
        return
    print(f"Mapeando columnas según el perfil: {nombre_perfil}")

    mapeo, excepciones, faltantes = mapear_encabezados(perfil, df.columns)
    if faltantes:
        print(f"[!] Aviso: no se encontró en el dataset maestro la columna para: {', '.join(faltantes)}. "
              "Se omiten; revisa el campo 'encabezado' del perfil.")

    # film_slug es el identificador de Letterboxd; si falta, se deduce del título
    # (lo que falla con títulos cortados o con tildes).
    df['film_id'] = df['Pelicula'].apply(parse_film_id)
    if 'film_slug' in df.columns:
        slug = df['film_slug'].astype('string').str.strip()
        df['film_id'] = slug.where(slug.notna() & (slug != ""), df['film_id'])
    df['film_title'] = df['Pelicula']  # Conservamos el original por si acaso

    for col_original, col_nueva in mapeo.items():
        df[col_nueva] = a_numerico(df[col_original])

    # En la planilla, un asterisco junto al puntaje de un filtro ("0*") indica
    # que su excepción aplica a la película.
    for col_original, col_excepcion in excepciones.items():
        con_asterisco = df[col_original].astype(str).str.contains('*', regex=False).astype(float)
        df[col_excepcion] = con_asterisco.where(df[mapeo[col_original]].notna())

    columnas_gt = [columna for columna in columnas_evaluacion(perfil) if columna in df.columns]

    no_mapeadas = set(df.columns) - set(mapeo) - set(columnas_gt) - {"Pelicula", "film_slug", "film_id", "film_title"}
    if no_mapeadas:
        print(f"[!] Aviso: columnas que no corresponden a ningún filtro del perfil, se ignoran: {', '.join(sorted(no_mapeadas))}")

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

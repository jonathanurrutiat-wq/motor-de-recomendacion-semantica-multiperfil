import pandas as pd

from src.config import RutasPerfil, rutas_perfil
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
# Gemini marca como "REPROBADA" (sin número) las películas en que un filtro de
# veto se activa sin excepción. Se les asigna esta nota: justo bajo la peor
# nota aprobada de la Verdad Base (2.5), para conservar el orden.
NOTA_REPROBADA = 2.0


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
    # Acepta asteriscos, coma decimal ("8,5") y "REPROBADA" (vale NOTA_REPROBADA).
    texto = serie.astype(str).str.strip().str.replace('*', '', regex=False).str.replace(',', '.', regex=False)
    texto = texto.mask(texto.str.upper() == "REPROBADA", str(NOTA_REPROBADA))
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


def importar_pendientes_evaluadas(rutas: RutasPerfil):
    # Mueve las filas ya evaluadas de pendientes_evaluar.csv a
    # evaluaciones_adicionales.csv, que persiste entre ejecuciones.
    if not rutas.pendientes.exists():
        return

    df = leer_csv_editado(rutas.pendientes)
    if "film_id" not in df.columns:
        print(f"[!] Aviso: {rutas.pendientes.name} no tiene la columna 'film_id', se omite.")
        return

    evaluadas = filas_evaluadas(df)
    if not evaluadas.any():
        return

    nuevas = df[evaluadas].copy()
    for columna in nuevas.columns:
        if columna.startswith("gt_"):
            nuevas[columna] = a_numerico(nuevas[columna])

    if rutas.adicionales.exists():
        nuevas = pd.concat([pd.read_csv(rutas.adicionales), nuevas], ignore_index=True)
    nuevas = nuevas.drop_duplicates(subset="film_id", keep="last")

    # Primero se guardan las evaluaciones y recién después se quitan de la plantilla.
    nuevas.to_csv(rutas.adicionales, index=False, encoding="utf-8")
    df[~evaluadas].to_csv(rutas.pendientes, index=False, encoding="utf-8")

    print(f"Importadas {int(evaluadas.sum())} evaluaciones desde {rutas.pendientes.name} "
          f"a {rutas.adicionales.name}.")


def cargar_dataset_maestro(ruta, perfil: dict) -> pd.DataFrame | None:
    # Lee la planilla de Gemini del perfil y la deja con film_id, film_title y las
    # columnas gt_* de sus filtros y afinidades. Devuelve None (tras avisar) si no sirve.
    print("Leyendo el dataset maestro...")
    df = pd.read_csv(ruta)

    # Quitar tilde en la palabra Pelicula para hacer más cómodo de trabajar en el futuro
    if "Película" in df.columns:
        df = df.rename(columns={"Película": "Pelicula"})

    if "Pelicula" not in df.columns:
        print("[!] Error: El dataset maestro no tiene la columna 'Película'.")
        return None

    if ENCABEZADO_NOTA_GLOBAL not in df.columns:
        print(f"[!] Error: El dataset maestro no tiene la columna '{ENCABEZADO_NOTA_GLOBAL}' (nota global), necesaria para entrenar.")
        return None

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

    return df[['film_id', 'film_title'] + columnas_gt]


def main(perfil_elegido=None):
    try:
        nombre_perfil, perfil = seleccionar_perfil(perfil_elegido)
    except (FileNotFoundError, ValueError) as error:
        print(f"[!] Error: {error}")
        return

    rutas = rutas_perfil(nombre_perfil)
    print(f"Perfil: {nombre_perfil} (archivos en {rutas.carpeta})")

    # Primero se importan las evaluaciones nuevas de la plantilla, para que las
    # adicionales estén al día.
    importar_pendientes_evaluadas(rutas)

    if rutas.dataset_maestro.exists():
        print(f"Mapeando columnas según el perfil: {nombre_perfil}")
        df_final = cargar_dataset_maestro(rutas.dataset_maestro, perfil)
        if df_final is None:
            return
    elif rutas.adicionales.exists():
        # Un perfil puede tener toda su Verdad Base en evaluaciones_adicionales.csv.
        print(f"No hay {rutas.dataset_maestro.name}: la Verdad Base sale solo de {rutas.adicionales.name}.")
        df_final = pd.DataFrame(columns=['film_id', 'film_title'])
    else:
        print(f"[!] Error: no se encontró {rutas.dataset_maestro} ni {rutas.adicionales}.")
        print(f"Guarda en {rutas.carpeta} el 'dataset_maestro.csv' del perfil (la planilla con las notas de Gemini) "
              "o su 'evaluaciones_adicionales.csv'.")
        return

    if rutas.adicionales.exists():
        adicionales = pd.read_csv(rutas.adicionales)
        adicionales['film_title'] = adicionales['film_id']

        en_maestro = set(df_final['film_id'].apply(canonicalizar_film_id))
        repetidas = adicionales['film_id'].apply(canonicalizar_film_id).isin(en_maestro)
        if repetidas.any():
            print(f"[!] Aviso: se ignoran evaluaciones adicionales ya presentes en el dataset maestro: "
                  f"{', '.join(adicionales.loc[repetidas, 'film_id'])}")

        nuevas = adicionales[~repetidas]
        if df_final.empty:
            columnas = ['film_id', 'film_title'] + [c for c in adicionales.columns if c not in ('film_id', 'film_title')]
            df_final = nuevas[columnas].reset_index(drop=True)
        else:
            df_final = pd.concat([df_final, nuevas], ignore_index=True)
        print(f"Sumadas {int((~repetidas).sum())} evaluaciones adicionales desde {rutas.adicionales.name}.")

    if df_final.empty:
        print("[!] Error: no hay ninguna película evaluada para este perfil.")
        return

    columnas_gt = [columna for columna in columnas_evaluacion(perfil) if columna in df_final.columns]

    print(f"Guardando Verdad Base en formato ligero: {rutas.gt}...")

    # guardar el DataFrame sobrescribiendo cualquier versión anterior
    rutas.carpeta.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(rutas.gt, index=False, encoding='utf-8')

    print(f"Éxito. {len(df_final)} películas ingestadas y normalizadas.")

    print("\n| -- Verificación de integridad matemática -- |")
    print(df_final[['film_id'] + columnas_gt].head())


if __name__ == '__main__':
    main()

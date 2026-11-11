"""
Genera, a partir de un perfil de perfiles.json, las instrucciones para que
un modelo de lenguaje (Gemini u otro) evalúe películas con el mismo criterio
de la Verdad Base y responda en el formato de pendientes_evaluar.csv.
"""

from src.normalizacion import columnas_evaluacion, nombre_columna_excepcion, nombre_columna_gt


def generar_instrucciones(nombre_perfil: str, perfil: dict, peliculas: list | None = None) -> str:
    restrictivos = perfil.get("restrictivos", {})
    afinidades = perfil.get("afinidad", {})
    lineas = [
        f"# Instrucciones de evaluación — perfil {nombre_perfil}",
        "",
        "Evalúa cada película según el perfil cinéfilo descrito abajo. El objetivo es predecir "
        "cómo resonaría la obra con esta sensibilidad específica, no producir crítica objetiva.",
        "",
        "## Procedimiento",
        "",
        "1. Investiga la película: sinopsis, dirección, tono, ritmo, estructura narrativa y tratamiento de los personajes.",
        "2. Detecta primero qué filtros restrictivos aplican y si opera su excepción. Recién después razona cada afinidad.",
        "3. Asigna los puntajes solo al final del análisis.",
        "4. Calcula la nota global con la regla global del perfil (no es un promedio).",
        "",
        "## Filtros restrictivos",
        "",
        "Puntaje de 0 a 10 según qué tan presente está el filtro en la película (0 = ausente, 10 = domina la película).",
        "",
    ]
    for nombre, datos in restrictivos.items():
        lineas.append(f"### {nombre}")
        lineas.append(datos.get("descripcion", ""))
        if datos.get("corrupcion_directa"):
            lineas.append(f"- Corrompe: {', '.join(datos['corrupcion_directa'])}.")
        if datos.get("excepcion"):
            lineas.append(f"- Excepción: {datos['excepcion']}")
        lineas.append("")

    lineas += [
        "## Afinidades",
        "",
        "Puntaje de 0 a 10 según qué tan bien la película realiza ese valor, no según cuánto lo intenta. "
        "Un puntaje bajo en una afinidad que no es el terreno de la película no es un castigo: solo indica menor relevancia.",
        "",
    ]
    for nombre, datos in afinidades.items():
        lineas.append(f"### {nombre}")
        lineas.append(datos.get("descripcion", ""))
        lineas.append("")

    lineas += ["## Regla de puntaje global", ""]
    regla = perfil.get("regla_global") or []
    lineas += [f"- {punto}" for punto in regla] if regla else ["- (Este perfil no tiene regla global definida.)"]
    lineas.append("")

    columnas = ["film_id"] + columnas_evaluacion(perfil)
    lineas += [
        "## Formato de respuesta",
        "",
        "Responde solo con un CSV (separado por comas, punto como decimal) con exactamente este encabezado:",
        "",
        "```",
        ",".join(columnas),
        "```",
        "",
        "Significado de las columnas:",
        "",
    ]
    for nombre, datos in restrictivos.items():
        lineas.append(f"- `{nombre_columna_gt('restrictivos', nombre)}`: puntaje del filtro {nombre} (0-10).")
        if datos.get("excepcion"):
            detalle = "1 si el filtro está presente pero su excepción (descrita arriba) lo neutraliza, 0 si no."
        else:
            detalle = ("1 si el filtro está presente pero algo en la película lo neutraliza "
                       "(este filtro no tiene una excepción definida), 0 si no.")
        lineas.append(f"- `{nombre_columna_excepcion(nombre)}`: {detalle}")
    for nombre in afinidades:
        lineas.append(f"- `{nombre_columna_gt('afinidad', nombre)}`: puntaje de la afinidad {nombre} (0-10).")
    lineas.append("- `gt_nota_global`: nota global (0-10) según la regla global.")
    lineas.append("")

    lineas += ["## Películas a evaluar", ""]
    if peliculas:
        lineas += [f"- {film_id}" for film_id in peliculas]
    else:
        lineas.append("[Lista de film_id a evaluar]")
    lineas.append("")

    return "\n".join(lineas)

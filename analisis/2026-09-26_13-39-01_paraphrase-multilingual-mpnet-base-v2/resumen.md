# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T13:39:01 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`.

## Datos

- Películas con embeddings: 158 (55769 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Variables del modelo: 21.

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.

| Evaluación | MSE | MAE | R² |
|---|---|---|---|
| Entrenamiento (optimista) | 0.646 | 0.590 | 0.481 |
| Validación cruzada (5 particiones) | 1.589 | 0.891 | -0.275 |
| Validación cruzada con Ridge (comparación) | 1.105 | 0.745 | 0.113 |
| Validación cruzada, modelo de reglas en dos etapas | 0.740 | 0.596 | 0.406 |
| Línea base (promedio) | 1.274 | 0.812 | -0.022 |

## Modelo de reglas en dos etapas

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11535 (regresiones Ridge desde el embedding de 768 dimensiones, una por criterio). Regresión lineal actual: 22.

- Nota base = 3.82 + 0.09·Resistencia Femenina + 0.11·Contemplación Inmersiva + 0.15·Ternura y Empatía Radical + 0.12·Humanismo Social + 0.20·Vanguardia y Simbolismo
- Si Camaradería Masculina Rancia supera 4.9 y su excepción no aplica: resta hasta 0.12 puntos.
- Si Insoportabilidad Prolongada supera 5.6 y su excepción no aplica: resta hasta 1.57 puntos.
- Si Control Emocional Artificial supera 8.7 y su excepción no aplica: resta hasta 2.26 puntos.
- Si Personajes Diorama supera 6.5 y su excepción no aplica: resta hasta 0.52 puntos.
- Si Caos Asfixiante supera 2.0 y su excepción no aplica: resta hasta 0.24 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Modelo | MSE | MAE | R² |
|---|---|---|---|
| Regla con condiciones | 0.195 | 0.319 | 0.880 |
| Regresión lineal sobre los puntajes | 0.194 | 0.325 | 0.881 |
| Línea base (promedio) | 1.643 | 0.911 | -0.013 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 1.330 | 0.291 |
| gt_afinidad_contemplación_inmersiva | 1.249 | 0.494 |
| gt_afinidad_ternura_y_empatía_radical | 1.422 | 0.288 |
| gt_afinidad_humanismo_social | 0.970 | 0.466 |
| gt_afinidad_vanguardia_y_simbolismo | 1.019 | 0.540 |
| gt_cols_camaradería_masculina_rancia | 0.530 | -0.075 |
| gt_cols_insoportabilidad_prolongada | 2.103 | 0.138 |
| gt_cols_control_emocional_artificial | 1.573 | 0.318 |
| gt_cols_personajes_diorama | 1.672 | 0.110 |
| gt_cols_caos_asfixiante | 1.605 | 0.137 |
| gt_excepcion_camaradería_masculina_rancia | 0.227 | 0.054 |
| gt_excepcion_insoportabilidad_prolongada | 0.400 | 0.066 |
| gt_excepcion_personajes_diorama | 0.020 | -0.029 |
| gt_excepcion_caos_asfixiante | 0.111 | 0.009 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes.

| representacion | dimensiones | MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|
| percentil 90 por dimensión, todas las reseñas | 768 | 0.587 | 0.407 | 0.423 | 0.142 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.588 | 0.407 | 0.423 | 0.142 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.593 | 0.411 | 0.422 | 0.129 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.593 | 0.419 | 0.426 | 0.139 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.594 | 0.420 | 0.425 | 0.138 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.594 | 0.411 | 0.422 | 0.130 |
| promedio, hasta 100 reseñas | 768 | 0.596 | 0.408 | 0.416 | 0.126 |
| promedio, todas las reseñas | 768 | 0.596 | 0.406 | 0.416 | 0.125 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.605 | 0.386 | 0.418 | 0.152 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.609 | 0.393 | 0.422 | 0.135 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.615 | 0.378 | 0.423 | 0.134 |
| promedio, hasta 50 reseñas | 768 | 0.616 | 0.375 | 0.415 | 0.097 |

## Variables con más peso (regresión lineal)

| variable | peso |
|---|---|
| filtro · Insoportabilidad Prolongada | -0.515 |
| afinidad · Contemplación Inmersiva | 0.453 |
| excepción · Insoportabilidad Prolongada | 0.426 |
| filtro · Control Emocional Artificial | -0.374 |
| afinidad · Resistencia Femenina | 0.348 |
| Ternura y Empatía Radical × Personajes Diorama | -0.259 |
| Contemplación Inmersiva × Control Emocional Artificial | 0.242 |
| excepción · Camaradería Masculina Rancia | -0.180 |
| filtro · Personajes Diorama | 0.175 |
| Contemplación Inmersiva × Caos Asfixiante | -0.163 |

## Películas peor predichas (validación cruzada)

| film_id | nota_gemini | nota_modelo_cv | error_cv |
|---|---|---|---|
| rocky | 9.20 | 14.23 | 5.03 |
| happy-go-lucky | 9.00 | 4.51 | -4.49 |
| amelie | 4.50 | 8.64 | 4.14 |
| manhattan | 5.00 | 8.50 | 3.50 |
| a-beautiful-day-in-the-neighborhood | 8.80 | 5.83 | -2.97 |
| beauty-and-the-beast | 6.00 | 7.93 | 1.93 |
| la-la-land | 5.50 | 7.35 | 1.85 |
| triangle-of-sadness | 7.00 | 8.81 | 1.81 |
| rara | 8.80 | 7.00 | -1.80 |
| marty-supreme | 5.50 | 7.30 | 1.80 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_reglas |
|---|---|---|
| taipei-suicide-story | 11.67 | 9.65 |
| sentimental-value | 10.27 | 9.47 |
| shaun-of-the-dead | 10.16 | 7.73 |
| under-the-skin | 9.54 | 9.14 |
| train-dreams | 9.54 | 9.30 |
| one-battle-after-another | 9.37 | 7.43 |
| twin-peaks | 9.31 | 8.61 |
| the-seventh-seal | 9.28 | 9.46 |
| wristcutters-a-love-story | 9.26 | 8.21 |
| dawn-of-the-dead | 9.19 | 8.46 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

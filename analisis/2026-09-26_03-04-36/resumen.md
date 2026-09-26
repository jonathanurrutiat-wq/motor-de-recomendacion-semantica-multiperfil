# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T03:04:37.

## Datos

- Películas con embeddings: 158 (106021 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Variables del modelo: 21.

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.

| Evaluación | MSE | MAE | R² |
|---|---|---|---|
| Entrenamiento (optimista) | 0.710 | 0.577 | 0.430 |
| Validación cruzada (5 particiones) | 1.362 | 0.828 | -0.094 |
| Validación cruzada con Ridge (comparación) | 1.239 | 0.809 | 0.005 |
| Validación cruzada, modelo de reglas en dos etapas | 0.855 | 0.608 | 0.314 |
| Línea base (promedio) | 1.274 | 0.812 | -0.022 |

## Modelo de reglas en dos etapas

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 5775 (regresiones Ridge desde el embedding de 384 dimensiones, una por criterio). Regresión lineal actual: 22.

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
| gt_afinidad_resistencia_femenina | 1.349 | 0.268 |
| gt_afinidad_contemplación_inmersiva | 1.339 | 0.412 |
| gt_afinidad_ternura_y_empatía_radical | 1.359 | 0.256 |
| gt_afinidad_humanismo_social | 1.033 | 0.400 |
| gt_afinidad_vanguardia_y_simbolismo | 1.122 | 0.464 |
| gt_cols_camaradería_masculina_rancia | 0.496 | -0.025 |
| gt_cols_insoportabilidad_prolongada | 2.086 | 0.141 |
| gt_cols_control_emocional_artificial | 1.571 | 0.345 |
| gt_cols_personajes_diorama | 1.619 | 0.189 |
| gt_cols_caos_asfixiante | 1.717 | 0.057 |
| gt_excepcion_camaradería_masculina_rancia | 0.233 | 0.006 |
| gt_excepcion_insoportabilidad_prolongada | 0.408 | 0.037 |
| gt_excepcion_personajes_diorama | 0.019 | -0.024 |
| gt_excepcion_caos_asfixiante | 0.113 | 0.004 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes.

| representacion | dimensiones | MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|
| promedio, hasta 100 reseñas | 384 | 0.608 | 0.334 | 0.355 | 0.135 |
| promedio, todas las reseñas | 384 | 0.608 | 0.314 | 0.360 | 0.142 |
| promedio + percentiles de similitud, hasta 100 reseñas | 432 | 0.609 | 0.328 | 0.356 | 0.135 |
| percentil 90 por dimensión, todas las reseñas | 384 | 0.611 | 0.326 | 0.373 | 0.150 |
| percentil 75 por dimensión, todas las reseñas | 384 | 0.612 | 0.315 | 0.356 | 0.143 |
| promedio + percentiles de similitud, todas las reseñas | 432 | 0.612 | 0.314 | 0.368 | 0.137 |
| percentil 90 por dimensión, hasta 50 reseñas | 384 | 0.615 | 0.342 | 0.367 | 0.145 |
| percentil 90 por dimensión, hasta 100 reseñas | 384 | 0.619 | 0.320 | 0.351 | 0.126 |
| percentil 75 por dimensión, hasta 100 reseñas | 384 | 0.620 | 0.319 | 0.350 | 0.131 |
| percentil 75 por dimensión, hasta 50 reseñas | 384 | 0.634 | 0.316 | 0.350 | 0.132 |
| promedio, hasta 50 reseñas | 384 | 0.635 | 0.306 | 0.349 | 0.134 |
| promedio + percentiles de similitud, hasta 50 reseñas | 432 | 0.635 | 0.302 | 0.351 | 0.126 |

## Variables con más peso (regresión lineal)

| variable | peso |
|---|---|
| afinidad · Resistencia Femenina | 0.699 |
| afinidad · Contemplación Inmersiva | 0.543 |
| filtro · Caos Asfixiante | -0.345 |
| filtro · Camaradería Masculina Rancia | -0.328 |
| Contemplación Inmersiva × Control Emocional Artificial | 0.234 |
| afinidad · Humanismo Social | 0.229 |
| Ternura y Empatía Radical × Insoportabilidad Prolongada | -0.229 |
| Resistencia Femenina × Camaradería Masculina Rancia | -0.216 |
| Camaradería Masculina Rancia × excepción | 0.194 |
| filtro · Personajes Diorama | -0.185 |

## Películas peor predichas (validación cruzada)

| film_id | nota_gemini | nota_modelo_cv | error_cv |
|---|---|---|---|
| amelie | 4.50 | 8.75 | 4.25 |
| manhattan | 5.00 | 8.18 | 3.18 |
| a-beautiful-day-in-the-neighborhood | 8.80 | 5.79 | -3.01 |
| emma | 6.50 | 9.51 | 3.01 |
| la-la-land | 5.50 | 8.17 | 2.67 |
| primer | 6.50 | 9.11 | 2.61 |
| anne-of-green-gables | 9.80 | 7.51 | -2.29 |
| marty-supreme | 5.50 | 7.72 | 2.22 |
| barry-lyndon | 6.50 | 8.70 | 2.20 |
| happy-go-lucky | 9.00 | 6.82 | -2.18 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_reglas |
|---|---|---|
| taipei-suicide-story | 12.26 | 9.57 |
| sentimental-value | 10.32 | 9.35 |
| the-seventh-seal | 9.96 | 9.33 |
| train-dreams | 9.56 | 9.18 |
| the-passion-of-joan-of-arc | 9.44 | 9.06 |
| princess-mononoke | 9.29 | 8.51 |
| seven-samurai | 9.26 | 9.16 |
| lady-bird | 9.21 | 8.58 |
| sorry-baby | 9.16 | 8.20 |
| under-the-skin | 9.15 | 9.21 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

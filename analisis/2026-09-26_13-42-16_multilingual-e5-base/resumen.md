# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T13:42:16 con el modelo de embeddings `intfloat/multilingual-e5-base`.

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
| Entrenamiento (optimista) | 0.613 | 0.564 | 0.508 |
| Validación cruzada (5 particiones) | 1.045 | 0.735 | 0.161 |
| Validación cruzada con Ridge (comparación) | 0.889 | 0.659 | 0.286 |
| Validación cruzada, modelo de reglas en dos etapas | 0.766 | 0.606 | 0.385 |
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
| gt_afinidad_resistencia_femenina | 1.330 | 0.316 |
| gt_afinidad_contemplación_inmersiva | 1.179 | 0.512 |
| gt_afinidad_ternura_y_empatía_radical | 1.255 | 0.392 |
| gt_afinidad_humanismo_social | 1.015 | 0.434 |
| gt_afinidad_vanguardia_y_simbolismo | 0.975 | 0.565 |
| gt_cols_camaradería_masculina_rancia | 0.493 | -0.037 |
| gt_cols_insoportabilidad_prolongada | 1.885 | 0.257 |
| gt_cols_control_emocional_artificial | 1.591 | 0.337 |
| gt_cols_personajes_diorama | 1.612 | 0.179 |
| gt_cols_caos_asfixiante | 1.472 | 0.288 |
| gt_excepcion_camaradería_masculina_rancia | 0.226 | 0.052 |
| gt_excepcion_insoportabilidad_prolongada | 0.373 | 0.125 |
| gt_excepcion_personajes_diorama | 0.020 | -0.025 |
| gt_excepcion_caos_asfixiante | 0.109 | 0.051 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes.

| representacion | dimensiones | MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|
| percentil 90 por dimensión, todas las reseñas | 768 | 0.584 | 0.394 | 0.454 | 0.198 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.586 | 0.392 | 0.455 | 0.197 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.595 | 0.387 | 0.441 | 0.188 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.604 | 0.386 | 0.445 | 0.202 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.604 | 0.388 | 0.445 | 0.202 |
| promedio, todas las reseñas | 768 | 0.606 | 0.385 | 0.444 | 0.205 |
| promedio, hasta 100 reseñas | 768 | 0.606 | 0.385 | 0.444 | 0.204 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.610 | 0.367 | 0.438 | 0.196 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.612 | 0.366 | 0.439 | 0.194 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.612 | 0.389 | 0.430 | 0.191 |
| promedio, hasta 50 reseñas | 768 | 0.617 | 0.377 | 0.423 | 0.191 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.619 | 0.360 | 0.428 | 0.180 |

## Variables con más peso (regresión lineal)

| variable | peso |
|---|---|
| afinidad · Contemplación Inmersiva | 0.667 |
| Contemplación Inmersiva × Control Emocional Artificial | -0.613 |
| Humanismo Social × Control Emocional Artificial | 0.547 |
| filtro · Control Emocional Artificial | -0.489 |
| excepción · Insoportabilidad Prolongada | 0.433 |
| afinidad · Resistencia Femenina | 0.413 |
| excepción · Camaradería Masculina Rancia | -0.380 |
| filtro · Caos Asfixiante | -0.368 |
| Contemplación Inmersiva × Caos Asfixiante | 0.310 |
| afinidad · Humanismo Social | 0.307 |

## Películas peor predichas (validación cruzada)

| film_id | nota_gemini | nota_modelo_cv | error_cv |
|---|---|---|---|
| amelie | 4.50 | 8.89 | 4.39 |
| barry-lyndon | 6.50 | 9.26 | 2.76 |
| rocky | 9.20 | 6.45 | -2.75 |
| manhattan | 5.00 | 7.39 | 2.39 |
| in-the-mood-for-love | 9.50 | 7.21 | -2.29 |
| la-la-land | 5.50 | 7.46 | 1.96 |
| the-fallout | 8.80 | 10.69 | 1.89 |
| the-royal-tenenbaums | 6.80 | 8.55 | 1.75 |
| a-woman-under-the-influence | 9.80 | 8.16 | -1.64 |
| primer | 6.50 | 7.94 | 1.44 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_reglas |
|---|---|---|
| taipei-suicide-story | 10.30 | 9.78 |
| the-seventh-seal | 10.17 | 9.28 |
| train-dreams | 9.49 | 9.44 |
| under-the-skin | 9.42 | 9.50 |
| burning | 9.28 | 8.85 |
| happy-together | 9.15 | 9.22 |
| let-the-right-one-in | 9.07 | 8.75 |
| princess-mononoke | 9.03 | 8.77 |
| neon-genesis-evangelion | 8.97 | 9.06 |
| before-midnight | 8.92 | 8.63 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

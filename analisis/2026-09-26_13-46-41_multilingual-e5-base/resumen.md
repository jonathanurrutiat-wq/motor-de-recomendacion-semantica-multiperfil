# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T13:46:41 con el modelo de embeddings `intfloat/multilingual-e5-base`.

## Datos

- Películas con embeddings: 158 (55932 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Variables del modelo: 21.

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.

| Evaluación | MSE | MAE | R² |
|---|---|---|---|
| Entrenamiento (optimista) | 0.613 | 0.563 | 0.508 |
| Validación cruzada (5 particiones) | 1.044 | 0.734 | 0.162 |
| Validación cruzada con Ridge (comparación) | 0.889 | 0.659 | 0.287 |
| Validación cruzada, modelo de reglas en dos etapas | 0.761 | 0.601 | 0.389 |
| Línea base (promedio) | 1.274 | 0.812 | -0.022 |

## Modelo de reglas en dos etapas

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11535 (regresiones Ridge desde el embedding de 768 dimensiones, una por criterio). Regresión lineal actual: 22.

- Nota base = 4.19 + 0.08·Resistencia Femenina + 0.12·Contemplación Inmersiva + 0.16·Ternura y Empatía Radical + 0.09·Humanismo Social + 0.19·Vanguardia y Simbolismo
- Si Insoportabilidad Prolongada supera 5.4 y su excepción no aplica: resta hasta 1.66 puntos.
- Si Control Emocional Artificial supera 8.8 y su excepción no aplica: resta hasta 2.98 puntos.
- Si Personajes Diorama supera 4.0 y su excepción no aplica: resta hasta 0.45 puntos.
- Si Caos Asfixiante supera 0.9 y su excepción no aplica: resta hasta 0.25 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Modelo | MSE | MAE | R² |
|---|---|---|---|
| Regla con condiciones | 0.192 | 0.317 | 0.882 |
| Regresión lineal sobre los puntajes | 0.194 | 0.325 | 0.881 |
| Línea base (promedio) | 1.643 | 0.911 | -0.013 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 1.330 | 0.316 |
| gt_afinidad_contemplación_inmersiva | 1.179 | 0.512 |
| gt_afinidad_ternura_y_empatía_radical | 1.255 | 0.392 |
| gt_afinidad_humanismo_social | 1.016 | 0.433 |
| gt_afinidad_vanguardia_y_simbolismo | 0.975 | 0.565 |
| gt_cols_camaradería_masculina_rancia | 0.493 | -0.037 |
| gt_cols_insoportabilidad_prolongada | 1.885 | 0.258 |
| gt_cols_control_emocional_artificial | 1.592 | 0.337 |
| gt_cols_personajes_diorama | 1.613 | 0.178 |
| gt_cols_caos_asfixiante | 1.473 | 0.288 |
| gt_excepcion_camaradería_masculina_rancia | 0.226 | 0.052 |
| gt_excepcion_insoportabilidad_prolongada | 0.373 | 0.125 |
| gt_excepcion_personajes_diorama | 0.020 | -0.025 |
| gt_excepcion_caos_asfixiante | 0.109 | 0.051 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes.

| representacion | dimensiones | MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|
| percentil 90 por dimensión, todas las reseñas | 768 | 0.585 | 0.391 | 0.452 | 0.196 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.587 | 0.389 | 0.453 | 0.193 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.593 | 0.384 | 0.438 | 0.188 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.599 | 0.392 | 0.445 | 0.202 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.600 | 0.393 | 0.445 | 0.199 |
| promedio, todas las reseñas | 768 | 0.601 | 0.388 | 0.444 | 0.205 |
| promedio, hasta 100 reseñas | 768 | 0.602 | 0.390 | 0.444 | 0.203 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.607 | 0.388 | 0.429 | 0.189 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.607 | 0.372 | 0.438 | 0.196 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.609 | 0.371 | 0.439 | 0.194 |
| promedio, hasta 50 reseñas | 768 | 0.612 | 0.378 | 0.422 | 0.191 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.615 | 0.363 | 0.428 | 0.180 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 5 repeticiones con particiones distintas; Δ MAE es la diferencia con el modelo sin frases en las mismas particiones (negativa = mejor) y su desviación indica cuánto varía entre repeticiones.

| representacion | dimensiones | MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros | Δ MAE | desv. Δ MAE |
|---|---|---|---|---|---|---|---|
| promedio + frases de reseña, ponderadas | 768-778 | 0.588 | 0.388 | 0.446 | 0.205 | -0.004 | 0.003 |
| promedio + frases de reseña | 768-778 | 0.592 | 0.384 | 0.446 | 0.195 | -0.001 | 0.001 |
| promedio + descripción (control) | 768-770 | 0.592 | 0.382 | 0.446 | 0.190 | -0.000 | 0.000 |
| promedio (sin frases) | 768 | 0.592 | 0.382 | 0.446 | 0.189 | 0.000 | 0.000 |
| solo frases de reseña | 8-768 | 0.594 | 0.375 | 0.446 | 0.041 | 0.001 | 0.004 |
| solo descripción (control) | 2-768 | 0.599 | 0.363 | 0.446 | -0.008 | 0.007 | 0.004 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña, ponderadas | solo frases de reseña | promedio + frases de reseña | promedio + descripción (control) | promedio (sin frases) | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.008 | -0.021 | 0.002 | 0.003 | 0.003 | -0.022 |
| insoportabilidad_prolongada | 0.204 | 0.084 | 0.223 | 0.227 | 0.226 | 0.032 |
| control_emocional_artificial | 0.337 | 0.052 | 0.300 | 0.283 | 0.283 | -0.009 |
| personajes_diorama | 0.187 | 0.019 | 0.157 | 0.146 | 0.146 | -0.023 |
| caos_asfixiante | 0.306 | 0.072 | 0.292 | 0.290 | 0.289 | -0.017 |

## Variables con más peso (regresión lineal)

| variable | peso |
|---|---|
| afinidad · Contemplación Inmersiva | 0.668 |
| Contemplación Inmersiva × Control Emocional Artificial | -0.615 |
| Humanismo Social × Control Emocional Artificial | 0.549 |
| filtro · Control Emocional Artificial | -0.491 |
| excepción · Insoportabilidad Prolongada | 0.434 |
| afinidad · Resistencia Femenina | 0.412 |
| excepción · Camaradería Masculina Rancia | -0.381 |
| filtro · Caos Asfixiante | -0.367 |
| Contemplación Inmersiva × Caos Asfixiante | 0.311 |
| afinidad · Humanismo Social | 0.305 |

## Películas peor predichas (validación cruzada)

| film_id | nota_gemini | nota_modelo_cv | error_cv |
|---|---|---|---|
| amelie | 4.50 | 8.89 | 4.39 |
| barry-lyndon | 6.50 | 9.26 | 2.76 |
| rocky | 9.20 | 6.45 | -2.75 |
| manhattan | 5.00 | 7.39 | 2.39 |
| in-the-mood-for-love | 9.50 | 7.20 | -2.30 |
| la-la-land | 5.50 | 7.46 | 1.96 |
| the-fallout | 8.80 | 10.70 | 1.90 |
| the-royal-tenenbaums | 6.80 | 8.55 | 1.75 |
| a-woman-under-the-influence | 9.80 | 8.16 | -1.64 |
| primer | 6.50 | 7.94 | 1.44 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_reglas |
|---|---|---|
| taipei-suicide-story | 10.30 | 9.81 |
| the-seventh-seal | 10.18 | 9.29 |
| train-dreams | 9.49 | 9.45 |
| under-the-skin | 9.42 | 9.50 |
| burning | 9.28 | 8.83 |
| happy-together | 9.15 | 9.25 |
| let-the-right-one-in | 9.07 | 8.76 |
| princess-mononoke | 9.03 | 8.78 |
| neon-genesis-evangelion | 8.97 | 9.09 |
| before-midnight | 8.92 | 8.65 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

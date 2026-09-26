# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T15:20:42 con el modelo de embeddings `intfloat/multilingual-e5-base` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 158 (55769 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Variables del modelo: 21.

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.

Métricas de ranking (lo que más importa para recomendar): NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y pesa más acertar arriba; Precisión@10 es la fracción de las 10 primeras que están entre las 10 mejores (con empates en el corte entran todas las empatadas); ρ de Spearman compara el orden completo. La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | NDCG@10 | Precisión@10 | ρ Spearman | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Entrenamiento (optimista) | 0.928 | 0.400 | 0.684 | 0.564 | 0.613 | 0.508 |
| Validación cruzada (5 particiones) | 0.897 | 0.300 | 0.546 | 0.735 | 1.045 | 0.161 |
| Validación cruzada con Ridge (comparación) | 0.944 | 0.500 | 0.597 | 0.659 | 0.889 | 0.286 |
| Validación cruzada, modelo de reglas en dos etapas | 0.927 | 0.300 | 0.662 | 0.601 | 0.761 | 0.389 |
| Línea base (promedio) | 0.780 | 0.129 | 0.000 | 0.812 | 1.274 | -0.022 |

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

| Evaluación | NDCG@10 | Precisión@10 | ρ Spearman | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.976 | 0.500 | 0.904 | 0.317 | 0.192 | 0.882 |
| Regresión lineal sobre los puntajes | 0.983 | 0.600 | 0.898 | 0.325 | 0.194 | 0.881 |
| Línea base (promedio) | 0.813 | 0.127 | 0.000 | 0.911 | 1.643 | -0.013 |

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

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 5 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (NDCG@10: positiva = mejor; MAE: negativa = mejor).

| representacion | dimensiones | NDCG@10 | Δ NDCG@10 | desv. Δ NDCG@10 | Precisión@10 | ρ Spearman | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.939 | 0.002 | 0.009 | 0.300 | 0.646 | 0.595 | 0.002 | 0.003 | 0.381 | 0.446 | 0.187 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.939 | 0.001 | 0.008 | 0.300 | 0.646 | 0.595 | 0.003 | 0.003 | 0.383 | 0.447 | 0.185 |
| promedio, hasta 100 reseñas | 768 | 0.938 | 0.001 | 0.001 | 0.300 | 0.655 | 0.593 | 0.001 | 0.001 | 0.382 | 0.448 | 0.188 |
| promedio, todas las reseñas | 768 | 0.937 | 0.000 | 0.000 | 0.300 | 0.656 | 0.592 | 0.000 | 0.000 | 0.382 | 0.447 | 0.190 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.937 | -0.001 | 0.008 | 0.240 | 0.653 | 0.594 | 0.002 | 0.009 | 0.366 | 0.440 | 0.187 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.937 | -0.001 | 0.007 | 0.260 | 0.654 | 0.593 | 0.000 | 0.011 | 0.367 | 0.439 | 0.189 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.937 | -0.001 | 0.017 | 0.240 | 0.657 | 0.598 | 0.006 | 0.009 | 0.370 | 0.432 | 0.166 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.935 | -0.002 | 0.016 | 0.320 | 0.633 | 0.607 | 0.015 | 0.010 | 0.357 | 0.439 | 0.181 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.934 | -0.003 | 0.015 | 0.320 | 0.634 | 0.607 | 0.014 | 0.009 | 0.357 | 0.437 | 0.183 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.933 | -0.004 | 0.007 | 0.320 | 0.655 | 0.597 | 0.004 | 0.004 | 0.376 | 0.441 | 0.183 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.933 | -0.004 | 0.012 | 0.280 | 0.654 | 0.593 | 0.000 | 0.011 | 0.379 | 0.454 | 0.186 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.933 | -0.004 | 0.007 | 0.320 | 0.655 | 0.597 | 0.004 | 0.003 | 0.377 | 0.443 | 0.182 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.932 | -0.005 | 0.013 | 0.280 | 0.654 | 0.592 | -0.001 | 0.011 | 0.381 | 0.453 | 0.188 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.931 | -0.007 | 0.018 | 0.240 | 0.641 | 0.605 | 0.013 | 0.014 | 0.350 | 0.413 | 0.178 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.928 | -0.010 | 0.011 | 0.260 | 0.648 | 0.600 | 0.007 | 0.009 | 0.385 | 0.430 | 0.174 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.927 | -0.011 | 0.016 | 0.280 | 0.632 | 0.609 | 0.017 | 0.010 | 0.357 | 0.427 | 0.164 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.922 | -0.015 | 0.019 | 0.280 | 0.650 | 0.607 | 0.015 | 0.010 | 0.369 | 0.419 | 0.166 |
| promedio, hasta 50 reseñas | 768 | 0.922 | -0.016 | 0.016 | 0.260 | 0.650 | 0.602 | 0.009 | 0.008 | 0.380 | 0.426 | 0.177 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 5 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (NDCG@10: positiva = mejor; MAE: negativa = mejor) y su desviación indica cuánto varían entre repeticiones.

| representacion | dimensiones | NDCG@10 | Δ NDCG@10 | desv. Δ NDCG@10 | Precisión@10 | ρ Spearman | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio (sin frases) | 768 | 0.937 | 0.000 | 0.000 | 0.300 | 0.656 | 0.592 | 0.000 | 0.000 | 0.382 | 0.447 | 0.190 |
| promedio + frases de reseña | 768-778 | 0.937 | 0.000 | 0.000 | 0.300 | 0.657 | 0.592 | -0.001 | 0.001 | 0.384 | 0.447 | 0.195 |
| promedio + descripción (control) | 768-770 | 0.937 | 0.000 | 0.000 | 0.300 | 0.656 | 0.592 | -0.000 | 0.000 | 0.383 | 0.447 | 0.190 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.936 | -0.001 | 0.003 | 0.280 | 0.666 | 0.588 | -0.004 | 0.003 | 0.389 | 0.447 | 0.206 |
| solo descripción (control) | 2-768 | 0.935 | -0.002 | 0.007 | 0.320 | 0.657 | 0.599 | 0.007 | 0.004 | 0.363 | 0.447 | -0.010 |
| solo frases de reseña | 8-768 | 0.935 | -0.003 | 0.004 | 0.280 | 0.666 | 0.595 | 0.002 | 0.004 | 0.375 | 0.447 | 0.039 |

R² de la etapa 1 de cada criterio con frases:

| criterio | solo frases de reseña | promedio + frases de reseña, ponderadas | promedio + frases de reseña | promedio (sin frases) | promedio + descripción (control) | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.022 | -0.010 | 0.002 | 0.003 | 0.003 | -0.022 |
| insoportabilidad_prolongada | 0.094 | 0.207 | 0.223 | 0.226 | 0.227 | 0.039 |
| control_emocional_artificial | 0.048 | 0.333 | 0.301 | 0.283 | 0.284 | -0.009 |
| personajes_diorama | 0.024 | 0.197 | 0.158 | 0.147 | 0.147 | -0.024 |
| caos_asfixiante | 0.049 | 0.300 | 0.292 | 0.291 | 0.290 | -0.034 |

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
| taipei-suicide-story | 10.30 | 9.81 |
| the-seventh-seal | 10.17 | 9.29 |
| train-dreams | 9.49 | 9.45 |
| under-the-skin | 9.42 | 9.50 |
| burning | 9.28 | 8.83 |
| happy-together | 9.15 | 9.25 |
| let-the-right-one-in | 9.07 | 8.76 |
| princess-mononoke | 9.03 | 8.78 |
| neon-genesis-evangelion | 8.97 | 9.10 |
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

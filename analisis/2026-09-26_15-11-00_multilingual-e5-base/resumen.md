# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T15:11:01 con el modelo de embeddings `intfloat/multilingual-e5-base`.

## Datos

- Películas con embeddings: 158 (55932 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Variables del modelo: 21.

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.

Métricas de ranking (lo que más importa para recomendar): NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y pesa más acertar arriba; Precisión@10 es la fracción de las 10 primeras que están entre las 10 mejores (con empates en el corte entran todas las empatadas); ρ de Spearman compara el orden completo. La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | NDCG@10 | Precisión@10 | ρ Spearman | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Entrenamiento (optimista) | 0.928 | 0.400 | 0.683 | 0.563 | 0.613 | 0.508 |
| Validación cruzada (5 particiones) | 0.897 | 0.300 | 0.546 | 0.734 | 1.044 | 0.162 |
| Validación cruzada con Ridge (comparación) | 0.944 | 0.500 | 0.597 | 0.659 | 0.889 | 0.287 |
| Validación cruzada, modelo de reglas en dos etapas | 0.928 | 0.300 | 0.659 | 0.606 | 0.767 | 0.385 |
| Línea base (promedio) | 0.780 | 0.129 | 0.000 | 0.812 | 1.274 | -0.022 |

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

| Evaluación | NDCG@10 | Precisión@10 | ρ Spearman | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.977 | 0.500 | 0.902 | 0.319 | 0.195 | 0.880 |
| Regresión lineal sobre los puntajes | 0.983 | 0.600 | 0.898 | 0.325 | 0.194 | 0.881 |
| Línea base (promedio) | 0.813 | 0.127 | 0.000 | 0.911 | 1.643 | -0.013 |

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

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 5 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (NDCG@10: positiva = mejor; MAE: negativa = mejor).

| representacion | dimensiones | NDCG@10 | Δ NDCG@10 | desv. Δ NDCG@10 | Precisión@10 | ρ Spearman | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.938 | 0.001 | 0.008 | 0.300 | 0.644 | 0.597 | 0.002 | 0.003 | 0.380 | 0.446 | 0.187 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.938 | 0.001 | 0.008 | 0.300 | 0.647 | 0.596 | 0.002 | 0.003 | 0.382 | 0.447 | 0.183 |
| promedio, hasta 100 reseñas | 768 | 0.937 | 0.000 | 0.002 | 0.300 | 0.653 | 0.595 | 0.001 | 0.000 | 0.381 | 0.448 | 0.188 |
| promedio, todas las reseñas | 768 | 0.937 | 0.000 | 0.000 | 0.300 | 0.655 | 0.594 | 0.000 | 0.000 | 0.381 | 0.446 | 0.189 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.937 | -0.000 | 0.007 | 0.240 | 0.652 | 0.596 | 0.002 | 0.010 | 0.363 | 0.441 | 0.189 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.937 | -0.000 | 0.007 | 0.260 | 0.654 | 0.594 | 0.000 | 0.012 | 0.366 | 0.439 | 0.190 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.936 | -0.001 | 0.017 | 0.240 | 0.656 | 0.599 | 0.005 | 0.009 | 0.369 | 0.430 | 0.168 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.934 | -0.003 | 0.008 | 0.320 | 0.655 | 0.598 | 0.004 | 0.004 | 0.374 | 0.441 | 0.183 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.934 | -0.003 | 0.008 | 0.320 | 0.654 | 0.599 | 0.005 | 0.004 | 0.376 | 0.444 | 0.181 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.934 | -0.003 | 0.011 | 0.300 | 0.654 | 0.594 | 0.000 | 0.012 | 0.377 | 0.452 | 0.186 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.934 | -0.003 | 0.011 | 0.280 | 0.654 | 0.595 | 0.001 | 0.011 | 0.376 | 0.453 | 0.184 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.934 | -0.003 | 0.014 | 0.320 | 0.630 | 0.609 | 0.015 | 0.010 | 0.355 | 0.439 | 0.180 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.934 | -0.003 | 0.014 | 0.320 | 0.631 | 0.609 | 0.015 | 0.009 | 0.354 | 0.437 | 0.182 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.932 | -0.005 | 0.018 | 0.240 | 0.641 | 0.605 | 0.011 | 0.014 | 0.352 | 0.413 | 0.182 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.926 | -0.011 | 0.012 | 0.260 | 0.646 | 0.601 | 0.007 | 0.009 | 0.385 | 0.429 | 0.174 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.925 | -0.012 | 0.016 | 0.260 | 0.633 | 0.610 | 0.016 | 0.011 | 0.358 | 0.425 | 0.165 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.922 | -0.015 | 0.018 | 0.280 | 0.649 | 0.607 | 0.013 | 0.011 | 0.370 | 0.418 | 0.164 |
| promedio, hasta 50 reseñas | 768 | 0.921 | -0.016 | 0.017 | 0.260 | 0.650 | 0.602 | 0.008 | 0.009 | 0.380 | 0.426 | 0.176 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 5 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (NDCG@10: positiva = mejor; MAE: negativa = mejor) y su desviación indica cuánto varían entre repeticiones.

| representacion | dimensiones | NDCG@10 | Δ NDCG@10 | desv. Δ NDCG@10 | Precisión@10 | ρ Spearman | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio (sin frases) | 768 | 0.937 | 0.000 | 0.000 | 0.300 | 0.655 | 0.594 | 0.000 | 0.000 | 0.381 | 0.446 | 0.189 |
| promedio + frases de reseña | 768-778 | 0.937 | 0.000 | 0.000 | 0.300 | 0.656 | 0.593 | -0.001 | 0.001 | 0.382 | 0.446 | 0.195 |
| promedio + descripción (control) | 768-770 | 0.937 | 0.000 | 0.000 | 0.300 | 0.655 | 0.594 | -0.000 | 0.000 | 0.381 | 0.446 | 0.190 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.935 | -0.002 | 0.002 | 0.280 | 0.664 | 0.590 | -0.004 | 0.003 | 0.387 | 0.446 | 0.205 |
| solo descripción (control) | 2-768 | 0.935 | -0.002 | 0.008 | 0.320 | 0.655 | 0.601 | 0.007 | 0.004 | 0.364 | 0.446 | -0.008 |
| solo frases de reseña | 8-768 | 0.933 | -0.004 | 0.004 | 0.280 | 0.663 | 0.594 | -0.000 | 0.006 | 0.376 | 0.446 | 0.041 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio (sin frases) | promedio + frases de reseña | promedio + descripción (control) | solo frases de reseña | solo descripción (control) | promedio + frases de reseña, ponderadas |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.003 | 0.002 | 0.003 | -0.021 | -0.022 | -0.008 |
| insoportabilidad_prolongada | 0.226 | 0.223 | 0.227 | 0.084 | 0.032 | 0.204 |
| control_emocional_artificial | 0.283 | 0.300 | 0.283 | 0.052 | -0.009 | 0.337 |
| personajes_diorama | 0.146 | 0.157 | 0.146 | 0.019 | -0.023 | 0.187 |
| caos_asfixiante | 0.289 | 0.292 | 0.290 | 0.072 | -0.017 | 0.306 |

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
| taipei-suicide-story | 10.30 | 9.78 |
| the-seventh-seal | 10.18 | 9.28 |
| train-dreams | 9.49 | 9.45 |
| under-the-skin | 9.42 | 9.51 |
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
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

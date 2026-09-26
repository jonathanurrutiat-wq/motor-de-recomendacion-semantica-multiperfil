# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T15:24:04 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` y pooling `media` para los modelos principales.

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
| Entrenamiento (optimista) | 0.931 | 0.300 | 0.716 | 0.590 | 0.646 | 0.481 |
| Validación cruzada (5 particiones) | 0.906 | 0.200 | 0.598 | 0.891 | 1.589 | -0.275 |
| Validación cruzada con Ridge (comparación) | 0.906 | 0.300 | 0.605 | 0.745 | 1.105 | 0.113 |
| Validación cruzada, modelo de reglas en dos etapas | 0.941 | 0.300 | 0.690 | 0.596 | 0.739 | 0.407 |
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

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 5 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (NDCG@10: positiva = mejor; MAE: negativa = mejor).

| representacion | dimensiones | NDCG@10 | Δ NDCG@10 | desv. Δ NDCG@10 | Precisión@10 | ρ Spearman | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 95 por dimensión, todas las reseñas | 768 | 0.942 | 0.003 | 0.011 | 0.380 | 0.630 | 0.602 | -0.000 | 0.011 | 0.337 | 0.388 | 0.128 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.941 | 0.001 | 0.007 | 0.300 | 0.641 | 0.595 | -0.007 | 0.005 | 0.377 | 0.406 | 0.128 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.941 | 0.001 | 0.007 | 0.280 | 0.640 | 0.598 | -0.004 | 0.008 | 0.375 | 0.406 | 0.128 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.940 | 0.001 | 0.013 | 0.360 | 0.629 | 0.602 | -0.000 | 0.010 | 0.336 | 0.389 | 0.129 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.940 | 0.000 | 0.007 | 0.320 | 0.632 | 0.604 | 0.002 | 0.007 | 0.356 | 0.403 | 0.126 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.940 | 0.000 | 0.007 | 0.320 | 0.631 | 0.603 | 0.001 | 0.006 | 0.357 | 0.402 | 0.125 |
| promedio, todas las reseñas | 768 | 0.940 | 0.000 | 0.000 | 0.300 | 0.638 | 0.602 | 0.000 | 0.000 | 0.362 | 0.397 | 0.120 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.940 | -0.000 | 0.003 | 0.340 | 0.644 | 0.596 | -0.006 | 0.003 | 0.366 | 0.405 | 0.126 |
| promedio, hasta 100 reseñas | 768 | 0.938 | -0.002 | 0.004 | 0.280 | 0.637 | 0.602 | 0.000 | 0.001 | 0.362 | 0.398 | 0.120 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.937 | -0.002 | 0.004 | 0.340 | 0.644 | 0.596 | -0.006 | 0.003 | 0.367 | 0.406 | 0.126 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.936 | -0.003 | 0.011 | 0.300 | 0.636 | 0.600 | -0.001 | 0.004 | 0.367 | 0.397 | 0.124 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.935 | -0.005 | 0.010 | 0.320 | 0.627 | 0.604 | 0.002 | 0.014 | 0.354 | 0.395 | 0.110 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.935 | -0.005 | 0.011 | 0.300 | 0.636 | 0.599 | -0.003 | 0.003 | 0.367 | 0.396 | 0.124 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.934 | -0.005 | 0.005 | 0.360 | 0.628 | 0.610 | 0.009 | 0.007 | 0.342 | 0.393 | 0.127 |
| promedio, hasta 50 reseñas | 768 | 0.933 | -0.007 | 0.008 | 0.300 | 0.624 | 0.610 | 0.008 | 0.010 | 0.348 | 0.395 | 0.103 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.933 | -0.007 | 0.013 | 0.400 | 0.624 | 0.625 | 0.023 | 0.013 | 0.303 | 0.375 | 0.112 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.932 | -0.008 | 0.011 | 0.300 | 0.633 | 0.607 | 0.005 | 0.011 | 0.349 | 0.403 | 0.115 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.931 | -0.009 | 0.011 | 0.320 | 0.634 | 0.602 | 0.000 | 0.011 | 0.360 | 0.401 | 0.116 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 5 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (NDCG@10: positiva = mejor; MAE: negativa = mejor) y su desviación indica cuánto varían entre repeticiones.

| representacion | dimensiones | NDCG@10 | Δ NDCG@10 | desv. Δ NDCG@10 | Precisión@10 | ρ Spearman | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + frases de reseña | 768-778 | 0.940 | 0.000 | 0.000 | 0.300 | 0.641 | 0.600 | -0.002 | 0.002 | 0.367 | 0.397 | 0.132 |
| promedio (sin frases) | 768 | 0.940 | 0.000 | 0.000 | 0.300 | 0.638 | 0.602 | 0.000 | 0.000 | 0.362 | 0.397 | 0.120 |
| promedio + descripción (control) | 768-770 | 0.940 | 0.000 | 0.000 | 0.300 | 0.639 | 0.601 | -0.000 | 0.000 | 0.363 | 0.397 | 0.124 |
| solo descripción (control) | 2-768 | 0.936 | -0.004 | 0.008 | 0.280 | 0.652 | 0.611 | 0.010 | 0.012 | 0.351 | 0.397 | 0.043 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.934 | -0.005 | 0.004 | 0.280 | 0.652 | 0.603 | 0.001 | 0.009 | 0.381 | 0.397 | 0.190 |
| solo frases de reseña | 8-768 | 0.934 | -0.005 | 0.006 | 0.280 | 0.652 | 0.613 | 0.011 | 0.009 | 0.370 | 0.397 | 0.097 |

R² de la etapa 1 de cada criterio con frases:

| criterio | solo descripción (control) | promedio (sin frases) | promedio + frases de reseña | promedio + descripción (control) | solo frases de reseña | promedio + frases de reseña, ponderadas |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.024 | -0.016 | -0.016 | -0.016 | -0.031 | -0.032 |
| insoportabilidad_prolongada | 0.207 | 0.135 | 0.159 | 0.142 | 0.251 | 0.252 |
| control_emocional_artificial | -0.041 | 0.314 | 0.324 | 0.314 | 0.099 | 0.342 |
| personajes_diorama | -0.011 | 0.088 | 0.098 | 0.093 | 0.009 | 0.163 |
| caos_asfixiante | 0.081 | 0.078 | 0.094 | 0.088 | 0.156 | 0.227 |

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
| taipei-suicide-story | 11.67 | 9.63 |
| sentimental-value | 10.27 | 9.45 |
| shaun-of-the-dead | 10.16 | 7.79 |
| under-the-skin | 9.54 | 9.10 |
| train-dreams | 9.54 | 9.32 |
| one-battle-after-another | 9.37 | 7.47 |
| twin-peaks | 9.31 | 8.62 |
| the-seventh-seal | 9.28 | 9.41 |
| wristcutters-a-love-story | 9.26 | 8.25 |
| dawn-of-the-dead | 9.19 | 8.49 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

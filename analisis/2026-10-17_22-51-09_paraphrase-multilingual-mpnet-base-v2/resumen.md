# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-10-17T22:51:10 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 158 (55769 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 130 en la Verdad Base.
- Evaluadas sin reseñas: 1917, all-quiet-on-the-western-front, american-sniper, avatar, avatar-the-way-of-water, black-panther, bohemian-rhapsody, dunkirk, elvis, everything-everywhere-all-at-once, extremely-loud-incredibly-close, frankenstein, green-book, hidden-figures, im-still-here, inception, joker, les-miserables, lincoln, maestro, nickel-boys, oppenheimer, the-blind-side, the-fabelmans, the-help, the-imitation-game, the-theory-of-everything, toy-story-3, war-horse.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con frases de reseña (ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.650 | 0.953 | 0.260 | 0.631 | 0.965 | 0.393 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.713 | 0.940 | 0.300 | 0.634 | 0.817 | 0.486 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.600 | 0.935 | 0.200 | 0.976 | 2.062 | -0.297 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.615 | 0.945 | 0.300 | 0.786 | 1.402 | 0.118 |
| Línea base (promedio) | 0.000 | 0.845 | 0.129 | 0.855 | 1.626 | -0.023 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11579 (regresiones Ridge desde el embedding de 768 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

- Nota base = 3.75 + 0.06·Resistencia Femenina + 0.12·Contemplación Inmersiva + 0.16·Ternura y Empatía Radical + 0.13·Humanismo Social + 0.21·Vanguardia y Simbolismo
- Si Camaradería Masculina Rancia supera 3.7 y su excepción no aplica: resta hasta 1.73 puntos.
- Si Insoportabilidad Prolongada supera 5.3 y su excepción no aplica: resta hasta 1.25 puntos.
- Si Control Emocional Artificial supera 7.8 y su excepción no aplica: resta hasta 1.52 puntos.
- Si Personajes Diorama supera 3.3 y su excepción no aplica: resta hasta 0.18 puntos.
- Si Caos Asfixiante supera 8.6 y su excepción no aplica: resta hasta 1.54 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.943 | 0.979 | 0.500 | 0.359 | 0.260 | 0.937 |
| Regresión lineal sobre los puntajes | 0.915 | 0.985 | 0.700 | 0.410 | 0.294 | 0.929 |
| Línea base (promedio) | 0.000 | 0.763 | 0.108 | 1.524 | 4.162 | -0.011 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 1.336 | 0.297 |
| gt_afinidad_contemplación_inmersiva | 1.306 | 0.437 |
| gt_afinidad_ternura_y_empatía_radical | 1.315 | 0.373 |
| gt_afinidad_humanismo_social | 1.003 | 0.464 |
| gt_afinidad_vanguardia_y_simbolismo | 0.992 | 0.569 |
| gt_cols_camaradería_masculina_rancia | 0.550 | -0.027 |
| gt_cols_insoportabilidad_prolongada | 1.911 | 0.287 |
| gt_cols_control_emocional_artificial | 1.560 | 0.340 |
| gt_cols_personajes_diorama | 1.595 | 0.185 |
| gt_cols_caos_asfixiante | 1.458 | 0.232 |
| gt_excepcion_camaradería_masculina_rancia | 0.232 | 0.018 |
| gt_excepcion_insoportabilidad_prolongada | 0.394 | 0.074 |
| gt_excepcion_personajes_diorama | 0.020 | -0.026 |
| gt_excepcion_caos_asfixiante | 0.095 | -0.005 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.658 | 0.011 | 0.004 | 10/10 | 0.952 | 0.260 | 0.626 | -0.003 | 0.004 | 0.361 | 0.415 | 0.129 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.657 | 0.009 | 0.004 | 10/10 | 0.952 | 0.260 | 0.625 | -0.004 | 0.003 | 0.361 | 0.413 | 0.130 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.655 | 0.007 | 0.012 | 8/10 | 0.956 | 0.280 | 0.621 | -0.007 | 0.005 | 0.373 | 0.416 | 0.132 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.654 | 0.007 | 0.012 | 8/10 | 0.956 | 0.280 | 0.623 | -0.006 | 0.005 | 0.373 | 0.419 | 0.131 |
| promedio, hasta 100 reseñas | 768 | 0.649 | 0.001 | 0.002 | 7/10 | 0.954 | 0.260 | 0.630 | 0.001 | 0.002 | 0.354 | 0.405 | 0.124 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.648 | 0.001 | 0.007 | 7/10 | 0.953 | 0.240 | 0.626 | -0.003 | 0.004 | 0.354 | 0.401 | 0.126 |
| promedio, todas las reseñas | 768 | 0.647 | 0.000 | 0.000 | referencia | 0.954 | 0.260 | 0.629 | 0.000 | 0.000 | 0.354 | 0.403 | 0.124 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.647 | -0.001 | 0.016 | 6/10 | 0.957 | 0.320 | 0.630 | 0.001 | 0.008 | 0.363 | 0.413 | 0.134 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.647 | -0.001 | 0.018 | 5/10 | 0.958 | 0.330 | 0.628 | -0.001 | 0.009 | 0.363 | 0.412 | 0.134 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.646 | -0.001 | 0.009 | 6/10 | 0.952 | 0.230 | 0.628 | -0.000 | 0.005 | 0.354 | 0.403 | 0.126 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.642 | -0.006 | 0.012 | 3/10 | 0.953 | 0.290 | 0.631 | 0.002 | 0.010 | 0.356 | 0.406 | 0.119 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.641 | -0.006 | 0.013 | 3/10 | 0.960 | 0.340 | 0.629 | -0.000 | 0.011 | 0.334 | 0.396 | 0.134 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.641 | -0.007 | 0.013 | 3/10 | 0.961 | 0.350 | 0.628 | -0.001 | 0.011 | 0.334 | 0.395 | 0.135 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.639 | -0.009 | 0.010 | 2/10 | 0.951 | 0.300 | 0.635 | 0.006 | 0.009 | 0.341 | 0.406 | 0.116 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.637 | -0.010 | 0.010 | 2/10 | 0.952 | 0.270 | 0.631 | 0.002 | 0.011 | 0.343 | 0.396 | 0.114 |
| promedio, hasta 50 reseñas | 768 | 0.631 | -0.016 | 0.011 | 1/10 | 0.950 | 0.270 | 0.638 | 0.009 | 0.008 | 0.338 | 0.397 | 0.111 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.630 | -0.018 | 0.019 | 2/10 | 0.953 | 0.330 | 0.638 | 0.009 | 0.010 | 0.345 | 0.401 | 0.130 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.624 | -0.023 | 0.023 | 1/10 | 0.952 | 0.350 | 0.649 | 0.020 | 0.011 | 0.305 | 0.380 | 0.116 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo descripción (control) | 2-768 | 0.650 | 0.002 | 0.005 | 6/10 | 0.954 | 0.270 | 0.639 | 0.010 | 0.009 | 0.342 | 0.403 | 0.041 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.650 | 0.002 | 0.009 | 5/10 | 0.953 | 0.260 | 0.631 | 0.002 | 0.008 | 0.393 | 0.403 | 0.186 |
| promedio + frases de reseña | 768-778 | 0.649 | 0.001 | 0.002 | 8/10 | 0.954 | 0.260 | 0.627 | -0.002 | 0.001 | 0.362 | 0.403 | 0.137 |
| solo frases de reseña | 8-768 | 0.649 | 0.001 | 0.007 | 4/10 | 0.953 | 0.260 | 0.640 | 0.012 | 0.008 | 0.374 | 0.403 | 0.092 |
| promedio + descripción (control) | 768-770 | 0.647 | 0.000 | 0.001 | 7/10 | 0.954 | 0.270 | 0.628 | -0.000 | 0.000 | 0.355 | 0.403 | 0.129 |
| promedio (sin frases) | 768 | 0.647 | 0.000 | 0.000 | referencia | 0.954 | 0.260 | 0.629 | 0.000 | 0.000 | 0.354 | 0.403 | 0.124 |

R² de la etapa 1 de cada criterio con frases:

| criterio | solo frases de reseña | promedio + frases de reseña, ponderadas | promedio + frases de reseña | promedio (sin frases) | promedio + descripción (control) | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.030 | -0.034 | -0.016 | -0.016 | -0.016 | -0.027 |
| insoportabilidad_prolongada | 0.281 | 0.277 | 0.192 | 0.166 | 0.174 | 0.220 |
| control_emocional_artificial | 0.090 | 0.309 | 0.311 | 0.301 | 0.301 | -0.035 |
| personajes_diorama | -0.014 | 0.169 | 0.110 | 0.100 | 0.105 | -0.025 |
| caos_asfixiante | 0.133 | 0.208 | 0.087 | 0.070 | 0.080 | 0.073 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| filtro · Insoportabilidad Prolongada | -0.733 |
| afinidad · Contemplación Inmersiva | 0.495 |
| excepción · Insoportabilidad Prolongada | 0.475 |
| filtro · Control Emocional Artificial | -0.468 |
| afinidad · Humanismo Social | 0.326 |
| afinidad · Resistencia Femenina | 0.320 |
| Ternura y Empatía Radical × Personajes Diorama | -0.318 |
| Contemplación Inmersiva × Control Emocional Artificial | 0.217 |
| Humanismo Social × Insoportabilidad Prolongada | 0.205 |
| filtro · Personajes Diorama | 0.198 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| marty-supreme | 2.00 | 6.86 | 4.86 |
| amelie | 4.50 | 8.35 | 3.85 |
| manhattan | 5.00 | 7.84 | 2.84 |
| la-la-land | 5.50 | 8.14 | 2.64 |
| primer | 6.50 | 8.74 | 2.24 |
| crouching-tiger-hidden-dragon | 9.50 | 7.73 | -1.77 |
| rocky | 9.20 | 7.45 | -1.75 |
| the-royal-tenenbaums | 6.80 | 8.49 | 1.69 |
| barry-lyndon | 6.50 | 8.11 | 1.61 |
| anne-of-green-gables | 9.80 | 8.57 | -1.23 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.69 | 11.71 |
| the-seventh-seal | 9.64 | 9.27 |
| 2046 | 9.60 | 9.09 |
| neon-genesis-evangelion | 9.42 | 8.35 |
| sentimental-value | 9.41 | 9.73 |
| train-dreams | 9.30 | 9.46 |
| happy-together | 9.22 | 8.43 |
| chungking-express | 9.16 | 8.04 |
| under-the-skin | 9.14 | 9.98 |
| portrait-of-a-lady-on-fire | 9.04 | 9.14 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

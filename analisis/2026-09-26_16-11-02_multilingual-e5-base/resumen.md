# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T16:11:02 con el modelo de embeddings `intfloat/multilingual-e5-base` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 158 (55769 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Variables del modelo: 21.

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Entrenamiento (optimista) | 0.684 | 0.928 | 0.400 | 0.564 | 0.613 | 0.508 |
| Validación cruzada (5 particiones) | 0.546 | 0.897 | 0.300 | 0.735 | 1.045 | 0.161 |
| Validación cruzada con Ridge (comparación) | 0.597 | 0.944 | 0.500 | 0.659 | 0.889 | 0.286 |
| Validación cruzada, modelo de reglas en dos etapas | 0.659 | 0.928 | 0.300 | 0.606 | 0.766 | 0.385 |
| Línea base (promedio) | 0.000 | 0.780 | 0.129 | 0.812 | 1.274 | -0.022 |

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

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.902 | 0.977 | 0.500 | 0.319 | 0.195 | 0.880 |
| Regresión lineal sobre los puntajes | 0.898 | 0.983 | 0.600 | 0.325 | 0.194 | 0.881 |
| Línea base (promedio) | 0.000 | 0.813 | 0.127 | 0.911 | 1.643 | -0.013 |

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

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 50 por dimensión, todas las reseñas | 768 | 0.667 | 0.001 | 0.005 | 6/10 | 0.936 | 0.290 | 0.588 | 0.002 | 0.004 | 0.386 | 0.447 | 0.186 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.666 | 0.001 | 0.004 | 7/10 | 0.936 | 0.290 | 0.588 | 0.003 | 0.004 | 0.387 | 0.449 | 0.184 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.666 | 0.000 | 0.012 | 5/10 | 0.931 | 0.260 | 0.586 | 0.001 | 0.009 | 0.389 | 0.458 | 0.188 |
| promedio, todas las reseñas | 768 | 0.665 | 0.000 | 0.000 | referencia | 0.938 | 0.290 | 0.586 | 0.000 | 0.000 | 0.388 | 0.449 | 0.191 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.665 | -0.000 | 0.012 | 5/10 | 0.933 | 0.260 | 0.587 | 0.002 | 0.009 | 0.388 | 0.460 | 0.186 |
| promedio, hasta 100 reseñas | 768 | 0.665 | -0.001 | 0.002 | 4/10 | 0.938 | 0.290 | 0.587 | 0.001 | 0.001 | 0.388 | 0.451 | 0.190 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.659 | -0.006 | 0.016 | 4/10 | 0.937 | 0.260 | 0.595 | 0.009 | 0.010 | 0.370 | 0.435 | 0.167 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.659 | -0.006 | 0.010 | 3/10 | 0.938 | 0.250 | 0.591 | 0.005 | 0.010 | 0.367 | 0.440 | 0.187 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.658 | -0.007 | 0.010 | 3/10 | 0.939 | 0.240 | 0.592 | 0.006 | 0.010 | 0.366 | 0.442 | 0.185 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.658 | -0.008 | 0.006 | 1/10 | 0.925 | 0.280 | 0.597 | 0.011 | 0.009 | 0.376 | 0.424 | 0.169 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.658 | -0.008 | 0.005 | 0/10 | 0.938 | 0.280 | 0.586 | 0.001 | 0.003 | 0.389 | 0.449 | 0.189 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.658 | -0.008 | 0.006 | 1/10 | 0.937 | 0.290 | 0.588 | 0.002 | 0.003 | 0.389 | 0.451 | 0.187 |
| promedio, hasta 50 reseñas | 768 | 0.657 | -0.009 | 0.006 | 1/10 | 0.928 | 0.260 | 0.593 | 0.008 | 0.006 | 0.381 | 0.428 | 0.177 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.655 | -0.010 | 0.007 | 1/10 | 0.930 | 0.260 | 0.592 | 0.006 | 0.006 | 0.386 | 0.431 | 0.175 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.645 | -0.021 | 0.007 | 0/10 | 0.935 | 0.310 | 0.599 | 0.014 | 0.007 | 0.362 | 0.441 | 0.182 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.644 | -0.022 | 0.008 | 0/10 | 0.934 | 0.290 | 0.600 | 0.015 | 0.007 | 0.362 | 0.443 | 0.180 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.639 | -0.027 | 0.025 | 2/10 | 0.930 | 0.220 | 0.605 | 0.019 | 0.017 | 0.343 | 0.414 | 0.176 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.638 | -0.027 | 0.013 | 0/10 | 0.932 | 0.300 | 0.603 | 0.018 | 0.010 | 0.358 | 0.429 | 0.165 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo frases de reseña | 8-768 | 0.678 | 0.012 | 0.006 | 10/10 | 0.936 | 0.270 | 0.586 | 0.000 | 0.004 | 0.381 | 0.449 | 0.036 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.674 | 0.008 | 0.005 | 10/10 | 0.937 | 0.280 | 0.581 | -0.004 | 0.002 | 0.393 | 0.449 | 0.200 |
| solo descripción (control) | 2-768 | 0.672 | 0.006 | 0.008 | 7/10 | 0.940 | 0.310 | 0.591 | 0.006 | 0.004 | 0.371 | 0.449 | -0.013 |
| promedio + frases de reseña | 768-778 | 0.667 | 0.002 | 0.002 | 9/10 | 0.938 | 0.290 | 0.584 | -0.001 | 0.001 | 0.390 | 0.449 | 0.197 |
| promedio (sin frases) | 768 | 0.665 | 0.000 | 0.000 | referencia | 0.938 | 0.290 | 0.586 | 0.000 | 0.000 | 0.388 | 0.449 | 0.191 |
| promedio + descripción (control) | 768-770 | 0.665 | -0.000 | 0.000 | 2/10 | 0.938 | 0.290 | 0.586 | -0.000 | 0.000 | 0.388 | 0.449 | 0.191 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña, ponderadas | solo frases de reseña | promedio (sin frases) | promedio + frases de reseña | promedio + descripción (control) | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.029 | -0.029 | -0.010 | -0.011 | -0.011 | -0.029 |
| insoportabilidad_prolongada | 0.206 | 0.097 | 0.236 | 0.235 | 0.236 | 0.040 |
| control_emocional_artificial | 0.349 | 0.039 | 0.301 | 0.319 | 0.302 | -0.012 |
| personajes_diorama | 0.177 | 0.023 | 0.148 | 0.156 | 0.148 | -0.029 |
| caos_asfixiante | 0.299 | 0.047 | 0.283 | 0.285 | 0.282 | -0.032 |

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
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

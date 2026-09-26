# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T17:37:18 con el modelo de embeddings `intfloat/multilingual-e5-base` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 158 (55769 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con frases de reseña (ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.674 | 0.938 | 0.280 | 0.580 | 0.755 | 0.394 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.684 | 0.928 | 0.400 | 0.564 | 0.613 | 0.508 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.546 | 0.897 | 0.300 | 0.735 | 1.045 | 0.161 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.597 | 0.944 | 0.500 | 0.659 | 0.889 | 0.286 |
| Línea base (promedio) | 0.000 | 0.780 | 0.129 | 0.812 | 1.274 | -0.022 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11579 (regresiones Ridge desde el embedding de 768 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

- Nota base = 4.19 + 0.08·Resistencia Femenina + 0.12·Contemplación Inmersiva + 0.16·Ternura y Empatía Radical + 0.09·Humanismo Social + 0.19·Vanguardia y Simbolismo
- Si Insoportabilidad Prolongada supera 5.4 y su excepción no aplica: resta hasta 1.66 puntos.
- Si Control Emocional Artificial supera 8.8 y su excepción no aplica: resta hasta 2.98 puntos.
- Si Personajes Diorama supera 4.0 y su excepción no aplica: resta hasta 0.45 puntos.
- Si Caos Asfixiante supera 0.9 y su excepción no aplica: resta hasta 0.25 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.904 | 0.976 | 0.500 | 0.317 | 0.192 | 0.882 |
| Regresión lineal sobre los puntajes | 0.898 | 0.983 | 0.600 | 0.325 | 0.194 | 0.881 |
| Línea base (promedio) | 0.000 | 0.813 | 0.127 | 0.911 | 1.643 | -0.013 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 1.318 | 0.311 |
| gt_afinidad_contemplación_inmersiva | 1.123 | 0.542 |
| gt_afinidad_ternura_y_empatía_radical | 1.164 | 0.458 |
| gt_afinidad_humanismo_social | 0.995 | 0.438 |
| gt_afinidad_vanguardia_y_simbolismo | 0.932 | 0.596 |
| gt_cols_camaradería_masculina_rancia | 0.513 | -0.014 |
| gt_cols_insoportabilidad_prolongada | 1.981 | 0.231 |
| gt_cols_control_emocional_artificial | 1.506 | 0.374 |
| gt_cols_personajes_diorama | 1.549 | 0.201 |
| gt_cols_caos_asfixiante | 1.365 | 0.327 |
| gt_excepcion_camaradería_masculina_rancia | 0.231 | 0.037 |
| gt_excepcion_insoportabilidad_prolongada | 0.373 | 0.114 |
| gt_excepcion_personajes_diorama | 0.020 | -0.023 |
| gt_excepcion_caos_asfixiante | 0.113 | -0.002 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.668 | 0.000 | 0.004 | 6/10 | 0.937 | 0.300 | 0.586 | 0.003 | 0.004 | 0.389 | 0.449 | 0.184 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.667 | 0.000 | 0.004 | 5/10 | 0.937 | 0.300 | 0.586 | 0.002 | 0.004 | 0.387 | 0.447 | 0.186 |
| promedio, todas las reseñas | 768 | 0.667 | 0.000 | 0.000 | referencia | 0.938 | 0.290 | 0.584 | 0.000 | 0.000 | 0.390 | 0.449 | 0.191 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.667 | -0.000 | 0.013 | 5/10 | 0.931 | 0.240 | 0.585 | 0.002 | 0.009 | 0.389 | 0.458 | 0.188 |
| promedio, hasta 100 reseñas | 768 | 0.667 | -0.000 | 0.002 | 4/10 | 0.939 | 0.290 | 0.585 | 0.001 | 0.001 | 0.390 | 0.451 | 0.190 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.667 | -0.000 | 0.014 | 5/10 | 0.933 | 0.250 | 0.586 | 0.003 | 0.008 | 0.389 | 0.460 | 0.186 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.661 | -0.006 | 0.017 | 4/10 | 0.937 | 0.260 | 0.594 | 0.010 | 0.011 | 0.370 | 0.435 | 0.167 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.660 | -0.007 | 0.010 | 3/10 | 0.939 | 0.240 | 0.591 | 0.007 | 0.009 | 0.367 | 0.442 | 0.185 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.660 | -0.007 | 0.005 | 0/10 | 0.938 | 0.280 | 0.585 | 0.001 | 0.003 | 0.390 | 0.449 | 0.189 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.660 | -0.007 | 0.010 | 3/10 | 0.938 | 0.250 | 0.590 | 0.006 | 0.010 | 0.368 | 0.440 | 0.187 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.660 | -0.007 | 0.006 | 1/10 | 0.938 | 0.290 | 0.586 | 0.002 | 0.003 | 0.391 | 0.451 | 0.187 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.660 | -0.007 | 0.006 | 1/10 | 0.925 | 0.280 | 0.595 | 0.011 | 0.009 | 0.377 | 0.424 | 0.169 |
| promedio, hasta 50 reseñas | 768 | 0.659 | -0.008 | 0.007 | 1/10 | 0.928 | 0.270 | 0.592 | 0.008 | 0.007 | 0.382 | 0.428 | 0.177 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.657 | -0.010 | 0.008 | 1/10 | 0.932 | 0.260 | 0.590 | 0.006 | 0.007 | 0.387 | 0.431 | 0.175 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.647 | -0.020 | 0.007 | 0/10 | 0.935 | 0.300 | 0.598 | 0.014 | 0.007 | 0.364 | 0.441 | 0.182 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.647 | -0.020 | 0.009 | 0/10 | 0.936 | 0.300 | 0.599 | 0.015 | 0.007 | 0.364 | 0.443 | 0.180 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.639 | -0.028 | 0.026 | 2/10 | 0.931 | 0.220 | 0.604 | 0.021 | 0.018 | 0.344 | 0.414 | 0.176 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.639 | -0.028 | 0.013 | 0/10 | 0.932 | 0.310 | 0.602 | 0.018 | 0.010 | 0.359 | 0.429 | 0.165 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo frases de reseña | 8-768 | 0.678 | 0.011 | 0.005 | 10/10 | 0.936 | 0.260 | 0.585 | 0.002 | 0.003 | 0.380 | 0.449 | 0.036 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.675 | 0.008 | 0.006 | 10/10 | 0.938 | 0.280 | 0.579 | -0.004 | 0.002 | 0.394 | 0.449 | 0.200 |
| solo descripción (control) | 2-768 | 0.673 | 0.005 | 0.006 | 7/10 | 0.939 | 0.300 | 0.590 | 0.007 | 0.004 | 0.370 | 0.449 | -0.013 |
| promedio + frases de reseña | 768-778 | 0.669 | 0.002 | 0.002 | 10/10 | 0.938 | 0.290 | 0.582 | -0.001 | 0.001 | 0.391 | 0.449 | 0.197 |
| promedio + descripción (control) | 768-770 | 0.667 | 0.000 | 0.000 | 8/10 | 0.938 | 0.290 | 0.583 | -0.000 | 0.000 | 0.390 | 0.449 | 0.191 |
| promedio (sin frases) | 768 | 0.667 | 0.000 | 0.000 | referencia | 0.938 | 0.290 | 0.584 | 0.000 | 0.000 | 0.390 | 0.449 | 0.191 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña, ponderadas | solo frases de reseña | promedio + descripción (control) | promedio + frases de reseña | promedio (sin frases) | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.029 | -0.029 | -0.011 | -0.011 | -0.010 | -0.029 |
| insoportabilidad_prolongada | 0.206 | 0.097 | 0.236 | 0.235 | 0.236 | 0.040 |
| control_emocional_artificial | 0.349 | 0.039 | 0.302 | 0.319 | 0.301 | -0.012 |
| personajes_diorama | 0.177 | 0.023 | 0.148 | 0.156 | 0.148 | -0.029 |
| caos_asfixiante | 0.299 | 0.047 | 0.282 | 0.285 | 0.283 | -0.032 |

## Variables con más peso (regresión lineal anterior)

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

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| amelie | 4.50 | 8.45 | 3.95 |
| manhattan | 5.00 | 8.32 | 3.32 |
| la-la-land | 5.50 | 8.00 | 2.50 |
| barry-lyndon | 6.50 | 8.67 | 2.17 |
| primer | 6.50 | 8.56 | 2.06 |
| beauty-and-the-beast | 6.00 | 7.69 | 1.69 |
| the-royal-tenenbaums | 6.80 | 8.44 | 1.64 |
| marty-supreme | 5.50 | 6.91 | 1.41 |
| rocky | 9.20 | 7.93 | -1.27 |
| the-bitter-tears-of-petra-von-kant | 8.20 | 9.35 | 1.15 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.75 | 10.30 |
| under-the-skin | 9.52 | 9.42 |
| train-dreams | 9.45 | 9.49 |
| 2046 | 9.43 | 8.53 |
| the-passion-of-joan-of-arc | 9.32 | 8.64 |
| the-seventh-seal | 9.30 | 10.17 |
| sentimental-value | 9.29 | 8.56 |
| happy-together | 9.23 | 9.15 |
| chungking-express | 9.18 | 8.50 |
| neon-genesis-evangelion | 9.12 | 8.97 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

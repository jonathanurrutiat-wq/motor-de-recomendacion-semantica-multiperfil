# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-10-19T01:20:59 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 187 (62965 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 129 de 130 en la Verdad Base.
- Evaluadas sin reseñas: nickel-boys.
- Candidatas a recomendar (sin nota de Gemini): 58.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con frases de reseña (ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.722 | 0.956 | 0.360 | 1.004 | 2.221 | 0.461 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.762 | 0.962 | 0.500 | 0.934 | 1.529 | 0.629 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.691 | 0.941 | 0.300 | 1.133 | 2.384 | 0.422 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.700 | 0.947 | 0.400 | 1.092 | 2.265 | 0.451 |
| Línea base (promedio) | 0.000 | 0.761 | 0.101 | 1.531 | 4.156 | -0.008 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11579 (regresiones Ridge desde el embedding de 768 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

- Nota base = 3.73 + 0.06·Resistencia Femenina + 0.13·Contemplación Inmersiva + 0.17·Ternura y Empatía Radical + 0.12·Humanismo Social + 0.21·Vanguardia y Simbolismo
- Si Camaradería Masculina Rancia supera 3.8 y su excepción no aplica: resta hasta 1.76 puntos.
- Si Insoportabilidad Prolongada supera 5.1 y su excepción no aplica: resta hasta 1.09 puntos.
- Si Control Emocional Artificial supera 7.8 y su excepción no aplica: resta hasta 1.48 puntos.
- Si Personajes Diorama supera 3.8 y su excepción no aplica: resta hasta 0.21 puntos.
- Si Caos Asfixiante supera 8.4 y su excepción no aplica: resta hasta 1.69 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.944 | 0.979 | 0.500 | 0.349 | 0.240 | 0.942 |
| Regresión lineal sobre los puntajes | 0.915 | 0.985 | 0.700 | 0.410 | 0.294 | 0.929 |
| Línea base (promedio) | 0.000 | 0.763 | 0.108 | 1.524 | 4.162 | -0.011 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 1.534 | 0.488 |
| gt_afinidad_contemplación_inmersiva | 1.447 | 0.569 |
| gt_afinidad_ternura_y_empatía_radical | 1.540 | 0.345 |
| gt_afinidad_humanismo_social | 1.405 | 0.389 |
| gt_afinidad_vanguardia_y_simbolismo | 1.236 | 0.579 |
| gt_cols_camaradería_masculina_rancia | 0.823 | 0.197 |
| gt_cols_insoportabilidad_prolongada | 1.791 | 0.316 |
| gt_cols_control_emocional_artificial | 1.676 | 0.525 |
| gt_cols_personajes_diorama | 1.925 | 0.327 |
| gt_cols_caos_asfixiante | 1.464 | 0.460 |
| gt_excepcion_camaradería_masculina_rancia | 0.188 | 0.032 |
| gt_excepcion_insoportabilidad_prolongada | 0.353 | 0.020 |
| gt_excepcion_personajes_diorama | 0.016 | -0.023 |
| gt_excepcion_caos_asfixiante | 0.090 | 0.005 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.731 | 0.009 | 0.009 | 9/10 | 0.960 | 0.390 | 1.011 | -0.002 | 0.011 | 0.429 | 0.463 | 0.302 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.729 | 0.007 | 0.005 | 10/10 | 0.953 | 0.360 | 1.003 | -0.009 | 0.005 | 0.436 | 0.470 | 0.307 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.728 | 0.006 | 0.004 | 10/10 | 0.953 | 0.360 | 1.003 | -0.010 | 0.004 | 0.436 | 0.470 | 0.307 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.728 | 0.006 | 0.004 | 9/10 | 0.963 | 0.450 | 1.006 | -0.007 | 0.005 | 0.435 | 0.464 | 0.303 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.727 | 0.005 | 0.009 | 7/10 | 0.953 | 0.380 | 1.010 | -0.002 | 0.016 | 0.433 | 0.464 | 0.311 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.727 | 0.005 | 0.005 | 9/10 | 0.963 | 0.450 | 1.005 | -0.007 | 0.006 | 0.434 | 0.463 | 0.306 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.726 | 0.004 | 0.010 | 7/10 | 0.956 | 0.410 | 1.016 | 0.003 | 0.022 | 0.426 | 0.466 | 0.297 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.726 | 0.004 | 0.009 | 6/10 | 0.945 | 0.370 | 1.007 | -0.006 | 0.017 | 0.430 | 0.469 | 0.303 |
| promedio, hasta 50 reseñas | 768 | 0.726 | 0.004 | 0.009 | 7/10 | 0.952 | 0.360 | 1.013 | 0.000 | 0.015 | 0.429 | 0.462 | 0.297 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.725 | 0.003 | 0.005 | 7/10 | 0.960 | 0.410 | 1.008 | -0.005 | 0.005 | 0.429 | 0.463 | 0.307 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.725 | 0.003 | 0.007 | 8/10 | 0.952 | 0.370 | 1.013 | -0.000 | 0.013 | 0.426 | 0.459 | 0.300 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.725 | 0.003 | 0.006 | 7/10 | 0.961 | 0.450 | 1.008 | -0.005 | 0.009 | 0.431 | 0.467 | 0.304 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.724 | 0.003 | 0.005 | 7/10 | 0.960 | 0.420 | 1.007 | -0.006 | 0.005 | 0.430 | 0.463 | 0.308 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.724 | 0.002 | 0.005 | 6/10 | 0.961 | 0.450 | 1.007 | -0.006 | 0.008 | 0.432 | 0.466 | 0.305 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.723 | 0.001 | 0.003 | 6/10 | 0.956 | 0.370 | 1.013 | 0.001 | 0.004 | 0.424 | 0.458 | 0.303 |
| promedio, todas las reseñas | 768 | 0.722 | 0.000 | 0.000 | referencia | 0.956 | 0.350 | 1.013 | 0.000 | 0.000 | 0.426 | 0.459 | 0.303 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.721 | -0.001 | 0.003 | 3/10 | 0.957 | 0.360 | 1.013 | 0.000 | 0.003 | 0.423 | 0.458 | 0.303 |
| promedio, hasta 100 reseñas | 768 | 0.721 | -0.001 | 0.002 | 5/10 | 0.956 | 0.350 | 1.013 | 0.001 | 0.001 | 0.426 | 0.458 | 0.303 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + frases de reseña | 768-778 | 0.723 | 0.001 | 0.001 | 6/10 | 0.956 | 0.350 | 1.009 | -0.004 | 0.002 | 0.434 | 0.459 | 0.314 |
| promedio + descripción (control) | 768-770 | 0.722 | 0.000 | 0.000 | 9/10 | 0.956 | 0.350 | 1.012 | -0.001 | 0.001 | 0.427 | 0.459 | 0.306 |
| promedio (sin frases) | 768 | 0.722 | 0.000 | 0.000 | referencia | 0.956 | 0.350 | 1.013 | 0.000 | 0.000 | 0.426 | 0.459 | 0.303 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.722 | -0.000 | 0.004 | 6/10 | 0.957 | 0.360 | 1.005 | -0.008 | 0.007 | 0.460 | 0.459 | 0.344 |
| solo descripción (control) | 2-768 | 0.718 | -0.004 | 0.006 | 3/10 | 0.957 | 0.380 | 1.035 | 0.022 | 0.016 | 0.391 | 0.459 | 0.061 |
| solo frases de reseña | 8-768 | 0.715 | -0.007 | 0.007 | 3/10 | 0.957 | 0.370 | 1.041 | 0.028 | 0.011 | 0.407 | 0.459 | 0.127 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + descripción (control) | promedio (sin frases) | promedio + frases de reseña | solo descripción (control) | promedio + frases de reseña, ponderadas | solo frases de reseña |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.179 | 0.179 | 0.178 | -0.018 | 0.170 | 0.010 |
| insoportabilidad_prolongada | 0.188 | 0.179 | 0.214 | 0.190 | 0.292 | 0.269 |
| control_emocional_artificial | 0.459 | 0.458 | 0.468 | 0.022 | 0.507 | 0.180 |
| personajes_diorama | 0.312 | 0.312 | 0.312 | 0.088 | 0.309 | 0.036 |
| caos_asfixiante | 0.391 | 0.386 | 0.398 | 0.026 | 0.442 | 0.140 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| filtro · Insoportabilidad Prolongada | -0.902 |
| Humanismo Social × Control Emocional Artificial | 0.863 |
| filtro · Personajes Diorama | 0.621 |
| filtro · Control Emocional Artificial | -0.616 |
| afinidad · Resistencia Femenina | 0.577 |
| excepción · Insoportabilidad Prolongada | 0.466 |
| afinidad · Vanguardia y Simbolismo | 0.371 |
| Ternura y Empatía Radical × Personajes Diorama | -0.367 |
| Contemplación Inmersiva × Control Emocional Artificial | -0.363 |
| afinidad · Contemplación Inmersiva | 0.346 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| american-sniper | 2.00 | 7.70 | 5.70 |
| marty-supreme | 2.00 | 7.27 | 5.27 |
| amelie | 4.50 | 8.74 | 4.24 |
| joker | 2.00 | 5.79 | 3.79 |
| elvis | 2.00 | 5.74 | 3.74 |
| bohemian-rhapsody | 3.20 | 6.87 | 3.67 |
| the-blind-side | 2.50 | 5.94 | 3.44 |
| the-help | 4.00 | 7.24 | 3.24 |
| maestro | 3.50 | 6.71 | 3.21 |
| green-book | 3.80 | 6.67 | 2.87 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| 2046 | 9.68 | 9.16 |
| sentimental-value | 9.65 | 9.98 |
| taipei-suicide-story | 9.56 | 10.82 |
| the-seventh-seal | 9.46 | 9.06 |
| chungking-express | 9.42 | 7.28 |
| portrait-of-a-lady-on-fire | 9.34 | 9.24 |
| happy-together | 9.27 | 9.03 |
| princess-mononoke | 9.22 | 8.57 |
| neon-genesis-evangelion | 9.21 | 7.73 |
| train-dreams | 8.96 | 8.67 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

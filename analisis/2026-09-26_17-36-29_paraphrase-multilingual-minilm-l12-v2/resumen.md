# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T17:36:29 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 158 (106021 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 110 en la Verdad Base.
- Evaluadas sin reseñas: all-quiet-on-the-western, avatar-the-way-of-water, elvis, everything-everywhere-all-at-once, frankenstein, im-still-here, nickel-boys, oppenheimer, the-fabelmans.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con frases de reseña (ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.605 | 0.929 | 0.280 | 0.632 | 0.888 | 0.287 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.693 | 0.956 | 0.500 | 0.577 | 0.710 | 0.430 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.464 | 0.909 | 0.200 | 0.828 | 1.362 | -0.094 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.400 | 0.886 | 0.300 | 0.809 | 1.239 | 0.005 |
| Línea base (promedio) | 0.000 | 0.780 | 0.129 | 0.812 | 1.274 | -0.022 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 5819 (regresiones Ridge desde el embedding de 384 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

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
| gt_afinidad_resistencia_femenina | 1.362 | 0.258 |
| gt_afinidad_contemplación_inmersiva | 1.278 | 0.450 |
| gt_afinidad_ternura_y_empatía_radical | 1.366 | 0.260 |
| gt_afinidad_humanismo_social | 1.039 | 0.362 |
| gt_afinidad_vanguardia_y_simbolismo | 1.123 | 0.471 |
| gt_cols_camaradería_masculina_rancia | 0.514 | -0.018 |
| gt_cols_insoportabilidad_prolongada | 1.952 | 0.213 |
| gt_cols_control_emocional_artificial | 1.525 | 0.395 |
| gt_cols_personajes_diorama | 1.726 | 0.111 |
| gt_cols_caos_asfixiante | 1.631 | 0.090 |
| gt_excepcion_camaradería_masculina_rancia | 0.237 | -0.006 |
| gt_excepcion_insoportabilidad_prolongada | 0.401 | 0.051 |
| gt_excepcion_personajes_diorama | 0.020 | -0.022 |
| gt_excepcion_caos_asfixiante | 0.118 | -0.030 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 95 por dimensión, hasta 50 reseñas | 384 | 0.636 | 0.040 | 0.024 | 9/10 | 0.953 | 0.460 | 0.623 | -0.007 | 0.015 | 0.309 | 0.352 | 0.089 |
| promedio, hasta 100 reseñas | 384 | 0.617 | 0.021 | 0.011 | 10/10 | 0.929 | 0.250 | 0.628 | -0.002 | 0.007 | 0.294 | 0.331 | 0.106 |
| promedio + percentiles de similitud, hasta 100 reseñas | 432 | 0.617 | 0.021 | 0.014 | 10/10 | 0.929 | 0.270 | 0.627 | -0.003 | 0.008 | 0.291 | 0.341 | 0.106 |
| percentil 95 por dimensión, hasta 100 reseñas | 384 | 0.616 | 0.020 | 0.023 | 8/10 | 0.948 | 0.430 | 0.621 | -0.009 | 0.010 | 0.324 | 0.348 | 0.107 |
| percentil 90 por dimensión, hasta 50 reseñas | 384 | 0.615 | 0.019 | 0.016 | 9/10 | 0.936 | 0.260 | 0.630 | -0.000 | 0.012 | 0.290 | 0.339 | 0.109 |
| percentil 50 por dimensión, hasta 100 reseñas | 384 | 0.610 | 0.015 | 0.010 | 9/10 | 0.924 | 0.240 | 0.634 | 0.004 | 0.003 | 0.276 | 0.315 | 0.101 |
| percentil 75 por dimensión, hasta 100 reseñas | 384 | 0.604 | 0.008 | 0.016 | 6/10 | 0.930 | 0.270 | 0.638 | 0.008 | 0.008 | 0.281 | 0.325 | 0.107 |
| percentil 90 por dimensión, hasta 100 reseñas | 384 | 0.603 | 0.008 | 0.024 | 7/10 | 0.941 | 0.320 | 0.633 | 0.003 | 0.009 | 0.284 | 0.328 | 0.103 |
| promedio + percentiles de similitud, todas las reseñas | 432 | 0.598 | 0.003 | 0.004 | 7/10 | 0.927 | 0.280 | 0.629 | -0.001 | 0.004 | 0.282 | 0.353 | 0.119 |
| percentil 90 por dimensión, todas las reseñas | 384 | 0.596 | 0.001 | 0.016 | 5/10 | 0.934 | 0.330 | 0.635 | 0.005 | 0.009 | 0.284 | 0.343 | 0.121 |
| promedio, todas las reseñas | 384 | 0.596 | 0.000 | 0.000 | referencia | 0.928 | 0.280 | 0.630 | 0.000 | 0.000 | 0.278 | 0.341 | 0.120 |
| percentil 50 por dimensión, todas las reseñas | 384 | 0.594 | -0.002 | 0.004 | 3/10 | 0.922 | 0.240 | 0.633 | 0.003 | 0.002 | 0.268 | 0.326 | 0.119 |
| percentil 95 por dimensión, todas las reseñas | 384 | 0.593 | -0.003 | 0.020 | 5/10 | 0.947 | 0.370 | 0.633 | 0.003 | 0.010 | 0.277 | 0.351 | 0.110 |
| percentil 75 por dimensión, hasta 50 reseñas | 384 | 0.592 | -0.003 | 0.022 | 5/10 | 0.923 | 0.210 | 0.642 | 0.012 | 0.013 | 0.270 | 0.315 | 0.102 |
| percentil 75 por dimensión, todas las reseñas | 384 | 0.591 | -0.005 | 0.010 | 4/10 | 0.924 | 0.240 | 0.639 | 0.009 | 0.009 | 0.272 | 0.335 | 0.122 |
| promedio + percentiles de similitud, hasta 50 reseñas | 432 | 0.591 | -0.005 | 0.016 | 3/10 | 0.916 | 0.170 | 0.638 | 0.008 | 0.012 | 0.270 | 0.323 | 0.100 |
| promedio, hasta 50 reseñas | 384 | 0.589 | -0.006 | 0.023 | 5/10 | 0.921 | 0.190 | 0.641 | 0.011 | 0.014 | 0.269 | 0.318 | 0.105 |
| percentil 50 por dimensión, hasta 50 reseñas | 384 | 0.583 | -0.013 | 0.011 | 1/10 | 0.913 | 0.160 | 0.645 | 0.015 | 0.012 | 0.256 | 0.296 | 0.094 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo frases de reseña | 8-384 | 0.606 | 0.010 | 0.009 | 10/10 | 0.927 | 0.280 | 0.635 | 0.005 | 0.009 | 0.277 | 0.341 | 0.053 |
| promedio + frases de reseña, ponderadas | 384-394 | 0.605 | 0.010 | 0.007 | 9/10 | 0.928 | 0.280 | 0.632 | 0.002 | 0.007 | 0.288 | 0.341 | 0.137 |
| solo descripción (control) | 2-384 | 0.605 | 0.009 | 0.011 | 8/10 | 0.929 | 0.290 | 0.631 | 0.001 | 0.008 | 0.270 | 0.341 | 0.018 |
| promedio + frases de reseña | 384-394 | 0.598 | 0.002 | 0.004 | 7/10 | 0.928 | 0.280 | 0.627 | -0.002 | 0.002 | 0.287 | 0.341 | 0.135 |
| promedio + descripción (control) | 384-386 | 0.596 | 0.001 | 0.001 | 8/10 | 0.928 | 0.280 | 0.629 | -0.001 | 0.001 | 0.281 | 0.341 | 0.124 |
| promedio (sin frases) | 384 | 0.596 | 0.000 | 0.000 | referencia | 0.928 | 0.280 | 0.630 | 0.000 | 0.000 | 0.278 | 0.341 | 0.120 |

R² de la etapa 1 de cada criterio con frases:

| criterio | solo descripción (control) | promedio + frases de reseña, ponderadas | solo frases de reseña | promedio + frases de reseña | promedio + descripción (control) | promedio (sin frases) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.029 | -0.026 | -0.028 | -0.019 | -0.019 | -0.019 |
| insoportabilidad_prolongada | 0.120 | 0.193 | 0.208 | 0.178 | 0.148 | 0.142 |
| control_emocional_artificial | -0.019 | 0.369 | 0.091 | 0.302 | 0.279 | 0.276 |
| personajes_diorama | -0.024 | 0.074 | -0.017 | 0.136 | 0.140 | 0.137 |
| caos_asfixiante | 0.043 | 0.077 | 0.011 | 0.079 | 0.073 | 0.064 |

## Variables con más peso (regresión lineal anterior)

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

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| amelie | 4.50 | 8.69 | 4.19 |
| manhattan | 5.00 | 8.69 | 3.69 |
| la-la-land | 5.50 | 8.34 | 2.84 |
| primer | 6.50 | 8.98 | 2.48 |
| marty-supreme | 5.50 | 7.63 | 2.13 |
| barry-lyndon | 6.50 | 8.59 | 2.09 |
| triangle-of-sadness | 7.00 | 8.42 | 1.42 |
| beauty-and-the-beast | 6.00 | 7.39 | 1.39 |
| rocky | 9.20 | 7.89 | -1.31 |
| anne-of-green-gables | 9.80 | 8.50 | -1.30 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.62 | 12.26 |
| 2046 | 9.46 | 8.78 |
| the-seventh-seal | 9.37 | 9.96 |
| seven-samurai | 9.18 | 9.26 |
| under-the-skin | 9.13 | 9.15 |
| happy-together | 9.12 | 8.78 |
| train-dreams | 9.10 | 9.56 |
| chungking-express | 9.05 | 8.69 |
| the-passion-of-joan-of-arc | 9.02 | 9.44 |
| neon-genesis-evangelion | 8.91 | 8.51 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

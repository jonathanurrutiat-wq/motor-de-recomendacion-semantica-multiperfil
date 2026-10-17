# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-10-17T21:28:56 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 158 (106021 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 130 en la Verdad Base.
- Evaluadas sin reseñas: 1917, all-quiet-on-the-western, american-sniper, avatar, avatar-the-way-of-water, black-panther, bohemian-rhapsody, dunkirk, elvis, everything-everywhere-all-at-once, extremely-loud-incredibly-close, frankenstein, green-book, hidden-figures, im-still-here, inception, joker, les-miserables, lincoln, maestro, nickel-boys, oppenheimer, the-blind-side, the-fabelmans, the-help, the-imitation-game, the-theory-of-everything, toy-story-3, war-horse.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con frases de reseña (ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.603 | 0.947 | 0.240 | 0.668 | 1.129 | 0.290 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.689 | 0.960 | 0.300 | 0.638 | 0.896 | 0.436 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.489 | 0.935 | 0.300 | 0.883 | 1.746 | -0.098 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.394 | 0.918 | 0.200 | 0.840 | 1.510 | 0.051 |
| Línea base (promedio) | 0.000 | 0.845 | 0.129 | 0.855 | 1.626 | -0.023 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 5819 (regresiones Ridge desde el embedding de 384 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

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
| gt_afinidad_resistencia_femenina | 1.385 | 0.262 |
| gt_afinidad_contemplación_inmersiva | 1.292 | 0.446 |
| gt_afinidad_ternura_y_empatía_radical | 1.413 | 0.240 |
| gt_afinidad_humanismo_social | 1.067 | 0.365 |
| gt_afinidad_vanguardia_y_simbolismo | 1.123 | 0.471 |
| gt_cols_camaradería_masculina_rancia | 0.555 | -0.018 |
| gt_cols_insoportabilidad_prolongada | 1.943 | 0.245 |
| gt_cols_control_emocional_artificial | 1.534 | 0.390 |
| gt_cols_personajes_diorama | 1.739 | 0.111 |
| gt_cols_caos_asfixiante | 1.644 | 0.090 |
| gt_excepcion_camaradería_masculina_rancia | 0.237 | -0.006 |
| gt_excepcion_insoportabilidad_prolongada | 0.401 | 0.051 |
| gt_excepcion_personajes_diorama | 0.020 | -0.022 |
| gt_excepcion_caos_asfixiante | 0.096 | -0.024 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 95 por dimensión, hasta 50 reseñas | 384 | 0.638 | 0.045 | 0.027 | 9/10 | 0.969 | 0.460 | 0.655 | -0.011 | 0.017 | 0.294 | 0.353 | 0.091 |
| percentil 95 por dimensión, hasta 100 reseñas | 384 | 0.618 | 0.025 | 0.023 | 9/10 | 0.964 | 0.410 | 0.655 | -0.011 | 0.011 | 0.311 | 0.351 | 0.111 |
| promedio + percentiles de similitud, hasta 100 reseñas | 432 | 0.618 | 0.025 | 0.012 | 10/10 | 0.951 | 0.250 | 0.664 | -0.002 | 0.009 | 0.274 | 0.338 | 0.109 |
| promedio, hasta 100 reseñas | 384 | 0.618 | 0.025 | 0.009 | 10/10 | 0.951 | 0.240 | 0.663 | -0.003 | 0.008 | 0.274 | 0.328 | 0.109 |
| percentil 90 por dimensión, hasta 50 reseñas | 384 | 0.613 | 0.020 | 0.016 | 9/10 | 0.956 | 0.270 | 0.666 | 0.000 | 0.012 | 0.264 | 0.336 | 0.108 |
| percentil 90 por dimensión, hasta 100 reseñas | 384 | 0.609 | 0.016 | 0.023 | 7/10 | 0.958 | 0.280 | 0.665 | -0.001 | 0.011 | 0.266 | 0.329 | 0.105 |
| percentil 50 por dimensión, hasta 100 reseñas | 384 | 0.607 | 0.015 | 0.008 | 10/10 | 0.948 | 0.220 | 0.670 | 0.004 | 0.003 | 0.253 | 0.309 | 0.106 |
| percentil 75 por dimensión, hasta 100 reseñas | 384 | 0.602 | 0.009 | 0.018 | 7/10 | 0.953 | 0.260 | 0.676 | 0.010 | 0.014 | 0.262 | 0.320 | 0.108 |
| promedio + percentiles de similitud, todas las reseñas | 432 | 0.597 | 0.004 | 0.006 | 8/10 | 0.946 | 0.260 | 0.663 | -0.004 | 0.006 | 0.268 | 0.348 | 0.121 |
| percentil 75 por dimensión, hasta 50 reseñas | 384 | 0.596 | 0.003 | 0.015 | 6/10 | 0.948 | 0.180 | 0.677 | 0.011 | 0.013 | 0.252 | 0.308 | 0.105 |
| promedio, todas las reseñas | 384 | 0.593 | 0.000 | 0.000 | referencia | 0.948 | 0.250 | 0.666 | 0.000 | 0.000 | 0.261 | 0.336 | 0.123 |
| percentil 90 por dimensión, todas las reseñas | 384 | 0.591 | -0.002 | 0.018 | 4/10 | 0.953 | 0.280 | 0.669 | 0.003 | 0.011 | 0.258 | 0.340 | 0.122 |
| percentil 95 por dimensión, todas las reseñas | 384 | 0.591 | -0.002 | 0.018 | 5/10 | 0.963 | 0.370 | 0.668 | 0.001 | 0.010 | 0.254 | 0.348 | 0.111 |
| percentil 50 por dimensión, todas las reseñas | 384 | 0.591 | -0.002 | 0.007 | 4/10 | 0.945 | 0.220 | 0.669 | 0.003 | 0.003 | 0.247 | 0.320 | 0.119 |
| promedio + percentiles de similitud, hasta 50 reseñas | 432 | 0.590 | -0.003 | 0.010 | 3/10 | 0.941 | 0.160 | 0.674 | 0.008 | 0.014 | 0.257 | 0.320 | 0.102 |
| promedio, hasta 50 reseñas | 384 | 0.588 | -0.005 | 0.014 | 4/10 | 0.946 | 0.160 | 0.675 | 0.009 | 0.013 | 0.255 | 0.314 | 0.108 |
| percentil 75 por dimensión, todas las reseñas | 384 | 0.579 | -0.014 | 0.017 | 2/10 | 0.948 | 0.230 | 0.677 | 0.011 | 0.009 | 0.254 | 0.329 | 0.123 |
| percentil 50 por dimensión, hasta 50 reseñas | 384 | 0.575 | -0.018 | 0.016 | 0/10 | 0.943 | 0.160 | 0.684 | 0.018 | 0.013 | 0.236 | 0.288 | 0.097 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo frases de reseña | 8-384 | 0.610 | 0.017 | 0.010 | 10/10 | 0.946 | 0.240 | 0.668 | 0.002 | 0.010 | 0.283 | 0.336 | 0.054 |
| solo descripción (control) | 2-384 | 0.606 | 0.014 | 0.007 | 10/10 | 0.948 | 0.260 | 0.663 | -0.003 | 0.006 | 0.263 | 0.336 | 0.020 |
| promedio + frases de reseña, ponderadas | 384-394 | 0.603 | 0.010 | 0.007 | 9/10 | 0.947 | 0.240 | 0.668 | 0.002 | 0.006 | 0.290 | 0.336 | 0.140 |
| promedio + frases de reseña | 384-394 | 0.597 | 0.004 | 0.005 | 7/10 | 0.947 | 0.250 | 0.663 | -0.003 | 0.003 | 0.279 | 0.336 | 0.141 |
| promedio + descripción (control) | 384-386 | 0.593 | 0.000 | 0.002 | 7/10 | 0.947 | 0.250 | 0.665 | -0.001 | 0.002 | 0.266 | 0.336 | 0.127 |
| promedio (sin frases) | 384 | 0.593 | 0.000 | 0.000 | referencia | 0.948 | 0.250 | 0.666 | 0.000 | 0.000 | 0.261 | 0.336 | 0.123 |

R² de la etapa 1 de cada criterio con frases:

| criterio | solo frases de reseña | solo descripción (control) | promedio + frases de reseña, ponderadas | promedio (sin frases) | promedio + descripción (control) | promedio + frases de reseña |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.037 | -0.026 | -0.036 | -0.015 | -0.015 | -0.016 |
| insoportabilidad_prolongada | 0.240 | 0.136 | 0.225 | 0.154 | 0.166 | 0.200 |
| control_emocional_artificial | 0.077 | -0.019 | 0.364 | 0.274 | 0.278 | 0.303 |
| personajes_diorama | -0.018 | -0.030 | 0.073 | 0.133 | 0.134 | 0.135 |
| caos_asfixiante | 0.006 | 0.041 | 0.077 | 0.067 | 0.074 | 0.083 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| afinidad · Resistencia Femenina | 0.655 |
| afinidad · Contemplación Inmersiva | 0.637 |
| filtro · Caos Asfixiante | -0.493 |
| afinidad · Humanismo Social | 0.352 |
| filtro · Camaradería Masculina Rancia | -0.316 |
| Humanismo Social × Insoportabilidad Prolongada | 0.210 |
| afinidad · Ternura y Empatía Radical | -0.200 |
| Ternura y Empatía Radical × Insoportabilidad Prolongada | -0.195 |
| Camaradería Masculina Rancia × excepción | 0.184 |
| Resistencia Femenina × Camaradería Masculina Rancia | -0.181 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| marty-supreme | 2.00 | 7.45 | 5.45 |
| amelie | 4.50 | 8.50 | 4.00 |
| manhattan | 5.00 | 8.66 | 3.66 |
| la-la-land | 5.50 | 8.25 | 2.75 |
| primer | 6.50 | 9.00 | 2.50 |
| barry-lyndon | 6.50 | 8.64 | 2.14 |
| anne-of-green-gables | 9.80 | 8.40 | -1.40 |
| rocky | 9.20 | 7.82 | -1.38 |
| beauty-and-the-beast | 6.00 | 7.35 | 1.35 |
| triangle-of-sadness | 7.00 | 8.35 | 1.35 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.60 | 12.12 |
| 2046 | 9.46 | 8.81 |
| the-seventh-seal | 9.42 | 10.17 |
| train-dreams | 9.26 | 9.57 |
| seven-samurai | 9.18 | 9.09 |
| under-the-skin | 9.16 | 9.25 |
| happy-together | 9.10 | 8.82 |
| the-passion-of-joan-of-arc | 9.06 | 9.42 |
| chungking-express | 9.01 | 8.90 |
| neon-genesis-evangelion | 8.94 | 8.25 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

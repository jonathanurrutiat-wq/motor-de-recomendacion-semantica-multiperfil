# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T16:56:22 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` y pooling `media` para los modelos principales.

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
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones)** | 0.547 | 0.919 | 0.200 | 0.652 | 0.931 | 0.253 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.693 | 0.956 | 0.500 | 0.577 | 0.710 | 0.430 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.464 | 0.909 | 0.200 | 0.828 | 1.362 | -0.094 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.400 | 0.886 | 0.300 | 0.809 | 1.239 | 0.005 |
| Línea base (promedio) | 0.000 | 0.780 | 0.129 | 0.812 | 1.274 | -0.022 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 5819 (regresiones Ridge desde el embedding de 384 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

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
| gt_afinidad_resistencia_femenina | 1.442 | 0.202 |
| gt_afinidad_contemplación_inmersiva | 1.373 | 0.344 |
| gt_afinidad_ternura_y_empatía_radical | 1.453 | 0.175 |
| gt_afinidad_humanismo_social | 1.068 | 0.335 |
| gt_afinidad_vanguardia_y_simbolismo | 1.125 | 0.454 |
| gt_cols_camaradería_masculina_rancia | 0.513 | -0.029 |
| gt_cols_insoportabilidad_prolongada | 1.950 | 0.212 |
| gt_cols_control_emocional_artificial | 1.500 | 0.365 |
| gt_cols_personajes_diorama | 1.745 | 0.083 |
| gt_cols_caos_asfixiante | 1.701 | -0.023 |
| gt_excepcion_camaradería_masculina_rancia | 0.251 | -0.079 |
| gt_excepcion_insoportabilidad_prolongada | 0.407 | 0.035 |
| gt_excepcion_personajes_diorama | 0.019 | -0.025 |
| gt_excepcion_caos_asfixiante | 0.128 | -0.090 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 95 por dimensión, hasta 50 reseñas | 384 | 0.635 | 0.039 | 0.022 | 10/10 | 0.953 | 0.460 | 0.624 | -0.007 | 0.015 | 0.309 | 0.352 | 0.089 |
| promedio, hasta 100 reseñas | 384 | 0.616 | 0.021 | 0.010 | 10/10 | 0.929 | 0.250 | 0.629 | -0.002 | 0.007 | 0.293 | 0.331 | 0.106 |
| promedio + percentiles de similitud, hasta 100 reseñas | 432 | 0.616 | 0.020 | 0.013 | 10/10 | 0.929 | 0.270 | 0.628 | -0.003 | 0.008 | 0.290 | 0.341 | 0.106 |
| percentil 95 por dimensión, hasta 100 reseñas | 384 | 0.615 | 0.019 | 0.022 | 8/10 | 0.947 | 0.420 | 0.622 | -0.009 | 0.009 | 0.323 | 0.348 | 0.107 |
| percentil 90 por dimensión, hasta 50 reseñas | 384 | 0.614 | 0.019 | 0.014 | 9/10 | 0.938 | 0.270 | 0.630 | 0.000 | 0.012 | 0.289 | 0.339 | 0.109 |
| percentil 50 por dimensión, hasta 100 reseñas | 384 | 0.609 | 0.013 | 0.010 | 10/10 | 0.925 | 0.250 | 0.634 | 0.004 | 0.003 | 0.275 | 0.315 | 0.101 |
| percentil 75 por dimensión, hasta 100 reseñas | 384 | 0.602 | 0.007 | 0.015 | 6/10 | 0.930 | 0.270 | 0.638 | 0.008 | 0.008 | 0.280 | 0.325 | 0.107 |
| percentil 90 por dimensión, hasta 100 reseñas | 384 | 0.601 | 0.006 | 0.025 | 7/10 | 0.941 | 0.320 | 0.634 | 0.004 | 0.009 | 0.283 | 0.328 | 0.103 |
| promedio + percentiles de similitud, todas las reseñas | 432 | 0.596 | 0.001 | 0.006 | 6/10 | 0.928 | 0.280 | 0.629 | -0.001 | 0.005 | 0.281 | 0.353 | 0.119 |
| promedio, todas las reseñas | 384 | 0.595 | 0.000 | 0.000 | referencia | 0.929 | 0.280 | 0.630 | 0.000 | 0.000 | 0.277 | 0.341 | 0.120 |
| percentil 90 por dimensión, todas las reseñas | 384 | 0.594 | -0.001 | 0.018 | 4/10 | 0.934 | 0.320 | 0.635 | 0.005 | 0.009 | 0.283 | 0.343 | 0.121 |
| percentil 50 por dimensión, todas las reseñas | 384 | 0.592 | -0.003 | 0.005 | 2/10 | 0.922 | 0.230 | 0.634 | 0.003 | 0.002 | 0.267 | 0.326 | 0.119 |
| percentil 75 por dimensión, hasta 50 reseñas | 384 | 0.591 | -0.004 | 0.021 | 5/10 | 0.924 | 0.210 | 0.642 | 0.012 | 0.014 | 0.269 | 0.315 | 0.102 |
| percentil 95 por dimensión, todas las reseñas | 384 | 0.591 | -0.005 | 0.021 | 4/10 | 0.946 | 0.360 | 0.633 | 0.003 | 0.010 | 0.276 | 0.351 | 0.110 |
| percentil 75 por dimensión, todas las reseñas | 384 | 0.589 | -0.007 | 0.011 | 1/10 | 0.922 | 0.240 | 0.639 | 0.009 | 0.010 | 0.271 | 0.335 | 0.122 |
| promedio, hasta 50 reseñas | 384 | 0.589 | -0.007 | 0.022 | 5/10 | 0.921 | 0.190 | 0.642 | 0.011 | 0.013 | 0.268 | 0.318 | 0.105 |
| promedio + percentiles de similitud, hasta 50 reseñas | 432 | 0.588 | -0.007 | 0.012 | 3/10 | 0.915 | 0.180 | 0.639 | 0.008 | 0.012 | 0.270 | 0.323 | 0.100 |
| percentil 50 por dimensión, hasta 50 reseñas | 384 | 0.581 | -0.014 | 0.010 | 2/10 | 0.913 | 0.160 | 0.646 | 0.016 | 0.012 | 0.255 | 0.296 | 0.094 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo frases de reseña | 8-384 | 0.603 | 0.008 | 0.012 | 9/10 | 0.928 | 0.290 | 0.635 | 0.005 | 0.009 | 0.277 | 0.341 | 0.053 |
| solo descripción (control) | 2-384 | 0.603 | 0.008 | 0.011 | 8/10 | 0.929 | 0.290 | 0.631 | 0.001 | 0.008 | 0.270 | 0.341 | 0.018 |
| promedio + frases de reseña, ponderadas | 384-394 | 0.602 | 0.007 | 0.008 | 8/10 | 0.928 | 0.280 | 0.632 | 0.002 | 0.007 | 0.287 | 0.341 | 0.137 |
| promedio + frases de reseña | 384-394 | 0.597 | 0.001 | 0.004 | 6/10 | 0.928 | 0.280 | 0.628 | -0.003 | 0.001 | 0.286 | 0.341 | 0.135 |
| promedio (sin frases) | 384 | 0.595 | 0.000 | 0.000 | referencia | 0.929 | 0.280 | 0.630 | 0.000 | 0.000 | 0.277 | 0.341 | 0.120 |
| promedio + descripción (control) | 384-386 | 0.595 | -0.000 | 0.002 | 6/10 | 0.928 | 0.280 | 0.629 | -0.001 | 0.001 | 0.280 | 0.341 | 0.124 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña, ponderadas | solo descripción (control) | promedio + frases de reseña | promedio + descripción (control) | solo frases de reseña | promedio (sin frases) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.026 | -0.029 | -0.019 | -0.019 | -0.028 | -0.019 |
| insoportabilidad_prolongada | 0.193 | 0.120 | 0.178 | 0.148 | 0.208 | 0.142 |
| control_emocional_artificial | 0.369 | -0.019 | 0.302 | 0.279 | 0.091 | 0.276 |
| personajes_diorama | 0.074 | -0.024 | 0.136 | 0.140 | -0.017 | 0.137 |
| caos_asfixiante | 0.077 | 0.043 | 0.079 | 0.073 | 0.011 | 0.064 |

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
| amelie | 4.50 | 8.96 | 4.46 |
| manhattan | 5.00 | 8.57 | 3.57 |
| la-la-land | 5.50 | 8.37 | 2.87 |
| primer | 6.50 | 9.15 | 2.65 |
| barry-lyndon | 6.50 | 8.77 | 2.27 |
| marty-supreme | 5.50 | 7.53 | 2.03 |
| anne-of-green-gables | 9.80 | 8.27 | -1.53 |
| beauty-and-the-beast | 6.00 | 7.42 | 1.42 |
| triangle-of-sadness | 7.00 | 8.39 | 1.39 |
| emma | 6.50 | 7.84 | 1.34 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.58 | 12.26 |
| 2046 | 9.41 | 8.78 |
| the-seventh-seal | 9.35 | 9.96 |
| under-the-skin | 9.19 | 9.15 |
| seven-samurai | 9.16 | 9.26 |
| train-dreams | 9.09 | 9.56 |
| happy-together | 9.08 | 8.78 |
| the-passion-of-joan-of-arc | 9.07 | 9.44 |
| chungking-express | 9.01 | 8.69 |
| portrait-of-a-lady-on-fire | 8.96 | 9.15 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

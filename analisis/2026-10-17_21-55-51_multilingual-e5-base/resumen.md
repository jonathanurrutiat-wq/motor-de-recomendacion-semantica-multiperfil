# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-10-17T21:55:52 con el modelo de embeddings `intfloat/multilingual-e5-base` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 158 (55769 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 101 de 130 en la Verdad Base.
- Evaluadas sin reseñas: 1917, all-quiet-on-the-western, american-sniper, avatar, avatar-the-way-of-water, black-panther, bohemian-rhapsody, dunkirk, elvis, everything-everywhere-all-at-once, extremely-loud-incredibly-close, frankenstein, green-book, hidden-figures, im-still-here, inception, joker, les-miserables, lincoln, maestro, nickel-boys, oppenheimer, the-blind-side, the-fabelmans, the-help, the-imitation-game, the-theory-of-everything, toy-story-3, war-horse.
- Candidatas a recomendar (sin nota de Gemini): 57.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con frases de reseña (ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.676 | 0.958 | 0.280 | 0.614 | 0.948 | 0.404 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.662 | 0.964 | 0.400 | 0.626 | 0.680 | 0.573 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.534 | 0.946 | 0.300 | 0.812 | 1.227 | 0.228 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.579 | 0.963 | 0.400 | 0.724 | 1.182 | 0.256 |
| Línea base (promedio) | 0.000 | 0.845 | 0.129 | 0.855 | 1.626 | -0.023 |

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
| gt_afinidad_resistencia_femenina | 1.341 | 0.319 |
| gt_afinidad_contemplación_inmersiva | 1.129 | 0.556 |
| gt_afinidad_ternura_y_empatía_radical | 1.197 | 0.468 |
| gt_afinidad_humanismo_social | 1.005 | 0.458 |
| gt_afinidad_vanguardia_y_simbolismo | 0.932 | 0.596 |
| gt_cols_camaradería_masculina_rancia | 0.547 | -0.005 |
| gt_cols_insoportabilidad_prolongada | 1.928 | 0.289 |
| gt_cols_control_emocional_artificial | 1.511 | 0.370 |
| gt_cols_personajes_diorama | 1.515 | 0.221 |
| gt_cols_caos_asfixiante | 1.370 | 0.336 |
| gt_excepcion_camaradería_masculina_rancia | 0.231 | 0.037 |
| gt_excepcion_insoportabilidad_prolongada | 0.373 | 0.114 |
| gt_excepcion_personajes_diorama | 0.020 | -0.023 |
| gt_excepcion_caos_asfixiante | 0.095 | -0.005 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio, todas las reseñas | 768 | 0.670 | 0.000 | 0.000 | referencia | 0.958 | 0.290 | 0.617 | 0.000 | 0.000 | 0.400 | 0.459 | 0.205 |
| promedio, hasta 100 reseñas | 768 | 0.669 | -0.001 | 0.002 | 2/10 | 0.959 | 0.290 | 0.617 | 0.001 | 0.001 | 0.403 | 0.461 | 0.203 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.669 | -0.001 | 0.016 | 5/10 | 0.954 | 0.250 | 0.617 | 0.000 | 0.010 | 0.391 | 0.464 | 0.199 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.668 | -0.001 | 0.015 | 5/10 | 0.954 | 0.240 | 0.618 | 0.002 | 0.010 | 0.390 | 0.466 | 0.197 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.668 | -0.002 | 0.007 | 5/10 | 0.958 | 0.300 | 0.620 | 0.003 | 0.004 | 0.390 | 0.455 | 0.196 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.666 | -0.003 | 0.007 | 4/10 | 0.957 | 0.290 | 0.619 | 0.002 | 0.004 | 0.388 | 0.453 | 0.197 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.663 | -0.007 | 0.005 | 0/10 | 0.957 | 0.300 | 0.617 | 0.001 | 0.003 | 0.408 | 0.460 | 0.203 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.662 | -0.007 | 0.004 | 0/10 | 0.958 | 0.310 | 0.618 | 0.002 | 0.003 | 0.409 | 0.461 | 0.201 |
| promedio, hasta 50 reseñas | 768 | 0.662 | -0.007 | 0.010 | 3/10 | 0.953 | 0.300 | 0.625 | 0.008 | 0.010 | 0.387 | 0.435 | 0.189 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.661 | -0.009 | 0.009 | 2/10 | 0.949 | 0.250 | 0.627 | 0.011 | 0.011 | 0.371 | 0.428 | 0.179 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.661 | -0.009 | 0.016 | 3/10 | 0.956 | 0.270 | 0.624 | 0.007 | 0.011 | 0.371 | 0.440 | 0.174 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.660 | -0.010 | 0.008 | 1/10 | 0.951 | 0.220 | 0.622 | 0.006 | 0.009 | 0.392 | 0.439 | 0.187 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.659 | -0.010 | 0.012 | 1/10 | 0.958 | 0.230 | 0.623 | 0.007 | 0.010 | 0.372 | 0.447 | 0.196 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.658 | -0.012 | 0.011 | 1/10 | 0.958 | 0.230 | 0.624 | 0.007 | 0.011 | 0.372 | 0.448 | 0.194 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.648 | -0.022 | 0.008 | 0/10 | 0.957 | 0.270 | 0.634 | 0.017 | 0.008 | 0.379 | 0.456 | 0.194 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.647 | -0.022 | 0.009 | 0/10 | 0.957 | 0.270 | 0.632 | 0.016 | 0.008 | 0.378 | 0.453 | 0.196 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.642 | -0.027 | 0.014 | 0/10 | 0.953 | 0.280 | 0.634 | 0.018 | 0.012 | 0.366 | 0.437 | 0.175 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.641 | -0.029 | 0.022 | 0/10 | 0.952 | 0.210 | 0.636 | 0.019 | 0.019 | 0.344 | 0.417 | 0.180 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo frases de reseña | 8-768 | 0.681 | 0.012 | 0.008 | 9/10 | 0.958 | 0.290 | 0.616 | -0.001 | 0.004 | 0.398 | 0.459 | 0.044 |
| solo descripción (control) | 2-768 | 0.678 | 0.009 | 0.010 | 8/10 | 0.959 | 0.310 | 0.619 | 0.002 | 0.004 | 0.374 | 0.459 | -0.012 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.676 | 0.006 | 0.004 | 9/10 | 0.958 | 0.280 | 0.614 | -0.003 | 0.003 | 0.404 | 0.459 | 0.219 |
| promedio + frases de reseña | 768-778 | 0.672 | 0.002 | 0.002 | 8/10 | 0.958 | 0.290 | 0.615 | -0.002 | 0.001 | 0.404 | 0.459 | 0.212 |
| promedio + descripción (control) | 768-770 | 0.670 | 0.000 | 0.000 | 2/10 | 0.958 | 0.290 | 0.616 | -0.000 | 0.000 | 0.400 | 0.459 | 0.206 |
| promedio (sin frases) | 768 | 0.670 | 0.000 | 0.000 | referencia | 0.958 | 0.290 | 0.617 | 0.000 | 0.000 | 0.400 | 0.459 | 0.205 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio (sin frases) | promedio + descripción (control) | solo descripción (control) | promedio + frases de reseña | promedio + frases de reseña, ponderadas | solo frases de reseña |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.008 | -0.008 | -0.029 | -0.009 | -0.025 | -0.031 |
| insoportabilidad_prolongada | 0.271 | 0.272 | 0.041 | 0.277 | 0.269 | 0.149 |
| control_emocional_artificial | 0.290 | 0.291 | -0.013 | 0.308 | 0.346 | 0.038 |
| personajes_diorama | 0.175 | 0.175 | -0.025 | 0.184 | 0.197 | 0.016 |
| caos_asfixiante | 0.298 | 0.299 | -0.032 | 0.299 | 0.307 | 0.046 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| afinidad · Contemplación Inmersiva | 0.888 |
| Contemplación Inmersiva × Control Emocional Artificial | -0.742 |
| excepción · Insoportabilidad Prolongada | 0.615 |
| Humanismo Social × Control Emocional Artificial | 0.574 |
| afinidad · Humanismo Social | 0.509 |
| afinidad · Ternura y Empatía Radical | -0.503 |
| filtro · Caos Asfixiante | -0.496 |
| filtro · Control Emocional Artificial | -0.479 |
| Contemplación Inmersiva × Caos Asfixiante | 0.467 |
| excepción · Camaradería Masculina Rancia | -0.317 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| marty-supreme | 2.00 | 6.85 | 4.85 |
| amelie | 4.50 | 8.26 | 3.76 |
| manhattan | 5.00 | 8.24 | 3.24 |
| la-la-land | 5.50 | 7.95 | 2.45 |
| barry-lyndon | 6.50 | 8.70 | 2.20 |
| primer | 6.50 | 8.50 | 2.00 |
| the-royal-tenenbaums | 6.80 | 8.38 | 1.58 |
| beauty-and-the-beast | 6.00 | 7.53 | 1.53 |
| rocky | 9.20 | 7.80 | -1.40 |
| coraline | 8.80 | 7.58 | -1.22 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.85 | 10.33 |
| under-the-skin | 9.53 | 9.78 |
| train-dreams | 9.51 | 9.44 |
| 2046 | 9.46 | 8.52 |
| the-passion-of-joan-of-arc | 9.42 | 8.57 |
| the-seventh-seal | 9.36 | 10.51 |
| sentimental-value | 9.29 | 8.29 |
| happy-together | 9.26 | 9.19 |
| chungking-express | 9.22 | 8.60 |
| neon-genesis-evangelion | 9.21 | 8.75 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

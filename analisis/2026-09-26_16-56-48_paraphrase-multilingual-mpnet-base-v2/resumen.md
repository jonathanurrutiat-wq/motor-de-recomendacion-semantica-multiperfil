# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T16:56:48 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` y pooling `media` para los modelos principales.

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
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones)** | 0.624 | 0.933 | 0.200 | 0.611 | 0.815 | 0.345 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.716 | 0.931 | 0.300 | 0.590 | 0.646 | 0.481 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.598 | 0.906 | 0.200 | 0.891 | 1.589 | -0.275 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.605 | 0.906 | 0.300 | 0.745 | 1.105 | 0.113 |
| Línea base (promedio) | 0.000 | 0.780 | 0.129 | 0.812 | 1.274 | -0.022 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11579 (regresiones Ridge desde el embedding de 768 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

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
| gt_afinidad_resistencia_femenina | 1.376 | 0.266 |
| gt_afinidad_contemplación_inmersiva | 1.279 | 0.421 |
| gt_afinidad_ternura_y_empatía_radical | 1.281 | 0.336 |
| gt_afinidad_humanismo_social | 0.985 | 0.425 |
| gt_afinidad_vanguardia_y_simbolismo | 0.989 | 0.547 |
| gt_cols_camaradería_masculina_rancia | 0.511 | -0.022 |
| gt_cols_insoportabilidad_prolongada | 1.913 | 0.266 |
| gt_cols_control_emocional_artificial | 1.505 | 0.370 |
| gt_cols_personajes_diorama | 1.675 | 0.131 |
| gt_cols_caos_asfixiante | 1.429 | 0.231 |
| gt_excepcion_camaradería_masculina_rancia | 0.246 | -0.085 |
| gt_excepcion_insoportabilidad_prolongada | 0.392 | 0.075 |
| gt_excepcion_personajes_diorama | 0.020 | -0.030 |
| gt_excepcion_caos_asfixiante | 0.117 | -0.058 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.651 | 0.008 | 0.003 | 10/10 | 0.936 | 0.310 | 0.596 | -0.004 | 0.003 | 0.366 | 0.411 | 0.123 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.651 | 0.008 | 0.003 | 10/10 | 0.937 | 0.310 | 0.595 | -0.004 | 0.003 | 0.366 | 0.409 | 0.123 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.650 | 0.006 | 0.005 | 9/10 | 0.938 | 0.270 | 0.596 | -0.004 | 0.006 | 0.375 | 0.413 | 0.128 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.650 | 0.006 | 0.005 | 9/10 | 0.939 | 0.280 | 0.593 | -0.006 | 0.005 | 0.376 | 0.412 | 0.128 |
| promedio, todas las reseñas | 768 | 0.644 | 0.000 | 0.000 | referencia | 0.936 | 0.260 | 0.600 | 0.000 | 0.000 | 0.362 | 0.401 | 0.119 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.644 | -0.000 | 0.006 | 5/10 | 0.933 | 0.260 | 0.598 | -0.002 | 0.003 | 0.365 | 0.402 | 0.121 |
| promedio, hasta 100 reseñas | 768 | 0.643 | -0.001 | 0.004 | 3/10 | 0.936 | 0.260 | 0.601 | 0.001 | 0.003 | 0.362 | 0.403 | 0.118 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.642 | -0.002 | 0.006 | 4/10 | 0.933 | 0.270 | 0.600 | -0.000 | 0.005 | 0.365 | 0.404 | 0.121 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.639 | -0.005 | 0.011 | 3/10 | 0.931 | 0.290 | 0.600 | 0.000 | 0.008 | 0.355 | 0.402 | 0.116 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.639 | -0.005 | 0.010 | 5/10 | 0.937 | 0.290 | 0.603 | 0.003 | 0.008 | 0.356 | 0.406 | 0.127 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.638 | -0.006 | 0.011 | 4/10 | 0.938 | 0.300 | 0.602 | 0.002 | 0.007 | 0.355 | 0.404 | 0.127 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.636 | -0.008 | 0.010 | 3/10 | 0.944 | 0.370 | 0.599 | -0.000 | 0.008 | 0.337 | 0.390 | 0.129 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.636 | -0.008 | 0.009 | 2/10 | 0.942 | 0.350 | 0.599 | -0.001 | 0.008 | 0.337 | 0.392 | 0.129 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.634 | -0.010 | 0.016 | 2/10 | 0.930 | 0.300 | 0.605 | 0.005 | 0.008 | 0.343 | 0.403 | 0.113 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.633 | -0.011 | 0.015 | 3/10 | 0.934 | 0.300 | 0.600 | 0.000 | 0.010 | 0.350 | 0.398 | 0.110 |
| promedio, hasta 50 reseñas | 768 | 0.627 | -0.017 | 0.012 | 1/10 | 0.931 | 0.290 | 0.608 | 0.008 | 0.007 | 0.341 | 0.396 | 0.106 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.624 | -0.020 | 0.021 | 2/10 | 0.932 | 0.330 | 0.610 | 0.010 | 0.008 | 0.335 | 0.394 | 0.124 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.618 | -0.026 | 0.025 | 2/10 | 0.929 | 0.340 | 0.620 | 0.021 | 0.010 | 0.301 | 0.376 | 0.112 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solo descripción (control) | 2-768 | 0.652 | 0.008 | 0.010 | 7/10 | 0.935 | 0.260 | 0.609 | 0.009 | 0.008 | 0.351 | 0.401 | 0.041 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.650 | 0.006 | 0.010 | 7/10 | 0.934 | 0.260 | 0.601 | 0.002 | 0.008 | 0.383 | 0.401 | 0.179 |
| solo frases de reseña | 8-768 | 0.649 | 0.005 | 0.013 | 5/10 | 0.935 | 0.260 | 0.612 | 0.012 | 0.007 | 0.369 | 0.401 | 0.087 |
| promedio + frases de reseña | 768-778 | 0.645 | 0.001 | 0.002 | 6/10 | 0.936 | 0.260 | 0.598 | -0.002 | 0.002 | 0.366 | 0.401 | 0.129 |
| promedio + descripción (control) | 768-770 | 0.644 | 0.001 | 0.001 | 8/10 | 0.936 | 0.260 | 0.599 | -0.000 | 0.000 | 0.363 | 0.401 | 0.122 |
| promedio (sin frases) | 768 | 0.644 | 0.000 | 0.000 | referencia | 0.936 | 0.260 | 0.600 | 0.000 | 0.000 | 0.362 | 0.401 | 0.119 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña | promedio + frases de reseña, ponderadas | promedio (sin frases) | promedio + descripción (control) | solo frases de reseña | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -0.022 | -0.036 | -0.022 | -0.022 | -0.035 | -0.029 |
| insoportabilidad_prolongada | 0.168 | 0.238 | 0.147 | 0.153 | 0.239 | 0.208 |
| control_emocional_artificial | 0.321 | 0.328 | 0.311 | 0.312 | 0.101 | -0.035 |
| personajes_diorama | 0.091 | 0.147 | 0.083 | 0.087 | -0.006 | -0.016 |
| caos_asfixiante | 0.089 | 0.219 | 0.074 | 0.081 | 0.135 | 0.075 |

## Variables con más peso (regresión lineal anterior)

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

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| amelie | 4.50 | 8.60 | 4.10 |
| la-la-land | 5.50 | 8.44 | 2.94 |
| manhattan | 5.00 | 7.91 | 2.91 |
| primer | 6.50 | 8.78 | 2.28 |
| marty-supreme | 5.50 | 7.33 | 1.83 |
| the-royal-tenenbaums | 6.80 | 8.56 | 1.76 |
| barry-lyndon | 6.50 | 8.12 | 1.62 |
| rocky | 9.20 | 7.68 | -1.52 |
| anne-of-green-gables | 9.80 | 8.30 | -1.50 |
| crouching-tiger-hidden-dragon | 9.50 | 8.03 | -1.47 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.67 | 11.67 |
| the-seventh-seal | 9.52 | 9.28 |
| 2046 | 9.51 | 8.91 |
| sentimental-value | 9.36 | 10.27 |
| train-dreams | 9.31 | 9.54 |
| neon-genesis-evangelion | 9.28 | 8.62 |
| happy-together | 9.22 | 8.41 |
| portrait-of-a-lady-on-fire | 9.17 | 9.15 |
| chungking-express | 9.16 | 8.08 |
| under-the-skin | 9.15 | 9.54 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

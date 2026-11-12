# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-11-12T04:51:48 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 187 (62965 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 187 de 248 en la Verdad Base.
- Evaluadas sin reseñas: 12-angry-men, 21-jump-street, 6-underground, american-pie, amores-perros, amour, asteroid-city, babylon, belfast, black-swan, city-of-god, clueless, coda, crash, dead-poets-society, fifty-shades-of-grey, fight-club, get-out, goodfellas, grave-of-the-fireflies, grown-ups, interstellar, knives-out, logan, mamma-mia, midsommar, moulin-rouge, nickel-boys, nightcrawler, old-school, pans-labyrinth, project-x, se7en, shrek, spider-man-into-the-spider-verse, spirited-away, step-brothers, superbad, the-batman, the-dark-knight, the-french-dispatch, the-godfather, the-grand-budapest-hotel, the-hangover, the-lobster, the-matrix, the-pursuit-of-happyness, the-room, the-silence-of-the-lambs, the-social-network, the-truman-show, the-wolf-of-wall-street, there-will-be-blood, titanic, train-to-busan, transformers-revenge-of-the-fallen, twilight, uncut-gems, whiplash, wonder, your-name.
- Candidatas a recomendar (sin nota de Gemini): 0.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con rasgos de similitud con las reseñas en 10 criterios (modo ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.670 | 0.953 | 0.250 | 0.987 | 2.017 | 0.415 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.708 | 0.950 | 0.400 | 0.963 | 1.676 | 0.514 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.616 | 0.946 | 0.400 | 1.148 | 2.330 | 0.324 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.634 | 0.933 | 0.300 | 1.098 | 2.274 | 0.340 |
| Línea base (promedio) | 0.000 | 0.757 | 0.070 | 1.370 | 3.455 | -0.002 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con rasgos de similitud usan además cuántas reseñas se parecen a su descripción y, si las tienen, a sus frases de reseña. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11589 (regresiones Ridge desde el embedding de 768 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

- Nota base = 3.23 + 0.08·Resistencia Femenina + 0.11·Contemplación Inmersiva + 0.16·Ternura y Empatía Radical + 0.17·Humanismo Social + 0.21·Vanguardia y Simbolismo
- Si Camaradería Masculina Rancia supera 2.8 y su excepción no aplica: resta hasta 1.06 puntos.
- Si Insoportabilidad Prolongada supera 5.3 y su excepción no aplica: resta hasta 1.35 puntos.
- Si Control Emocional Artificial supera 7.8 y su excepción no aplica: resta hasta 0.73 puntos.
- Si Personajes Diorama supera 8.7 y su excepción no aplica: resta hasta 1.05 puntos.
- Si Caos Asfixiante supera 8.3 y su excepción no aplica: resta hasta 1.05 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.937 | 0.979 | 0.500 | 0.403 | 0.272 | 0.946 |
| Regresión lineal sobre los puntajes | 0.944 | 0.984 | 0.700 | 0.421 | 0.284 | 0.944 |
| Línea base (promedio) | 0.000 | 0.732 | 0.060 | 1.764 | 5.077 | -0.008 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 1.506 | 0.429 |
| gt_afinidad_contemplación_inmersiva | 1.391 | 0.521 |
| gt_afinidad_ternura_y_empatía_radical | 1.425 | 0.380 |
| gt_afinidad_humanismo_social | 1.270 | 0.390 |
| gt_afinidad_vanguardia_y_simbolismo | 1.163 | 0.539 |
| gt_cols_camaradería_masculina_rancia | 1.209 | 0.126 |
| gt_cols_insoportabilidad_prolongada | 1.752 | 0.271 |
| gt_cols_control_emocional_artificial | 1.699 | 0.364 |
| gt_cols_personajes_diorama | 1.628 | 0.330 |
| gt_cols_caos_asfixiante | 1.507 | 0.420 |
| gt_excepcion_camaradería_masculina_rancia | 0.179 | 0.016 |
| gt_excepcion_insoportabilidad_prolongada | 0.325 | 0.028 |
| gt_excepcion_personajes_diorama | 0.011 | -0.020 |
| gt_excepcion_caos_asfixiante | 0.062 | 0.002 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.680 | 0.007 | 0.008 | 7/10 | 0.957 | 0.340 | 0.974 | -0.006 | 0.010 | 0.408 | 0.431 | 0.291 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.680 | 0.007 | 0.008 | 7/10 | 0.955 | 0.320 | 0.974 | -0.006 | 0.010 | 0.408 | 0.430 | 0.294 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.679 | 0.006 | 0.003 | 10/10 | 0.961 | 0.290 | 0.975 | -0.005 | 0.003 | 0.407 | 0.435 | 0.274 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.679 | 0.005 | 0.003 | 10/10 | 0.961 | 0.290 | 0.976 | -0.005 | 0.003 | 0.407 | 0.434 | 0.275 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.679 | 0.005 | 0.006 | 8/10 | 0.959 | 0.300 | 0.982 | 0.001 | 0.009 | 0.401 | 0.427 | 0.287 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.678 | 0.005 | 0.006 | 8/10 | 0.959 | 0.300 | 0.982 | 0.002 | 0.008 | 0.401 | 0.426 | 0.289 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.678 | 0.005 | 0.009 | 6/10 | 0.951 | 0.300 | 0.979 | -0.001 | 0.009 | 0.407 | 0.423 | 0.277 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.677 | 0.004 | 0.003 | 9/10 | 0.965 | 0.340 | 0.979 | -0.001 | 0.004 | 0.399 | 0.426 | 0.279 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.677 | 0.004 | 0.003 | 9/10 | 0.965 | 0.340 | 0.980 | 0.000 | 0.004 | 0.398 | 0.425 | 0.281 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.676 | 0.003 | 0.008 | 6/10 | 0.952 | 0.300 | 0.979 | -0.001 | 0.007 | 0.406 | 0.424 | 0.284 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.675 | 0.002 | 0.004 | 6/10 | 0.958 | 0.300 | 0.980 | -0.000 | 0.002 | 0.401 | 0.425 | 0.266 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.675 | 0.001 | 0.004 | 6/10 | 0.958 | 0.300 | 0.980 | -0.000 | 0.002 | 0.401 | 0.425 | 0.266 |
| promedio, hasta 100 reseñas | 768 | 0.674 | 0.000 | 0.001 | 7/10 | 0.960 | 0.310 | 0.980 | -0.001 | 0.001 | 0.404 | 0.428 | 0.266 |
| promedio, todas las reseñas | 768 | 0.673 | 0.000 | 0.000 | referencia | 0.961 | 0.310 | 0.980 | 0.000 | 0.000 | 0.404 | 0.428 | 0.268 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.672 | -0.002 | 0.004 | 5/10 | 0.959 | 0.310 | 0.974 | -0.006 | 0.005 | 0.410 | 0.431 | 0.270 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.671 | -0.003 | 0.004 | 2/10 | 0.962 | 0.310 | 0.977 | -0.003 | 0.006 | 0.410 | 0.424 | 0.262 |
| promedio, hasta 50 reseñas | 768 | 0.670 | -0.004 | 0.005 | 4/10 | 0.958 | 0.300 | 0.977 | -0.003 | 0.006 | 0.409 | 0.427 | 0.262 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.669 | -0.004 | 0.005 | 2/10 | 0.955 | 0.310 | 0.985 | 0.005 | 0.005 | 0.396 | 0.421 | 0.271 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + frases de reseña | 768-778 | 0.674 | 0.000 | 0.001 | 6/10 | 0.961 | 0.310 | 0.981 | 0.000 | 0.002 | 0.406 | 0.428 | 0.275 |
| promedio + descripción (control) | 768-770 | 0.674 | 0.000 | 0.001 | 6/10 | 0.961 | 0.310 | 0.981 | 0.001 | 0.001 | 0.403 | 0.428 | 0.270 |
| promedio (sin frases) | 768 | 0.673 | 0.000 | 0.000 | referencia | 0.961 | 0.310 | 0.980 | 0.000 | 0.000 | 0.404 | 0.428 | 0.268 |
| promedio + frases de reseña, ponderadas | 768-778 | 0.667 | -0.006 | 0.004 | 0/10 | 0.960 | 0.300 | 0.991 | 0.011 | 0.006 | 0.408 | 0.428 | 0.283 |
| solo descripción (control) | 2-768 | 0.661 | -0.012 | 0.004 | 0/10 | 0.957 | 0.310 | 1.003 | 0.023 | 0.007 | 0.363 | 0.428 | 0.030 |
| solo frases de reseña | 8-768 | 0.660 | -0.014 | 0.004 | 0/10 | 0.958 | 0.290 | 1.002 | 0.022 | 0.008 | 0.384 | 0.428 | 0.090 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + descripción (control) | promedio + frases de reseña | promedio (sin frases) | promedio + frases de reseña, ponderadas | solo frases de reseña | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.124 | 0.123 | 0.124 | 0.117 | 0.027 | -0.006 |
| insoportabilidad_prolongada | 0.210 | 0.225 | 0.202 | 0.240 | 0.202 | 0.114 |
| control_emocional_artificial | 0.341 | 0.344 | 0.341 | 0.349 | 0.063 | -0.006 |
| personajes_diorama | 0.329 | 0.327 | 0.328 | 0.306 | 0.009 | -0.001 |
| caos_asfixiante | 0.347 | 0.354 | 0.343 | 0.402 | 0.148 | 0.050 |

## Similitud con la descripción de cada criterio (modelo de reglas, validación cruzada)

Para cada filtro y afinidad se mide la similitud de cada chunk de reseña con su descripción y se resume en la fracción de chunks muy similares (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud, sin necesitar frases_resenia. Se agrega al embedding promedio (concatenada o ponderada) o lo reemplaza. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el promedio solo en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor).

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + similitud con la descripción | 770 | 0.674 | 0.001 | 0.001 | 6/10 | 0.960 | 0.310 | 0.981 | 0.000 | 0.001 | 0.404 | 0.429 | 0.270 |
| promedio (sin rasgos) | 768 | 0.673 | 0.000 | 0.000 | referencia | 0.961 | 0.310 | 0.980 | 0.000 | 0.000 | 0.404 | 0.428 | 0.268 |
| promedio + similitud con la descripción, ponderada | 770 | 0.673 | -0.000 | 0.006 | 5/10 | 0.954 | 0.260 | 0.983 | 0.003 | 0.008 | 0.409 | 0.431 | 0.281 |
| solo similitud con la descripción | 2 | 0.571 | -0.103 | 0.015 | 0/10 | 0.931 | 0.190 | 1.103 | 0.123 | 0.019 | 0.174 | 0.218 | 0.030 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| afinidad · Resistencia Femenina | 0.768 |
| filtro · Insoportabilidad Prolongada | -0.685 |
| filtro · Control Emocional Artificial | -0.587 |
| filtro · Personajes Diorama | 0.525 |
| afinidad · Contemplación Inmersiva | 0.485 |
| filtro · Caos Asfixiante | 0.436 |
| filtro · Camaradería Masculina Rancia | -0.411 |
| Humanismo Social × Control Emocional Artificial | 0.336 |
| excepción · Camaradería Masculina Rancia | 0.253 |
| afinidad · Ternura y Empatía Radical | 0.214 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| american-sniper | 2.00 | 7.16 | 5.16 |
| marty-supreme | 2.00 | 6.53 | 4.53 |
| amelie | 4.50 | 8.98 | 4.48 |
| extremely-loud-incredibly-close | 2.00 | 5.95 | 3.95 |
| the-blind-side | 2.50 | 6.37 | 3.87 |
| joker | 2.00 | 5.75 | 3.75 |
| the-help | 4.00 | 7.72 | 3.72 |
| climax | 4.50 | 8.20 | 3.70 |
| requiem-for-a-dream | 4.20 | 7.76 | 3.56 |
| a-clockwork-orange | 3.80 | 7.34 | 3.54 |

## Mejores candidatas a recomendar

No hay películas candidatas.

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_descripcion.csv`: comparación con y sin los rasgos de similitud con la descripción de cada criterio.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

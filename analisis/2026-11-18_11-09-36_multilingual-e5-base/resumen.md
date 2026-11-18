# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-11-18T11:09:36 con el modelo de embeddings `intfloat/multilingual-e5-base` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 187 (62965 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 129 de 190 en la Verdad Base.
- Evaluadas sin reseñas: 12-angry-men, 21-jump-street, 6-underground, american-pie, amores-perros, amour, asteroid-city, babylon, belfast, black-swan, city-of-god, clueless, coda, crash, dead-poets-society, fifty-shades-of-grey, fight-club, get-out, goodfellas, grave-of-the-fireflies, grown-ups, interstellar, knives-out, logan, mamma-mia, midsommar, moulin-rouge, nickel-boys, nightcrawler, old-school, pans-labyrinth, project-x, se7en, shrek, spider-man-into-the-spider-verse, spirited-away, step-brothers, superbad, the-batman, the-dark-knight, the-french-dispatch, the-godfather, the-grand-budapest-hotel, the-hangover, the-lobster, the-matrix, the-pursuit-of-happyness, the-room, the-silence-of-the-lambs, the-social-network, the-truman-show, the-wolf-of-wall-street, there-will-be-blood, titanic, train-to-busan, transformers-revenge-of-the-fallen, twilight, uncut-gems, whiplash, wonder, your-name.
- Candidatas a recomendar (sin nota de Gemini): 58.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con rasgos de similitud con las reseñas en 10 criterios (modo ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.712 | 0.949 | 0.200 | 0.970 | 1.924 | 0.533 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.731 | 0.947 | 0.200 | 0.917 | 1.493 | 0.638 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.617 | 0.917 | 0.200 | 1.157 | 2.365 | 0.426 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.653 | 0.946 | 0.300 | 1.084 | 2.178 | 0.472 |
| Línea base (promedio) | 0.000 | 0.761 | 0.101 | 1.531 | 4.156 | -0.008 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con rasgos de similitud usan además cuántas reseñas se parecen a su descripción y, si las tienen, a sus frases de reseña. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11589 (regresiones Ridge desde el embedding de 768 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

- Nota base = 3.08 + 0.08·Resistencia Femenina + 0.10·Contemplación Inmersiva + 0.19·Ternura y Empatía Radical + 0.17·Humanismo Social + 0.23·Vanguardia y Simbolismo
- Si Camaradería Masculina Rancia supera 3.8 y su excepción no aplica: resta hasta 1.15 puntos.
- Si Insoportabilidad Prolongada supera 5.1 y su excepción no aplica: resta hasta 1.43 puntos.
- Si Control Emocional Artificial supera 7.1 y su excepción no aplica: resta hasta 0.65 puntos.
- Si Personajes Diorama supera 8.8 y su excepción no aplica: resta hasta 1.18 puntos.
- Si Caos Asfixiante supera 8.5 y su excepción no aplica: resta hasta 1.20 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.957 | 0.977 | 0.500 | 0.405 | 0.320 | 0.946 |
| Regresión lineal sobre los puntajes | 0.954 | 0.982 | 0.700 | 0.443 | 0.328 | 0.945 |
| Línea base (promedio) | 0.000 | 0.719 | 0.079 | 1.968 | 5.990 | -0.011 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 1.425 | 0.542 |
| gt_afinidad_contemplación_inmersiva | 1.275 | 0.651 |
| gt_afinidad_ternura_y_empatía_radical | 1.421 | 0.425 |
| gt_afinidad_humanismo_social | 1.389 | 0.395 |
| gt_afinidad_vanguardia_y_simbolismo | 1.033 | 0.685 |
| gt_cols_camaradería_masculina_rancia | 0.800 | 0.246 |
| gt_cols_insoportabilidad_prolongada | 1.907 | 0.277 |
| gt_cols_control_emocional_artificial | 1.688 | 0.528 |
| gt_cols_personajes_diorama | 1.862 | 0.351 |
| gt_cols_caos_asfixiante | 1.471 | 0.497 |
| gt_excepcion_camaradería_masculina_rancia | 0.188 | 0.029 |
| gt_excepcion_insoportabilidad_prolongada | 0.336 | 0.065 |
| gt_excepcion_personajes_diorama | 0.015 | -0.020 |
| gt_excepcion_caos_asfixiante | 0.091 | 0.008 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio, hasta 50 reseñas | 768 | 0.733 | 0.002 | 0.010 | 6/10 | 0.950 | 0.260 | 0.974 | 0.004 | 0.013 | 0.526 | 0.531 | 0.341 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.732 | 0.001 | 0.004 | 5/10 | 0.955 | 0.290 | 0.977 | 0.006 | 0.005 | 0.513 | 0.536 | 0.344 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.732 | 0.001 | 0.004 | 6/10 | 0.956 | 0.290 | 0.977 | 0.007 | 0.005 | 0.512 | 0.536 | 0.343 |
| promedio, todas las reseñas | 768 | 0.731 | 0.000 | 0.000 | referencia | 0.958 | 0.300 | 0.970 | 0.000 | 0.000 | 0.519 | 0.536 | 0.347 |
| promedio, hasta 100 reseñas | 768 | 0.731 | -0.000 | 0.002 | 5/10 | 0.958 | 0.290 | 0.970 | -0.000 | 0.001 | 0.518 | 0.537 | 0.346 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.730 | -0.000 | 0.010 | 7/10 | 0.946 | 0.220 | 0.989 | 0.019 | 0.014 | 0.512 | 0.525 | 0.331 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.728 | -0.003 | 0.008 | 5/10 | 0.941 | 0.220 | 0.975 | 0.005 | 0.014 | 0.525 | 0.531 | 0.337 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.726 | -0.005 | 0.010 | 3/10 | 0.957 | 0.330 | 0.987 | 0.017 | 0.012 | 0.499 | 0.520 | 0.322 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.726 | -0.005 | 0.004 | 1/10 | 0.955 | 0.290 | 0.975 | 0.005 | 0.006 | 0.520 | 0.538 | 0.346 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.726 | -0.005 | 0.010 | 3/10 | 0.950 | 0.260 | 0.995 | 0.025 | 0.013 | 0.505 | 0.524 | 0.324 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.725 | -0.006 | 0.004 | 1/10 | 0.955 | 0.290 | 0.976 | 0.005 | 0.005 | 0.521 | 0.537 | 0.347 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.718 | -0.013 | 0.006 | 0/10 | 0.954 | 0.280 | 0.995 | 0.024 | 0.007 | 0.503 | 0.531 | 0.333 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.717 | -0.013 | 0.007 | 0/10 | 0.954 | 0.270 | 0.995 | 0.025 | 0.008 | 0.503 | 0.532 | 0.332 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.716 | -0.014 | 0.009 | 0/10 | 0.958 | 0.350 | 0.982 | 0.012 | 0.008 | 0.493 | 0.525 | 0.336 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.716 | -0.015 | 0.008 | 1/10 | 0.958 | 0.340 | 0.982 | 0.012 | 0.008 | 0.494 | 0.525 | 0.336 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.711 | -0.020 | 0.009 | 0/10 | 0.953 | 0.220 | 0.999 | 0.028 | 0.012 | 0.483 | 0.516 | 0.338 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.710 | -0.021 | 0.009 | 0/10 | 0.954 | 0.230 | 0.998 | 0.028 | 0.012 | 0.484 | 0.517 | 0.339 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.710 | -0.021 | 0.009 | 0/10 | 0.952 | 0.270 | 1.008 | 0.038 | 0.019 | 0.486 | 0.506 | 0.338 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + frases de reseña, ponderadas | 768-778 | 0.739 | 0.008 | 0.003 | 10/10 | 0.958 | 0.300 | 0.950 | -0.020 | 0.007 | 0.550 | 0.536 | 0.357 |
| solo frases de reseña | 8-768 | 0.735 | 0.004 | 0.006 | 7/10 | 0.956 | 0.250 | 0.974 | 0.004 | 0.011 | 0.521 | 0.536 | 0.117 |
| promedio + frases de reseña | 768-778 | 0.733 | 0.002 | 0.001 | 10/10 | 0.959 | 0.310 | 0.963 | -0.007 | 0.001 | 0.527 | 0.536 | 0.353 |
| promedio (sin frases) | 768 | 0.731 | 0.000 | 0.000 | referencia | 0.958 | 0.300 | 0.970 | 0.000 | 0.000 | 0.519 | 0.536 | 0.347 |
| promedio + descripción (control) | 768-770 | 0.731 | -0.000 | 0.000 | 3/10 | 0.958 | 0.300 | 0.970 | -0.000 | 0.000 | 0.519 | 0.536 | 0.347 |
| solo descripción (control) | 2-768 | 0.730 | -0.001 | 0.005 | 3/10 | 0.957 | 0.290 | 1.008 | 0.038 | 0.008 | 0.460 | 0.536 | 0.048 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña, ponderadas | solo frases de reseña | promedio + frases de reseña | promedio (sin frases) | promedio + descripción (control) | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.214 | 0.016 | 0.236 | 0.237 | 0.237 | -0.012 |
| insoportabilidad_prolongada | 0.267 | 0.193 | 0.240 | 0.221 | 0.222 | 0.034 |
| control_emocional_artificial | 0.511 | 0.259 | 0.484 | 0.474 | 0.474 | 0.109 |
| personajes_diorama | 0.322 | 0.095 | 0.355 | 0.356 | 0.356 | 0.125 |
| caos_asfixiante | 0.470 | 0.025 | 0.451 | 0.446 | 0.446 | -0.017 |

## Similitud con la descripción de cada criterio (modelo de reglas, validación cruzada)

Para cada filtro y afinidad se mide la similitud de cada chunk de reseña con su descripción y se resume en la fracción de chunks muy similares (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud, sin necesitar frases_resenia. Se agrega al embedding promedio (concatenada o ponderada) o lo reemplaza. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el promedio solo en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor).

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio (sin rasgos) | 768 | 0.731 | 0.000 | 0.000 | referencia | 0.958 | 0.300 | 0.970 | 0.000 | 0.000 | 0.519 | 0.536 | 0.347 |
| promedio + similitud con la descripción | 770 | 0.731 | -0.000 | 0.001 | 3/10 | 0.958 | 0.300 | 0.971 | 0.001 | 0.001 | 0.519 | 0.537 | 0.347 |
| promedio + similitud con la descripción, ponderada | 770 | 0.705 | -0.026 | 0.007 | 0/10 | 0.949 | 0.200 | 0.990 | 0.020 | 0.005 | 0.506 | 0.521 | 0.341 |
| solo similitud con la descripción | 2 | 0.483 | -0.248 | 0.016 | 0/10 | 0.929 | 0.100 | 1.227 | 0.257 | 0.025 | 0.237 | 0.254 | 0.048 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| Contemplación Inmersiva × Control Emocional Artificial | -1.365 |
| afinidad · Contemplación Inmersiva | 1.335 |
| Humanismo Social × Control Emocional Artificial | 1.280 |
| filtro · Personajes Diorama | 0.887 |
| excepción · Insoportabilidad Prolongada | 0.721 |
| filtro · Caos Asfixiante | -0.558 |
| filtro · Insoportabilidad Prolongada | -0.526 |
| Ternura y Empatía Radical × Personajes Diorama | -0.497 |
| Contemplación Inmersiva × Caos Asfixiante | 0.461 |
| Ternura y Empatía Radical × Insoportabilidad Prolongada | 0.429 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| american-sniper | 2.00 | 6.79 | 4.79 |
| marty-supreme | 2.00 | 6.43 | 4.43 |
| joker | 2.00 | 6.12 | 4.12 |
| amelie | 4.50 | 8.59 | 4.09 |
| the-blind-side | 2.50 | 6.58 | 4.08 |
| elvis | 2.00 | 5.33 | 3.33 |
| the-help | 4.00 | 7.22 | 3.22 |
| rocky | 9.20 | 6.05 | -3.15 |
| maestro | 3.50 | 5.97 | 2.47 |
| all-quiet-on-the-western-front | 5.20 | 7.58 | 2.38 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.91 | 10.31 |
| the-passion-of-joan-of-arc | 9.87 | 8.38 |
| chungking-express | 9.73 | 8.59 |
| 2046 | 9.67 | 8.38 |
| sentimental-value | 9.64 | 7.89 |
| portrait-of-a-lady-on-fire | 9.63 | 8.48 |
| happy-together | 9.56 | 9.19 |
| the-seventh-seal | 9.29 | 10.39 |
| under-the-skin | 9.19 | 9.47 |
| train-dreams | 9.15 | 9.77 |

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

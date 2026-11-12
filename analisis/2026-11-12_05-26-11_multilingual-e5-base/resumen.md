# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-11-12T05:26:11 con el modelo de embeddings `intfloat/multilingual-e5-base` y pooling `media` para los modelos principales.

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
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.676 | 0.930 | 0.120 | 0.961 | 1.843 | 0.465 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.691 | 0.943 | 0.300 | 0.958 | 1.588 | 0.539 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.618 | 0.903 | 0.300 | 1.107 | 2.151 | 0.376 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.645 | 0.905 | 0.200 | 1.056 | 2.108 | 0.388 |
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
| gt_afinidad_resistencia_femenina | 1.450 | 0.452 |
| gt_afinidad_contemplación_inmersiva | 1.312 | 0.580 |
| gt_afinidad_ternura_y_empatía_radical | 1.351 | 0.427 |
| gt_afinidad_humanismo_social | 1.310 | 0.392 |
| gt_afinidad_vanguardia_y_simbolismo | 1.056 | 0.594 |
| gt_cols_camaradería_masculina_rancia | 1.185 | 0.157 |
| gt_cols_insoportabilidad_prolongada | 1.733 | 0.307 |
| gt_cols_control_emocional_artificial | 1.695 | 0.373 |
| gt_cols_personajes_diorama | 1.547 | 0.384 |
| gt_cols_caos_asfixiante | 1.485 | 0.441 |
| gt_excepcion_camaradería_masculina_rancia | 0.179 | 0.025 |
| gt_excepcion_insoportabilidad_prolongada | 0.306 | 0.099 |
| gt_excepcion_personajes_diorama | 0.011 | -0.016 |
| gt_excepcion_caos_asfixiante | 0.063 | -0.003 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.688 | 0.007 | 0.008 | 7/10 | 0.921 | 0.260 | 0.955 | -0.015 | 0.009 | 0.452 | 0.470 | 0.310 |
| promedio, hasta 50 reseñas | 768 | 0.684 | 0.004 | 0.004 | 7/10 | 0.921 | 0.210 | 0.959 | -0.011 | 0.008 | 0.462 | 0.477 | 0.313 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.683 | 0.003 | 0.005 | 6/10 | 0.927 | 0.210 | 0.967 | -0.002 | 0.007 | 0.450 | 0.472 | 0.306 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.682 | 0.002 | 0.004 | 8/10 | 0.941 | 0.210 | 0.976 | 0.007 | 0.003 | 0.439 | 0.478 | 0.311 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.682 | 0.002 | 0.005 | 7/10 | 0.941 | 0.210 | 0.976 | 0.007 | 0.004 | 0.439 | 0.478 | 0.309 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.682 | 0.001 | 0.008 | 6/10 | 0.906 | 0.200 | 0.964 | -0.006 | 0.014 | 0.439 | 0.456 | 0.321 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.681 | 0.001 | 0.005 | 6/10 | 0.916 | 0.170 | 0.959 | -0.010 | 0.008 | 0.461 | 0.476 | 0.309 |
| promedio, hasta 100 reseñas | 768 | 0.680 | 0.000 | 0.001 | 4/10 | 0.938 | 0.220 | 0.969 | -0.000 | 0.001 | 0.448 | 0.482 | 0.314 |
| promedio, todas las reseñas | 768 | 0.680 | 0.000 | 0.000 | referencia | 0.938 | 0.210 | 0.969 | 0.000 | 0.000 | 0.448 | 0.482 | 0.315 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.679 | -0.001 | 0.005 | 4/10 | 0.921 | 0.210 | 0.967 | -0.002 | 0.008 | 0.451 | 0.476 | 0.302 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.677 | -0.003 | 0.006 | 3/10 | 0.917 | 0.230 | 0.964 | -0.006 | 0.006 | 0.439 | 0.476 | 0.319 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.677 | -0.003 | 0.006 | 3/10 | 0.917 | 0.230 | 0.964 | -0.005 | 0.006 | 0.439 | 0.476 | 0.319 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.675 | -0.005 | 0.009 | 4/10 | 0.910 | 0.170 | 0.964 | -0.006 | 0.010 | 0.436 | 0.475 | 0.324 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.675 | -0.005 | 0.008 | 4/10 | 0.909 | 0.160 | 0.965 | -0.004 | 0.010 | 0.435 | 0.475 | 0.324 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.675 | -0.006 | 0.002 | 0/10 | 0.930 | 0.170 | 0.973 | 0.004 | 0.002 | 0.446 | 0.481 | 0.315 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.675 | -0.006 | 0.003 | 0/10 | 0.930 | 0.180 | 0.973 | 0.003 | 0.002 | 0.446 | 0.481 | 0.313 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.672 | -0.008 | 0.004 | 0/10 | 0.930 | 0.190 | 0.979 | 0.010 | 0.005 | 0.436 | 0.480 | 0.309 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.672 | -0.008 | 0.004 | 0/10 | 0.930 | 0.190 | 0.979 | 0.010 | 0.005 | 0.436 | 0.480 | 0.309 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + frases de reseña, ponderadas | 768-778 | 0.686 | 0.006 | 0.003 | 10/10 | 0.936 | 0.200 | 0.957 | -0.012 | 0.003 | 0.471 | 0.482 | 0.315 |
| promedio + frases de reseña | 768-778 | 0.682 | 0.002 | 0.002 | 8/10 | 0.936 | 0.200 | 0.965 | -0.004 | 0.002 | 0.454 | 0.482 | 0.320 |
| promedio + descripción (control) | 768-770 | 0.680 | 0.000 | 0.000 | 6/10 | 0.938 | 0.210 | 0.969 | -0.000 | 0.000 | 0.448 | 0.482 | 0.315 |
| promedio (sin frases) | 768 | 0.680 | 0.000 | 0.000 | referencia | 0.938 | 0.210 | 0.969 | 0.000 | 0.000 | 0.448 | 0.482 | 0.315 |
| solo frases de reseña | 8-768 | 0.675 | -0.005 | 0.003 | 1/10 | 0.937 | 0.180 | 0.977 | 0.007 | 0.008 | 0.444 | 0.482 | 0.097 |
| solo descripción (control) | 2-768 | 0.668 | -0.012 | 0.004 | 0/10 | 0.934 | 0.190 | 0.999 | 0.029 | 0.008 | 0.391 | 0.482 | 0.030 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña | promedio + frases de reseña, ponderadas | promedio + descripción (control) | promedio (sin frases) | solo frases de reseña | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.148 | 0.141 | 0.147 | 0.148 | 0.042 | -0.005 |
| insoportabilidad_prolongada | 0.275 | 0.296 | 0.257 | 0.256 | 0.209 | 0.028 |
| control_emocional_artificial | 0.382 | 0.355 | 0.380 | 0.380 | 0.106 | 0.072 |
| personajes_diorama | 0.369 | 0.360 | 0.365 | 0.366 | 0.062 | 0.070 |
| caos_asfixiante | 0.429 | 0.423 | 0.425 | 0.426 | 0.067 | -0.017 |

## Similitud con la descripción de cada criterio (modelo de reglas, validación cruzada)

Para cada filtro y afinidad se mide la similitud de cada chunk de reseña con su descripción y se resume en la fracción de chunks muy similares (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud, sin necesitar frases_resenia. Se agrega al embedding promedio (concatenada o ponderada) o lo reemplaza. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el promedio solo en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor).

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + similitud con la descripción | 770 | 0.681 | 0.001 | 0.001 | 9/10 | 0.938 | 0.210 | 0.969 | -0.000 | 0.000 | 0.448 | 0.482 | 0.315 |
| promedio (sin rasgos) | 768 | 0.680 | 0.000 | 0.000 | referencia | 0.938 | 0.210 | 0.969 | 0.000 | 0.000 | 0.448 | 0.482 | 0.315 |
| promedio + similitud con la descripción, ponderada | 770 | 0.671 | -0.009 | 0.007 | 2/10 | 0.929 | 0.120 | 0.970 | 0.001 | 0.005 | 0.448 | 0.472 | 0.313 |
| solo similitud con la descripción | 2 | 0.462 | -0.218 | 0.012 | 0/10 | 0.920 | 0.090 | 1.136 | 0.167 | 0.019 | 0.170 | 0.187 | 0.030 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| afinidad · Contemplación Inmersiva | 1.060 |
| Contemplación Inmersiva × Control Emocional Artificial | -0.853 |
| filtro · Insoportabilidad Prolongada | -0.829 |
| Humanismo Social × Control Emocional Artificial | 0.737 |
| filtro · Personajes Diorama | 0.501 |
| Ternura y Empatía Radical × Insoportabilidad Prolongada | 0.495 |
| filtro · Control Emocional Artificial | -0.479 |
| afinidad · Resistencia Femenina | 0.445 |
| Insoportabilidad Prolongada × excepción | -0.338 |
| Humanismo Social × Insoportabilidad Prolongada | 0.261 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| american-sniper | 2.00 | 6.73 | 4.73 |
| marty-supreme | 2.00 | 6.19 | 4.19 |
| the-blind-side | 2.50 | 6.68 | 4.18 |
| amelie | 4.50 | 8.58 | 4.08 |
| joker | 2.00 | 5.79 | 3.79 |
| the-help | 4.00 | 7.66 | 3.66 |
| climax | 4.50 | 8.00 | 3.50 |
| requiem-for-a-dream | 4.20 | 7.63 | 3.43 |
| a-clockwork-orange | 3.80 | 7.22 | 3.42 |
| elvis | 2.00 | 5.42 | 3.42 |

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

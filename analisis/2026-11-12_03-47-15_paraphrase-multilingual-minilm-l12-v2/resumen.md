# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-11-12T03:47:15 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 187 (113217 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 187 de 248 en la Verdad Base.
- Evaluadas sin reseñas: 12-angry-men, 21-jump-street, 6-underground, american-pie, amores-perros, amour, asteroid-city, babylon, belfast, black-swan, city-of-god, clueless, coda, crash, dead-poets-society, fifty-shades-of-grey, fight-club, get-out, goodfellas, grave-of-the-fireflies, grown-ups, interstellar, knives-out, logan, mamma-mia, midsommar, moulin-rouge, nickel-boys, nightcrawler, old-school, pans-labyrinth, project-x, se7en, shrek, spider-man-into-the-spider-verse, spirited-away, step-brothers, superbad, the-batman, the-dark-knight, the-french-dispatch, the-godfather, the-grand-budapest-hotel, the-hangover, the-lobster, the-matrix, the-pursuit-of-happyness, the-room, the-silence-of-the-lambs, the-social-network, the-truman-show, the-wolf-of-wall-street, there-will-be-blood, titanic, train-to-busan, transformers-revenge-of-the-fallen, twilight, uncut-gems, whiplash, wonder, your-name.
- Candidatas a recomendar (sin nota de Gemini): 0.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con rasgos de similitud con las reseñas en 10 criterios (modo ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.677 | 0.936 | 0.140 | 0.979 | 2.088 | 0.394 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.677 | 0.960 | 0.500 | 0.972 | 1.740 | 0.495 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.574 | 0.913 | 0.400 | 1.161 | 2.521 | 0.269 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.620 | 0.918 | 0.300 | 1.081 | 2.245 | 0.349 |
| Línea base (promedio) | 0.000 | 0.757 | 0.070 | 1.370 | 3.455 | -0.002 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con rasgos de similitud usan además cuántas reseñas se parecen a su descripción y, si las tienen, a sus frases de reseña. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 5829 (regresiones Ridge desde el embedding de 384 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

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
| gt_afinidad_resistencia_femenina | 1.499 | 0.418 |
| gt_afinidad_contemplación_inmersiva | 1.472 | 0.471 |
| gt_afinidad_ternura_y_empatía_radical | 1.486 | 0.318 |
| gt_afinidad_humanismo_social | 1.349 | 0.327 |
| gt_afinidad_vanguardia_y_simbolismo | 1.257 | 0.455 |
| gt_cols_camaradería_masculina_rancia | 1.178 | 0.170 |
| gt_cols_insoportabilidad_prolongada | 1.732 | 0.277 |
| gt_cols_control_emocional_artificial | 1.787 | 0.311 |
| gt_cols_personajes_diorama | 1.757 | 0.280 |
| gt_cols_caos_asfixiante | 1.664 | 0.333 |
| gt_excepcion_camaradería_masculina_rancia | 0.182 | -0.010 |
| gt_excepcion_insoportabilidad_prolongada | 0.325 | 0.026 |
| gt_excepcion_personajes_diorama | 0.011 | -0.014 |
| gt_excepcion_caos_asfixiante | 0.063 | -0.010 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + percentiles de similitud, todas las reseñas | 432 | 0.682 | 0.007 | 0.004 | 10/10 | 0.927 | 0.140 | 0.976 | -0.011 | 0.004 | 0.388 | 0.396 | 0.254 |
| percentil 95 por dimensión, hasta 50 reseñas | 384 | 0.679 | 0.004 | 0.016 | 6/10 | 0.949 | 0.270 | 0.998 | 0.011 | 0.017 | 0.396 | 0.387 | 0.227 |
| percentil 95 por dimensión, todas las reseñas | 384 | 0.678 | 0.003 | 0.011 | 6/10 | 0.937 | 0.200 | 0.984 | -0.003 | 0.013 | 0.393 | 0.398 | 0.257 |
| promedio, todas las reseñas | 384 | 0.675 | 0.000 | 0.000 | referencia | 0.931 | 0.170 | 0.987 | 0.000 | 0.000 | 0.379 | 0.386 | 0.248 |
| percentil 90 por dimensión, todas las reseñas | 384 | 0.674 | -0.001 | 0.007 | 5/10 | 0.934 | 0.200 | 0.992 | 0.004 | 0.006 | 0.381 | 0.385 | 0.255 |
| percentil 75 por dimensión, hasta 50 reseñas | 384 | 0.672 | -0.003 | 0.010 | 4/10 | 0.939 | 0.200 | 0.990 | 0.003 | 0.013 | 0.396 | 0.387 | 0.245 |
| percentil 75 por dimensión, todas las reseñas | 384 | 0.672 | -0.003 | 0.006 | 3/10 | 0.929 | 0.140 | 0.989 | 0.002 | 0.010 | 0.383 | 0.388 | 0.257 |
| promedio + percentiles de similitud, hasta 50 reseñas | 432 | 0.672 | -0.003 | 0.008 | 3/10 | 0.933 | 0.180 | 0.984 | -0.004 | 0.014 | 0.390 | 0.390 | 0.241 |
| percentil 90 por dimensión, hasta 50 reseñas | 384 | 0.672 | -0.003 | 0.014 | 5/10 | 0.949 | 0.230 | 0.999 | 0.012 | 0.016 | 0.382 | 0.379 | 0.234 |
| percentil 95 por dimensión, hasta 100 reseñas | 384 | 0.671 | -0.004 | 0.011 | 4/10 | 0.945 | 0.200 | 0.999 | 0.011 | 0.014 | 0.394 | 0.393 | 0.242 |
| percentil 50 por dimensión, todas las reseñas | 384 | 0.670 | -0.005 | 0.006 | 2/10 | 0.932 | 0.160 | 0.992 | 0.004 | 0.005 | 0.370 | 0.380 | 0.243 |
| promedio + percentiles de similitud, hasta 100 reseñas | 432 | 0.669 | -0.005 | 0.004 | 0/10 | 0.937 | 0.150 | 0.988 | 0.001 | 0.008 | 0.374 | 0.391 | 0.240 |
| promedio, hasta 50 reseñas | 384 | 0.668 | -0.007 | 0.006 | 1/10 | 0.936 | 0.190 | 0.993 | 0.006 | 0.011 | 0.384 | 0.385 | 0.237 |
| promedio, hasta 100 reseñas | 384 | 0.663 | -0.012 | 0.004 | 0/10 | 0.934 | 0.160 | 0.998 | 0.011 | 0.005 | 0.365 | 0.381 | 0.233 |
| percentil 90 por dimensión, hasta 100 reseñas | 384 | 0.661 | -0.013 | 0.008 | 0/10 | 0.941 | 0.170 | 1.007 | 0.020 | 0.013 | 0.368 | 0.375 | 0.239 |
| percentil 75 por dimensión, hasta 100 reseñas | 384 | 0.660 | -0.015 | 0.007 | 0/10 | 0.934 | 0.140 | 0.999 | 0.011 | 0.009 | 0.376 | 0.383 | 0.240 |
| percentil 50 por dimensión, hasta 50 reseñas | 384 | 0.660 | -0.015 | 0.009 | 0/10 | 0.929 | 0.150 | 0.997 | 0.010 | 0.017 | 0.376 | 0.380 | 0.232 |
| percentil 50 por dimensión, hasta 100 reseñas | 384 | 0.658 | -0.017 | 0.005 | 0/10 | 0.934 | 0.130 | 1.003 | 0.016 | 0.008 | 0.357 | 0.376 | 0.229 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + frases de reseña | 384-394 | 0.676 | 0.001 | 0.002 | 8/10 | 0.931 | 0.170 | 0.984 | -0.003 | 0.003 | 0.389 | 0.386 | 0.261 |
| promedio + descripción (control) | 384-386 | 0.675 | 0.001 | 0.001 | 7/10 | 0.931 | 0.170 | 0.987 | -0.001 | 0.001 | 0.380 | 0.386 | 0.250 |
| promedio (sin frases) | 384 | 0.675 | 0.000 | 0.000 | referencia | 0.931 | 0.170 | 0.987 | 0.000 | 0.000 | 0.379 | 0.386 | 0.248 |
| promedio + frases de reseña, ponderadas | 384-394 | 0.669 | -0.006 | 0.008 | 1/10 | 0.931 | 0.170 | 0.991 | 0.004 | 0.007 | 0.385 | 0.386 | 0.253 |
| solo descripción (control) | 2-384 | 0.665 | -0.010 | 0.009 | 1/10 | 0.931 | 0.150 | 1.009 | 0.021 | 0.015 | 0.326 | 0.386 | 0.038 |
| solo frases de reseña | 8-384 | 0.664 | -0.010 | 0.009 | 1/10 | 0.933 | 0.140 | 1.004 | 0.016 | 0.015 | 0.355 | 0.386 | 0.079 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio (sin frases) | promedio + descripción (control) | promedio + frases de reseña | solo frases de reseña | solo descripción (control) | promedio + frases de reseña, ponderadas |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.153 | 0.153 | 0.152 | 0.056 | 0.008 | 0.157 |
| insoportabilidad_prolongada | 0.188 | 0.200 | 0.243 | 0.212 | 0.074 | 0.237 |
| control_emocional_artificial | 0.312 | 0.314 | 0.317 | 0.062 | -0.004 | 0.297 |
| personajes_diorama | 0.290 | 0.289 | 0.288 | 0.065 | 0.083 | 0.264 |
| caos_asfixiante | 0.297 | 0.296 | 0.304 | 0.001 | 0.026 | 0.312 |

## Similitud con la descripción de cada criterio (modelo de reglas, validación cruzada)

Para cada filtro y afinidad se mide la similitud de cada chunk de reseña con su descripción y se resume en la fracción de chunks muy similares (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud, sin necesitar frases_resenia. Se agrega al embedding promedio (concatenada o ponderada) o lo reemplaza. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el promedio solo en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor).

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + similitud con la descripción, ponderada | 386 | 0.685 | 0.010 | 0.005 | 9/10 | 0.934 | 0.140 | 0.973 | -0.014 | 0.009 | 0.392 | 0.383 | 0.259 |
| promedio + similitud con la descripción | 386 | 0.677 | 0.002 | 0.002 | 8/10 | 0.931 | 0.160 | 0.984 | -0.004 | 0.002 | 0.381 | 0.388 | 0.250 |
| promedio (sin rasgos) | 384 | 0.675 | 0.000 | 0.000 | referencia | 0.931 | 0.170 | 0.987 | 0.000 | 0.000 | 0.379 | 0.386 | 0.248 |
| solo similitud con la descripción | 2 | 0.581 | -0.094 | 0.016 | 0/10 | 0.947 | 0.170 | 1.090 | 0.103 | 0.030 | 0.187 | 0.195 | 0.038 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| afinidad · Ternura y Empatía Radical | 0.775 |
| filtro · Insoportabilidad Prolongada | -0.689 |
| afinidad · Vanguardia y Simbolismo | 0.528 |
| afinidad · Resistencia Femenina | 0.512 |
| filtro · Personajes Diorama | 0.455 |
| Humanismo Social × Insoportabilidad Prolongada | 0.383 |
| filtro · Control Emocional Artificial | -0.364 |
| Insoportabilidad Prolongada × excepción | -0.200 |
| filtro · Caos Asfixiante | 0.189 |
| filtro · Camaradería Masculina Rancia | -0.176 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| american-sniper | 2.00 | 7.12 | 5.12 |
| amelie | 4.50 | 9.29 | 4.79 |
| extremely-loud-incredibly-close | 2.00 | 6.27 | 4.27 |
| marty-supreme | 2.00 | 6.17 | 4.17 |
| requiem-for-a-dream | 4.20 | 8.32 | 4.12 |
| joker | 2.00 | 6.04 | 4.04 |
| the-blind-side | 2.50 | 6.49 | 3.99 |
| climax | 4.50 | 8.38 | 3.88 |
| the-help | 4.00 | 7.61 | 3.61 |
| maestro | 3.50 | 6.96 | 3.46 |

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

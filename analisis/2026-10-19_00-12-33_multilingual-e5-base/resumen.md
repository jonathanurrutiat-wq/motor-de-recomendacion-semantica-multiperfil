# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-10-19T00:12:34 con el modelo de embeddings `intfloat/multilingual-e5-base` y pooling `media` para los modelos principales.

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
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.739 | 0.959 | 0.310 | 0.945 | 1.928 | 0.532 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.731 | 0.947 | 0.200 | 0.917 | 1.493 | 0.638 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.617 | 0.917 | 0.200 | 1.157 | 2.365 | 0.426 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.653 | 0.946 | 0.300 | 1.084 | 2.178 | 0.472 |
| Línea base (promedio) | 0.000 | 0.761 | 0.101 | 1.531 | 4.156 | -0.008 |

## Modelo de reglas en dos etapas (opciones 7 y 8)

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas; los criterios con frases de reseña usan además cuántas reseñas se parecen a su descripción y a sus frases. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 11579 (regresiones Ridge desde el embedding de 768 dimensiones y los rasgos de frases, una por criterio). Regresión lineal anterior: 22.

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
| gt_afinidad_resistencia_femenina | 1.467 | 0.524 |
| gt_afinidad_contemplación_inmersiva | 1.227 | 0.666 |
| gt_afinidad_ternura_y_empatía_radical | 1.393 | 0.448 |
| gt_afinidad_humanismo_social | 1.335 | 0.437 |
| gt_afinidad_vanguardia_y_simbolismo | 1.019 | 0.699 |
| gt_cols_camaradería_masculina_rancia | 0.800 | 0.246 |
| gt_cols_insoportabilidad_prolongada | 1.907 | 0.277 |
| gt_cols_control_emocional_artificial | 1.688 | 0.528 |
| gt_cols_personajes_diorama | 1.862 | 0.351 |
| gt_cols_caos_asfixiante | 1.472 | 0.497 |
| gt_excepcion_camaradería_masculina_rancia | 0.188 | 0.029 |
| gt_excepcion_insoportabilidad_prolongada | 0.336 | 0.065 |
| gt_excepcion_personajes_diorama | 0.015 | -0.020 |
| gt_excepcion_caos_asfixiante | 0.091 | 0.008 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio, hasta 50 reseñas | 768 | 0.735 | 0.000 | 0.008 | 6/10 | 0.951 | 0.270 | 0.978 | 0.005 | 0.012 | 0.497 | 0.531 | 0.341 |
| promedio, todas las reseñas | 768 | 0.735 | 0.000 | 0.000 | referencia | 0.959 | 0.320 | 0.973 | 0.000 | 0.000 | 0.493 | 0.536 | 0.347 |
| promedio, hasta 100 reseñas | 768 | 0.734 | -0.001 | 0.001 | 1/10 | 0.959 | 0.320 | 0.974 | 0.000 | 0.002 | 0.492 | 0.537 | 0.346 |
| percentil 50 por dimensión, todas las reseñas | 768 | 0.734 | -0.002 | 0.004 | 4/10 | 0.955 | 0.280 | 0.980 | 0.006 | 0.005 | 0.487 | 0.536 | 0.344 |
| percentil 50 por dimensión, hasta 100 reseñas | 768 | 0.733 | -0.002 | 0.004 | 4/10 | 0.955 | 0.280 | 0.981 | 0.007 | 0.004 | 0.486 | 0.536 | 0.343 |
| percentil 50 por dimensión, hasta 50 reseñas | 768 | 0.732 | -0.003 | 0.011 | 5/10 | 0.946 | 0.230 | 0.993 | 0.019 | 0.012 | 0.482 | 0.525 | 0.331 |
| percentil 90 por dimensión, hasta 50 reseñas | 768 | 0.732 | -0.003 | 0.009 | 4/10 | 0.960 | 0.340 | 0.993 | 0.020 | 0.010 | 0.466 | 0.520 | 0.322 |
| promedio + percentiles de similitud, hasta 50 reseñas | 816 | 0.732 | -0.003 | 0.006 | 3/10 | 0.944 | 0.260 | 0.978 | 0.005 | 0.012 | 0.496 | 0.531 | 0.337 |
| promedio + percentiles de similitud, todas las reseñas | 816 | 0.730 | -0.005 | 0.005 | 1/10 | 0.953 | 0.270 | 0.976 | 0.002 | 0.005 | 0.497 | 0.537 | 0.347 |
| promedio + percentiles de similitud, hasta 100 reseñas | 816 | 0.729 | -0.006 | 0.005 | 0/10 | 0.953 | 0.250 | 0.975 | 0.002 | 0.006 | 0.497 | 0.538 | 0.346 |
| percentil 75 por dimensión, hasta 50 reseñas | 768 | 0.728 | -0.008 | 0.008 | 1/10 | 0.951 | 0.290 | 1.001 | 0.027 | 0.012 | 0.474 | 0.524 | 0.324 |
| percentil 75 por dimensión, todas las reseñas | 768 | 0.721 | -0.014 | 0.005 | 0/10 | 0.953 | 0.280 | 0.999 | 0.025 | 0.005 | 0.477 | 0.531 | 0.333 |
| percentil 75 por dimensión, hasta 100 reseñas | 768 | 0.721 | -0.014 | 0.004 | 0/10 | 0.953 | 0.260 | 1.000 | 0.026 | 0.006 | 0.476 | 0.532 | 0.332 |
| percentil 90 por dimensión, hasta 100 reseñas | 768 | 0.719 | -0.017 | 0.008 | 1/10 | 0.959 | 0.340 | 0.990 | 0.017 | 0.006 | 0.465 | 0.525 | 0.336 |
| percentil 90 por dimensión, todas las reseñas | 768 | 0.718 | -0.017 | 0.007 | 0/10 | 0.959 | 0.340 | 0.990 | 0.017 | 0.006 | 0.466 | 0.525 | 0.336 |
| percentil 95 por dimensión, hasta 50 reseñas | 768 | 0.715 | -0.020 | 0.009 | 0/10 | 0.951 | 0.240 | 1.008 | 0.035 | 0.017 | 0.456 | 0.506 | 0.338 |
| percentil 95 por dimensión, hasta 100 reseñas | 768 | 0.715 | -0.020 | 0.007 | 0/10 | 0.955 | 0.240 | 1.004 | 0.030 | 0.007 | 0.454 | 0.516 | 0.338 |
| percentil 95 por dimensión, todas las reseñas | 768 | 0.714 | -0.021 | 0.008 | 0/10 | 0.955 | 0.240 | 1.004 | 0.031 | 0.008 | 0.455 | 0.517 | 0.339 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio + frases de reseña, ponderadas | 768-778 | 0.739 | 0.004 | 0.004 | 6/10 | 0.959 | 0.310 | 0.945 | -0.028 | 0.006 | 0.532 | 0.536 | 0.357 |
| promedio + frases de reseña | 768-778 | 0.736 | 0.001 | 0.001 | 9/10 | 0.959 | 0.320 | 0.966 | -0.007 | 0.002 | 0.502 | 0.536 | 0.353 |
| promedio + descripción (control) | 768-770 | 0.735 | 0.000 | 0.000 | 4/10 | 0.959 | 0.320 | 0.973 | -0.000 | 0.001 | 0.494 | 0.536 | 0.347 |
| promedio (sin frases) | 768 | 0.735 | 0.000 | 0.000 | referencia | 0.959 | 0.320 | 0.973 | 0.000 | 0.000 | 0.493 | 0.536 | 0.347 |
| solo frases de reseña | 8-768 | 0.732 | -0.003 | 0.006 | 2/10 | 0.954 | 0.270 | 0.985 | 0.012 | 0.013 | 0.485 | 0.536 | 0.117 |
| solo descripción (control) | 2-768 | 0.727 | -0.008 | 0.006 | 2/10 | 0.954 | 0.270 | 1.021 | 0.048 | 0.011 | 0.429 | 0.536 | 0.048 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + frases de reseña, ponderadas | promedio + frases de reseña | promedio (sin frases) | promedio + descripción (control) | solo frases de reseña | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.214 | 0.236 | 0.237 | 0.237 | 0.016 | -0.012 |
| insoportabilidad_prolongada | 0.267 | 0.240 | 0.221 | 0.222 | 0.193 | 0.034 |
| control_emocional_artificial | 0.511 | 0.484 | 0.474 | 0.474 | 0.259 | 0.109 |
| personajes_diorama | 0.322 | 0.355 | 0.356 | 0.356 | 0.095 | 0.125 |
| caos_asfixiante | 0.470 | 0.451 | 0.446 | 0.446 | 0.025 | -0.017 |

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
| american-sniper | 2.00 | 7.05 | 5.05 |
| marty-supreme | 2.00 | 6.85 | 4.85 |
| joker | 2.00 | 6.48 | 4.48 |
| amelie | 4.50 | 8.55 | 4.05 |
| elvis | 2.00 | 5.67 | 3.67 |
| the-blind-side | 2.50 | 6.08 | 3.58 |
| the-help | 4.00 | 7.23 | 3.23 |
| rocky | 9.20 | 6.18 | -3.02 |
| maestro | 3.50 | 6.31 | 2.81 |
| avatar-the-way-of-water | 6.00 | 8.51 | 2.51 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.83 | 10.31 |
| the-passion-of-joan-of-arc | 9.80 | 8.38 |
| 2046 | 9.75 | 8.38 |
| sentimental-value | 9.72 | 7.89 |
| chungking-express | 9.59 | 8.59 |
| happy-together | 9.51 | 9.19 |
| under-the-skin | 9.48 | 9.47 |
| portrait-of-a-lady-on-fire | 9.40 | 8.48 |
| train-dreams | 9.22 | 9.77 |
| the-seventh-seal | 9.20 | 10.39 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

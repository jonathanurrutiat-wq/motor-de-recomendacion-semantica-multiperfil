# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-10-19T01:39:22 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 187 (113217 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 129 de 130 en la Verdad Base.
- Evaluadas sin reseñas: nickel-boys.
- Candidatas a recomendar (sin nota de Gemini): 58.
- Modelo de las opciones 7 y 8: reglas en dos etapas, pooling `media`, con frases de reseña (ponderar).

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Las opciones 7 y 8 usan el modelo de reglas; la regresión lineal de las versiones anteriores (y su variante con regularización Ridge) se incluye como comparación.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| **Modelo de reglas (opciones 7 y 8), validación cruzada (5 particiones, promedio de 10 repeticiones)** | 0.718 | 0.946 | 0.310 | 1.041 | 2.454 | 0.405 |
| Regresión lineal anterior, entrenamiento (optimista) | 0.697 | 0.942 | 0.400 | 1.011 | 1.852 | 0.551 |
| Regresión lineal anterior, validación cruzada (5 particiones) | 0.585 | 0.932 | 0.400 | 1.273 | 2.921 | 0.291 |
| Regresión lineal anterior con Ridge, validación cruzada | 0.633 | 0.931 | 0.200 | 1.148 | 2.528 | 0.387 |
| Línea base (promedio) | 0.000 | 0.761 | 0.101 | 1.531 | 4.156 | -0.008 |

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
| gt_afinidad_resistencia_femenina | 1.549 | 0.463 |
| gt_afinidad_contemplación_inmersiva | 1.483 | 0.519 |
| gt_afinidad_ternura_y_empatía_radical | 1.544 | 0.331 |
| gt_afinidad_humanismo_social | 1.428 | 0.346 |
| gt_afinidad_vanguardia_y_simbolismo | 1.275 | 0.519 |
| gt_cols_camaradería_masculina_rancia | 0.804 | 0.272 |
| gt_cols_insoportabilidad_prolongada | 1.868 | 0.263 |
| gt_cols_control_emocional_artificial | 1.754 | 0.475 |
| gt_cols_personajes_diorama | 1.964 | 0.316 |
| gt_cols_caos_asfixiante | 1.686 | 0.353 |
| gt_excepcion_camaradería_masculina_rancia | 0.195 | -0.026 |
| gt_excepcion_insoportabilidad_prolongada | 0.371 | -0.044 |
| gt_excepcion_personajes_diorama | 0.015 | -0.019 |
| gt_excepcion_caos_asfixiante | 0.091 | -0.009 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| percentil 95 por dimensión, hasta 50 reseñas | 384 | 0.738 | 0.017 | 0.015 | 9/10 | 0.953 | 0.410 | 1.027 | -0.002 | 0.013 | 0.415 | 0.431 | 0.254 |
| percentil 75 por dimensión, hasta 50 reseñas | 384 | 0.733 | 0.011 | 0.009 | 9/10 | 0.937 | 0.250 | 1.013 | -0.017 | 0.010 | 0.430 | 0.424 | 0.287 |
| promedio + percentiles de similitud, hasta 100 reseñas | 432 | 0.731 | 0.009 | 0.006 | 9/10 | 0.941 | 0.340 | 1.022 | -0.007 | 0.009 | 0.415 | 0.431 | 0.284 |
| percentil 95 por dimensión, hasta 100 reseñas | 384 | 0.730 | 0.008 | 0.009 | 7/10 | 0.955 | 0.460 | 1.027 | -0.002 | 0.008 | 0.410 | 0.426 | 0.262 |
| promedio, hasta 50 reseñas | 384 | 0.729 | 0.008 | 0.010 | 7/10 | 0.940 | 0.280 | 1.022 | -0.008 | 0.013 | 0.420 | 0.424 | 0.284 |
| promedio + percentiles de similitud, todas las reseñas | 432 | 0.727 | 0.005 | 0.003 | 10/10 | 0.937 | 0.310 | 1.007 | -0.023 | 0.006 | 0.431 | 0.441 | 0.301 |
| promedio, hasta 100 reseñas | 384 | 0.727 | 0.005 | 0.006 | 8/10 | 0.946 | 0.360 | 1.029 | -0.000 | 0.007 | 0.410 | 0.417 | 0.279 |
| percentil 90 por dimensión, hasta 50 reseñas | 384 | 0.726 | 0.005 | 0.013 | 7/10 | 0.946 | 0.360 | 1.035 | 0.005 | 0.017 | 0.400 | 0.415 | 0.265 |
| percentil 75 por dimensión, todas las reseñas | 384 | 0.723 | 0.002 | 0.005 | 6/10 | 0.945 | 0.320 | 1.027 | -0.002 | 0.005 | 0.413 | 0.418 | 0.292 |
| percentil 75 por dimensión, hasta 100 reseñas | 384 | 0.723 | 0.001 | 0.006 | 6/10 | 0.946 | 0.360 | 1.031 | 0.002 | 0.007 | 0.408 | 0.414 | 0.277 |
| promedio + percentiles de similitud, hasta 50 reseñas | 432 | 0.722 | 0.001 | 0.016 | 6/10 | 0.927 | 0.200 | 1.016 | -0.013 | 0.012 | 0.419 | 0.431 | 0.284 |
| promedio, todas las reseñas | 384 | 0.722 | 0.000 | 0.000 | referencia | 0.945 | 0.320 | 1.029 | 0.000 | 0.000 | 0.410 | 0.420 | 0.290 |
| percentil 90 por dimensión, hasta 100 reseñas | 384 | 0.720 | -0.001 | 0.007 | 4/10 | 0.955 | 0.430 | 1.038 | 0.009 | 0.008 | 0.390 | 0.408 | 0.262 |
| percentil 50 por dimensión, hasta 100 reseñas | 384 | 0.719 | -0.002 | 0.006 | 3/10 | 0.943 | 0.320 | 1.037 | 0.008 | 0.007 | 0.402 | 0.410 | 0.275 |
| percentil 50 por dimensión, hasta 50 reseñas | 384 | 0.719 | -0.003 | 0.015 | 5/10 | 0.936 | 0.260 | 1.029 | -0.001 | 0.011 | 0.416 | 0.421 | 0.279 |
| percentil 95 por dimensión, todas las reseñas | 384 | 0.718 | -0.004 | 0.007 | 3/10 | 0.952 | 0.400 | 1.029 | -0.001 | 0.008 | 0.402 | 0.429 | 0.282 |
| percentil 50 por dimensión, todas las reseñas | 384 | 0.716 | -0.005 | 0.005 | 3/10 | 0.942 | 0.290 | 1.035 | 0.006 | 0.005 | 0.404 | 0.413 | 0.286 |
| percentil 90 por dimensión, todas las reseñas | 384 | 0.715 | -0.007 | 0.005 | 1/10 | 0.951 | 0.390 | 1.038 | 0.009 | 0.004 | 0.392 | 0.415 | 0.277 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio (sin frases) | 384 | 0.722 | 0.000 | 0.000 | referencia | 0.945 | 0.320 | 1.029 | 0.000 | 0.000 | 0.410 | 0.420 | 0.290 |
| promedio + descripción (control) | 384-386 | 0.722 | -0.000 | 0.001 | 3/10 | 0.945 | 0.320 | 1.029 | -0.000 | 0.001 | 0.411 | 0.420 | 0.294 |
| promedio + frases de reseña | 384-394 | 0.720 | -0.001 | 0.001 | 1/10 | 0.945 | 0.320 | 1.030 | 0.000 | 0.003 | 0.416 | 0.420 | 0.306 |
| promedio + frases de reseña, ponderadas | 384-394 | 0.718 | -0.004 | 0.006 | 2/10 | 0.946 | 0.310 | 1.041 | 0.012 | 0.011 | 0.405 | 0.420 | 0.315 |
| solo frases de reseña | 8-384 | 0.712 | -0.010 | 0.007 | 2/10 | 0.945 | 0.310 | 1.055 | 0.025 | 0.014 | 0.378 | 0.420 | 0.134 |
| solo descripción (control) | 2-384 | 0.711 | -0.011 | 0.006 | 0/10 | 0.944 | 0.290 | 1.056 | 0.026 | 0.013 | 0.358 | 0.420 | 0.055 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio + descripción (control) | promedio (sin frases) | promedio + frases de reseña | promedio + frases de reseña, ponderadas | solo frases de reseña | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | 0.251 | 0.251 | 0.250 | 0.246 | 0.030 | -0.005 |
| insoportabilidad_prolongada | 0.171 | 0.158 | 0.211 | 0.250 | 0.249 | 0.107 |
| control_emocional_artificial | 0.421 | 0.420 | 0.435 | 0.458 | 0.253 | 0.013 |
| personajes_diorama | 0.306 | 0.306 | 0.303 | 0.290 | 0.117 | 0.153 |
| caos_asfixiante | 0.320 | 0.316 | 0.331 | 0.332 | 0.022 | 0.005 |

## Variables con más peso (regresión lineal anterior)

| variable | peso |
|---|---|
| filtro · Insoportabilidad Prolongada | -0.632 |
| afinidad · Ternura y Empatía Radical | 0.587 |
| filtro · Personajes Diorama | 0.540 |
| Humanismo Social × Insoportabilidad Prolongada | 0.511 |
| afinidad · Vanguardia y Simbolismo | 0.362 |
| afinidad · Resistencia Femenina | 0.356 |
| filtro · Camaradería Masculina Rancia | -0.351 |
| afinidad · Contemplación Inmersiva | 0.278 |
| Humanismo Social × Control Emocional Artificial | 0.261 |
| Ternura y Empatía Radical × Personajes Diorama | -0.224 |

## Películas peor predichas por el modelo de reglas (validación cruzada)

| film_id | nota_gemini | nota_reglas_cv | error_reglas_cv |
|---|---|---|---|
| american-sniper | 2.00 | 7.83 | 5.83 |
| marty-supreme | 2.00 | 6.97 | 4.97 |
| extremely-loud-incredibly-close | 2.00 | 6.70 | 4.70 |
| amelie | 4.50 | 8.93 | 4.43 |
| the-blind-side | 2.50 | 6.55 | 4.05 |
| joker | 2.00 | 6.05 | 4.05 |
| elvis | 2.00 | 5.81 | 3.81 |
| maestro | 3.50 | 7.08 | 3.58 |
| frankenstein | 9.20 | 6.03 | -3.17 |
| the-help | 4.00 | 7.16 | 3.16 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_lineal |
|---|---|---|
| taipei-suicide-story | 9.69 | 10.38 |
| 2046 | 9.48 | 8.58 |
| portrait-of-a-lady-on-fire | 9.40 | 9.83 |
| happy-together | 9.15 | 8.56 |
| chungking-express | 9.12 | 8.57 |
| under-the-skin | 9.07 | 9.36 |
| train-dreams | 9.00 | 10.12 |
| the-secret-agent | 8.93 | 8.11 |
| neon-genesis-evangelion | 8.93 | 8.76 |
| seven-samurai | 8.85 | 8.00 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas (`nota_modelo` es la del modelo de reglas, `nota_lineal` la de la regresión lineal anterior) y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal anterior.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

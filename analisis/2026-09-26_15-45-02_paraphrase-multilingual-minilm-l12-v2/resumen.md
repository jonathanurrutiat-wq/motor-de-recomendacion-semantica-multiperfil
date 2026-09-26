# Análisis del modelo — perfil Ignacio Araya

Generado el 2026-09-26T15:45:02 con el modelo de embeddings `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` y pooling `media` para los modelos principales.

## Datos

- Películas con embeddings: 10 (163 chunks de reseñas).
- Películas para entrenar (con reseñas y nota de Gemini): 2 de 110 en la Verdad Base.
- Evaluadas sin reseñas: 4-months-3-weeks-and-2-days, a-beautiful-day-in-the-neighborhood, a-place-further-than-the-universe, a-woman-under-the-influence, aguirre-the-wrath-of-god, all-quiet-on-the-western, all-we-imagine-as-light, amelie, anne-of-green-gables, arrival, avatar-the-way-of-water, barry-lyndon, beauty-and-the-beast, before-sunset, bicycle-thieves, blade-runner, blue-is-the-warmest-color, certain-women, cha-cha-real-smooth, cleo-from-5-to-7, close-up, close-your-eyes, columbus, coraline, crouching-tiger-hidden-dragon, daisies, disobedience, do-not-expect-too-much-from-the-end-of-the-world, elvis, ema, emma, everything-everywhere-all-at-once, extraordinary-stories, fallen-leaves, frankenstein, ghost-in-the-shell, gueros, hal-harper, happy-go-lucky, her, im-still-here, in-the-mood-for-love, india-song, jurassic-park, kikis-delivery-service, killers-of-the-flower-moon, la-la-land, little-forest-summer-autumn, little-white-dove, love-life, mad-max-fury-road, manhattan, melancholia, memories-of-murder, mississippi-masala, mommy, monos, mulholland-drive, neon-genesis-evangelion-the-end-of-evangelion, nickel-boys, norte-the-end-of-history, oldboy, once-upon-a-time-in-hollywood, oppenheimer, pacifiction, paju, paterson, persona, personal-shopper, poor-things, portrait-of-a-young-girl-at-the-end-of-the-60s-in-brussels, primer, psycho, raise-the-red-lantern, ran, rara, riceboy-sleeps, rocky, secret-sunshine, shoplifters, spring-summer-fall-winter-and-spring, stalker, the-assassination-of-jesse-james-by-the-coward-robert-ford, the-bitter-tears-of-petra-von-kant, the-celebration, the-disciple, the-fabelmans, the-fallout, the-girl-with-the-needle, the-green-ray, the-headless-woman, the-master, the-novelists-film, the-power-of-the-dog, the-royal-tenenbaums, the-souvenir-part-ii, the-testament-of-ann-lee, the-tree-of-life, the-worst-person-in-the-world, tokyo-story, triangle-of-sadness, viola, vivre-sa-vie, werckmeister-harmonies, winter-sleep, woman-in-the-dunes, women-workers-leaving-the-factory, zama.
- Candidatas a recomendar (sin nota de Gemini): 8.
- Variables del modelo: 21.

## Métricas

La validación cruzada mide el error sobre películas que el modelo no vio al entrenar; es la que importa. La línea base predice siempre el promedio: un modelo útil debe tener menos error que ella. Ridge es la misma regresión lineal con regularización; se incluye para comparar, el modelo guardado no la usa.

Para recomendar importa más el orden que el error de la nota, así que la métrica principal es ρ de Spearman: compara el orden de las películas según el modelo con el orden según Gemini (1 = mismo orden, 0 = sin relación). Como complemento, NDCG@10 vale 1 si las 10 primeras según el modelo son las 10 mejores según Gemini y en ese orden, y Precisión@10 es la fracción de esas 10 que están entre las 10 mejores (con empates en el corte entran todas las empatadas). La línea base no ordena: sus valores son los esperados con un orden al azar.

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Entrenamiento (optimista) | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 |
| Validación cruzada (2 particiones) | -1.000 | 0.631 | 1.000 | 2.000 | 4.000 | -3.000 |
| Validación cruzada con Ridge (comparación) | -1.000 | 0.631 | 1.000 | 2.000 | 4.000 | -3.000 |
| Validación cruzada, modelo de reglas en dos etapas | -1.000 | 0.631 | 1.000 | 1.927 | 4.005 | -3.005 |
| Línea base (promedio) | 0.000 | 0.815 | 1.000 | 2.000 | 4.000 | -3.000 |

## Modelo de reglas en dos etapas

Etapa 1: predice el puntaje de cada filtro y afinidad (y si aplica cada excepción) desde las reseñas. Etapa 2: calcula la nota global con la forma de la regla global, con pesos y umbrales aprendidos.

### Reglas aprendidas (modelo final)

Parámetros: etapa 2 (la regla) 16; etapa 1 0 (regresiones Ridge desde el embedding de 384 dimensiones, una por criterio). Regresión lineal actual: 22.

- Nota base = 4.19 + 0.08·Resistencia Femenina + 0.12·Contemplación Inmersiva + 0.16·Ternura y Empatía Radical + 0.09·Humanismo Social + 0.19·Vanguardia y Simbolismo
- Si Insoportabilidad Prolongada supera 5.4 y su excepción no aplica: resta hasta 1.66 puntos.
- Si Control Emocional Artificial supera 8.8 y su excepción no aplica: resta hasta 2.98 puntos.
- Si Personajes Diorama supera 4.0 y su excepción no aplica: resta hasta 0.45 puntos.
- Si Caos Asfixiante supera 0.9 y su excepción no aplica: resta hasta 0.25 puntos.

### Etapa 2 por separado: ¿cuánto de la nota global explican los puntajes de Gemini?

| Evaluación | ρ Spearman | NDCG@10 | Precisión@10 | MAE | MSE | R² |
|---|---|---|---|---|---|---|
| Regla con condiciones | 0.904 | 0.976 | 0.500 | 0.317 | 0.192 | 0.882 |
| Regresión lineal sobre los puntajes | 0.898 | 0.983 | 0.600 | 0.325 | 0.194 | 0.881 |
| Línea base (promedio) | 0.000 | 0.813 | 0.127 | 0.911 | 1.643 | -0.013 |

### Etapa 1: qué tan bien se predice cada puntaje desde las reseñas (validación cruzada)

| criterio | MAE | R² |
|---|---|---|
| gt_afinidad_resistencia_femenina | 3.000 | -3.000 |
| gt_afinidad_contemplación_inmersiva | 4.000 | -3.000 |
| gt_afinidad_ternura_y_empatía_radical | 2.000 | -3.000 |
| gt_afinidad_humanismo_social | 2.000 | -3.000 |
| gt_afinidad_vanguardia_y_simbolismo | 1.000 | -3.000 |
| gt_cols_camaradería_masculina_rancia | 2.000 | -3.000 |
| gt_cols_insoportabilidad_prolongada | 6.000 | -3.000 |
| gt_cols_caos_asfixiante | 5.000 | -3.000 |
| gt_excepcion_caos_asfixiante | 1.000 | -3.000 |

## Comparación de pooling y número de reseñas (modelo de reglas, validación cruzada)

Cómo se resumen los chunks de reseñas de cada película antes de la etapa 1: promedio (el actual), percentil de cada dimensión del embedding, o promedio más los percentiles 50/75/90/máximo de la similitud de los chunks con cada término del perfil. Las reseñas se toman en orden de likes. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con «promedio, todas las reseñas» en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), y «mejora ρ» cuenta en cuántas repeticiones superó a esa referencia.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio, hasta 50 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio, hasta 100 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio, todas las reseñas | 384 | -1.000 | 0.000 | 0.000 | referencia | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 50 por dimensión, hasta 50 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 50 por dimensión, hasta 100 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 50 por dimensión, todas las reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 75 por dimensión, hasta 50 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 75 por dimensión, hasta 100 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 75 por dimensión, todas las reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 90 por dimensión, hasta 50 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 90 por dimensión, hasta 100 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 90 por dimensión, todas las reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 95 por dimensión, hasta 50 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 95 por dimensión, hasta 100 reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| percentil 95 por dimensión, todas las reseñas | 384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio + percentiles de similitud, hasta 50 reseñas | 432 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio + percentiles de similitud, hasta 100 reseñas | 432 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio + percentiles de similitud, todas las reseñas | 432 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |

## Frases de reseña (modelo de reglas, validación cruzada)

Para los criterios con frases_resenia, la etapa 1 recibe además (o en vez del embedding promedio) la fracción de chunks de cada película muy similares a cada frase (sobre el percentil 95 de todos los chunks) y el percentil 90 de esa similitud. Los controles usan lo mismo pero solo con la descripción del perfil. Promedios de 10 repeticiones con particiones distintas; los Δ son la diferencia con el modelo sin frases en las mismas particiones (ρ: positiva = mejor; MAE: negativa = mejor), su desviación indica cuánto varían entre repeticiones y «mejora ρ» cuenta en cuántas repeticiones superó al modelo sin frases.

| representacion | dimensiones | ρ Spearman | Δ ρ | desv. Δ ρ | mejora ρ | NDCG@10 | Precisión@10 | MAE | Δ MAE | desv. Δ MAE | R² | R² etapa 1 afinidades | R² etapa 1 filtros |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| promedio (sin frases) | 384 | -1.000 | 0.000 | 0.000 | referencia | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio + frases de reseña | 384-394 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio + frases de reseña, ponderadas | 384-394 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| solo frases de reseña | 8-384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| promedio + descripción (control) | 384-386 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |
| solo descripción (control) | 2-384 | -1.000 | 0.000 | 0.000 | 0/10 | 0.631 | 1.000 | 1.927 | 0.000 | 0.000 | -3.005 | -3.000 | -3.000 |

R² de la etapa 1 de cada criterio con frases:

| criterio | promedio (sin frases) | promedio + frases de reseña | promedio + frases de reseña, ponderadas | solo frases de reseña | promedio + descripción (control) | solo descripción (control) |
|---|---|---|---|---|---|---|
| camaradería_masculina_rancia | -3.000 | -3.000 | -3.000 | -3.000 | -3.000 | -3.000 |
| insoportabilidad_prolongada | -3.000 | -3.000 | -3.000 | -3.000 | -3.000 | -3.000 |
| caos_asfixiante | -3.000 | -3.000 | -3.000 | -3.000 | -3.000 | -3.000 |

## Variables con más peso (regresión lineal)

| variable | peso |
|---|---|
| filtro · Camaradería Masculina Rancia | 0.083 |
| filtro · Insoportabilidad Prolongada | -0.083 |
| filtro · Control Emocional Artificial | 0.083 |
| filtro · Personajes Diorama | 0.083 |
| filtro · Caos Asfixiante | 0.083 |
| afinidad · Resistencia Femenina | 0.083 |
| afinidad · Contemplación Inmersiva | 0.083 |
| afinidad · Ternura y Empatía Radical | -0.083 |
| afinidad · Humanismo Social | 0.083 |
| afinidad · Vanguardia y Simbolismo | 0.083 |

## Películas peor predichas (validación cruzada)

| film_id | nota_gemini | nota_modelo_cv | error_cv |
|---|---|---|---|
| sinners | 7.50 | 5.50 | -2.00 |
| marty-supreme | 5.50 | 7.50 | 2.00 |

## Mejores candidatas a recomendar

| film_id | nota_modelo | nota_reglas |
|---|---|---|
| the-secret-agent | 8.30 | 7.59 |
| weapons | 7.46 | 7.59 |
| it-was-just-an-accident | 7.29 | 7.59 |
| one-battle-after-another | 6.68 | 7.59 |
| sorry-baby | 6.54 | 7.59 |
| train-dreams | 6.16 | 7.59 |
| hamnet | 5.72 | 7.59 |
| sentimental-value | 4.04 | 7.59 |

## Archivos

- `peliculas.csv`: una fila por película, con sus similitudes con cada término del perfil, los puntajes que predice el modelo de reglas, notas y errores.
- `pesos.csv`: peso de cada variable de la regresión lineal.
- `reglas.json`: reglas y parámetros aprendidos por el modelo de reglas, con sus métricas.
- `pooling.csv`: comparación de formas de resumir las reseñas y de cuántas usar.
- `frases_resenia.csv` y `frases_resenia_por_criterio.csv`: comparación con y sin las frases de reseña del perfil.
- `similitud_perfil.csv`: similitud entre los términos del perfil (valores altos entre un filtro y una afinidad indican que el modelo los confunde).
- `ranking.csv`: ranking completo de recomendaciones.
- `resumen.json`: estos datos en formato legible por programas.

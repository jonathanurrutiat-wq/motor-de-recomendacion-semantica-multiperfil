# Instrucciones de evaluación — perfil Valentina Soto

Evalúa cada película según el perfil cinéfilo descrito abajo. El objetivo es predecir cómo resonaría la obra con esta sensibilidad específica, no producir crítica objetiva.

## Procedimiento

1. Investiga la película: sinopsis, dirección, tono, ritmo, estructura narrativa y tratamiento de los personajes.
2. Detecta primero qué filtros restrictivos aplican y si opera su excepción. Recién después razona cada afinidad.
3. Asigna los puntajes solo al final del análisis.
4. Calcula la nota global con la regla global del perfil (no es un promedio).

## Filtros restrictivos

Puntaje de 0 a 10 según qué tan presente está el filtro en la película (0 = ausente, 10 = domina la película).

### Humor a Costa de Otros
Comedia que se ríe de la humillación, el cuerpo, la pobreza o la discapacidad de personajes vulnerables, sin ironía ni mirada crítica. La burla es el chiste.
- Corrompe: Calidez Cómica, Sátira Social.
- Excepción: El humor apunta hacia arriba (poder, privilegio, hipocresía) o el propio personaje que sufre la burla la domina y la película lo trata con cariño.

### Fórmula Reciclada
Chistes y estructuras vistos cientos de veces. Comedia romántica o de equipo que sigue la plantilla sin sorpresas y trata al espectador como si no hubiera visto nada antes.
- Corrompe: Absurdo Inteligente, Ingenio Verbal.

### Sentimentalismo Forzado
Giros melodramáticos, música lacrimógena y discursos morales al final que interrumpen la comedia para decir cómo sentir, sin que la película se los haya ganado.
- Corrompe: Calidez Cómica, Timing y Química Actoral.

### Improvisación Sin Estructura
Escenas que se alargan con improvisaciones que no avanzan nada, donde los actores se ríen de sus propios chistes y la película pierde forma y dirección.
- Corrompe: Timing y Química Actoral, Sátira Social.

### Referencias Vacías
Humor que consiste solo en nombrar cultura pop o memes del momento, sin ingenio propio. El chiste es reconocer la referencia, no lo que se dice sobre ella.
- Corrompe: Ingenio Verbal.

## Afinidades

Puntaje de 0 a 10 según qué tan bien la película realiza ese valor, no según cuánto lo intenta. Un puntaje bajo en una afinidad que no es el terreno de la película no es un castigo: solo indica menor relevancia.

### Ingenio Verbal
Diálogo afilado y rápido. Juegos de palabras, réplicas memorables y una escritura donde el chiste nace de la inteligencia de los personajes y no del esfuerzo por ser gracioso.

### Absurdo Inteligente
Comedia que construye lógica interna en situaciones disparatadas. El absurdo tiene reglas, escala con precisión y sorprende sin perder coherencia.

### Calidez Cómica
Comedia que quiere a sus personajes. Se ríe con ellos de sus defectos, hay ternura entre las bromas y el humor nace de la humanidad, no de la burla.

### Sátira Social
Humor con puntería. Se burla del poder, la hipocresía, las clases sociales o las costumbres con ironía e inteligencia, y deja una incomodidad útil después de la risa.

### Timing y Química Actoral
Precisión de los intérpretes. Pausas, miradas y reacciones exactas, y duplas o elencos cuya química hace funcionar el chiste incluso cuando el guion es simple.

## Regla de puntaje global

- La nota global NO es un promedio de los puntajes.
- Si Ingenio Verbal llega a 9-10 (diálogo afilado donde el chiste nace de la inteligencia de los personajes), la nota global debe quedar alta (mínimo 7.5-8.0), aunque la trama sea convencional o la película sea modesta en lo formal.
- Si aplica Humor a Costa de Otros (veto absoluto) sin que opere su excepción (el humor apunta hacia arriba, hacia el poder, el privilegio o la hipocresía, o quien recibe la burla la domina y la película lo trata con cariño), la nota global puede desplomarse aunque la película sea muy ingeniosa. Fórmula Reciclada y Sentimentalismo Forzado (intermedios) restan de forma moderada; Improvisación Sin Estructura y Referencias Vacías, de forma leve.
- En el resto de los casos, ponderar cualitativamente: las afinidades donde la película juega pesan más que las que le son ajenas, y a igualdad pesan más Ingenio Verbal (10), luego Absurdo Inteligente y Calidez Cómica (9), y Sátira Social y Timing y Química Actoral (8).

## Formato de respuesta

Responde solo con un CSV (separado por comas, punto como decimal) con exactamente este encabezado:

```
film_id,gt_cols_humor_a_costa_de_otros,gt_excepcion_humor_a_costa_de_otros,gt_cols_fórmula_reciclada,gt_excepcion_fórmula_reciclada,gt_cols_sentimentalismo_forzado,gt_excepcion_sentimentalismo_forzado,gt_cols_improvisación_sin_estructura,gt_excepcion_improvisación_sin_estructura,gt_cols_referencias_vacías,gt_excepcion_referencias_vacías,gt_afinidad_ingenio_verbal,gt_afinidad_absurdo_inteligente,gt_afinidad_calidez_cómica,gt_afinidad_sátira_social,gt_afinidad_timing_y_química_actoral,gt_nota_global
```

Significado de las columnas:

- `gt_cols_humor_a_costa_de_otros`: puntaje del filtro Humor a Costa de Otros (0-10).
- `gt_excepcion_humor_a_costa_de_otros`: 1 si el filtro está presente pero su excepción (descrita arriba) lo neutraliza, 0 si no.
- `gt_cols_fórmula_reciclada`: puntaje del filtro Fórmula Reciclada (0-10).
- `gt_excepcion_fórmula_reciclada`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_sentimentalismo_forzado`: puntaje del filtro Sentimentalismo Forzado (0-10).
- `gt_excepcion_sentimentalismo_forzado`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_improvisación_sin_estructura`: puntaje del filtro Improvisación Sin Estructura (0-10).
- `gt_excepcion_improvisación_sin_estructura`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_referencias_vacías`: puntaje del filtro Referencias Vacías (0-10).
- `gt_excepcion_referencias_vacías`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_afinidad_ingenio_verbal`: puntaje de la afinidad Ingenio Verbal (0-10).
- `gt_afinidad_absurdo_inteligente`: puntaje de la afinidad Absurdo Inteligente (0-10).
- `gt_afinidad_calidez_cómica`: puntaje de la afinidad Calidez Cómica (0-10).
- `gt_afinidad_sátira_social`: puntaje de la afinidad Sátira Social (0-10).
- `gt_afinidad_timing_y_química_actoral`: puntaje de la afinidad Timing y Química Actoral (0-10).
- `gt_nota_global`: nota global (0-10) según la regla global.

## Películas a evaluar

Evalúa estas 130 películas, una fila por cada una. Copia el `film_id` tal cual aparece aquí (cuando termina en año, es para distinguir películas homónimas).

### Tanda 1 (películas 1-20)

- in-the-mood-for-love
- kikis-delivery-service
- persona
- close-up
- memories-of-murder
- stalker
- a-woman-under-the-influence
- barry-lyndon
- before-sunset
- mommy-2014
- the-celebration
- shoplifters
- happy-go-lucky
- portrait-of-a-young-girl-at-the-end-of-the-60s-in-brussels
- mulholland-drive
- 4-months-3-weeks-and-2-days
- tokyo-story
- poor-things-2023
- emma-2020
- cleo-from-5-to-7

### Tanda 2 (películas 21-40)

- the-power-of-the-dog
- the-bitter-tears-of-petra-von-kant
- blue-is-the-warmest-color
- the-headless-woman
- india-song
- vivre-sa-vie
- certain-women
- raise-the-red-lantern
- daisies
- arrival-2016
- mad-max-fury-road
- ghost-in-the-shell
- the-worst-person-in-the-world
- killers-of-the-flower-moon
- her
- beauty-and-the-beast-1991
- primer
- little-white-dove
- once-upon-a-time-in-hollywood
- oldboy

### Tanda 3 (películas 41-60)

- the-souvenir-part-ii
- the-fallout
- disobedience-2017
- ema
- rara
- zama
- amelie
- the-assassination-of-jesse-james-by-the-coward-robert-ford
- columbus-2017
- little-forest-summer-autumn
- the-novelists-film
- spring-summer-fall-winter-and-spring
- close-your-eyes-2023
- manhattan
- aguirre-the-wrath-of-god
- melancholia
- paterson
- personal-shopper
- the-green-ray
- the-tree-of-life-2011

### Tanda 4 (películas 61-80)

- ran
- the-disciple-2020
- do-not-expect-too-much-from-the-end-of-the-world
- extraordinary-stories
- pacifiction
- werckmeister-harmonies
- winter-sleep
- viola
- la-la-land
- cha-cha-real-smooth
- coraline
- jurassic-park
- blade-runner-2049
- the-royal-tenenbaums
- triangle-of-sadness
- rocky
- crouching-tiger-hidden-dragon
- psycho
- the-master-2012
- neon-genesis-evangelion-the-end-of-evangelion

### Tanda 5 (películas 81-100)

- secret-sunshine
- bicycle-thieves
- fallen-leaves-2023
- a-beautiful-day-in-the-neighborhood
- woman-in-the-dunes
- paju
- all-we-imagine-as-light
- gueros
- anne-of-green-gables-1979
- monos
- norte-the-end-of-history
- women-workers-leaving-the-factory
- the-girl-with-the-needle
- sinners-2025
- hal-harper
- riceboy-sleeps
- the-testament-of-ann-lee
- mississippi-masala
- a-place-further-than-the-universe
- love-life-2022

### Tanda 6 (películas 101-120)

- marty-supreme
- frankenstein-2025
- im-still-here-2024
- nickel-boys
- oppenheimer-2023
- avatar-the-way-of-water
- all-quiet-on-the-western-front-2022
- the-fabelmans
- elvis-2022
- everything-everywhere-all-at-once
- toy-story-3
- dunkirk-2017
- hidden-figures
- 1917
- inception
- black-panther
- avatar
- lincoln
- the-theory-of-everything-2014
- war-horse

### Tanda 7 (películas 121-130)

- the-imitation-game
- the-help
- green-book
- maestro-2023
- les-miserables-2012
- bohemian-rhapsody
- the-blind-side
- joker-2019
- american-sniper
- extremely-loud-incredibly-close

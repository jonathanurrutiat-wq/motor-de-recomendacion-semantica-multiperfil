# Instrucciones de evaluación — perfil Matías Fuentes

Evalúa cada película según el perfil cinéfilo descrito abajo. El objetivo es predecir cómo resonaría la obra con esta sensibilidad específica, no producir crítica objetiva.

## Procedimiento

1. Investiga la película: sinopsis, dirección, tono, ritmo, estructura narrativa y tratamiento de los personajes.
2. Detecta primero qué filtros restrictivos aplican y si opera su excepción. Recién después razona cada afinidad.
3. Asigna los puntajes solo al final del análisis.
4. Calcula la nota global con la regla global del perfil (no es un promedio).

## Filtros restrictivos

Puntaje de 0 a 10 según qué tan presente está el filtro en la película (0 = ausente, 10 = domina la película).

### Acción Digital Sin Peso
Secuencias dominadas por CGI evidente, donde los cuerpos no pesan, nada tiene consecuencias físicas y el espectáculo se siente como una animación sin gravedad.
- Corrompe: Coreografía de Acción Física, Catarsis Heroica.
- Excepción: La película es abiertamente animada o estilizada, y su artificio digital es una decisión estética coherente que mantiene el riesgo y el peso dramático de cada escena.

### Montaje Ilegible
Cámara temblorosa y cortes tan rápidos que el espectador no entiende quién golpea a quién ni dónde ocurre la escena. El caos oculta la falta de coreografía.
- Corrompe: Coreografía de Acción Física, Ritmo Cinético.

### Cinismo Autoparódico
Película que se burla de su propio género con chistes constantes y guiños al espectador, y rompe la tensión cada vez que algo importante está por ocurrir.
- Corrompe: Catarsis Heroica, Mundo Inmersivo y Épico.

### Villano Sin Amenaza
Antagonistas planos, caricaturescos o sin motivación creíble, que nunca representan un peligro real para el héroe y hacen que el conflicto carezca de tensión.
- Corrompe: Catarsis Heroica.

### Exposición Verbosa
Tramas sobrecargadas de diálogo explicativo, reglas del universo repetidas y escenas de reunión que frenan la acción para justificar una historia innecesariamente compleja.
- Corrompe: Ritmo Cinético.

## Afinidades

Puntaje de 0 a 10 según qué tan bien la película realiza ese valor, no según cuánto lo intenta. Un puntaje bajo en una afinidad que no es el terreno de la película no es un castigo: solo indica menor relevancia.

### Coreografía de Acción Física
Peleas, persecuciones y acrobacias construidas con cuerpos reales y planos legibles. Cada golpe tiene peso, el espacio se entiende y el talento físico de los intérpretes es protagonista.

### Ritmo Cinético
Energía narrativa constante. La película avanza con escenas eficientes, sin relleno, y alterna clímax y respiro con precisión para mantener la adrenalina.

### Catarsis Heroica
Satisfacción emocional del héroe que se levanta, sacrifica algo y vence. Momentos de triunfo ganados con esfuerzo, que provocan ganas de aplaudir.

### Mundo Inmersivo y Épico
Escala y construcción de mundo. Escenarios memorables, reglas coherentes, banda sonora que eleva el espectáculo y la sensación de estar dentro de una aventura grande.

### Carisma y Química de Reparto
Protagonistas con presencia magnética y duplas o equipos con química genuina, cuyas bromas, lealtades y rivalidades hacen disfrutable la película entre escenas de acción.

## Regla de puntaje global

- La nota global NO es un promedio de los puntajes.
- Si Coreografía de Acción Física llega a 9-10 (cuerpos reales, planos legibles y peso en cada golpe), la nota global debe quedar alta (mínimo 7.5-8.0), aunque la historia sea simple o los personajes poco memorables.
- Si aplica Acción Digital Sin Peso (sin que opere su excepción) o Montaje Ilegible, ambos de veto absoluto, la nota global puede desplomarse aunque la película tenga gran escala o un elenco carismático. Los filtros intermedios (Cinismo Autoparódico, Villano Sin Amenaza) restan de forma moderada y Exposición Verbosa, de forma leve.
- En el resto de los casos, ponderar cualitativamente: las afinidades donde la película juega pesan más que las que le son ajenas, y a igualdad pesan más Coreografía de Acción Física (10), luego Ritmo Cinético y Catarsis Heroica (9), Mundo Inmersivo y Épico (8) y Carisma y Química de Reparto (7).

## Formato de respuesta

Responde solo con un CSV (separado por comas, punto como decimal) con exactamente este encabezado:

```
film_id,gt_cols_acción_digital_sin_peso,gt_excepcion_acción_digital_sin_peso,gt_cols_montaje_ilegible,gt_excepcion_montaje_ilegible,gt_cols_cinismo_autoparódico,gt_excepcion_cinismo_autoparódico,gt_cols_villano_sin_amenaza,gt_excepcion_villano_sin_amenaza,gt_cols_exposición_verbosa,gt_excepcion_exposición_verbosa,gt_afinidad_coreografía_de_acción_física,gt_afinidad_ritmo_cinético,gt_afinidad_catarsis_heroica,gt_afinidad_mundo_inmersivo_y_épico,gt_afinidad_carisma_y_química_de_reparto,gt_nota_global
```

Significado de las columnas:

- `gt_cols_acción_digital_sin_peso`: puntaje del filtro Acción Digital Sin Peso (0-10).
- `gt_excepcion_acción_digital_sin_peso`: 1 si el filtro está presente pero su excepción (descrita arriba) lo neutraliza, 0 si no.
- `gt_cols_montaje_ilegible`: puntaje del filtro Montaje Ilegible (0-10).
- `gt_excepcion_montaje_ilegible`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_cinismo_autoparódico`: puntaje del filtro Cinismo Autoparódico (0-10).
- `gt_excepcion_cinismo_autoparódico`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_villano_sin_amenaza`: puntaje del filtro Villano Sin Amenaza (0-10).
- `gt_excepcion_villano_sin_amenaza`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_exposición_verbosa`: puntaje del filtro Exposición Verbosa (0-10).
- `gt_excepcion_exposición_verbosa`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_afinidad_coreografía_de_acción_física`: puntaje de la afinidad Coreografía de Acción Física (0-10).
- `gt_afinidad_ritmo_cinético`: puntaje de la afinidad Ritmo Cinético (0-10).
- `gt_afinidad_catarsis_heroica`: puntaje de la afinidad Catarsis Heroica (0-10).
- `gt_afinidad_mundo_inmersivo_y_épico`: puntaje de la afinidad Mundo Inmersivo y Épico (0-10).
- `gt_afinidad_carisma_y_química_de_reparto`: puntaje de la afinidad Carisma y Química de Reparto (0-10).
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

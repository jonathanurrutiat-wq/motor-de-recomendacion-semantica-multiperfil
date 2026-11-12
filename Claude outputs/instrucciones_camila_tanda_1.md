# Instrucciones de evaluación — perfil Camila Rojas

Evalúa cada película según el perfil cinéfilo descrito abajo. El objetivo es predecir cómo resonaría la obra con esta sensibilidad específica, no producir crítica objetiva.

## Procedimiento

1. Investiga la película: sinopsis, dirección, tono, ritmo, estructura narrativa y tratamiento de los personajes.
2. Detecta primero qué filtros restrictivos aplican y si opera su excepción. Recién después razona cada afinidad.
3. Asigna los puntajes solo al final del análisis.
4. Calcula la nota global con la regla global del perfil (no es un promedio).

## Filtros restrictivos

Puntaje de 0 a 10 según qué tan presente está el filtro en la película (0 = ausente, 10 = domina la película).

### Sustos Baratos
Terror basado en ruidos fuertes repentinos y apariciones sin construcción previa. El susto reemplaza a la atmósfera y se repite como truco hasta agotar la tensión.
- Corrompe: Atmósfera y Dread, Tensión Sostenida.
- Excepción: El susto aparece como cierre de una tensión larga y bien construida, y la película no depende de él como recurso principal.

### Violencia Explotadora
Película que disfruta el sufrimiento de mujeres o personajes vulnerables, lo encuadra para el goce del espectador y usa el abuso como espectáculo sin mirada crítica.
- Corrompe: Subtexto Social.
- Excepción: La película condena claramente la violencia y se centra en la perspectiva y la resistencia de la víctima, sin erotizar ni regodearse en el daño.

### Gore Gratuito
Violencia gráfica sin función narrativa ni simbólica, que busca el asco o el shock por sí misma y reemplaza la sugestión y el miedo psicológico.
- Corrompe: Horror Psicológico, Atmósfera y Dread.

### Personajes Tontos por Guion
Personajes que toman decisiones absurdas solo para que el miedo ocurra: separarse, entrar al sótano, ignorar las señales evidentes. La amenaza funciona porque ellos se vuelven incompetentes.
- Corrompe: Tensión Sostenida, Horror Psicológico.

### Explicación Excesiva del Misterio
Cierre que explica todo con un monólogo o un flashback, elimina la ambigüedad y convierte lo inquietante en una solución lógica que apaga el miedo.
- Corrompe: Atmósfera y Dread, Horror Psicológico.

## Afinidades

Puntaje de 0 a 10 según qué tan bien la película realiza ese valor, no según cuánto lo intenta. Un puntaje bajo en una afinidad que no es el terreno de la película no es un castigo: solo indica menor relevancia.

### Atmósfera y Dread
Miedo que nace del ambiente. Silencios, espacios inquietantes, iluminación y ritmo lento que instalan una amenaza constante antes de que ocurra algo.

### Tensión Sostenida
Suspenso que no afloja. Cada escena aprieta un poco más, el espectador anticipa lo peor y la película controla cuándo soltar la presión.

### Horror Psicológico
Miedo interior. Paranoia, percepción poco fiable, culpa y descomposición mental que desorientan al espectador y hacen dudar de lo que es real.

### Subtexto Social
Terror con algo que decir. El monstruo o la amenaza simboliza duelo, clase, raza, género o trauma, y la lectura simbólica profundiza el miedo.

### Diseño Sonoro y Visual Perturbador
Imágenes y sonidos que se quedan en la cabeza. Encuadres extraños, criaturas o efectos prácticos memorables y una banda sonora que inquieta en lugar de subrayar.

## Regla de puntaje global

- La nota global NO es un promedio de los puntajes.
- Si Atmósfera y Dread llega a 9-10 (miedo que nace del ambiente: silencios, espacios inquietantes y ritmo lento que instalan una amenaza constante), la nota global debe quedar alta (mínimo 7.5-8.0), aunque la historia sea simple o el cierre poco memorable.
- Si aplica Sustos Baratos o Violencia Explotadora, ambos de veto absoluto, y no opera su excepción (que el susto cierre una tensión larga y bien construida, o que la película condene la violencia y se centre en la resistencia de la víctima), la nota global puede desplomarse aunque tenga un diseño sonoro y visual notable. Gore Gratuito y Personajes Tontos por Guion (intermedios) restan de forma moderada; Explicación Excesiva del Misterio, de forma leve.
- En el resto de los casos, ponderar cualitativamente: las afinidades donde la película juega pesan más que las que le son ajenas, y a igualdad pesan más Atmósfera y Dread (10), luego Tensión Sostenida y Horror Psicológico (9), Subtexto Social (8) y Diseño Sonoro y Visual Perturbador (7).

## Formato de respuesta

Responde solo con un CSV (separado por comas, punto como decimal) con exactamente este encabezado:

```
film_id,gt_cols_sustos_baratos,gt_excepcion_sustos_baratos,gt_cols_violencia_explotadora,gt_excepcion_violencia_explotadora,gt_cols_gore_gratuito,gt_excepcion_gore_gratuito,gt_cols_personajes_tontos_por_guion,gt_excepcion_personajes_tontos_por_guion,gt_cols_explicación_excesiva_del_misterio,gt_excepcion_explicación_excesiva_del_misterio,gt_afinidad_atmósfera_y_dread,gt_afinidad_tensión_sostenida,gt_afinidad_horror_psicológico,gt_afinidad_subtexto_social,gt_afinidad_diseño_sonoro_y_visual_perturbador,gt_nota_global
```

Significado de las columnas:

- `gt_cols_sustos_baratos`: puntaje del filtro Sustos Baratos (0-10).
- `gt_excepcion_sustos_baratos`: 1 si el filtro está presente pero su excepción (descrita arriba) lo neutraliza, 0 si no.
- `gt_cols_violencia_explotadora`: puntaje del filtro Violencia Explotadora (0-10).
- `gt_excepcion_violencia_explotadora`: 1 si el filtro está presente pero su excepción (descrita arriba) lo neutraliza, 0 si no.
- `gt_cols_gore_gratuito`: puntaje del filtro Gore Gratuito (0-10).
- `gt_excepcion_gore_gratuito`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_personajes_tontos_por_guion`: puntaje del filtro Personajes Tontos por Guion (0-10).
- `gt_excepcion_personajes_tontos_por_guion`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_explicación_excesiva_del_misterio`: puntaje del filtro Explicación Excesiva del Misterio (0-10).
- `gt_excepcion_explicación_excesiva_del_misterio`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_afinidad_atmósfera_y_dread`: puntaje de la afinidad Atmósfera y Dread (0-10).
- `gt_afinidad_tensión_sostenida`: puntaje de la afinidad Tensión Sostenida (0-10).
- `gt_afinidad_horror_psicológico`: puntaje de la afinidad Horror Psicológico (0-10).
- `gt_afinidad_subtexto_social`: puntaje de la afinidad Subtexto Social (0-10).
- `gt_afinidad_diseño_sonoro_y_visual_perturbador`: puntaje de la afinidad Diseño Sonoro y Visual Perturbador (0-10).
- `gt_nota_global`: nota global (0-10) según la regla global.

## Películas a evaluar

- 12-angry-men
- 21-jump-street
- 6-underground
- american-pie
- amores-perros
- amour
- asteroid-city
- babylon
- belfast
- black-swan
- city-of-god
- clueless
- coda
- crash
- dead-poets-society
- fifty-shades-of-grey
- fight-club
- get-out
- goodfellas
- grave-of-the-fireflies

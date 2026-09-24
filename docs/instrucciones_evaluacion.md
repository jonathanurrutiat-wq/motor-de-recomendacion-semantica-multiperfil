# Instrucciones de evaluación — perfil Ignacio Araya

Evalúa cada película según el perfil cinéfilo descrito abajo. El objetivo es predecir cómo resonaría la obra con esta sensibilidad específica, no producir crítica objetiva.

## Procedimiento

1. Investiga la película: sinopsis, dirección, tono, ritmo, estructura narrativa y tratamiento de los personajes.
2. Detecta primero qué filtros restrictivos aplican y si opera su excepción. Recién después razona cada afinidad.
3. Asigna los puntajes solo al final del análisis.
4. Calcula la nota global con la regla global del perfil (no es un promedio).

## Filtros restrictivos

Puntaje de 0 a 10 según qué tan presente está el filtro en la película (0 = ausente, 10 = domina la película).

### Camaradería Masculina Rancia
Dinámicas que validan el sexismo desde el cinismo o la burla, donde la mujer es un trofeo o un chiste.
- Corrompe: Resistencia Femenina.
- Excepción: La protección masculina o la nostalgia, cuando la mirada de la película hacia el personaje femenino está construida desde la reverencia, el amor o la inocencia.

### Insoportabilidad Prolongada
Obligar al espectador a convivir excesivamente con personajes arrogantes, crueles o de una superioridad moral sofocante.
- Corrompe: Ternura y Empatía Radical, Humanismo Social.
- Excepción: El personaje sufre un desarme temprano y su ego es bajado a tierra rápidamente. La película combina alta contemplación inmersiva y empatía radical para hacernos entender que la toxicidad nace de un trauma o abuso sistémico.

### Control Emocional Artificial
Perfección técnica fría, música manipuladora y montaje que clausura el temblor humano para dictar exactamente qué debes sentir.
- Corrompe: Humanismo Social, Contemplación Inmersiva.

### Personajes Diorama
Estética de vitrina. Cuadros visualmente hermosos y simétricos, habitados por personajes fríos y decorativos, distantes como figuras de museo.
- Corrompe: Ternura y Empatía Radical.

### Caos Asfixiante
Caos hiperactivo, montaje frenético y una narrativa atropellada que entrega todas las respuestas masticadas.
- Corrompe: Contemplación Inmersiva.

## Afinidades

Puntaje de 0 a 10 según qué tan bien la película realiza ese valor, no según cuánto lo intenta. Un puntaje bajo en una afinidad que no es el terreno de la película no es un castigo: solo indica menor relevancia.

### Resistencia Femenina
Agencia y dignidad en la adversidad. Mujeres complejas, redes de apoyo, respuesta activa frente a injusticias, o la valentía de elegir el amor, la vulnerabilidad y el cuidado dentro de entornos hostiles o trágicos.

### Contemplación Inmersiva
La 'calma aterradora'. Ritmo paciente que da oxígeno para procesar conflictos y tragedias. El tiempo y el espacio narrativo respiran.

### Ternura y Empatía Radical
La ética del cuidado. Empatía radical hacia lo roto, gestos mínimos, compasión genuina por las fallas humanas. Mirada sincera y afectuosa.

### Humanismo Social
Retrato crudo de la realidad. Naturalismo ético, comprensión del origen de la marginalidad, el trauma o la clase, observando a los afectados con respeto, cercanía y horizontalidad.

### Vanguardia y Simbolismo
Riesgo y forma cinematográfica. Narrativas abiertas, pensamiento visual, significado que nace del desvío, la contradicción y la búsqueda de formas propias y arriesgadas.

## Regla de puntaje global

- La nota global NO es un promedio de los puntajes.
- Si Resistencia Femenina llega a 9-10 (agencia, dignidad y complejidad), la nota global debe quedar alta (mínimo 7.5-8.0), aunque la película sea comercial o poco arriesgada formalmente.
- Si aplica un filtro restrictivo sin que opere su excepción (sobre todo Camaradería Masculina Rancia, Insoportabilidad Prolongada, o una toxicidad enmarcada en Caos Asfixiante), la nota global puede desplomarse aunque la película tenga grandes virtudes formales.

## Formato de respuesta

Responde solo con un CSV (separado por comas, punto como decimal) con exactamente este encabezado:

```
film_id,gt_cols_camaradería_masculina_rancia,gt_excepcion_camaradería_masculina_rancia,gt_cols_insoportabilidad_prolongada,gt_excepcion_insoportabilidad_prolongada,gt_cols_control_emocional_artificial,gt_excepcion_control_emocional_artificial,gt_cols_personajes_diorama,gt_excepcion_personajes_diorama,gt_cols_caos_asfixiante,gt_excepcion_caos_asfixiante,gt_afinidad_resistencia_femenina,gt_afinidad_contemplación_inmersiva,gt_afinidad_ternura_y_empatía_radical,gt_afinidad_humanismo_social,gt_afinidad_vanguardia_y_simbolismo,gt_nota_global
```

Significado de las columnas:

- `gt_cols_camaradería_masculina_rancia`: puntaje del filtro Camaradería Masculina Rancia (0-10).
- `gt_excepcion_camaradería_masculina_rancia`: 1 si el filtro está presente pero su excepción (descrita arriba) lo neutraliza, 0 si no.
- `gt_cols_insoportabilidad_prolongada`: puntaje del filtro Insoportabilidad Prolongada (0-10).
- `gt_excepcion_insoportabilidad_prolongada`: 1 si el filtro está presente pero su excepción (descrita arriba) lo neutraliza, 0 si no.
- `gt_cols_control_emocional_artificial`: puntaje del filtro Control Emocional Artificial (0-10).
- `gt_excepcion_control_emocional_artificial`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_personajes_diorama`: puntaje del filtro Personajes Diorama (0-10).
- `gt_excepcion_personajes_diorama`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_cols_caos_asfixiante`: puntaje del filtro Caos Asfixiante (0-10).
- `gt_excepcion_caos_asfixiante`: 1 si el filtro está presente pero algo en la película lo neutraliza (este filtro no tiene una excepción definida), 0 si no.
- `gt_afinidad_resistencia_femenina`: puntaje de la afinidad Resistencia Femenina (0-10).
- `gt_afinidad_contemplación_inmersiva`: puntaje de la afinidad Contemplación Inmersiva (0-10).
- `gt_afinidad_ternura_y_empatía_radical`: puntaje de la afinidad Ternura y Empatía Radical (0-10).
- `gt_afinidad_humanismo_social`: puntaje de la afinidad Humanismo Social (0-10).
- `gt_afinidad_vanguardia_y_simbolismo`: puntaje de la afinidad Vanguardia y Simbolismo (0-10).
- `gt_nota_global`: nota global (0-10) según la regla global.

## Películas a evaluar

[Lista de film_id a evaluar]

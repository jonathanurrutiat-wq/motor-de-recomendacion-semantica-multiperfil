<h1 align="center">Motor de Recomendación Semántica Multiperfil</h1>

<img src="https://img.shields.io/badge/version-1.0.0-blue" alt="version">

[![Last Commit](https://img.shields.io/github/last-commit/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/main-dev?style=flat-square&logo=github&color=blue&cache_bust=1)](https://github.com/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/tree/main-dev)

## **Premisa**
### "motor-de-recomendacion-semantica-multiperfil"


Este proyecto consiste en el desarrollo de un sistema híbrido de recomendación cinematográfica diseñado para superar las limitaciones de los algoritmos de filtrado colaborativo tradicionales. En lugar de basarse en metadatos genéricos o calificaciones numéricas masivas, el sistema evalúa obras cinematográficas analizando semánticamente cientos de reseñas críticas (texto libre) y contrastándolas contra un perfil de usuario dinámico y estructurado en lenguaje natural.
La arquitectura es genérica: el modelo no está rígidamente programado para un solo usuario, sino que recibe el "Perfil Cinéfilo" como una entrada de datos (input), permitiendo procesar las preferencias de múltiples usuarios (Multiperfil).

## **¿Cómo ejecutar el programa?**

* Instalar las dependencias (idealmente dentro de un entorno virtual):
    `pip install -r requirements.txt`

* (Opcional) Para partir con un perfil ya armado, copiar `src/db/profiles/perfiles.ejemplo.json` como `src/db/profiles/perfiles.json`. Contiene el perfil de Ignacio Araya, el mismo con que se evaluó `dataset_maestro.csv` y con que se generaron los embeddings incluidos en el repositorio.

* Desde la raíz del repositorio, ejecutar:
    `python src/main.py`

    Las rutas se resuelven relativas a los archivos del proyecto, así que también funciona desde cualquier otro directorio indicando la ruta completa a `src/main.py`.

## **Guía del menú principal**

<small>*Nota: cada opción depende de que las anteriores ya se hayan corrido al menos una vez (ej. no se puede entrenar el modelo sin haber generado los embeddings y el Ground-truth antes). Si hay más de un perfil guardado, las opciones 6 y 7 preguntan cuál usar. El Ground-truth (`dataset_maestro.csv`) corresponde a un único perfil, así que se debe elegir ese mismo perfil al entrenar.*</small>

* **1) Gestionar perfiles cinéfilos.**
    Abre el menú de `profiles.py` para crear un perfil nuevo, o editar/eliminar uno existente (filtros restrictivos y afinidades). Se guarda en `perfiles.json`.

* **2) Ejecutar pipeline ETL (filtrar CSVs crudos).**
    Corre `filter.py` sobre los `.csv` crudos de `db/raw/` (extraídos desde Letterboxd): limpia texto, descarta reseñas vacías o sin contenido real, y convierte la calificación en estrellas a un número. Guarda el resultado en `db/filtered/result/`.

* **3) Generar embeddings de un perfil.**
    Pide el nombre de un perfil ya creado y genera los vectores semánticos de sus filtros y afinidades (`procesing_profiles.py`), persistiéndolos en la colección `perfiles` de ChromaDB. Cada filtro y afinidad se vectoriza solo con su nombre y descripción; cada excepción tiene su propio vector. Reemplaza por completo los embeddings anteriores de ese perfil y ofrece eliminar los de perfiles que ya no existen.

* **4) Generar embeddings de los lotes de reseñas pendientes.**
    Toma todos los `.csv` filtrados de `db/filtered/result/` que todavía no están en ChromaDB, chunkea el texto de cada reseña y genera sus embeddings (`procesing_reviews.py`), guardándolos en la colección `resenias`. Cada chunk se identifica como `pelicula::lote::review_N::chunk_M`, así que reseñas de lotes distintos no se pisan.

* **5) Cargar Ground-truth (dataset_maestro.csv).**
    Lee `dataset_maestro.csv` (las notas que evaluó Gemini para un grupo de películas según el perfil), lo limpia y normaliza, y genera `matriz_perdida.csv`: el archivo liviano que usan las opciones 6, 7 y 8. Las columnas se asocian a los filtros y afinidades del perfil elegido: cada uno se busca en la planilla por su campo `encabezado` (la abreviatura usada al evaluar, ej. `"Insoport."`) o, si no lo tiene, por su nombre. La nota global se lee de la columna `Global`. Además importa las películas ya evaluadas en `pendientes_evaluar.csv` (las que tienen `gt_nota_global`): las mueve a `evaluaciones_adicionales.csv`, que se suma a la Verdad Base en cada ejecución.

* **6) Revisar películas pendientes de evaluar.**
    Compara las películas que ya tienen reseña procesada contra las que ya están en `matriz_perdida.csv`, y muestra cuáles todavía no tienen nota de Gemini. Genera `pendientes_evaluar.csv` con la estructura lista para completar esas evaluaciones (se puede editar en Excel; se aceptan `;` como separador y coma decimal). Si la plantilla tiene evaluaciones aún sin importar, no la sobrescribe.

* **7) Entrenar modelo predictivo (Regresión Lineal).**
    Entrena una regresión lineal que aprende a aproximar la nota de Gemini a partir de la similitud de coseno entre los embeddings de las reseñas (promediados por película) y los del perfil. Además de la similitud con cada filtro, afinidad y excepción, el modelo recibe un término por cada relación del perfil, siguiendo la cadena **afinidad ← filtro ← excepción**: afinidad × filtro (el filtro corrompe la afinidad, según `corrupcion_directa`) y filtro × excepción (la excepción neutraliza el filtro). El perfil define qué relaciones existen y la regresión aprende cuánto pesa cada una. La severidad, el nivel y la importancia base no se usan en el modelo. Informa el error del modelo (MSE), la varianza explicada (R²) y el peso aprendido para cada filtro/afinidad, y guarda el modelo en `src/loss/modelo_regresion.joblib`.

* **8) Recomendar películas según el perfil.**
    Carga el modelo guardado en la opción 7 (y el perfil con el que se entrenó) para estimar una nota a todas las películas con reseña procesada (tanto a las que ya evaluó Gemini, para comparar, como a las nuevas que todavía no tienen nota). Muestra todo en un único ranking ordenado de mayor a menor nota estimada.

* **9) Salir.**
    Cierra el programa.

## **Librerias Utilizadas**

<small>*Nota: Se recomienda instalar un entorno virtual*</small>

* <code><b><span style="font-size:1.3em;">sentence-transformers</span></b></code>
* <code><b><span style="font-size:1.3em;">langchain_core.documents</span></b></code>
* <code><b><span style="font-size:1.3em;">chromadb</span></b></code> 
* <code><b><span style="font-size:1.3em;">numpy</span></b></code> 
* <code><b><span style="font-size:1.3em;">Semchunk</span></b></code> 
* <code><b><span style="font-size:1.3em;">pandas</span></b></code> 
* <code><b><span style="font-size:1.3em;">scikit-learn</span></b></code> 
* <code><b><span style="font-size:1.3em;">torch</span></b></code> 


## **Distribución de directorios**
<pre><code><i><span style="color: #00fed4ed;">Cómo se organiza el código?</span></i></code></pre>

* <code><b><span style="color: #23c523d4;">src/</span></b></code>: Directorio principal del código fuente. Contiene las funcionalidades clave del programa y la lógica central del mismo.

    * <code><b><span style="color: #23c523d4;">db/</span></b></code>: Módulo destinado al manejo de la base de datos del sistema.
        
        * <code><b><span style="color: #23c523d4;">filtered/</span></b></code>:
            
            * <code><b><span style="color: #23c523d4;">result/</span></b></code>: Directorio donde se almacenan los archivos (`.csv`) ya procesados, limpios y listos para trabajar.

            * <code><b><span style="color: #009dff;">filter.py</span></b></code>: Contiene la lógica general de filtrado y limpieza de los archivos .csv de la base de datos.
        
        * <code><b><span style="color: #23c523d4;">raw/</span></b></code>: Carpeta donde se almacenan los archivos .csv crudos extraídos desde letterboxd.

        * <code><b><span style="color: #009dff;">extract.ipynb</span></b></code>: Archivo encargado de extraer reseñas de letterboxd y serializarlas.

        * <code><b><span style="color: #23c523d4;">embeddings/</span></b></code>: Carpeta donde se persisten los vectores generados a partir de los perfiles y las reseñas.

            * <code><b><span style="color: #23c523d4;">chroma/</span></b></code>: Base de datos vectorial (ChromaDB) con las colecciones `perfiles` y `resenias`, generadas por `procesing_profiles.py` y `procesing_reviews.py` respectivamente.

    * <code><b><span style="color: #23c523d4;">loss/</span></b></code>: Módulo dedicado a construir y supervisar el entrenamiento del modelo matemático.
        
        * <code><b><span style="color: #009dff;">gt_matrix_pipeline.py</span></b></code>: Despachador de datos que administra la ingesta de archivos procesados y utiliza álgebra de conjuntos para garantizar evaluaciones únicas.

        * <code><b><span style="color: #009dff;">ingest_maestro.py</span></b></code>: Encargado de preparar el archivo maestro de ground-truth para el sistema de recomendación. Lee el dataset, normaliza los títulos de las películas para crear identificadores más adecuados y convierte las métricas de evaluación a valores numéricos.
        
        * <code><b><span style="color: #009dff;">matrix.py</span></b></code>: Motor generador de la matriz de Verdad base, extrae la topología de los perfiles de usuario para crear el tensor objetivo ($Y$) contra el cual el Perceptrón Multicapa validará sus predicciones.

        * <code><b><span style="color: #23c523d4;">dataset_maestro.csv</span></b></code>: Archivo de ground-truth evaluado a mano, insumo de `ingest_maestro.py`.

        * <code><b><span style="color: #23c523d4;">matriz_perdida.csv</span></b></code>: <i>(generado)</i> Salida normalizada de `ingest_maestro.py`, usada como Verdad Base para comparar contra las predicciones del modelo.

    * <code><b><span style="color: #009dff;">main.py</span></b></code>: Archivo principal del programa, orquesta el resto de los módulos a través de un menú central.

    * <code><b><span style="color: #009dff;">profiles.py</span></b></code>: Encargado de crear, editar y eliminar perfiles cinéfilos de usuario, guardándolos en `perfiles.json`.

    * <code><b><span style="color: #009dff;">visuals.py</span></b></code>: Centraliza los menús de texto que se muestran por consola, tanto los de `main.py` como los de `profiles.py`.

    * <code><b><span style="color: #009dff;">procesing_profiles.py</span></b></code>: Genera los chunks y embeddings de un perfil cinéfilo puntual (recibido por nombre) y los persiste en ChromaDB.

    * <code><b><span style="color: #009dff;">procesing_reviews.py</span></b></code>: Genera los chunks y embeddings de los lotes de reseñas filtradas que aún no están vectorizados y los persiste en ChromaDB.

    * <code><b><span style="color: #009dff;">normalizacion.py</span></b></code>: Funciones compartidas para normalizar y comparar el `film_id` entre las distintas fuentes de datos del proyecto (reseñas vs. ground-truth).

    * <code><b><span style="color: #009dff;">config.py</span></b></code>: Archivo de configuración centralizada del proyecto: nombre del modelo de embeddings y todas las rutas del proyecto.

    * <code><b><span style="color: #009dff;">scoring.py</span></b></code>: Entrena la regresión lineal (perfil vs. reseñas) contra la Verdad Base y la guarda en `src/loss/modelo_regresion.joblib`.

    * <code><b><span style="color: #009dff;">recommend.py</span></b></code>: Carga el modelo entrenado y genera el ranking de recomendaciones.

* <code><b><span style="color: #23c523d4;">perfiles.json</span></b></code>: <i>(en `src/db/profiles/`)</i> Almacena los perfiles cinéfilos creados desde `profiles.py`.



## **Changelog (historial de cambios)**
<small>*Nota: Este changelog está en orden cronológico inverso.*</small>

### [1.0.4] - 24-09-2026
> Embeddings del perfil sin contaminación y excepciones incorporadas al modelo.

* Arreglado

    * `procesing_profiles.py` vectorizaba cada filtro junto con su nivel, severidad, afinidades corrompidas y excepción, lo que acercaba su vector a los conceptos opuestos (ej. "Camaradería Masculina Rancia" quedaba con similitud 0.65 con "Resistencia Femenina"). Ahora solo se vectoriza el nombre y la descripción; el resto queda como metadatos.

    * `perfiles.ejemplo.json`: descripciones reescritas en positivo, porque los embeddings no distinguen bien las negaciones ("sin superioridad moral" acercaba "Humanismo Social" a "Insoportabilidad Prolongada"). La nota de "Camaradería Masculina Rancia" pasó a ser su excepción.

* Añadido

    * Cada excepción tiene su propio embedding, y `scoring.py` incorpora la cadena afinidad ← filtro ← excepción como términos de interacción de la regresión.

    * Campo opcional `encabezado` en cada filtro/afinidad del perfil (se pide al crearlo o editarlo en la opción 1). `ingest_maestro.py` arma con él el mapeo de columnas de la planilla, en vez del diccionario `MAPEO_ENCABEZADOS` fijo en el código que solo servía para un perfil.

* Cambios

    * El modelo guardado incluye la estructura del perfil; un modelo de la versión anterior pide reentrenar (opción 7). Tras actualizar hay que volver a ejecutar las opciones 3 y 7.

### [1.0.3] - 23-09-2026
> Integridad de los embeddings en ChromaDB y cierre del ciclo de evaluación de películas pendientes.

* Arreglado

    * `procesing_reviews.py`: el id de cada chunk no incluía el lote, así que reseñas de lotes distintos en la misma fila se sobrescribían. Ahora el id incluye el lote, y se ofrece eliminar los chunks con el formato antiguo.

    * La opción 4 solo vectorizaba el `.csv` filtrado más reciente; ahora procesa todos los lotes que aún no están en ChromaDB.

    * `profiles.py`: al renombrar un perfil no se aplicaba `.title()`, y un perfil renombrado ya no se podía vectorizar ni eliminar. Los nombres se buscan ahora sin distinguir mayúsculas, y ya no se puede renombrar un perfil con el nombre de otro existente (antes lo sobrescribía).

    * `procesing_profiles.py`: los embeddings de filtros eliminados y de perfiles borrados o renombrados quedaban en ChromaDB. Ahora cada perfil se reemplaza completo al vectorizarlo, y se ofrece limpiar los perfiles huérfanos.

* Añadido

    * `ingest_maestro.py` importa las evaluaciones completadas en `pendientes_evaluar.csv` hacia `evaluaciones_adicionales.csv`, que se une a la Verdad Base.

    * `gt_matrix_pipeline.py` no sobrescribe `pendientes_evaluar.csv` si tiene evaluaciones sin importar.

    * `src/db/profiles/perfiles.ejemplo.json`: perfil de Ignacio Araya reconstruido desde ChromaDB (reproduce exactamente los textos de sus embeddings), para poder correr el pipeline sin crear el perfil a mano.

### [1.0.2] - 23-09-2026
> Corrección del entrenamiento del modelo, soporte real para elegir perfil y rutas independientes del directorio de ejecución.

* Arreglado

    * `scoring.py` comparaba el id compuesto de cada chunk (`pelicula::review_N::chunk_M`) contra el `film_id` de la Verdad Base, así que la opción 7 nunca lograba cruzar datos. Ahora promedia los embeddings por película, igual que `recommend.py`.

    * `scoring.py` y `recommend.py` buscaban el embedding de cada filtro solo por nombre, pudiendo tomar el de otro perfil que tuviera un filtro con el mismo nombre. Ahora filtran por persona.

    * La opción 8 reentrenaba su propio modelo en vez de usar el de la opción 7. Ahora la opción 7 guarda el modelo (`modelo_regresion.joblib`) y la opción 8 lo carga.

    * `procesing_profiles.py` fallaba con `TypeError` al ejecutarse directamente (llamaba `main(nombre)` con un `main()` sin parámetros).

    * `ingest_maestro.py` fallaba con `KeyError` si al dataset maestro le faltaba alguna columna; ahora la omite con un aviso, y también avisa de columnas sin mapeo.

    * `filter.py` volvía a filtrar todos los CSV crudos en cada ejecución, duplicando archivos en `result/`. Ahora omite los que ya fueron filtrados y no han cambiado (el nombre de salida incluye el nombre del crudo).

* Cambios

    * Las rutas se centralizan en `config.py` y se resuelven relativas a los archivos del proyecto, no a `Path.cwd()`: el programa ya no depende del directorio desde donde se ejecuta.

    * `normalizacion.py`: `cargar_perfil_actual()` (que tomaba siempre el primer perfil de `perfiles.json`) se reemplazó por `seleccionar_perfil()`, que pregunta cuál usar cuando hay más de uno.

    * `scoring.py` avisa cuando hay menos películas que filtros (modelo sobreajustado, métricas no confiables).

* Añadido

    * `requirements.txt` con las dependencias del proyecto.

### [1.0.1] - 17-09-2026
>Arreglos menores sobre verificación de datos por medio de los inputs para mantener el flujo de datos correcto y sin guardados fantasmas.

* Arreglado

    * Se agregaron verificaciones a las variables para los nombre en `procesing_profiles.py` para evitar cargar el modelo si no se introduce un nombre válido.

    * En la gestión de perfiles de `profiles` se agregó verificaciones para que no se introduzcan valores nulos en afinidad y restriccion, además de que el guardado de datos se va a realizar una vez que pase todo el ingreso de datos sin problemas.

* Cambios

    * Se hicieron pequeños cambios de interfaces para que sea un poco más precisa la información que se muestra en pantalla por medio de la consola.

### [1.0.0] - 17-09-2026
> Corrección de bugs críticos de rutas y del pipeline de ground-truth, reorganización del menú principal, nuevo módulo de recomendaciones, y desacople del perfil activo en vez de mapeos fijos por código.

* Arreglado

    * `perfiles.json` apuntaba a la raíz del proyecto en `profiles.py`, `procesing_profiles.py` y `matrix.py`, pero el archivo real vive en `src/db/profiles/perfiles.json`. Corregidas las tres rutas.

    * `src/loss/gt_matrix_pipeline.py` no tenía su lógica real: por error contenía una copia del menú de `main.py`, con un import que se importaba a sí mismo. Reescrito para cruzar (álgebra de conjuntos, con `film_id` canonicalizado) las películas con reseña procesada contra la Verdad Base, reportar los nombres de las pendientes y generar `pendientes_evaluar.csv`.

    * `visuals.py` tenía `mostrar_menu_principal()` definida dos veces (código muerto); eliminada la duplicada.

    * `procesing_profiles.py` y `procesing_reviews.py` forzaban `device="cuda"` sin verificar disponibilidad; ahora detectan automáticamente con `torch.cuda.is_available()` y usan CPU si no hay GPU.

* Añadido

    * `src/recommend.py`: nuevo módulo que aplica el modelo ya entrenado (regresión lineal) sobre las películas con reseña procesada que todavía no tienen nota de Gemini, y muestra un único ranking (evaluadas + candidatas) con columnas Película / Nota Modelo / Nota de Gemini (`NaN` cuando no hay nota de Gemini todavía).

    * `src/normalizacion.py`: `cargar_perfil_actual()`, `obtener_filtros_del_perfil()` y `nombre_columna_gt()`, para armar dinámicamente el orden y los nombres de columna de los filtros/afinidades del perfil activo.

    * Opción 8 del menú ("Recomendar películas según el perfil").

    * Sección "Guía del menú principal" en este README, con la descripción de cada opción.

* Cambios

    * `main.py` y `visuals.py`: menú reorganizado — opción 6 ahora ejecuta el pipeline de pendientes, opción 7 el entrenamiento (regresión lineal), opción 8 las recomendaciones, y opción 9 pasó a ser "Salir".

    * `scoring.py` y `recommend.py`: el diccionario fijo de filtros (`filterMapping`) fue reemplazado por las funciones dinámicas de `normalizacion.py`, para que agregar un perfil nuevo o cambiarle los filtros a uno existente no requiera editar código.

    * Librerías utilizadas actualizadas: agregadas `pandas`, `scikit-learn` y `torch`, que ya se usaban en el código pero no estaban documentadas.

### [0.2.0] - 20-08-2026
> Sincronización completa de todos los módulos a través de `main.py`, con persistencia real de embeddings y corrección de bugs de integración entre archivos.

* Añadido

    * `src/normalizacion.py`: nuevo módulo compartido con `parse_film_id()` (migrada desde `ingest_maestro.py`) y la nueva `canonicalizar_film_id()`, para poder cruzar el `film_id` de las reseñas contra el del ground-truth sin importar si trae o no el año.

    * Persistencia real de embeddings en **ChromaDB**: tanto los perfiles como las reseñas se guardan ahora en colecciones (`perfiles`, `resenias`) dentro de `src/db/embeddings/chroma/`, usando `upsert` para que reprocesar un perfil o un lote no genere duplicados.

    * `procesing_reviews.py`: agregadas `obtener_csv_mas_reciente()`, `cargar_resenias()` (con validación de columnas requeridas) y `guardar_coleccion()`.

    * `main.py`: nuevas opciones de menú para generar embeddings de reseñas y para revisar qué películas siguen pendientes de evaluación (la función de `gt_matrix_pipeline.py` ya estaba importada desde antes, pero nunca se usaba en ningún lado del menú).

    * `visuals.py` ahora también centraliza los menús que antes vivían directamente dentro de `profiles.py`.

* Cambios

    * `profiles.py` reestructurado con una función `main()` y su guardia `if __name__ == '__main__':`, para poder importarse desde `main.py` sin que el menú se dispare automáticamente al hacer `import`.

    * Unificados los nombres de campo del perfil (`descripcion_texto`/`excepcion_texto` → `descripcion`/`excepcion`) para que filtros restrictivos y afinidades usen el mismo esquema, tanto en `perfiles.json` como en `profiles.py`.

    * `perfiles.json`: migrado el perfil real de Ignacio Araya (antes vivía hardcodeado dentro de `procesing_profiles.py`); se eliminaron los campos `descripcion_fragmentos`/`excepcion_fragmentos` por ser innecesarios, ya que los embeddings se generan a partir de la descripción completa.

    * `procesing_profiles.py` ahora recibe el nombre del perfil como parámetro (`main(nombre_perfil)`) y lo lee desde `perfiles.json`, en vez de tener un perfil fijo hardcodeado dentro del propio archivo.

    * `procesing_reviews.py`: reemplazado el recorrido por índice (`for i in range(len(...))`) por `iterrows()`, y el `.csv` fijo hardcodeado por selección dinámica del lote filtrado más reciente (según fecha real de modificación del archivo).

    * `ingest_maestro.py` ahora importa `parse_film_id` desde `src/normalizacion.py` en vez de definirla localmente.

    * `gt_matrix_pipeline.py`: la comparación de películas pendientes ahora canonicaliza el `film_id` antes de cruzarlo contra el ground-truth, y además reporta los nombres de las películas pendientes (antes solo mostraba el conteo).

    * `main.py` reescrito por completo: el menú quedó reducido a las 7 acciones realmente funcionales hasta el momento, cada una con su mensaje de estado antes de ejecutarse.

* Arreglado

    * Bug en `procesing_profiles.py` que usaba f-strings con comillas dobles anidadas, sintaxis válida solo desde Python 3.12+ (impedía incluso importar el archivo en versiones anteriores).

    * Bug en `profiles.py` donde `menu_afinidades()` dependía de la variable `es_nuevo` como si fuera global, sin recibirla como parámetro.

    * Bug en `profiles.py` donde, al crear un perfil nuevo, `datos[nombre_perfil] = {"restrictivos": {}}` quedaba sobreescrito inmediatamente por `datos[nombre_perfil] = {"afinidad": {}}`.

    * Bug de cruce de datos entre `gt_matrix_pipeline.py` y `ingest_maestro.py`: el `film_id` de las reseñas (a veces con sufijo de año, según si Letterboxd necesitó desambiguar el título) no coincidía con el del ground-truth (que siempre lo omite), generando falsos positivos de "película pendiente de evaluar".

    * Ruta hardcodeada con backslashes de Windows en `procesing_reviews.py`, reemplazada por manejo de rutas con `pathlib` para que funcione en cualquier sistema operativo.

    * Import roto en `main.py` (`import src.embeddings`, que apuntaba a un archivo inexistente).

### [0.1.1] - 18-08-2026

* Cambios
    
    * Reajustada selección de `.csv` utilizado como ground-truth.

    * Archivo `main.py` refactorizado para acomodar las modificaciones realizadas.

* Añadido
    
    * Archivo `ingest_maestro.py` para procesar el archivo de ground-truth `dataset_maestro.csv`

### [0.1.0] - 03-08-2026
> Conseguida versión funcional del programa con todas las funcionalidades principales.

* Cambios
    
    * Añadido mecanismo básico de ingesta para el oráculo con `ingest_oraculo.py`.

    * Concretada estructura base de la función `main.py` para acceder a las funcionalidades del programa.

    * Implementada base de datos final utilizando sqlite3 para guardar las calificaciones (manuales) finales de las películas en `ground_truth.db`.

    * Refactorizados archivos `embeddings.py` y `profiles.py` para definir una función maestra local (main) y así poder importar la misma a través del archivo principal del programa, `main.py`.

    * Cambios generales para permitir sincronización y estabilidad con Google Colab: Adaptar localización de rutas con Path.cwd, acceder a sub-directorios de forma más explícita, etc.

### **Versión 0.0.1** (14-07-2026)
> Implementacion temprana de chunking para los perfiles de usuario.

* Parche 0.0.5 (31-07-2026)
    > Creado módulo `loss/` e implementadas funcionalidades principales de Ground truth:
    
    * Creación dinámica de la matriz de Verdad Base mediante `matrix.py`.

    * Script despachador `gt_matrix_pipeline` para controlar el flujo de la base de datos.

    * Utilizada álgebra de conjuntos en el *pipeline* para rastrear películas pendientes y obviar aquellas ya evaluadas.
    * Implementación de sistema generador de chunks y embedings para las reseñas
    * Correcion al sistema de generacion de usuarios

* Parche 0.0.4 (31-07-2026)

    * Añadido nuevo filtro para el procesado de la base de datos: ahora se eliminan reseñas con textos tanto completamente vacíos como con números (*presuntamente*) fuera de contexto, es decir, sin ningún tipo de texto además de los propios números.

    * Actualizada serialización de archivos extraídos desde (`extract.ipynb`) de tal forma que los archivos csv resultantes sean guardados correctamente dentro de la carpeta (`raw`) y siguiendo la convención: **prefijo**_YY-MM-DD_HH-MM-SS.

* Parche 0.0.3 (30-07-2026)
    > Implementación de base de datos: extracción y filtrado.

    * Estructuración inicial del módulo de base de datos (`db/`) para aislar la lógica de ingesta de la lógica de procesamiento.

    * Implementación del archivo de extracción (`extract.ipynb`) para la captura y guardado automatizado dentro de la carpeta de archivos crudos (`raw`).

    * Desarrollado motor de sanitización y normalización (`filter.py`) para depurar los datos extraídos, prepararlos para su vectorización y almacenarlos dentro de la carpeta de archivos procesados (`result`).

* Parche 0.0.2
    > Implementacion de sistema de embeddings para los perfiles de usuario.
    * Creación y finalización de entorno de creación de perfiles cinéfilos de usuarios (nombre perfil, filtros, afinidades)
<h1 align="center">Motor de Recomendación Semántica Multiperfil</h1>

<img src="https://img.shields.io/badge/version-0.2.0-blue" alt="version">

[![Last Commit](https://img.shields.io/github/last-commit/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/main-dev?style=flat-square&logo=github&color=blue&cache_bust=1)](https://github.com/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/tree/main-dev)

## **Premisa**
### "motor-de-recomendacion-semantica-multiperfil"


Este proyecto consiste en el desarrollo de un sistema híbrido de recomendación cinematográfica diseñado para superar las limitaciones de los algoritmos de filtrado colaborativo tradicionales. En lugar de basarse en metadatos genéricos o calificaciones numéricas masivas, el sistema evalúa obras cinematográficas analizando semánticamente cientos de reseñas críticas (texto libre) y contrastándolas contra un perfil de usuario dinámico y estructurado en lenguaje natural.
La arquitectura es genérica: el modelo no está rígidamente programado para un solo usuario, sino que recibe el "Perfil Cinéfilo" como una entrada de datos (input), permitiendo procesar las preferencias de múltiples usuarios (Multiperfil).

## **Cómmo ejecutar el programa?**

* Abrir el terminal CMD o Powershell y utilizar el siguiente comando:
    `python motor_recomendacion_semantica/src/main.py`

## **Librerias Utilizadas**

<small>*Nota: Se recomienda instalar un entorno virtual*</small>

* <code><b><span style="font-size:1.3em;">sentence-transformers</span></b></code>
* <code><b><span style="font-size:1.3em;">langchain_core.documents</span></b></code>
* <code><b><span style="font-size:1.3em;">chromadb</span></b></code> 
* <code><b><span style="font-size:1.3em;">numpy</span></b></code> 
* <code><b><span style="font-size:1.3em;">Semchunk</span></b></code> 


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

    * <code><b><span style="color: #009dff;">procesing_reviews.py</span></b></code>: Genera los chunks y embeddings del lote de reseñas filtradas más reciente y los persiste en ChromaDB.

    * <code><b><span style="color: #009dff;">normalizacion.py</span></b></code>: Funciones compartidas para normalizar y comparar el `film_id` entre las distintas fuentes de datos del proyecto (reseñas vs. ground-truth).

    * <code><b><span style="color: #009dff;">config.py</span></b></code>: Archivo de configuración centralizada del proyecto, contiene constantes reutilizadas por los distintos módulos.

    * <code><b><span style="color: #009dff;">scoring.py</span></b></code>: <i>(pendiente)</i> Módulo donde se implementará el modelo de puntaje/regresión final que combina perfil y reseñas.

* <code><b><span style="color: #23c523d4;">perfiles.json</span></b></code>: <i>(en la raíz del proyecto)</i> Almacena los perfiles cinéfilos creados desde `profiles.py`.



## **Changelog (historial de cambios)**
<small>*Nota: Este changelog está en orden cronológico inverso.*</small>

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
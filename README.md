<h1 align="center">Motor de Recomendación Semántica Multiperfil</h1>

<img src="https://img.shields.io/badge/version-0.0.1.2-blue" alt="version">

[![Last Commit](https://img.shields.io/github/last-commit/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/main-dev?style=flat-square&logo=github&color=blue&cache_bust=1)](https://github.com/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/tree/main-dev)

## **Premisa**
### "motor-de-recomendacion-semantica-multiperfil"


Este proyecto consiste en el desarrollo de un sistema híbrido de recomendación cinematográfica diseñado para superar las limitaciones de los algoritmos de filtrado colaborativo tradicionales. En lugar de basarse en metadatos genéricos o calificaciones numéricas masivas, el sistema evalúa obras cinematográficas analizando semánticamente cientos de reseñas críticas (texto libre) y contrastándolas contra un perfil de usuario dinámico y estructurado en lenguaje natural.
La arquitectura es genérica: el modelo no está rígidamente programado para un solo usuario, sino que recibe el "Perfil Cinéfilo" como una entrada de datos (input), permitiendo procesar las preferencias de múltiples usuarios (Multiperfil).


## **Librerias Utilizadas**

<small>*Nota: Se recomienda instalar un entorno virtual*</small>

* <code><b><span style="font-size:1.3em;">sentence-transformers</span></b></code>
* <code><b><span style="font-size:1.3em;">langchain</span></b></code>
* <code><b><span style="font-size:1.3em;">chromadb</span></b></code>


## **Distribución de directorios**
<pre><code><i><span style="color: #00fed4ed;">Cómo se organiza el código?</span></i></code></pre>

* <code><b><span style="color: #23c523d4;">src/</span></b></code>: Directorio principal del código fuente. Contiene las funcionalidades clave del programa y la lógica central del mismo.

    * <code><b><span style="color: #23c523d4;">db/</span></b></code>: Carpeta destinada al manejo de la base de datos del sistema.
        
        * <code><b><span style="color: #23c523d4;">filtered/</span></b></code>:
            
            * <code><b><span style="color: #23c523d4;">result/</span></b></code>: Directorio donde se almacenan los archivos (`.csv`) ya procesados, limpios y listos para trabajar.

            * <code><b><span style="color: #009dff;">filter.py</span></b></code>: Contiene la lógica general de filtrado y limpieza de los archivos .csv de la base de datos.
        
        * <code><b><span style="color: #23c523d4;">raw/</span></b></code>: Carpeta donde se almacenan los archivos .csv crudos extraídos desde letterboxd.

        * <code><b><span style="color: #009dff;">extract.ipynb</span></b></code>: Archivo encargado de extraer reseñas de letterboxd y serializarlas.
        

    * <code><b><span style="color: #009dff;">main.py</span></b></code>: Archivo principal del programa.

    <small> *Corregir nombre: "embeddings" en plural y **con** 'g', no "embeddins* </small>:
    * <code><b><span style="color: #009dff;">embeddins.py</span></b></code>: Archivo encargado de las incrustaciones vectoriales.



## **Changelog (historial de cambios)**
<small>*Nota: Este changelog está en orden cronológico inverso.*</small>

### **Versión 0.0.1.0** (14-07-2026)
> Implementación de base de datos: extracción y filtrado.
> Versiones iniciales de chunking para los perfiles de usuario y sistema de embeddings para los mismos.

* Parche 0.0.1.4

    * Añadido nuevo filtro para el procesado de la base de datos: ahora se eliminan reseñas con textos tanto completamente vacíos como con números (*presuntamente*) fuera de contexto, es decir, sin ningún tipo de texto además de los propios números.

    * Actualizada serialización de archivos extraídos desde (`extract.ipynb`) de tal forma que los archivos csv resultantes sean guardados correctamente dentro de la carpeta (`raw`) y siguiendo la convención: **prefijo**_YY-MM-DD_HH-MM-SS.

* Parche 0.0.1.3

    * Estructuración inicial del módulo de base de datos (`db/`) para aislar la lógica de ingesta de la lógica de procesamiento.

    * Implementación del archivo de extracción (`extract.ipynb`) para la captura y guardado automatizado dentro de la carpeta de archivos crudos (`raw`).

    * Desarrollado motor de sanitización y normalización (`filter.py`) para depurar los datos extraídos, prepararlos para su vectorización y almacenarlos dentro de la carpeta de archivos procesados (`result`).

* Parche 0.0.1.2

    * Implementacion de sistema de embeddings para los perfiles de usuario

* Parche 0.0.1.1

    * Implementacion temprana de chunking para los perfiles de usuario

### **Versión 0.0.0.1**
* Versión inicial del programa: Initial commits y organización básica
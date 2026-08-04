<h1 align="center">Motor de Recomendación Semántica Multiperfil</h1>

<img src="https://img.shields.io/badge/version-0.0.0.1-blue" alt="version">

[![Last Commit](https://img.shields.io/github/last-commit/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/main-dev?style=flat-square&logo=github&color=blue&cache_bust=1)](https://github.com/jonathanurrutiat-wq/motor-de-recomendacion-semantica-multiperfil/tree/main-dev)

## **Premisa**
### "motor-de-recomendacion-semantica-multiperfil"


Este proyecto consiste en el desarrollo de un sistema híbrido de recomendación cinematográfica diseñado para superar las limitaciones de los algoritmos de filtrado colaborativo tradicionales. En lugar de basarse en metadatos genéricos o calificaciones numéricas masivas, el sistema evalúa obras cinematográficas analizando semánticamente cientos de reseñas críticas (texto libre) y contrastándolas contra un perfil de usuario dinámico y estructurado en lenguaje natural.
La arquitectura es genérica: el modelo no está rígidamente programado para un solo usuario, sino que recibe el "Perfil Cinéfilo" como una entrada de datos (input), permitiendo procesar las preferencias de múltiples usuarios (Multiperfil).


## **Librerias Utilizadas**

<small>*Nota: Se recomienda instalar un entorno virtual*</small>

* <code><b><span style="font-size:1.3em;">sentence-transformers</span></b></code>
* <code><b><span style="font-size:1.3em;">langchain_core.documents</span></b></code>
* <code><b><span style="font-size:1.3em;">chromadb</span></b></code> 
* <code><b><span style="font-size:1.3em;">numpy</span></b></code> 


## **Distribución de directorios**
<pre><code><i><span style="color: #00fed4ed;">Cómo se organiza el código?</span></i></code></pre>

* <code><b><span style="color: #23c523d4;">src/</span></b></code>: Directorio principal del código fuente. Contiene las funcionalidades clave del programa y la lógica central del mismo.

    * <code><b><span style="color: #009dff;">main.py</span></b></code>: Archivo principal del programa.

    
    * <code><b><span style="color: #009dff;">embeddings.py</span></b></code>: Archivo encargado de las incrustaciones vectoriales.

    * <code><b><span style="color: #009dff;">config.py</span></b></code>: Archivo de configuración centralizada del proyecto, contiene constantes reutilizadas por los distintos módulos.



## **Aclaraciones**
    > El modelo usado para crear los embedings no genera problemas si se usan reseñas en ingles/español

## **Changelog (historial de cambios)**
<small>*Nota: Este changelog está en orden cronológico inverso.*</small>

### **Versión 0.0.1** (14-07-2026) 
> Implementacion temprana de chunking para los perfiles de usuario

* Parche 0.0.2
  + Implementacion de sistema de embeddings para los perfiles de usuario
---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.2
---

<!-- #region slideshow={"slide_type": "slide"} -->
# Analizando de manera reproducible el riesgo de inundaciones con NASA Earthdata cloud.

<div style="display: flex; align-items: center;">
    <img src="../../assets/TOPS.png" alt="Image" style="width: 100px; height: auto; margin-right: 10px;">
    <h3>ScienceCore:<br>Climate Risk</h3>
</div>



<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Objetivo

Utilizar los productos abiertos de la NASA llamados Opera Dynamic Surface Water eXtent (DSWx) - Landsat Sentinel-2 armonizado (HLS) para mapear la extensión de la inundación como resultado del evento monzónico de septiembre de 2022 en Pakistán.

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
En 2022, las lluvias monzónicas de Pakistán alcanzaron niveles récord, provocando devastadoras inundaciones y deslizamientos de tierra que afectaron a las cuatro provincias del país y a alrededor del 14% de su población. En este ejemplo, podrás ver cómo utilizar los productos abiertos de NASA Opera DSWx-HLS para mapear la extensión de las inundaciones causadas por el monzón ocurrido en septiembre de 2022 en Pakistán.

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Hoja de Ruta

- Productos Opera DSWx-HLS
- Configurar el ambiente de trabajo
- Definir el área de interés
- Búsqueda y obtención de datos
- Análisis de datos
- Procesamiento y visualización
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
Primero, definiremos qué son los productos Opera DSWx-HLS y qué tipo de información puedes obtener de ellos. 
Luego, aprenderás a configurarás tu ambiente de trabajo, definir el área de interés sobre la que quieres recolectar información, realizar la búsqueda y recolección de datos, analizaros y visualizarlos. 

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Qué te llevarás

-- Insertar imagen resultante --
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
Este es el resultado final al que llegarás, luego de completar las actividades del taller. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Antes de empezar

- Para participar de esta clase, debes aceptar las pautas de convivencia detalladas [aquí]().
- Si hablas, luego silencia tu micrófono para evitar interrupciones por ruidos de fondo. Puede que lo hagamos por ti.
- Para decir algo, pide la palabra o usa el chat.
- ¿Podemos grabar el chat? ¿Podemos “sacar fotos”?

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
Pautas de convencia:
- Si están en este curso aceptaron las pautas de convivencia de nuestra comunidad el cuál implica, a grandes rasgos, que nos vamos a comportar de forma educada y amable para que este sea un ambiente abierto, seguro y amigable y garantizar la participación de todas las personas en nuestras actividades y espacios virtuales. 
- Si alguno de ustedes ve o siente que no está lo suficientemente cómodo o cómoda, nos puede escribir a nosotros por mensajes privados. 
- En caso de que quienes no los hagamos sentir cómodo seamos --docentes-- lo pueden indicar enviando un mail a --agregar mail de referencia --
Cómo participar:
- Vamos a pedirles que se silencien/apaguen los micrófonos mientras no están hablando para que no nos moleste el sonido ambiente de cada uno de nosotros. 
- Pueden pedir la palabra levantando la mano o en el chat y --docentes-- vamos a estar atentos para que puedan participar en el momento adecuado.
Acerca de la grabación:
- El curso va a grabarse, si no desean aparecer en la grabación les pedimos que apaguen la camara. 
- Si alguno de ustedes quiere contar lo que estamos haciendo en redes sociales, por favor, antes de sacar una foto o captura de pantalla con las caras de cada una de las personas que están presentes, pidamos permiso porque puede haber gente que no se sienta cómoda compartiendo su imagen en internet. No hay inconvenientes en que compartan imágenes de las diapositivas o --la cara del docente--. 


<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Dataset Opera DSWx-HLS

- Contiene observaciones de la extensión superficial de agua en ubicaciones y momentos específicos (de febrero de 2019 hasta septiembre de 2022).
- Se distribuyen sobre coordenadas de mapa proyectadas como mosaicos.
- Cada mosaico cubre un área de 109.8 x 109.8 km.
- Cada mosaico incluye 10 GeoTIFF (capas).

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
Este conjunto de datos contiene observaciones de la extensión superficial de agua en ubicaciones y momentos específicos que abarcan desde febrero de 2019 hasta septiembre de 2022. El conjunto de datos de entrada para generar cada producto es el producto Harmonized Landsat-8 y Sentinel-2A/B (HLS) versión 2.0. Los productos HLS proporcionan datos de reflectancia de superficie (SR) del Operador de Imágenes Terrestres (OLI) a bordo del satélite Landsat 8 y del Instrumento Multiespectral (MSI) a bordo de los satélites Sentinel-2A/B.

Los productos de extensión superficial de agua se distribuyen sobre coordenadas de mapa proyectadas. Cada mosaico UTM cubre un área de 109,8 km × 109,8 km. Esta área se divide en 3,660 filas y 3,660 columnas con un espaciado de píxeles de 30 m.

Cada producto se distribuye como un conjunto de 10 archivos GeoTIFF (capas) que incluyen clasificación de agua, confianza asociada, clasificación de cobertura terrestre, capa de sombra del terreno, clasificación de nubes/sombras de nubes, Modelo Digital de Elevación (DEM) y capa diagnóstica en formato PNG.


<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Dataset Opera DSWx-HLS

1. B02_BWTR (Capa binaria de agua):
    - 1 (blanco) = presencia de agua. 
    - 0 (negro) = ausencia de agua. 

2. B03_CONF (Capa de confianza):
    - % de confianza en sus predicciones de agua. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
En este taller, utilizaremos dos capas:
1. **B02_BWTR (Capa binaria de agua):**
Esta capa nos brinda una imagen simple de las áreas inundadas. Donde hay agua, la capa vale 1 (blanco) y donde no hay agua, toma valor 0 (negro). Es como un mapa binario de las inundaciones, ideal para obtener una visión general rápida de la extensión del desastre.
2. **B03_CONF (Capa de confianza):**
Esta capa nos indica qué tan seguro está el sistema DSWx-HLS de sus predicciones de agua. Donde la capa muestra valores altos (cerca de 100%), podemos estar muy seguros de que hay agua. En áreas con valores más bajos, la confianza disminuye, lo que significa que lo que parece agua podría ser otra cosa, como sombras o nubes.

Para ayudarte a visualizar mejor cómo funciona esto piensa en una imagen satelital de la zona afectada por las inundaciones. Las áreas con agua se ven azul oscuro, mientras que las áreas secas se ven de color marrón o verde.
La capa binaria de agua (B02_BWTR), superpuesta sobre la imagen, sombrearía de blanco todas las áreas azules, creando un mapa simple de agua sí/no.
En cambio, la capa de confianza (B03_CONF) funcionaría como una transparencia superpuesta sobre la imagen, con áreas blancas sólidas donde la confianza es alta y transparencia creciente hacia el negro donde la confianza es baja. Esto te permite ver dónde el sistema DSWx-HLS está más seguro de que sus predicciones de agua son correctas.
Al combinar estas capas, los científicos y los trabajadores humanitarios pueden obtener una imagen clara de la extensión de las inundaciones y priorizar los esfuerzos de rescate y recuperación.

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Configurar el ambiente de trabajo

A COMPLETAR.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
ESTO HAY QUE DEFINIRLO A PARTIR DE LA MODIFICACIÓN DE LAS NOTEBOOKS. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Vamos a la notebook XXXXX.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Selección del área de interés (AOI)

- Inicializar parámetros definidos por el usuario.  
- Relizar una búsqueda de datos específicos en la NASA. 
- Buscar imágenes dentro de colección DSWx-HLS que coincidan con el AOI.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
A continuación, aprenderás a:

1. Inicializar parámetros definidos por el usuario:

* Define la zona de búsqueda: Dibuja un rectángulo en el mapa para indicar el área donde quieres buscar datos.
* Establece el periodo de búsqueda: Marca la fecha de inicio y de fin para acotar los resultados a un rango de tiempo específico.
* Muestra los parámetros: Imprime en la pantalla los detalles de la zona de búsqueda y las fechas elegidas para que puedas verificarlos.

2. Realizar la búsqueda de datos específicos en la NASA:

* Se conecta a la base de datos: Enlaza con la API CMR-STAC de la NASA para poder acceder a sus archivos.
* Especifica la colección: Indica que quiere buscar datos de la colección "OPERA_L3_DSWX-HLS_PROVISIONAL_V0".
* Realiza la búsqueda: Filtra los resultados según la zona de búsqueda, las fechas y un límite máximo de 1000 resultados.

3. Buscar imágenes (de la colección DSWx-HLS) que coincidan con el área de interés:

* Mide la superposición: Calcula cuánto se solapa cada imagen con el área que te interesa.
* Muestra los porcentajes: Imprime en la pantalla estos porcentajes para que puedas ver la cobertura.
* Filtra las imágenes: Selecciona solo aquellas que tengan una superposición mayor a un límite establecido.


<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Vamos a la notebook XXXXX.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Actividad 1: 

Modifica los parámetros XXX para definir una nueva área de interés. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Búsqueda y obtención de datos

- Transformar los datos filtrados en una lista. 
- Mostrar los detalles del primer resultado:
    - Contar los resultados. 
    - Mostrar superposición. 
    - Indicar nubosidad. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
En la siguiente sección aprenderás:

1. Cómo transformar los resultados filtrados en una lista para poder trabajar con ellos más fácilmente.
2. Cómo mostrar los detalles del primer resultado para ver cómo es la información que contiene.
    - Contar los resultado: cuántos archivos se encontraron después de aplicar los filtros.
    - Mostrar la superposición: cuánto se solapa cada archivo con la zona que buscas, para que sepas qué tan bien cubren el área.
    - Indicar la nubosidad: cantidad de nubes que había en cada archivo antes de filtrarlo, para que puedas considerar si la cobertura de nubes es un factor importante para ti.



<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Vamos a la notebook XXXX. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Actividad 2:

A DEFINIR
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Análisis de datos

A DEFINIR
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Vamos a la notebook XXXX. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Actividad 3:

A DEFINIR
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Procesamiento y visualización

A DEFINIR
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Vamos a la notebook XXXX.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Actividad 4:

A DEFINIR
<!-- #endregion -->

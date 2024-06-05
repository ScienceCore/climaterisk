---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.2
  kernelspec:
    display_name: opera_app_dev
    language: python
    name: python3
---

<!-- #region id="Ii5lh32eyTz_" -->
# **Introducción a la generación de mapas de inundaciones utilizando datos de teledetección**
**Guía para principiantes:** Este tutorial te enseñará cómo consultar y trabajar con los datos provisionales de OPERA DSWx-HLS desde la nube . Para conocer más sobre los datos utilizados en esta notebook, podes acceder a [OPERA_L3_DSWX-HLS_PROVISIONAL_V0](https://dx.doi.org/10.5067/OPDSW-PL3V0) )



<!-- #endregion -->

<!-- #region id="NMdZpg37zMG6" -->



**Cómo empezar con los mapas de agua utilizando el dataset de OPERA DSWx-HLS:**
Esta guía te muestrará cómo explorar los cambios en el agua en todo el mundo utilizando herramientas basadas en la nube. Usaremos OPERA DSWx-HLS, un conjunto de datos, obtenidos mediante teledetección, que rastrea la extensión de agua desde febrero de 2019 hasta septiembre de 2022 (ACTUALIZAR RANGO DE FECHA).

**1. Conectándote a la información desde la nube:**

Accederás a imágenes optimizadas de la Tierra (llamadas COG) directamente desde la nube, sin descargas pesadas.
Usarás un catálogo espacial súper práctico, denominado Catálogo de Activos Espaciales y Temporales de CMR (CMR-STAC), para encontrar las imágenes que necesitas, como si buscaras un libro en una biblioteca.

**2. Explorando los datos de los productos OPERA DSWx-HLS:**

Trabajarás con imágenes provisionales de la extensión de agua en la superficie terrestre (OPERA_L3_DSWX-HLS_PROVISIONAL_V0), recopiladas entre febrero de 2019 y septiembre de 2022, ¡una buena cantidad de información! (ACTUALIZAR RANGO DE FECHA). Dichas imágenes combinan lo mejor de dos satélites: Landsat 8 y Sentinel-2A/B, para una visión más completa.
Además, tendrás acceso a 10 capas de información por imagen, incluyendo clasificación de agua, confianza en los datos, cobertura del suelo, sombras del terreno, nubes, ¡y más!

**3. Visualizando los datos a tu gusto:**

Aprenderás a visualizar estas imágenes de la forma que más te convenga para analizarlas.


**Inundaciones en Pakistán con DSWx-HLS: Un ejemplo práctico**

En 2022, las lluvias monzónicas de Pakistán alcanzaron niveles récord, provocando devastadoras inundaciones y deslizamientos de tierra que afectaron a las cuatro provincias del país y a alrededor del 14% de su población [CDP]. En este ejemplo, te mostramos cómo el sistema DSWx-HLS puede usarse para mapear la extensión de las inundaciones causadas por el monzón en septiembre de 2022.

Capas del conjunto de datos científico (SDS):
DSWx-HLS nos brinda capas de información que nos permiten visualizar y analizar la situación con mayor detalle.
1. **B02_BWTR (Capa binaria de agua):**
Esta capa nos brinda una imagen simple de las áreas inundadas. Donde hay agua, la capa vale 1 (blanco) y donde no hay agua, toma valor 0 (negro). Es como un mapa binario de las inundaciones, ideal para obtener una visión general rápida de la extensión del desastre.
2. **B03_CONF (Capa de confianza):**
Esta capa nos indica qué tan seguro está el sistema DSWx-HLS de sus predicciones de agua. Donde la capa muestra valores altos (cerca de 100%), podemos estar muy seguros de que hay agua. En áreas con valores más bajos, la confianza disminuye, lo que significa que lo que parece agua podría ser otra cosa, como sombras o nubes.

Para ayudarte a visualizar mejor cómo funciona esto piensa en una imagen satelital de la zona afectada por las inundaciones. Las áreas con agua se ven azul oscuro, mientras que las áreas secas se ven de color marrón o verde.
La capa binaria de agua (B02_BWTR), superpuesta sobre la imagen, sombrearía de blanco todas las áreas azules, creando un mapa simple de agua sí/no.
En cambio, la capa de confianza (B03_CONF) funcionaría como una transparencia superpuesta sobre la imagen, con áreas blancas sólidas donde la confianza es alta y transparencia creciente hacia el negro donde la confianza es baja. Esto te permite ver dónde el sistema DSWx-HLS está más seguro de que sus predicciones de agua son correctas.
Al combinar estas capas, los científicos y los trabajadores humanitarios pueden obtener una imagen clara de la extensión de las inundaciones y priorizar los esfuerzos de rescate y recuperación.

**Recuerda:**
DSWx-HLS es una herramienta poderosa, pero los datos no son perfectos. Siempre es importante tener en cuenta la capa de confianza al interpretar los resultados.
Este es solo un ejemplo de cómo se puede usar DSWx-HLS para mapear las inundaciones. Hay muchas otras aplicaciones potenciales para este sistema.

**Qué necesitas:**
- Una computadora con acceso a Internet
(Opcional)
- Conocimientos básicos de mapas e imágenes satelitales

**Bono:** Para obtener más detalles técnicos, consulta el documento de especificación del [producto OPERA](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf).

<!-- #endregion -->

<!-- #region id="HtKY5dao0m66" -->

# **¡Antes de empezar!**

Para estar preparado paa el tutorial y aprovechar al máximo, por favor revisa la sección` 1_Primeros pasos.md.`


<!-- #endregion -->

<!-- #region id="DUqf_BgZ0CSD" -->

## **Parte 1: Setear el Ambiente de Trabajo**
<!-- #endregion -->

<!-- #region id="hiKMPoJq0CSD" -->


### **1.1 Importar Paquetes**
<!-- #endregion -->

<!-- #region id="bwthxJRN3stl" -->
El código Python %load_ext autoreload y %autoreload 2 habilitan la recarga automática de módulos en un cuaderno de Jupyter. Esto significa que si modifica un módulo que ha importado en su cuaderno, los cambios se reflejarán automáticamente en su cuaderno sin tener que reiniciarlo.
<!-- #endregion -->

<!-- #region id="pT1s6zEy3uip" -->
En la siguiente sección se importa una variedad de bibliotecas y herramientas que permiten:
* Obtener datos geoespaciales de diferentes fuentes.
* Procesar y analizar estos datos.
* Crear visualizaciones estáticas e interactivas para explorar y comunicar los resultados.


<!-- #endregion -->

```python id="4-SnwjZJ0CSF" outputId="884b26b5-08a3-45d3-9570-1a27e6a1dd2c"
import os
from netrc import netrc
from subprocess import Popen
from platform import system
from getpass import getpass

from pystac_client import Client
from pystac_client import ItemSearch

import json

import matplotlib.pyplot as plt
from matplotlib import cm
from datetime import datetime
from tqdm import tqdm

from shapely.geometry import box
from shapely.geometry import shape
from shapely.ops import transform

import numpy as np
import pandas as pd
import geopandas as gpd
from skimage import io

from osgeo import gdal
from rioxarray.merge import merge_arrays

import pyproj
from pyproj import Proj

import folium
from folium import plugins
import geoviews as gv
import hvplot.xarray
import holoviews as hv
hv.extension('bokeh')
gv.extension('bokeh', 'matplotlib')

import sys
sys.path.append('../../')
from src.dswx_utils import intersection_percent, colorize, getbasemaps, transform_data_for_folium

import warnings
warnings.filterwarnings('ignore')
```

<!-- #region id="zS82xJxi0CSH" -->

### **1.2 Setear el Ambiente de Trabajo**
<!-- #endregion -->

<!-- #region id="ovo0W8xW3JcA" -->
El código siguiente proporciona instrucciones para establecer el entorno de trabajo. Primero, se obtiene la ruta del directorio de trabajo actual y luego se define como directorio de trabajo.
<!-- #endregion -->

```python id="zS09y7Ff0CSH"
inDir = os.getcwd()
```

<!-- #region id="lkPCUGEs0CSI" -->


### **1.3 Generar token de autenticación**

<!-- #endregion -->

<!-- #region id="pd0nj_CY5h8I" -->
Este código te ayuda a acceder a datos de la NASA de forma segura:

* Revisa si ya guardaste tus datos de acceso: Si encuentra tu usuario y contraseña guardados, los usa automáticamente.
* Si es necesario, pide tu usuario y contraseña: Si no encuentra tus datos, te pide ingresarlos para guardarlos de forma segura para la próxima vez.
* Genera un token de autenticación: Este token permite que el código acceda a los datos de la NASA sin que tengas que ingresar tu usuario y contraseña cada vez.
<!-- #endregion -->

```python id="UXe44Ncb0CSI"
# Generates authentication token
# Asks for your Earthdata username and password for first time, if netrc does not exists in your home directory.

urs = 'urs.earthdata.nasa.gov'    # Earthdata URL endpoint for authentication
prompts = ['Enter NASA Earthdata Login Username: ',
           'Enter NASA Earthdata Login Password: ']

# Determine the OS (Windows machines usually use an '_netrc' file)
netrc_name = "_netrc" if system()=="Windows" else ".netrc"

# Determine if netrc file exists, and if so, if it includes NASA Earthdata Login Credentials
try:
    netrcDir = os.path.expanduser(f"~/{netrc_name}")
    netrc(netrcDir).authenticators(urs)[0]

```

<!-- #region id="jQkRQz2P58z2" -->
El siguiente código:
* Prepara el acceso a los datos en la nube: Guarda la información necesaria para conectarse a los datos de PODAAC en un archivo llamado "cookies.txt".
* Evita errores al buscar archivos: Le indica a la herramienta GDAL que no pierda tiempo buscando archivos en carpetas vacías.
* Se enfoca en los archivos que necesitas: Le dice a GDAL que solo trabaje con archivos que tengan la extensión TIF o TIFF.


<!-- #endregion -->

```python id="LkOCFmpm0CSJ"
# GDAL configurations used to successfully access PODAAC Cloud Assets via vsicurl
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')
```

<!-- #region id="CcSEXWZYyjPO" -->
# **Parte 2: Selección del Área de interés (AOI)**
<!-- #endregion -->

<!-- #region id="AY6x31sX0CSK" -->

## **2. API CMR-STAC: Búsqueda de datos basada en consultas espaciales** <a id="searchstac"></a>
<!-- #endregion -->

<!-- #region id="kXk3qSE60CSK" -->


### **2.1 Inicializar parámetros definidos por el usuario <a id="2.1"></a>**
<!-- #endregion -->

<!-- #region id="hakyfFya7m3F" -->
* Define la zona de búsqueda: Dibuja un rectángulo en el mapa para indicar el área donde quieres buscar datos.
* Establece el periodo de búsqueda: Marca la fecha de inicio y de fin para acotar los resultados a un rango de tiempo específico.
* Muestra los parámetros: Imprime en la pantalla los detalles de la zona de búsqueda y las fechas elegidas para que puedas verificarlos.
<!-- #endregion -->

```python id="bDyra8KD0CSK" outputId="2ca06a37-54b3-4ade-cc6b-761efe056c5f"
# USER-DEFINED PARAMETERS
aoi = box(67.4, 26.2, 68.0, 27.5)
start_date = datetime(2022, 1, 1)                                       # in 2022-01-01 00:00:00 format
stop_date = f"{datetime.today().strftime('%Y-%m-%d')} 23:59:59"         # in 2022-01-01 00:00:00 format
overlap_threshold = 10                                                  # in percent
#cloud_cover_threshold = 20                                             # in percent

print(f"Search between {start_date} and {stop_date}")
print(f"With AOI: {aoi.__geo_interface__}")
```

<!-- #region id="0uO50wXF74MV" -->
Este código busca datos específicos en la NASA:

* Se conecta a la base de datos: Enlaza con la API CMR-STAC de la NASA para poder acceder a sus archivos.
* Especifica la colección: Indica que quiere buscar datos de la colección "OPERA_L3_DSWX-HLS_PROVISIONAL_V0".
* Realiza la búsqueda: Filtra los resultados según la zona de búsqueda, las fechas y un límite máximo de 1000 resultados.
<!-- #endregion -->

```python id="ixhkdWNE0CSK"
# Search data through CMR-STAC API
stac = 'https://cmr.earthdata.nasa.gov/cloudstac/'    # CMR-STAC API Endpoint
api = Client.open(f'{stac}/POCLOUD/')
collections = ['OPERA_L3_DSWX-HLS_PROVISIONAL_V0']

search_params = {"collections": collections,
                 "intersects": aoi.__geo_interface__,
                 "datetime": [start_date, stop_date],
                 "max_items": 1000}
search_dswx = api.search(**search_params)
```

<!-- #region id="WQyuJWhv0CSL" -->

### **2.2 Búsqueda de imágenes (de la colección DSWx-HLS) que coincidan con el área de interés**
<!-- #endregion -->

<!-- #region id="oNa7hFHu-Dtu" -->
El siguiente código:

* Mide la superposición: Calcula cuánto se solapa cada imagen con el área que te interesa.
* Muestra los porcentajes: Imprime en la pantalla estos porcentajes para que puedas ver la cobertura.
* Filtra las imágenes: Selecciona solo aquellas que tengan una superposición mayor a un límite establecido.
<!-- #endregion -->

```python id="H9s93OUm0CSL" outputId="8c38f171-0034-42d8-a5c8-638d00827034"
# Filter datasets based on spatial overlap
intersects_geometry = aoi.__geo_interface__

#Check percent overlap values
print("Percent overlap before filtering: ")
print([f"{intersection_percent(i, intersects_geometry):.2f}" for i in search_dswx.items()])

# Apply spatial overlap and cloud cover filter # utilizamos la variable overloap definida anteriormente
dswx_filtered = (
    i for i in search_dswx.items() if (intersection_percent(i, intersects_geometry) > overlap_threshold)
)
```

<!-- #region id="HSZU2BmB1IZv" -->
# **Parte 3: Búsqueda y obtención de datos**

<!-- #endregion -->

<!-- #region id="6ejmlI7yCCRH" -->
El siguiente código:

1. Transforma los resultados filtrados en una lista para poder trabajar con ellos más fácilmente.
2. Muestra los detalles del primer resultado para ver cómo es la información que contiene.
<!-- #endregion -->

```python id="3BL5APaz0CSL" outputId="cdd13930-819a-4f1a-a087-bf182dc42c0f"
# Inspect the items inside the filtered query
dswx_data = list(dswx_filtered)
# Inspect one data
dswx_data[0].to_dict()
```

<!-- #region id="wL__Zq8YC329" -->
**A continuación, se muestra un resumen de los resultados de la búsqueda:**

* Cuenta los resultados: Te dice cuántos archivos encontró después de aplicar los filtros.
* Muestra la superposición: Te indica cuánto se solapa cada archivo con la zona que buscas, para que sepas qué tan bien cubren el área.
* Indica la nubosidad: Te informa la cantidad de nubes que había en cada archivo antes de filtrarlo, para que puedas considerar si la cobertura de nubes es un factor importante para ti.


<!-- #endregion -->

```python id="gGPdYpKc0CSM"
## Print search information
# Tota granules
print(f"Total granules after search filter: {len(dswx_data)}")

#Check percent overlap values
print("Percent-overlap: ")
print([f"{intersection_percent(i, intersects_geometry):.2f}" for i in dswx_data])

# Check percent cloud cover values
print("\nPercent cloud cover before filtering: ")
print([f"{i.properties['eo:cloud_cover']}" for i in search_dswx.items()])
```

<!-- #region id="Q9xi2biGKLVA" -->
# **Actividad práctica A**: Exploración y obtención del área de interés.
<!-- #endregion -->

<!-- #region id="pAW9vtLZ6z9y" -->
# **Parte 4: Análisis de los datos obtenidos**

Análisis de Series de tiempo con los datos de la zonade interés.
<!-- #endregion -->

<!-- #region id="fOrYeX9uKVs6" -->
# **Actividad práctica B: Series de tiempo aplicada al área de interés.**
<!-- #endregion -->

<!-- #region id="PYkoYYgB7BnC" -->
# **Parte 5: Procesamiento y visualización de los datos**
<!-- #endregion -->

<!-- #region id="i5lldnSVDb2s" -->
**Crea un mapa para que puedas ver cómo encajan los datos con tu zona de interés:**

* Dibuja los límites de los archivos: Traza los bordes de cada archivo encontrado en color azul para que puedas ver su forma y ubicación.
* Coloca un mapa de fondo: Agrega un mapa base de la zona para que tengas una referencia visual del terreno.
* Marca tu área de interés: Dibuja un rectángulo amarillo alrededor de la zona que especificaste en la búsqueda para que puedas ver cómo se superponen los archivos con ella.
* Muestra el mapa: Te presenta el mapa resultante para que puedas analizar la cobertura de los datos y la coincidencia con tu zona de interés.
<!-- #endregion -->

```python id="8hDY5sJD0CSM"
# Visualize the DSWx tile boundary and the user-defined bbox
geom_df = []
for d,_ in enumerate(dswx_data):
    geom_df.append(shape(dswx_data[d].geometry))

geom_granules = gpd.GeoDataFrame({'geometry':geom_df})
granules_poly = gv.Polygons(geom_granules, label='DSWx tile boundary').opts(line_color='blue', color=None, show_legend=True)

# Use geoviews to combine a basemap with the shapely polygon of our Region of Interest (ROI)
base = gv.tile_sources.EsriImagery.opts(width=1000, height=1000)

# Get the user-specified aoi
geom_aoi = shape(intersects_geometry)
aoi_poly = gv.Polygons(geom_aoi, label='User-specified bbox').opts(line_color='yellow', color=None, show_legend=True)

# Plot using geoviews wrapper
granules_poly*base*aoi_poly
```

<!-- #region id="hFxiVD8M0CSM" -->


### **5.1 Presentar los resultados de la búsqueda en una tabla <a id="2.3"></a>**
<!-- #endregion -->

<!-- #region id="owZ5qAmSDwGl" -->
Crea una tabla para que puedas revisar los resultados de forma organizada:

* Recorre los resultados: Lee cada uno de los archivos encontrados y extrae la información más relevante.
* Organiza los datos: Coloca la información en columnas para que sea fácil de leer y comparar:
ID del archivo
Sensor que lo capturó
Fecha de la captura
Coordenadas del archivo
Límites del área que cubre
Porcentaje de superposición con tu área de interés
Cobertura de nubes en el archivo
Enlaces para descargar las bandas del archivo
* Muestra la tabla: Te presenta la tabla completa para que puedas analizar los resultados y seleccionar los archivos que mejor se adapten a tus necesidades.
<!-- #endregion -->

```python id="uYhO2Ycs0CSM"
# Create table of search results
dswx_data_df = []
for item in dswx_data:
    item.to_dict()
    fn = item.id.split('_')
    ID = fn[3]
    sensor = fn[6]
    dat = item.datetime.strftime('%Y-%m-%d')
    spatial_overlap = intersection_percent(item, intersects_geometry)
    geom = item.geometry
    bbox = item.bbox

    # Take all the band href information
    band_links = [item.assets[links].href for links in item.assets.keys()]
    dswx_data_df.append([ID,sensor,dat,geom,bbox,spatial_overlap,cloud_cover,band_links])

dswx_data_df = pd.DataFrame(dswx_data_df, columns = ['TileID', 'Sensor', 'Date', 'Coords', 'bbox', 'SpatialOverlap', 'CloudCover', 'BandLinks'])
dswx_data_df
```

<!-- #region id="Ah4Kj7Hv0CSN" -->

## **5.2. Carga y visualización de la extensión de la inundación**
<!-- #endregion -->

<!-- #region id="9HcbKIiAEQE1" -->
Antes de avanzar, repasemos los pasos necesarios para visualizar la extensión de inundación:

1. **Obtención de los datos de inundación:**

 En este ejemplo se utilizan imágenes satelitales del sitio de la NASA.
En cuanto al formato de datos, existen diferentes tipos como ráster, shapefile, KML, o GeoJSON. En nuestro caso, trabajamos con ráster.

2. **Carga de datos:**

  Utilizamos las bibliotecas como GDAL o rasterio en Python para cargar los datos de inundación.

3. **Visualización la extensión de inundación:**

  Simbología: Es necesario, asignar un color y transparencia apropiados a las áreas inundadas para diferenciarlas del terreno seco. Puedes usar una escala de colores para representar la profundidad de la inundación.

  Superposición: Superpone la extensión de inundación sobre un mapa base, como una imagen aérea o un mapa topográfico, para proporcionar contexto geográfico.
También será de utilidad añadir leyendas, escalas, rótulos y otros elementos gráficos para mejorar la claridad y la interpretación del mapa.

  Ejemplo de visualización:

  [Imagen de un mapa que muestra la extensión de inundación en una ciudad. Las áreas inundadas están representadas en azul claro, con mayor transparencia para las zonas de menor profundidad. El mapa base es una imagen aérea y se incluyen una leyenda, una escala y rótulos.][Agregar imagen]
<!-- #endregion -->

<!-- #region id="PYA0TNiC0CSN" -->

### **5.2.1 Cargar B02-BWTR (Capa binaria de agua) y B03-CONF (Capa de confianza)**
<!-- #endregion -->

<!-- #region id="TTbd0M88E2PX" -->
Para cargar estas capas, necesitarás un programa compatible con el formato de los datos y las herramientas específicas de carga. Utilizamos GDAL y Rasterio para el procesamiento de imágenes comunes que te permitirán cargar estas capas.

<!-- #endregion -->

```python id="dCH6j5wp0CSN"
# Take one of the flooded dataset and check what files are included.
dswx_data_df.iloc[43].BandLinks
```

<!-- #region id="_-TlWOrh0CSN" -->

### **5.2.2 "Fusionar mosaicos".**
<!-- #endregion -->

<!-- #region id="14TeUFMeFOQ1" -->
"Fusionar mosaicos". Esta frase se refiere a la acción de combinar dos o más mosaicos de datos para crear un mosaico más grande.

En el contexto de imágenes satelitales, los mosaicos son imágenes individuales que se superponen para cubrir un área más grande. La fusión de mosaicos se utiliza a menudo para crear imágenes de mayor resolución espacial o temporal que las que se pueden obtener a partir de un solo mosaico.

Para fusionar mosaicos, se necesitan dos o más mosaicos que tengan el mismo formato y resolución. Los mosaicos se pueden fusionar utilizando un software de SIG o una biblioteca de procesamiento de imágenes.
<!-- #endregion -->

<!-- #region id="b5Co7WspF03R" -->
El código está preparando imágenes para mostrarlas en un mapa interactivo.Imagina que tienes un rompecabezas que quieres armar en un mapa. Entonces, el código hace lo siguiente:

* Busca las piezas correctas: Encuentra las imágenes del 30 de septiembre que muestran dónde hay agua (capa B02-BWTR) y qué tan confiable es esa información (capa B03-CONF).

* Prepara las piezas: Adapta las imágenes para que encajen en el mapa (como si estuvieras recortando los bordes del rompecabezas para que calcen bien).
Las coloca en la posición correcta sobre el mapa (como ir poniendo las piezas en su lugar).

* Une las piezas: Combina las imágenes separadas para crear una vista completa, como si unieras las piezas del rompecabezas.

* Revisa una pieza: Mira de cerca una de las imágenes para asegurarse de que todo esté bien (como revisar una pieza del rompecabezas antes de seguir armando).
<!-- #endregion -->

```python id="V4mhzgDZ0CSN"
# Get B02-BWTR layer for tiles acquired on 2022-09-30, project to folium's projection and merge tiles
T42RUR_B02, T42RUR_B02_cm = transform_data_for_folium(dswx_data_df.iloc[42].BandLinks[1])
T42RUQ_B02, T42RUQ_B02_cm = transform_data_for_folium(dswx_data_df.iloc[43].BandLinks[1])
merged_B02 = merge_arrays([T42RUR_B02, T42RUQ_B02])

# Get B03-CONF layer for tiles acquired on 2022-09-30, project to folium's projection and merge tiles
T42RUR_B03, T42RUR_B03_cm = transform_data_for_folium(dswx_data_df.iloc[42].BandLinks[2])
T42RUQ_B03, T42RUQ_B03_cm = transform_data_for_folium(dswx_data_df.iloc[43].BandLinks[2])
merged_B03 = merge_arrays([T42RUR_B03, T42RUQ_B03])

# Check one of the DataArrays
merged_B02
```

<!-- #region id="3n4QkYKP0CSO" -->


### **5.3 Visualiza las imágenes en un mapa interactivo**
<!-- #endregion -->

<!-- #region id="bB355oMFGCxp" -->
 El código está prepara los colores para que las imágenes sean claras y fáciles de interpretar. Podes imagianr que tenes un libro para colorear con áreas numeradas, y cada número corresponde a un color específico. El código está haciendo lo siguiente:

  - Toma los dibujos en blanco y negro: Busca las imágenes que ya preparó (las que muestran el agua y la confianza).
  - Encuentra la paleta de colores adecuada: Tiene la lista de colores que se deben usar para cada área de las imágenes (como la lista de colores del libro para colorear).
  - Pinta cuidadosamente cada área: Asigna los colores correctos a cada zona de las imágenes, siguiendo la paleta elegida.
  - Guarda los dibujos coloreados: Almacena las imágenes ya coloreadas para usarlas en el mapa.

<!-- #endregion -->

```python id="RLcoFzy10CSO"
# Colorize the map using  predefined colors from DSWx for Folium display
colored_B02,cmap_B02 = colorize(merged_B02[0], cmap=T42RUR_B02_cm)
colored_B03,cmap_B03 = colorize(merged_B03[0], cmap=T42RUR_B03_cm)
```

<!-- #region id="YkwRntd6GDKu" -->

Imagina que estás creando un mapa interactivo con capas superpuestas, el código está haciendo lo siguiente:

* Extiende el lienzo: Despliega un mapa base sobre la mesa, como un mapamundi,
para tener un fondo sobre el que trabajar.

* Agrega mapas extra: Coloca varios mapas transparentes encima del mapa base, como si fueran hojas de acetato. Así, podrás elegir la vista que más te guste.

* Dibuja las áreas inundadas: En una de las hojas transparentes, pinta con colores llamativos las zonas donde hay agua, para que se vean claramente.

* Marca la confianza en la información: En otra hoja transparente, dibuja con colores más tenues la confianza que se tiene en los datos de las áreas inundadas, como si fuera una pista extra para los más aventureros.

* Añade herramientas útiles: Coloca sobre la mesa una lupa para ampliar zonas, un botón para ver el mapa en pantalla completa y una mini versión del mapa en una esquina, como si fuera una brújula.

* Muestra las coordenadas: Activa un indicador que te dice en qué lugar del mapa estás apuntando en cada momento, como si fuera una guía de coordenadas.
<!-- #endregion -->

```python id="AP5r2kHN0CSQ"
# Initialize Folium basemap
xmid =(merged_B02.x.values.min()+merged_B02.x.values.max())/2 ; ymid = (merged_B02.y.values.min()+merged_B02.y.values.max())/2
m = folium.Map(location=[ymid, xmid], zoom_start=9, tiles='CartoDB positron', show=True)

# Add custom basemaps
basemaps = getbasemaps()
for basemap in basemaps:
    basemaps[basemap].add_to(m)

# Overlay B02 and B03 layers
folium.raster_layers.ImageOverlay(colored_B02,
                                        opacity=0.6,
                                        bounds=[[merged_B02.y.values.min(),merged_B02.x.values.min()],[merged_B02.y.values.max(),merged_B02.x.values.max()]],
                                        name='Flooded Area',
                                        show=True).add_to(m)

folium.raster_layers.ImageOverlay(colored_B03,
                                        opacity=0.8,
                                        bounds=[[merged_B03.y.values.min(),merged_B03.x.values.min()],[merged_B03.y.values.max(),merged_B03.x.values.max()]],
                                        name='Confidence Layer',
                                        show=False).add_to(m)

#layer Control
m.add_child(folium.LayerControl())

# Add fullscreen button
plugins.Fullscreen().add_to(m)

#Add inset minimap image
minimap = plugins.MiniMap(width=300, height=300)
m.add_child(minimap)

#Mouse Position
fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
plugins.MousePosition(position='bottomright', separator=' | ', prefix="Lat/Lon:",
                     lat_formatter=fmtr, lng_formatter=fmtr).add_to(m)

#Display
m
```

<!-- #region id="YW7hZ3CZKtJL" -->
# **Actividad práctica C: Visualización de la extensión de agua en el área seleccionada**
<!-- #endregion -->

```python id="hdF6iHO5Ljzz"

```

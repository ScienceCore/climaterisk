---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: "1.3"
      jupytext_version: 1.16.2
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Uso de la API PySTAC

<!-- #region jupyter={"source_hidden": true} -->

En el [Earthdata Search website](https://search.earthdata.nasa.gov) (sitio web Earthdata Search) de la NASA se puede buscar gran cantidad de datos. El enlace anterior se conecta a una interfaz gráfica de usuario para buscar en [SpatioTemporal Asset Catalogs (STACs)](https://stacspec.org/) (catálogos de activos espaciotemporales (STAC)) al especificar una área de interés (AOI) y una _ventana temporal_ o un _intervalo de fechas_.

Por motivos de reproducibilidad, queremos ser capaces de buscar en los catálogos de activos mediante programación. Aquí es donde entra en juego la biblioteca [PySTAC](https://pystac.readthedocs.io/en/stable/).

<!-- #endregion -->

---

## Esquema de las etapas del análisis

<!-- #region jupyter={"source_hidden": true} -->

- Identificación de los parámetros de búsqueda
  - AOI, ventana temporal
  - Endpoint, proveedor, identificador del catálogo ("nombre corto")
- Obtención de los resultados de la búsqueda
  - Instrospección, análisis para identificar características, bandas de interés
  - Envolver los resultados en un DataFrame para facilitar la exploración
- Explorar y refinar los resultados de la búsqueda
  - Identificar los gránulos de mayor valor
  - Filtrar los gránulos extraños con una contribución mínima
  - Reunir los gránulos filtrados correspondientes en un DataFrame
  - Identificar el tipo de resultado que se quiere generar
- Procesamiento de los datos para generar resultados relevantes
  - Descargar los gránulos relevantes en Xarray DataArray, apilados adecuadamente
  - Llevar a cabo los cálculos intermedios necesarios
  - Ensamblar los fragmentos de datos relevantes en la visualización

<!-- #endregion -->

---

## Identificar los parámetros de búsqueda

### Definir el AOI y el rango de fechas

<!-- #region jupyter={"source_hidden": true} -->

Empezaremos tomando en cuenta un ejemplo concreto. [Heavy rains severely impacted Southeast Texas in May 2024](https://www.texastribune.org/2024/05/03/texas-floods-weather-harris-county/) (Fuertes lluvias afectaron gravemente al sureste de Texas en mayo del 2024), provocando [flooding and causing significant damage to property and human life](https://www.texastribune.org/series/east-texas-floods-2024/) (inundaciones y causando importantes daños materiales y humanos).

Como es usual, se requieren ciertas importaciones relevantes. Las dos primeras celdas son familiares (relacionadas con las herramientas de análisis y la visualización de los datos que ya se examinaron). La tercera celda incluye importaciones de la biblioteca `pystac_client` y de la biblioteca `gdal`, seguidas de algunos ajustes necesarios para utilizar la [GDAL (the Geospatial Data Abstraction Library)](https://gdal.org) (Biblioteca de Abstracción de Datos Geoespaciales). Estos detalles en la configuración permiten que las sesiones de tu cuaderno interactúen sin problemas con las fuentes remotas de datos geoespaciales.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')
# data wrangling imports
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rio
import rasterio
```

```python jupyter={"source_hidden": true}
# Imports for plotting
import hvplot.pandas
import hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```python jupyter={"source_hidden": true}
# STAC imports to retrieve cloud data
from pystac_client import Client
from osgeo import gdal
# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')
```

<!-- #region jupyter={"source_hidden": true} -->

A continuación, definiremos los parámetros de búsqueda geográfica para poder recuperar los datos correspondientes a ese evento de inundación. Esto consiste en especificar un _área de interés (AOI)_ y un _intervalo de fechas_.

- El AOI se especifica como un rectángulo de coordenadas de longitud-latitud en una única 4-tupla con la forma
  $$({\mathtt{longitude}}_{\mathrm{min}},{\mathtt{latitude}}_{\mathrm{min}},{\mathtt{longitude}}_{\mathrm{max}},{\mathtt{latitude}}_{\mathrm{max}}),$$
  por ejemplo, las coordenadas de la esquina inferior izquierda seguidas de las coordenadas de la esquina superior derecha.
- El intervalo de fechas se especifica como una cadena de la forma
  $${\mathtt{date}_{\mathrm{start}}}/{\mathtt{date}_{\mathrm{end}}},$$
  donde las fechas se especifican en el formato estándar `YYYY-MM-DD`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Center of the AOI
livingston_tx_lonlat = (-95.09,30.69) # (lon, lat) form
```

<!-- #region jupyter={"source_hidden": true} -->

Escribiremos algunas funciones cortas para encapsular la lógica de nuestros flujos de trabajo genéricos. Para el código de investigación, estas se colocarían en archivos de módulos Python. Por conveniencia, incrustaremos las funciones en este cuaderno y otras para que puedan ejecutarse correctamente con dependencias mínimas.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
# simple utility to make a rectangle with given center of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding-box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

```python jupyter={"source_hidden": true}
# simple utility to plot an AOI or bounding-box
def plot_bbox(bbox):
    '''Given bounding-box, returns GeoViews plot of Rectangle & Point at center
    + bbox: bounding-box specified as (lon_min, lat_min, lon_max, lat_max)
    Assume longitude-latitude coordinates.
    '''
    # These plot options are fixed but can be over-ridden
    point_opts = opts.Points(size=12, alpha=0.25, color='blue')
    rect_opts = opts.Rectangles(line_width=0, alpha=0.1, color='red')
    lon_lat = (0.5*sum(bbox[::2]), 0.5*sum(bbox[1::2]))
    return (gv.Points([lon_lat]) * gv.Rectangles([bbox])).opts(point_opts, rect_opts)
```

```python jupyter={"source_hidden": true}
AOI = make_bbox(livingston_tx_lonlat, 0.5, 0.25)
basemap = gv.tile_sources.OSM.opts(width=500, height=500)
plot_bbox(AOI) * basemap
```

<!-- #region jupyter={"source_hidden": true} -->

Agreguemos un intervalo de fechas. Las inundaciones ocurrieron principalmente entre el 30 de abril y el 2 de mayo. Estableceremos una ventana temporal más larga que cubra los meses de abril y mayo.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
start_date, stop_date = '2024-04-01', '2024-05-31'
DATE_RANGE = f'{start_date}/{stop_date}'
```

<!-- #region jupyter={"source_hidden": true} -->

Por último, crearemos un un diccionario `search_params` que almacene el AOI y el intervalo de fechas. Este diccionario se utilizará para buscar datos en los STAC.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

---

## Obtención de los resultados de búsqueda

### Ejecución de una búsqueda con la API PySTAC

<!-- #region jupyter={"source_hidden": true} -->

Para iniciar una búsqueda de datos se necesitan tres datos más: el _Endpoint_ (una URL), el _Proveedor_ (una cadena que representa una ruta que extiende el Endpoint) y los _Identificadores de la colección_ (una lista de cadenas que hacen referencia a catálogos específicos). Generalmente, debemos experimentar con [Earthdata Search website](https://search.earthdata.nasa.gov) (sitio web Earthdata Search) de la NASA para determinar correctamente estos valores para los productos de los datos específicos que queremos recuperar. El [NASA CMR STAC GitHub repository also monitors issues](https://github.com/nasa/cmr-stac/issues) (repositorio de GitHub de la NASA CMR STAC también supervisa los problemas) relacionados con la API para las consultas de búsqueda de EarthData Cloud.

Para la búsqueda de productos de datos DSWx que queremos ejecutar, estos parámetros son los que se definen en la siguiente celda de código.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac' # base URL for the STAC to search
PROVIDER = 'POCLOUD'
COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

<!-- #region jupyter={"source_hidden": true} -->

Una vez que se definieron los parámetros de búsqueda en el diccionario de Python `search_params`, podemos instanciar un `Cliente` y buscar en el catálogo espacio-temporal de activos utilizando el método `Client.search`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
print(f'{type(search_results)=}\n',search_results)
```

<!-- #region jupyter={"source_hidden": true} -->

El objeto `search_results` que se obtuvo al llamar al método `search` es del tipo `ItemSearch`. Para recuperar los resultados, invocamos el método `items` y lanzamos el resultado como una `list` de Python que enlazaremos con los gránulos identificadores.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
granules = list(search_results.items())
print(f"Number of granules found with tiles overlapping given AOI: {len(granules)}")
```

<!-- #region jupyter={"source_hidden": true} -->

Analicemos el contenido de la lista `granules`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
granule = granules[0]
print(f'{type(granule)=}')
```

```python jupyter={"source_hidden": true}
granule
```

<!-- #region jupyter={"source_hidden": true} -->

El objeto `granule` tiene una representación de salida enriquecida en este cuaderno de Jupyter. Podemos ampliar los atributos en la celda de salida haciendo clic en los triángulos.

![](../assets/granule_output_repr.png)

El término _gránulo_ se refiere a una colección de archivos de datos (datos ráster en este caso), todos ellos asociados a datos sin procesar adquiridos por un satélite concreto en una fecha y hora fijas sobre un mosaico geográfico concreto. Hay una gran variedad de atributos interesantes asociados con este gránulo.

- properties['datetime']: una cadena que representa la hora de adquisición de los datos de los archivos de datos ráster de este gránulo,
- properties['eo:cloud_cover']: el porcentaje de píxeles oscurecidos por nubes y sombras de nubes en los archivos de datos ráster de este gránulo, y
- `assets`: un `dict` de Python cuyos valores resumen las bandas o niveles de los datos ráster asociados con este gránulo.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(f"{type(granule.properties)=}\n")
print(f"{granule.properties['datetime']=}\n")
print(f"{granule.properties['eo:cloud_cover']=}\n")
print(f"{type(granule.assets)=}\n")
print(f"{granule.assets.keys()=}\n")
```

<!-- #region jupyter={"source_hidden": true} -->

Cada objeto en `granule.assets` es una instancia de la clase `Asset` que tiene un atributo `href`. Es el atributo `href` el que nos indica dónde localizar un archivo GeoTiff asociado con este activo de este gránulo.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
for a in granule.assets:
    print(f"{a=}\t{type(granule.assets[a])=}")
    print(f"{granule.assets[a].href=}\n\n")
```

<!-- #region jupyter={"source_hidden": true} -->

Además, el `Item` tiene un atributo `.id` que almacena una cadena. Al igual que ocurre con los nombres de archivo asociados a los productos OPERA, esta cadena `.id` contiene el identificador de un mosaico geográfico MGRS. Podemos extraer ese identificador aplicando manipulaciones de cadenas de Python al atributo `.id` del gránulo. Hagámoslo y almacenemos el resultado en `tile_id`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(granule.id)
tile_id = granule.id.split('_')[3]
print(f"{tile_id=}")
```

---

### Resumiendo los resultados de la búsqueda en un DataFrame

<!-- #region jupyter={"source_hidden": true} -->

Los detalles de los resultados de la búsqueda son complicados de analizar de esta manera. Vamos a extraer algunos campos concretos de los gránulos obtenidos en un Pandas `DataFrame` utilizando una cómoda función de Python. Definiremos la función aquí y la reutilizaremos en cuadernos posteriores.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
# utility to extract search results into a Pandas DataFrame
def search_to_dataframe(search):
    '''Constructs Pandas DataFrame from PySTAC Earthdata search results.
    DataFrame columns are determined from search item properties and assets.
    'asset': string identifying an Asset type associated with a granule
    'href': data URL for file associated with the Asset in a given row.'''
    granules = list(search.items())
    assert granules, "Error: empty list of search results"
    props = list({prop for g in granules for prop in g.properties.keys()})
    tile_ids = map(lambda granule: granule.id.split('_')[3], granules)
    rows = (([g.properties.get(k, None) for k in props] + [a, g.assets[a].href, t])
                for g, t in zip(granules,tile_ids) for a in g.assets )
    df = pd.concat(map(lambda x: pd.DataFrame(x, index=props+['asset','href', 'tile_id']).T, rows),
                   axis=0, ignore_index=True)
    assert len(df), "Empty DataFrame"
    return df
```

<!-- #region jupyter={"source_hidden": true} -->

Invocar `search_to_dataframe` en `search_results` codifica la mayor parte de la información importante de la búsqueda como un Pandas `DataFrame`, tal como se muestra a continuación.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->

El método `DataFrame.info` nos permite examinar el esquema de este DataFrame.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
df.info()
```

<!-- #region jupyter={"source_hidden": true} -->

Vamos a limpiar el DataFrame de resultados de búsqueda. Esto podría estar incrustado en una función, pero, vale la pena saber cómo se hace esto interactivamente con Pandas.

En primer lugar, para estos resultados, solo es necesaria una columna `Datetime`, podemos eliminar las demás.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
df = df.drop(['start_datetime', 'end_datetime'], axis=1)
df.info()
```

<!-- #region jupyter={"source_hidden": true} -->

A continuación, arreglaremos el esquema del `DataFrame` `df` convirtiendo las columnas en tipos de datos sensibles. También será conveniente utilizar la marca de tiempo de la adquisición como índice del DataFrame. Hagámoslo utilizando el método `DataFrame.set_index`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
df['datetime'] = pd.DatetimeIndex(df['datetime'])
df['eo:cloud_cover'] = df['eo:cloud_cover'].astype(np.float16)
str_cols = ['asset', 'href', 'tile_id']
for col in str_cols:
    df[col] = df[col].astype(pd.StringDtype())
df = df.set_index('datetime').sort_index()
```

```python jupyter={"source_hidden": true}
df.info()
```

<!-- #region jupyter={"source_hidden": true} -->

Al final esto da un DataFrame con un esquema conciso que puede utilizarse para manipulaciones posteriores. Agrupar los resultados de la búsqueda STAC en un Pandas `DataFrame` de forma sensata es un poco complicado. Varias de las manipulaciones anteriores podrían haberse incluido en la función `search_to_dataframe`. Pero, dado que los resultados de búsqueda de la API STAC aún están evolucionando, actualmente es mejor ser flexible y utilizar Pandas de forma interactiva para trabajar con los resultados de búsqueda. Veremos esto con más detalle en ejemplos posteriores.

<!-- #endregion -->

---

## Explorar y refinar los resultados de búsqueda

<!-- #region jupyter={"source_hidden": true} -->

Si examinamos la columna numérica `eo:cloud_cover` del DataFrame `df`, podemos recopilar estadísticas utilizando agregaciones estándar y el método `DataFrame.agg`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
df['eo:cloud_cover'].agg(['min','mean','median','max'])
```

<!-- #region jupyter={"source_hidden": true} -->

Observa que hay varias entradas `nan` en esta columna. Las funciones de agregación estadística de Pandads suelen ser "`nan`-aware", esto significa que ignoran implícitamente las entradas `nan` ("Not-a-Number") al calcular las estadísticas.

<!-- #endregion -->

### Filtrado del DataFrame de búsqueda con Pandas

<!-- #region jupyter={"source_hidden": true} -->

Como primera operación de filtrado, vamos a mantener solo las filas para las que la cobertura en la nube es inferior al 50%.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
df_clear = df.loc[df['eo:cloud_cover']<50]
df_clear
```

<!-- #region jupyter={"source_hidden": true} -->

Para esta consulta de búsqueda, cada gránulo DSWX comprende datos ráster para diez bandas o niveles. Podemos ver esto aplicando el método Pandas `Series.value_counts` a la columna `asset`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
df_clear.asset.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->

Vamos a filtrar las filas que corresponden a la banda `B01_WTR` del producto de datos DSWx. El accesorio de Pandas `DataFrame.str` hace que esta operación sea sencilla. Llamaremos al `DataFrame` filtrado `b01_wtr`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
b01_wtr = df_clear.loc[df_clear.asset.str.contains('B01_WTR')]
b01_wtr.info()
b01_wtr.asset.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->

También podemos ver que hay varios mosaicos geográficos asociados a los gránulos encontrados que intersecan el AOI proporcionado.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
b01_wtr.tile_id.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->

Recuerda que estos códigos se refieren a mosaicos geográficos MGRS especificados en un sistema de coordenadas concreto. Como identificamos estos códigos en la columna `tile_id`, podemos filtrar las filas que corresponden, por ejemplo, a los archivos recopilados sobre el mosaico T15RUQ del MGRS:

<!-- #endregion -->

```python jupyter={"source_hidden": true}
b01_wtr_t15ruq = b01_wtr.loc[b01_wtr.tile_id=='T15RUQ']
b01_wtr_t15ruq
```

<!-- #region jupyter={"source_hidden": true} -->

Ahora tenemos un `DataFrame` `b01_wtr_t15ruq` mucho más corto que resume las ubicaciones remotas de los archivos (por ejemplo, GeoTiffs) que almacenan datos ráster para la banda de aguas superficiales `B01_WTR` en el mosaico MGRS `T15RUQ` recopilados en varias marcas de tiempo que se encuentran dentro de la ventana de tiempo que especificamos. Podemos utilizar este DataFrame para descargar esos archivos para su análisis o visualización.

<!-- #endregion -->

---

## Procesamiento de datos para obtener resultados relevantes

### Apilamiento de los datos

<!-- #region jupyter={"source_hidden": true} -->

Tenemos un `DataFrame` que identifica archivos remotos específicos de datos ráster. El siguiente paso es combinar estos datos ráster en una estructura de datos adecuada para el análisis. El Xarray `DataArray` es adecuado en este caso. La combinación puede generarse utilizando la función `concat` de Xarray. La función `urls_to_stack` en la siguiente celda es larga pero no complicada. Toma un `DataFrame` con marcas de tiempo en el índice y una columna etiquetada `href` de las URL, lee los archivos asociados a esas URL uno a uno, y apila las matrices bidimensionales relevantes de datos ráster en una matriz tridimensional.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
def urls_to_stack(granule_dataframe):
    '''Processes DataFrame of PySTAC search results (with OPERA tile URLs) &
    returns stacked Xarray DataArray (dimensions time, latitude, & longitude)'''
    
    stack = []
    for i, row in granule_dataframe.iterrows():
        with rasterio.open(row.href) as ds:
            # extract CRS string
            crs = str(ds.crs).split(':')[-1]
            # extract the image spatial extent (xmin, ymin, xmax, ymax)
            xmin, ymin, xmax, ymax = ds.bounds
            # the x and y resolution of the image is available in image metadata
            x_res = np.abs(ds.transform[0])
            y_res = np.abs(ds.transform[4])
            # read the data 
            img = ds.read()
            # Ensure img has three dimensions (bands, y, x)
            if img.ndim == 2:
                img = np.expand_dims(img, axis=0) 
            lon = np.arange(xmin, xmax, x_res)
            lat = np.arange(ymax, ymin, -y_res)
            bands = np.arange(img.shape[0])
            da = xr.DataArray(
                                data=img,
                                dims=["band", "lat", "lon"],
                                coords=dict(
                                            lon=(["lon"], lon),
                                            lat=(["lat"], lat),
                                            time=i,
                                            band=bands
                                            ),
                                attrs=dict(
                                            description="OPERA DSWx B01",
                                            units=None,
                                          ),
                             )
            da.rio.write_crs(crs, inplace=True)   
            stack.append(da)
    return xr.concat(stack, dim='time').squeeze()
```

```python jupyter={"source_hidden": true}
%%time
stack = urls_to_stack(b01_wtr_t15ruq)
```

```python jupyter={"source_hidden": true}
stack
```

### Producir una visualización de los datos

```python jupyter={"source_hidden": true}
#  Define a colormap with RGBA tuples
COLORS = [(150, 150, 150, 0.1)]*256  # Setting all values to gray with low opacity
COLORS[0] = (0, 255, 0, 0.1)         # Not-water class to green
COLORS[1] = (0, 0, 255, 1)           # Open surface water
COLORS[2] = (0, 0, 255, 1)           # Partial surface water
```

```python jupyter={"source_hidden": true}
image_opts = dict(
                   x='lon',
                   y='lat',
                   project=True,
                   rasterize=True,
                   cmap=COLORS, 
                   colorbar=False,
                   tiles = gv.tile_sources.OSM,
                   widget_location='bottom',
                   frame_width=500,
                   frame_height=500,
                   xlabel='Longitude (degrees)',
                   ylabel='Latitude (degrees)',
                   title = 'DSWx data for May 2024 Texas floods',
                   fontscale=1.25
                  )
```

<!-- #region jupyter={"source_hidden": true} -->

Trazar las imágenes totalmente puede consumir mucha memoria. Vamos a utilizar el método Xarray `DataArray.isel` para extraer un trozo del arreglo `stack` con menos píxeles. Esto permitirá un renderizado y desplazamiento rápidos.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
view = stack.isel(lon=slice(3000,None), lat=slice(3000,None))
view.hvplot.image(**image_opts)
```

```python jupyter={"source_hidden": true}
stack.hvplot.image(**image_opts) # Construct view from all slices.
```

<!-- #region jupyter={"source_hidden": true} -->

Antes de continuar, recuerda apagar el kernel de este cuaderno para liberar memoria para otros cálculos.

<!-- #endregion -->

---

<!-- #region jupyter={"source_hidden": true} -->

Este cuaderno proporciona principalmente un ejemplo para ilustrar el uso de la API PySTAC.

En cuadernos posteriores, utilizaremos este flujo de trabajo general:

1. Establecer una consulta de búsqueda mediante la identificación de un _AOI_ particular y un _intervalo de fechas_.
2. Identificar un _endpoint_, un _proveedor_ y un _catálogo de activos_ adecuados, y ejecutar la búsqueda utilizando `pystac.Client`.
3. Convertir los resultados de la búsqueda en un Pandas DataFrame que contenga los principales campos de interés.
4. Utilizar el DataFrame resultante para filtrar los archivos de datos remotos más relevantes necesarios para el análisis y/o la visualización.
5. Ejecutar el análisis y/o la visualización utilizando el DataFrame para recuperar los datos requeridos.

<!-- #endregion -->

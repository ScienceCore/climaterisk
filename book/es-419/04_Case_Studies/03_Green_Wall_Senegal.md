---
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

# La Gran Muralla Verde en Senegal

[La Gran Muralla Verde](https://es.wikipedia.org/wiki/Gran_muralla_verde_\(%C3%81frica\)) es un esfuerzo para combatir la expansión del desierto del Sahara mediante el crecimiento de vegetación de forma sistemática y científica. El [producto OPERA DIST-ALERT](https://lpdaac.usgs.gov/documents/1766/OPERA_DIST_HLS_Product_Specification_V1.pdf) también puede utilizarse para identificar cambios en el crecimiento de la vegetación (que impliquen causas naturales o, en este caso, antropogénicas).

<center>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Sahara_satellite_hires.jpg/800px-Sahara_satellite_hires.jpg">
</center>

***

## Esquema de las etapas del análisis

- Identificación de los parámetros de búsqueda (AOI, ventana de tiempo, _endpoint_, etc.)
- Obtención de los resultados de la búsqueda en un `DataFrame`
- Exploración y refinamiento de los resultados de la búsqueda
- Procesamiento de los datos para obtener resultados relevantes

En este caso, crearemos un DataFrame para resumir los resultados de la búsqueda, los reduciremos a un tamaño manejable y crearemos un control deslizante para analizar los datos recuperados.

***

### Importación preliminar

```{code-cell} python
from warnings import filterwarnings
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
import rasterio
```

```{code-cell} python
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```{code-cell} python
from pystac_client import Client
from osgeo import gdal
# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')
```

### Funciones de utilidad

```{code-cell} python
# simple utility to make a rectangle with given center of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding-box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

```{code-cell} python
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

```{code-cell} python
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

Estas funciones podrían incluirse en archivos modulares para proyectos de investigación más desarrollados. Para fines didácticos, se incluyen en este cuaderno computacional.

***

## Obtención de los resultados de búsqueda

La Gran Muralla Verde se extiende por el continente africano. Elegiremos un área de interés centrada en las coordenadas geográficas $(-16.0913^{\circ}, 16.528^{\circ})$ en Senegal. Analizaremos todos los datos disponibles desde enero de 2022 hasta finales de marzo de 2024. Usaremos los identificadores `AOI` y `DATE_RANGE` para utilizarlos eventualmente en una consulta de búsqueda PySTAC.

```{code-cell} python
AOI = make_bbox((-16.0913, 16.528), 0.1, 0.1)
DATE_RANGE = "2022-01-01/2024-03-31"
```

El gráfico que se genera a continuación ilustra el AOI. Las herramientas Bokeh Zoom son útiles para analizar la caja en varias escalas de longitud.

```{code-cell} python
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(padding=0.1, alpha=0.25)
plot_bbox(AOI) * basemap
```

```{code-cell} python
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

Para ejecutar la búsqueda, definimos la URI del punto final e instanciamos el objeto `Client`.

```{code-cell} python
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = 'LPCLOUD'
COLLECTIONS = ["OPERA_L3_DIST-ALERT-HLS_V1_1"]
search_params.update(collections=COLLECTIONS)
print(search_params)

catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

La búsqueda en sí es bastante rápida y arroja algunos miles de resultados que pueden analizarse más fácilmente en un  DataFrame de Pandas.

```{code-cell} python
%%time
df = search_to_dataframe(search_results)
df.info()
df.head()
```

Limpiaremos el `DataFrame` `df` como lo venimos haciendo de manera habitual:

- renombramos la columna `eo:cloud_cover` como `cloud_cover`,
- eliminamos las columnas `datetime` extrañas,
- convertimos las columnas en tipos de datos sensibles,
- convertimos la columna `datetime` en `DatetimeIndex`, y
- establecemos la columna `datetime` como `Index`.

```{code-cell} python
df = df.rename(columns={'eo:cloud_cover':'cloud_cover'})
df.cloud_cover = df.cloud_cover.astype(np.float16)
df = df.drop(['start_datetime', 'end_datetime'], axis=1)
df = df.convert_dtypes()
df.datetime = pd.DatetimeIndex(df.datetime)
df = df.set_index('datetime').sort_index()
```

```{code-cell} python
df.info()
```

El siguiente paso es identificar un conjunto con una cantidad menor de filas a partir de los resultados de la búsqueda con los que podamos trabajar más fácilmente.

***

## Exploración y refinamiento de los resultados de la búsqueda

Lo que queremos es la banda `VEG-DIST-STATUS` de los datos DIST-ALERT, así que debemos extraer solamente las filas del `df` asociadas a esa banda. Para ello, podemos construir una serie booleana `c1` que sea `True` siempre que la cadena de la columna `asset` incluya `VEG-DIST-STATUS` como subcadena. También podemos construir una serie booleana `c2` para filtrar las filas cuya `cloud_cover` exceda el 20%.

```{code-cell} python
c1 = df.asset.str.contains('VEG-DIST-STATUS')
```

```{code-cell} python
c2 = df.cloud_cover<20
```

Si analizamos la columna `tile_id`, podemos ver que un único mosaico MGRS contiene el AOI que especificamos. Como tal, todos los datos indexados en `df` corresponden a mediciones distintas tomadas de un mosaico geográfico fijo en diferentes momentos.

```{code-cell} python
df.tile_id.value_counts()
```

Podemos combinar la información anterior para reducir el `DataFrame` a una secuencia de filas mucho más pequeña. También podemos eliminar las columnas `asset` y `tile_id` porque serán las mismas en todas las filas después del filtrado. También podemos eliminar la columna `cloud_cover`, ya que en lo sucesivo solo necesitaremos la columna `href`.

```{code-cell} python
df = df.loc[c1 & c2].drop(['asset', 'tile_id', 'cloud_cover'], axis=1)
df.info()
```

***

## Procesamiento de los datos para obtener resultados relevantes

Podemos analizar el `DataFrame` para ver cuál es la información resultante.

```{code-cell} python
df
```

Hay casi ochenta filas, cada una de las cuales está asociada a un gránulo distinto (en este contexto, un archivo GeoTIFF producido a partir de una observación efectuada en una fecha y hora determinadas). Utilizaremos un bucle para crear un `DataArray` apilado a partir de los archivos remotos utilizando `xarray.concat`. Dado que se deben recuperar algunas docenas de archivos de una fuente remota, esto puede tardar unos minutos y el resultado requerirá algo de memoria (unos 12 MiB por cada fila, ya que cada GeoTIFF corresponde a una matriz de $3,660\times3,660$ de enteros de 8 bits sin signo).

```{code-cell} python
%%time
stack = []
for timestamp, row in df.iterrows():
    data = rio.open_rasterio(row.href).squeeze()
    data = data.rename(dict(x='longitude', y='latitude'))
    del data.coords['band']
    data.coords.update({'time':timestamp})
    data.attrs = dict(description=f"OPERA DIST: VEG-DIST-STATUS", units=None)
    stack.append(data)
stack = xr.concat(stack, dim='time')
stack
```

A modo de recordatorio, para la banda `VEG-DIST-STATUS`, interpretaremos los valores del ráster de la siguiente manera:

- **0:** Sin alteración
- **1:** Primera detección de alteraciones con cambios en la cobertura vegetal <50%
- **2:** Detección provisional de alteraciones con cambios en la cobertura vegetal <50%
- **3:** Detección confirmada de alteraciones con cambios en la cobertura vegetal < 50%
- **4:** Primera detección de alteraciones con cambios en la cobertura vegetal ≥50%
- **5:** Detección provisional de alteraciones con cambios en la cobertura vegetal ≥50%
- **6:** Detección confirmada de alteraciones con cambios en la cobertura vegetal ≥50%
- **7:** Detección finalizada de alteraciones con cambios en la cobertura vegetal <50%
- **8:** Detección finalizada de alteraciones con cambios en la cobertura vegetal ≥50%
- **255** Datos faltantes

Al aplicar `np.unique` a la pila de rásters, vemos que estos 10 valores distintos aparecen en algún lugar de los datos.

```{code-cell} python
np.unique(stack)
```

Trataremos los píxeles con valores faltantes (por ejemplo, el `255`) igual que los píxeles sin alteraciones (por ejemplo, el valor `0`). Podríamos reasignar el valor `nan` a esos píxeles, pero eso convierte todos los datos a `float32` o `float64` y, por lo tanto, aumenta la cantidad de memoria requerida. Es decir, reasignar `255->0` nos permite ignorar los valores que faltan sin utilizar más memoria.

```{code-cell} python
stack = stack.where(stack!=255, other=0)

np.unique(stack)
```

Definiremos un mapa de colores para identificar los píxeles que muestran signos de alteraciones. En vez de asignar colores diferentes a cada una de las 8 categorías de alteraciones, utilizaremos [valores RGBA](https://es.wikipedia.org/wiki/Espacio_de_color_RGBA) para asignar colores con un valor de transparencia. Con el mapa de colores definido en la siguiente celda, la mayoría de los píxeles serán totalmente transparentes. Los píxeles restantes son de color rojo con valores `alpha` estrictamente positivos. Los valores que realmente queremos ver son `3`, `6`, `7` y `8` (que indican una alteración confirmada en curso o una alteración confirmada que finalizó).

```{code-cell} python
# Define a colormap using RGBA values; these need to be written manually here...
COLORS = [
            (255, 255, 255, 0.0),   # No disturbance
            (255,   0,   0, 0.25),  # <50% disturbance, first detection
            (255,   0,   0, 0.25),  # <50% disturbance, provisional
            (255,   0,   0, 0.50),  # <50% disturbance, confirmed, ongoing
            (255,   0,   0, 0.50),  # ≥50% disturbance, first detection
            (255,   0,   0, 0.50),  # ≥50% disturbance, provisional
            (255,   0,   0, 1.00),  # ≥50% disturbance, confirmed, ongoing
            (255,   0,   0, 0.75),  # <50% disturbance, finished
            (255,   0,   0, 1.00),  # ≥50% disturbance, finished
         ]
```

Ya podemos, entonces, producir visualizaciones utilizando la matriz `stack`.

- Definimos `view` como un subconjunto de `stack` que se salta `steps` de píxeles en cada dirección para acelerar el renderizado (cambiar a `steps=1` o `steps=None` cuando querramos graficar a resolución completa).
- Definimos los diccionarios `image_opts` y `layout_opts` para controlar los argumentos que pasaremos a `hvplot.image`.
- El resultado, cuando se visualiza, es un gráfico interactivo con un selector que nos permite ver cortes temporales específicos de los datos.

```{code-cell} python
steps = 100
subset=slice(0,None,steps)
view = stack.isel(longitude=subset, latitude=subset)

image_opts = dict(
                    x='longitude',
                    y='latitude',
                    cmap=COLORS,
                    colorbar=False,
                    clim=(-0.5,8.5),
                    crs = stack.rio.crs,
                    tiles=gv.tile_sources.ESRI,
                    tiles_opts=dict(alpha=0.1, padding=0.1),
                    project=True,
                    rasterize=True,
                    widget_location='bottom',
                 )

layout_opts = dict(
                    title = 'Great Green Wall, Sahel Region, Africa\nDisturbance Alerts',
                    xlabel='Longitude (°)',ylabel='Latitude (°)',
                    fontscale=1.25,
                    frame_width=500,
                    frame_height=500,
                  )
```

```{code-cell} python
view.hvplot.image(**image_opts, **layout_opts)
```

Puede ser difícil ver los píxeles de color rojo con toda la región a la vista. Las herramientas zoom de caja y zoom de rueda son útiles aquí. También hay cierta latencia cuando se utiliza el selector, ya que se tarda un tiempo en renderizar.

***

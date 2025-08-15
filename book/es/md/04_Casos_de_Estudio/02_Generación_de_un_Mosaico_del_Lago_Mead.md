---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Generación de un mosaico del lago Mead

<!-- #region jupyter={"source_hidden": true} -->
El [Lake Mead](https://es.wikipedia.org/wiki/Lago_Mead) es un embalse de agua que se encuentra en el suroeste de los Estados Unidos y es importante para el riego en esa zona. El lago ha tenido una importante sequía durante la última década y, en particular, entre 2020 y 2023. En este cuaderno computacional, buscaremos datos GeoTIFF relacionados con este lago y sintetizaremos varios archivos ráster para producir una visualización.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Esquema de los pasos para el análisis

<!-- #region jupyter={"source_hidden": true} -->
- Identificar los parámetros de búsqueda
  - AOI y ventana temporal
  - _Endpoint_, proveedor, identificador del catálogo ("nombre corto")
- Obtención de los resultados de búsqueda
  - Exploracion, análisis para identificar características, bandas de interés
  - Almacenar los resultados en un DataFrame para facilitar la exploración
- Exploración y refinamiento de los resultados de la búsqueda
  - Identificar los gránulos de mayor valor
  - Filtrar los gránulos atípicos con contribución mínima
  - Combinar los gránulos filtrados en un DataFrame
  - Identificar el tipo de salida a generar
- Procesamiento de los datos para obtener resultados relevantes
  - Descargar los gránulos relevantes en Xarray DataArray, apilados adecuadamente
  - Realizar los cálculos intermedios necesarios
  - Unir los datos relevantes en una visualización
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### Importación preliminar

```python jupyter={"source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
```

```python jupyter={"source_hidden": true}
# Imports for plotting
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
from bokeh.models import FixedTicker
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

### Funciones prácticas

<!-- #region jupyter={"source_hidden": true} -->
Estas funciones podrían incluirse en archivos modulares para proyectos de investigación más evolucionados. Para fines didácticos, se incluyen en este cuaderno computacional.
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
# utility to extract search results into a Pandas DataFrame
def search_to_dataframe(search_results):
    '''Constructs Pandas DataFrame from PySTAC Earthdata search results.
    DataFrame columns are determined from search item properties and assets.'''
    # Extract granules into a list of searh items
    granules = list(search_results.items())
    assert granules, "Error: empty list of search results"
    # Determine column labels from unique properties from all granules
    properties = sorted(list({prop for g in granules for prop in g.properties.keys()}))
    # Assemble blocks of rows from each granule
    blocks = []
    for g in granules:
        # Leftmost columns determined from properties
        left = pd.Series(index=properties)
        for p in properties:
            left.loc[p] = g.properties.get(p, None)
        tile_id = g.id.split('_')[3]
        left.loc['tile_id'] = tile_id
        left = pd.DataFrame(left).T
        right = []
        for a in sorted(g.assets.keys()):
            href = g.assets[a].href
            # Ignore hrefs using Amazon s3 (not currently working with rasterio)
            if href.startswith('s3://'):
                continue
            right.append(pd.DataFrame(data=dict(asset=a, href=href), index=[0]))
        # Use outer join to create block from left row and right block
        blocks.append(left.join(pd.concat(right, axis=0, ignore_index=True), how='outer'))
    # Stack blocks into final dataframe, forward-filling as needed
    df = pd.concat(blocks, axis=0, ignore_index=True).ffill(axis=0)
    assert len(df), "Empty DataFrame"
    return df
```

```python jupyter={"source_hidden": true}
# utility to remap pixel values to a sequence of contiguous integers
def relabel_pixels(data, values, null_val=255, transparent_val=0, replace_null=True, start=0):
    """
    This function accepts a DataArray with a finite number of categorical values as entries.
    It reassigns the pixel labels to a sequence of consecutive integers starting from start.
    data:            Xarray DataArray with finitely many categories in its array of values.
    null_val:        (default 255) Pixel value used to flag missing data and/or exceptions.
    transparent_val: (default 0) Pixel value that will be fully transparent when rendered.
    replace_null:    (default True) Maps null_value->transparent_value everywhere in data.
    start:           (default 0) starting range of consecutive integer values for new labels.
    The values returned are:
    new_data:        Xarray DataArray containing pixels with new values
    relabel:         dictionary associating old pixel values with new pixel values
    """
    new_data = data.copy(deep=True)
    if values:
        values = np.sort(np.array(values, dtype=np.uint8))
    else:
        values = np.sort(np.unique(data.values.flatten()))
    if replace_null:
        new_data = new_data.where(new_data!=null_val, other=transparent_val)
        values = values[np.where(values!=null_val)]
    n_values = len(values)
    new_values = np.arange(start=start, stop=start+n_values, dtype=values.dtype)
    assert transparent_val in new_values, f"{transparent_val=} not in {new_values}"
    relabel = dict(zip(values, new_values))
    for old, new in relabel.items():
        if new==old: continue
        new_data = new_data.where(new_data!=old, other=new)
    return new_data, relabel
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Identificación de los parámetros de búsqueda

<!-- #region jupyter={"source_hidden": true} -->
Identificaremos un punto geográfico cerca de la orilla norte del [lago Mead](https://es.wikipedia.org/wiki/Lago_Mead), haremos un cuadro delimitador y elegiremos un intervalo de fechas que cubra marzo y parte de abril del 2023.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
lake_mead = (-114.754, 36.131)
AOI = make_bbox(lake_mead, 0.1, 0.1)
DATE_RANGE = "2023-03-01/2023-04-15"
```

```python jupyter={"source_hidden": true}
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(width=500, height=500, padding=0.1)
plot_bbox(AOI) * basemap
```

```python jupyter={"source_hidden": true}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Obtención de los resultados de búsqueda

<!-- #region jupyter={"source_hidden": true} -->
Como siempre, especificaremos el _endpoint_ de búsqueda, el proveedor y el catálogo. Para la familia de productos de datos DSWx son los siguientes.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = 'POCLOUD'
COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```python jupyter={"source_hidden": true}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

<!-- #region jupyter={"source_hidden": true} -->
Convertimos los resultados de la búsqueda en un `DataFrame` para facilitar su lectura.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df = search_to_dataframe(search_results)
display(df.head())
df.info()
```

<!-- #region jupyter={"source_hidden": true} -->
Limpiaremos el DataFrame `df` de maneras estándar:

- eliminando las columnas `start_datetime` y `end_datetime`,
- renombrando la columna `eo:cloud_cover`,
- convirtiendo las columnas a tipos de datos adecuados, y
- asignando la columna `datetime` como el índice.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df.datetime = pd.DatetimeIndex(df.datetime)
df = df.drop(['start_datetime', 'end_datetime'], axis=1)
df = df.rename({'eo:cloud_cover':'cloud_cover'}, axis=1)
df['cloud_cover'] = df['cloud_cover'].astype(np.float16)
for col in ['asset', 'href', 'tile_id']:
    df[col] = df[col].astype(pd.StringDtype())
df = df.set_index('datetime').sort_index()
```

```python jupyter={"source_hidden": true}
display(df.head())
df.info()
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Exploración y refinamiento de los resultados de la búsqueda

<!-- #region jupyter={"source_hidden": true} -->
Podemos observar la columna `assets` para ver cuáles bandas diferentes están disponibles en los resultados devueltos.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df.asset.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->
La banda `0_B01_WTR` es con la que queremos trabajar posteriormente.

También podemos ver cuánta nubosidad hay en los resultados de nuestra búsqueda.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df.cloud_cover.agg(['min','mean','median','max'])
```

<!-- #region jupyter={"source_hidden": true} -->
Podemos extraer las filas seleccionadas del `DataFrame` usando `Series` booleanas. Específicamente, seleccionaremos las filas que tengan menos de 10% de nubosidad y en las que el `asset` sea la banda `0_B01_WTR`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
c1 = (df.cloud_cover <= 10)
c2 = (df.asset.str.contains('B01_WTR'))
b01_wtr = df.loc[c1 & c2].drop(['asset', 'cloud_cover'], axis=1)
b01_wtr
```

<!-- #region jupyter={"source_hidden": true} -->
Por último, podemos ver cuántos mosaicos MGRS diferentes intersecan nuestro AOI.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
b01_wtr.tile_id.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->
Hay cuatro mosaicos geográficos distintos que intersecan este AOI en particular.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Procesamiento de los datos para obtener resultados relevantes

<!-- #region jupyter={"source_hidden": true} -->
Esta vez, utilizaremos una técnica llamada _creación de mosaicos_ para combinar datos ráster de mosaicos adyacentes en un conjunto único de datos ráster. Esto requiere la función `rasterio.merge.merge` como antes. También necesitaremos la función `rasterio.transform.array_bounds` para alinear correctamente las coordenadas.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
import rasterio
from rasterio.merge import merge
from rasterio.transform import array_bounds
```

<!-- #region jupyter={"source_hidden": true} -->
Ya hemos utilizado la función `merge` para combinar distintos conjuntos de datos ráster asociados a un único mosaico MGRS. En esta ocasión, los datos ráster combinados provendrán de mosaicos MGRS adyacentes. Al llamar a la función `merge` en la siguiente celda de código, la columna `b01_wtr.href` se tratará como una lista de URL ([Localizadores Uniformes de Recursos](https://es.wikipedia.org/wiki/Localizador_de_recursos_uniforme) (URL, por su siglas en inglés de _Uniform Resource Locator_)). Para cada URL de la lista, se descargará y se procesará un archivo GeoTIFF. El resultado neto es un mosaico de imágenes, es decir, un ráster fusionado que contiene una combinación de todos los rásteres. Los detalles del algoritmo de fusión se describen en la [documentación del módulo `rasterio.merge`](https://rasterio.readthedocs.io/en/latest/api/rasterio.merge.html).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
mosaicked_img, mosaic_transform = merge(b01_wtr.href)
```

<!-- #region jupyter={"source_hidden": true} -->
La salida consiste de nuevo en un arreglo de NumPy y una transformación de coordenadas.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(f"{type(mosaicked_img)=}\n")
print(f"{mosaicked_img.shape=}\n")
print(f"{type(mosaic_transform)=}\n")
print(f"{mosaic_transform=}\n")
```

<!-- #region jupyter={"source_hidden": true} -->
Las entradas de `mosaic_transform` describen una [_transformación afín_](https://es.wikipedia.org/wiki/Transformaci%C3%B3n_af%C3%ADn) de coordenadas de píxel a coordenadas UTM continuas. En particular:

- la entrada `mosaic_transform[0]` es el ancho horizontal de cada píxel en metros, y
- la entrada `mosaic_transform[4]` es la altura vertical de cada píxel en metros.

Observa también que, en este caso, `mosaic_transform[4]` es un valor negativo (es decir, `mosaic_transform[4]==-30.0`). Esto nos dice que la orientación del eje vertical de coordenadas continuas se opone a la orientación del eje vertical de coordenadas de píxeles, es decir, la coordenada continua vertical disminuye en dirección descendente, a diferencia de la coordenada vertical de píxeles.

Cuando pasamos el objeto `mosaic_transform` a la función `rasterio.transform.array_bounds`, el valor que se devuelve es un cuadro delimitador, es decir, una tupla de la forma `(x_min, y_min, x_max, y_max)` que describe las esquinas inferior izquierda y superior derecha de la imagen en mosaico resultante en coordenadas continuas UTM.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
bounds = array_bounds(*mosaicked_img.shape[1:], mosaic_transform)

bounds
```

<!-- #region jupyter={"source_hidden": true} -->
La combinación de toda la información anterior nos permite reconstruir las coordenadas UTM continuas asociadas a cada píxel. Computaremos arreglos para estas coordenadas continuas y las etiquetaremos como `longitude` y `latitude`. Estas coordenadas serían más precisas si se llamaran `easting` y `northing`, pero utilizaremos las etiquetas `longitude` y `latitude` respectivamente cuando adjuntemos los arreglos de coordenadas a un Xarray `DataArray`. Elegimos estas etiquetas porque, cuando los datos ráster se visualizan con `hvplot.image`, la salida utilizará coordenadas longitud-latitud.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
longitude = np.arange(bounds[0], bounds[2], mosaic_transform[0])
latitude = np.arange(bounds[3], bounds[1], mosaic_transform[4])
```

<!-- #region jupyter={"source_hidden": true} -->
Almacenamos la imagen en mosaico y los metadatos relevantes en un Xarray `DataArray`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
raster = xr.DataArray(
        data=mosaicked_img,
        dims=["band", "latitude", "longitude"],
        coords=dict(
            longitude=(["longitude"], longitude),
            latitude=(["latitude"], latitude),
        ),
        attrs=dict(
            description="OPERA DSWx B01",
            units=None,
        ),
    )
raster
```

<!-- #region jupyter={"source_hidden": true} -->
Necesitamos adjuntar un objeto CRS al objeto `raster`. Para ello, utilizaremos `rasterio.open` para cargar los metadatos relevantes de uno de los gránulos asociados a `b01_wtr` (deberían ser los mismos para todos estos archivos).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(b01_wtr.href[0]) as ds:
    crs = ds.crs

raster.rio.write_crs(crs, inplace=True)
print(raster.rio.crs)
```

<!-- #region jupyter={"source_hidden": true} -->
En el código de investigación, podríamos agrupar los comandos anteriores en una función y guardarla en un módulo. No lo haremos aquí porque, para los propósitos de este tutorial, es preferible asegurarse de que podemos analizar la salida de varias líneas de código interactivamente.

Con todos los pasos anteriores completados, estamos listos para producir una visualización del mosaico. Reetiquetaremos los valores de los píxeles para que la barra de colores del resultado final sea más prolija.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
raster, relabel = relabel_pixels(raster, values=[0,1,2,253,254,255])
```

<!-- #region jupyter={"source_hidden": true} -->
Vamos a definir las opciones de imagen, las opciones de diseño, y un mapa de color en los diccionarios como lo hicimos anteriormente para generar una única visualización.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts = dict(
                    x='longitude',
                    y='latitude',                   
                    rasterize=True, 
                    dynamic=True,
                    crs=raster.rio.crs
                 )
layout_opts = dict(
                    xlabel='Longitude',
                    ylabel='Latitude',
                  )
```

```python jupyter={"source_hidden": true}
# Define a colormap using RGBA values; these need to be written manually here...
COLORS = {
0: (255, 255, 255, 0.0),  # No Water
1:  (0,   0, 255, 1.0),   # Open Water
2:  (180, 213, 244, 1.0), # Partial Surface Water
3: (  0, 255, 255, 1.0),  # Snow/Ice
4: (175, 175, 175, 1.0),  # Cloud/Cloud Shadow
5: ( 0,   0, 127, 0.5),   # Ocean Masked
}
```

```python jupyter={"source_hidden": true}
c_labels = ["Not water", "Open water", "Partial Surface Water", "Snow/Ice",
            "Cloud/Cloud Shadow", "Ocean Masked"]
c_ticks = list(COLORS.keys())
limits = (c_ticks[0]-0.5, c_ticks[-1]+0.5)

c_bar_opts = dict( ticker=FixedTicker(ticks=c_ticks),
                   major_label_overrides=dict(zip(c_ticks, c_labels)),
                   major_tick_line_width=0, )
```

```python jupyter={"source_hidden": true}
image_opts.update({ 'cmap': list(COLORS.values()),
                    'clim': limits,
                  })

layout_opts.update(dict(colorbar_opts=c_bar_opts))
```

<!-- #region jupyter={"source_hidden": true} -->
Definiremos el mapa base como un objeto separado para superponerlo usando el operador `*`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
basemap = gv.tile_sources.ESRI(frame_width=500, frame_height=500, padding=0.05, alpha=0.25)
```

<!-- #region jupyter={"source_hidden": true} -->
Por último, podemos utilizar la función `slice` de Python para extraer rápidamente las imágenes reducidas antes de tratar de ver la imagen completa. Recuerda que reducir el valor de `steps` a `1` (o `None`) visualiza el ráster a resolución completa.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
steps = 200
view = raster.isel(longitude=slice(0,None,steps), latitude=slice(0,None,steps)).squeeze()

view.hvplot.image(**image_opts).opts(**layout_opts) * basemap
```

<!-- #region jupyter={"source_hidden": true} -->
Este ráster es mucho más grande de los que analizamos anteriormente (requiere aproximadamente 4 veces más espacio de almacenamiento). Este proceso podría ser iterado para hacer un deslizador que muestre los resultados fusionados de mosaicos vecinos en diferentes momentos. Esto, por supuesto, requiere que haya suficiente memoria disponible.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

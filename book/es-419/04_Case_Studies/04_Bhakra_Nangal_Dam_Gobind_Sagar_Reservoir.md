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

# La represa de Bhakra Nangal y el embalse de Gobind Sagar

La [represa de Bhakra Nangal](https://en.wikipedia.org/wiki/Bhakra_Dam) se inauguró en 1963 en la India. La represa forma el embalse de Gobind Sagar y proporciona riego a 10 millones de acres en los estados vecinos de Punjab, Haryana y Rajastán. Podemos utilizar los datos del producto OPERA DSWx para observar las fluctuaciones en el nivel del agua durante largos periodos.

<center>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bhakra_Dam_Aug_15_2008.JPG/440px-Bhakra_Dam_Aug_15_2008.JPG">
</center>

## Esquema de las etapas del análisis

- Identificar los parámetros de búsqueda
  - Área de interés (AOI) y ventana temporal
  - _Endpoint_, proveedor, identificador del catálogo ("nombre corto")
- Obtención de los resultados de la búsqueda
  - Instrospección, análisis para identificar características, bandas de interés
  - Almacenar los resultados en un DataFrame para facilitar la exploración
- Exploración y refinamiento de los resultados de la búsqueda
  - Identificar los gránulos de mayor valor
  - Filtrar los gránulos atípicos con mínima contribución
  - Combinar los gránulos filtrados relevantes en un DataFrame
  - Identificar el tipo de salida a generar
- Procesar los datos para obtener resultados relevantes
  - Descargar los gránulos relevantes en un Xarray DataArray, apilados adecuadamente
  - Realizar los cálculos intermedios necesarios
  - Combinar los fragmentos de datos relevantes en la visualización

***

### Importación preliminar de librerías

```{code-cell} python
from warnings import filterwarnings
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
import rasterio
```

```{code-cell} python
# Imports for plotting
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```{code-cell} python
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

```{code-cell} python
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

Estas funciones podrían incluirse en archivos módular para proyectos de investigación más evolucionados. Para fines didácticos, se incluyen en este cuaderno computacional.

***

## Identificación de los parámetros de búsqueda

Para las coordenadas de la represa, utilizaremos $(76.46^{\circ}, 31.42^{\circ})$. También buscaremos los datos de todo un año completo entre el 1 de abril de 2023 y el 1 de abril de 2024.

```{code-cell} python
AOI = make_bbox((76.46, 31.42), 0.2, 0.2)
DATE_RANGE = "2023-04-01/2024-04-01"
```

```{code-cell} python
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(alpha=0.5, padding=0.1)
plot_bbox(AOI) * basemap
```

```{code-cell} python
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

***

## Obtención de los resultados de búsqueda

Buscaremos productos de datos OPERA DSWx, así que definimos el `ENDPOINT`, el `PROVIDER` y las `COLLECTIONS` de la siguiente manera (estos valores se modifican ocasionalmente, así que puede ser necesario hacer algunas búsquedas en el [sitio web Earthdata Search](https://search.earthdata.nasa.gov) de la NASA).

```{code-cell} python
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = "POCLOUD"
COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```{code-cell} python
%%time
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

Una vez que ejecutamos la búsqueda, los resultados se pueden consultar en un `DataFrame`.

```{code-cell} python
%%time
df = search_to_dataframe(search_results)
df.head()
```

Limpiaremos el `DataFrame` `df` cambiando el nombre de la columna `eo:cloud_cover`, eliminando las columnas adicionales de fecha y hora, convirtiendo los tipos de datos de forma adecuada y seteando el índice.

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
df.head()
```

En esta fase, el `DataFrame` de los resultados de la búsqueda tendrá más de dos mil filas. Entonces, vamos a reducirlo.

***

## Exploración y refinamiento de los resultados de la búsqueda

Filtraremos las filas del `df` para capturar solo los gránulos capturados que tengan menos del 10% de nubosidad y la banda `B01_WTR` de los datos DSWx.

```{code-cell} python
c1 = df.cloud_cover<10
c2 = df.asset.str.contains('B01_WTR')
```

```{code-cell} python
df = df.loc[c1 & c2]
df.info()
```

Podemos contar todas las entradas distintas de la columna `tile_id` y encontrar que solo hay una (`T43RFQ`). Eso significa que el AOI especificado se encuentra estrictamente dentro de un mosaico MGRS único y que todos los gránulos encontrados estarán asociados a ese mosaico geográfico específico.

```{code-cell} python
df.tile_id.value_counts()
```

Redujimos el número total de gránulos a un poco más de cincuenta. Y los utilizaremos para generar una visualización.

***

## Procesamiento los datos para obtener resultados relevantes

Como ya vimos varias veces, apilaremos los arreglos bidimensionales de los archivos GeoTIFF listados en `df.href` en un `DataArray` tridimensional. Utilizaremos el identificador `stack` para etiquetar el resultado.

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

Podemos ver los valores de los pixeles que realmente aparecen en el arreglo `stack` utilizando la función NumPy `unique`.

```{code-cell} python
np.unique(stack)
```

Como recordatorio, de acuerdo con la [especificación del producto DSWx](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf), los significados de los valores ráster son los siguientes:

- **0**: Sin agua&mdash;cualquier área con datos de reflectancia válidos que no sean de una de las otras categorías permitidas (agua abierta, agua superficial parcial, nieve/hielo, nube/sombra de nube, u océano enmascarado).
- **1**: Agua abierta&mdash;cualquier píxel que sea completamente agua sin obstrucciones para el sensor, incluyendo obstrucciones por vegetación, terreno y edificios.
- **2**: Agua parcialmente superficial&mdash;un área que es por lo menos 50% y menos de 100% agua abierta (por ejemplo, sumideros inundados, vegetación flotante, y píxeles bisecados por líneas costeras).
- **252**: Nieve/Hielo.
- **253**: Nube o sombra de nube&mdash;un área oscurecida por, o adyacente a, una nube o sombra de nube.
- **254**: Océano enmascarado&mdash;un área identificada como océano utilizando una base de datos de la línea costera con un margen añadido.
- **255**: Valor de relleno (datos faltantes).

Observa que el valor `254`&mdash;océano enmascarado&mdash; no aparece en esta colección particular de rásteres porque esta región en particular está lejos de la costa.

Para limpiar los datos (en caso de que querramos utilizar un mapa de colores), reasignemos los valores de los píxeles con nuestra función `relabel_pixels`. Esta vez, vamos a mantener los valores "sin datos" (`255`) para que podamos ver dónde faltan datos.

```{code-cell} python
stack, relabel = relabel_pixels(stack, values=[0,1,2,252,253,255], replace_null=False)
```

Podemos ejecutar `np.unique` de nuevo para asegurarnos de que los datos se modificaron como queríamos.

```{code-cell} python
np.unique(stack)
```

Ahora asignemos un mapa de colores para ayudar a visualizar las imágenes ráster. En este caso, el mapa de colores utiliza varios colores distintos con opacidad total y píxeles negros parcialmente transparentes para indicar los datos que faltan.

```{code-cell} python
# Define a colormap using RGBA values; these need to be written manually here...
COLORS = {
0: (255, 255, 255, 0.0),  # Not Water
1: (  0,   0, 255, 1.0),  # Open Water
2: (180, 213, 244, 1.0),  # Partial Surface Water
3: (  0, 255, 255, 1.0),  # Snow/Ice
4: (175, 175, 175, 1.0),  # Cloud/Cloud Shadow
5: (  0,   0, 0, 0.5),    # Missing
}
```

Podemo, entonces, visualizar los datos.

- Definimos las opciones adecuadas en los diccionarios `image_opts` y `layout_opts`.
- Construimos un objeto `view` que consiste en cortes extraídos del `stack` por submuestreo de cada píxel `steps` (reduce los `steps` a `1` o `None` para ver los rásteres a resolución completa).

```{code-cell} python
image_opts = dict(  
                    x='longitude',
                    y='latitude',
                    cmap = list(COLORS.values()),
                    colorbar=False,
                    tiles = gv.tile_sources.OSM,
                    tiles_opts=dict(padding=0.05, alpha=0.25),
                    project=True,
                    rasterize=True, 
                    framewise=False,
                    widget_location='bottom',
                 )

layout_opts = dict(
                    title = 'Bhakra Nangal Dam, India - water extent over a year',
                    xlabel='Longitude (degrees)',
                    ylabel='Latitude (degrees)',
                    fontscale=1.25,
                    frame_width=500, 
                    frame_height=500
                   )
```

```{code-cell} python
steps = 100
subset = slice(0,None,steps)
view = stack.isel(longitude=subset, latitude=subset)
view.hvplot.image( **image_opts, **layout_opts)
```

La visualización anterior puede tardar un poco en actualizarse (según la elección de `steps`). Esta permite ver la acumulación de agua a lo largo de un año. Hay algunos cortes en los que faltan muchos datos, así que debemos tener cuidado al interpretarlos.

***

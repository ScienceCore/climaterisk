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

# La represa de Bhakra Nangal y el embalse de Gobind Sagar

<!-- #region jupyter={"source_hidden": true} -->
La [represa de Bhakra Nangal](https://en.wikipedia.org/wiki/Bhakra_Dam) se inauguró en 1963 en la India. La represa forma el embalse de Gobind Sagar y proporciona riego a 10 millones de acres en los estados vecinos de Punjab, Haryana y Rajastán. Podemos utilizar los datos del producto OPERA DSWx para observar las fluctuaciones en el nivel del agua durante largos periodos.

<center>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bhakra_Dam_Aug_15_2008.JPG/440px-Bhakra_Dam_Aug_15_2008.JPG">
</center>
<!-- #endregion -->

## Esquema de las etapas del análisis

<!-- #region jupyter={"source_hidden": true} -->
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
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### Importación preliminar de librerías

```python jupyter={"source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
import rasterio
```

```python jupyter={"source_hidden": true}
# Imports for plotting
import hvplot.pandas, hvplot.xarray
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

### Funciones prácticas

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
# utility to process DataFrame of search results & return DataArray of stacked raster images
def stack_time_slices(granule_dataframe):
    '''This function returns a three-dimensional Xarray DataArray comprising time slices read from GeoTIFF files.
    - Input: a DataFrame of granules (i.e., a DataFrame with a DateTimeIndex and a column 'href' of URIs).
    - Output: a stacked DataArray with dimensions ('time', 'longitude', 'latitude')
    - GeoTIFF data are assumed to have been acquired over the same MGRS tile (NOT verified within).
    - Note CRS explicitly embedded into DataArray stack as extracted from GeoTIFF file.
    - DataArray is constructed using np.datetime64 time axis to simplify visualization.'''
    slices, timestamps = list(), list()
    for timestamp_, row_ in granule_dataframe.iterrows():
        da_ = rio.open_rasterio(row_['href'])
        # Preserve coordinate arrays from last GeoTIFF file parsed
        x, y = da_.coords['x'].values, da_.coords['y'].values
        slices.append(da_.values)
        timestamps.append(np.datetime64(timestamp_,'s'))
    # Construct time axis from accumulated timestamps
    time = np.array(timestamps)
    # Construct DataArray stack from accumulated slices & coordinates
    slices = np.concatenate(slices, axis=0)
    coords = dict(time=time, longitude=x, latitude=y)
    stack = xr.DataArray(data=slices, coords=coords, dims=['time', 'latitude', 'longitude'])
    # Preserve coordinate reference system (CRS) in DataArray stack
    crs = da_.rio.crs
    stack.rio.write_crs(crs, inplace=True)
    return stack
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

<!-- #region jupyter={"source_hidden": true} -->
Estas funciones podrían incluirse en archivos módular para proyectos de investigación más evolucionados. Para fines didácticos, se incluyen en este cuaderno computacional.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Identificación de los parámetros de búsqueda

<!-- #region jupyter={"source_hidden": true} -->
Para las coordenadas de la represa, utilizaremos $(76.46^{\circ}, 31.42^{\circ})$. También buscaremos los datos de todo un año completo entre el 1 de abril de 2023 y el 1 de abril de 2024.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
AOI = make_bbox((76.46, 31.42), 0.2, 0.2)
DATE_RANGE = "2023-04-01/2024-04-01"
```

```python jupyter={"source_hidden": true}
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(alpha=0.5, padding=0.1)
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
Buscaremos productos de datos OPERA DSWx, así que definimos el `ENDPOINT`, el `PROVIDER` y las `COLLECTIONS` de la siguiente manera (estos valores se modifican ocasionalmente, así que puede ser necesario hacer algunas búsquedas en el [sitio web Earthdata Search](https://search.earthdata.nasa.gov) de la NASA).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = "POCLOUD"
COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```python jupyter={"source_hidden": true}
%%time
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

<!-- #region jupyter={"source_hidden": true} -->
Una vez que ejecutamos la búsqueda, los resultados se pueden consultar en un `DataFrame`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->
Limpiaremos el `DataFrame` `df` cambiando el nombre de la columna `eo:cloud_cover`, eliminando las columnas adicionales de fecha y hora, convirtiendo los tipos de datos de forma adecuada y seteando el índice.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df = df.rename(columns={'eo:cloud_cover':'cloud_cover'})
df.cloud_cover = df.cloud_cover.astype(np.float16)
df = df.drop(['start_datetime', 'end_datetime'], axis=1)
df = df.convert_dtypes()
df.datetime = pd.DatetimeIndex(df.datetime)
df = df.set_index('datetime').sort_index()
```

```python jupyter={"source_hidden": true}
df.info()
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->
En esta fase, el `DataFrame` de los resultados de la búsqueda tendrá más de dos mil filas. Entonces, vamos a reducirlo.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Exploración y refinamiento de los resultados de la búsqueda

<!-- #region jupyter={"source_hidden": true} -->
Filtraremos las filas del `df` para capturar solo los gránulos capturados que tengan menos del 10% de nubosidad y la banda `B01_WTR` de los datos DSWx.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
c1 = df.cloud_cover<10
c2 = df.asset.str.contains('B01_WTR')
```

```python jupyter={"source_hidden": true}
df = df.loc[c1 & c2]
df.info()
```

<!-- #region jupyter={"source_hidden": true} -->
Podemos contar todas las entradas distintas de la columna `tile_id` y encontrar que solo hay una (`T43RFQ`). Eso significa que el AOI especificado se encuentra estrictamente dentro de un mosaico MGRS único y que todos los gránulos encontrados estarán asociados a ese mosaico geográfico específico.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df.tile_id.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->
Redujimos el número total de gránulos a un poco más de cincuenta. Y los utilizaremos para generar una visualización.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Procesamiento los datos para obtener resultados relevantes

<!-- #region jupyter={"source_hidden": true} -->
Como ya vimos varias veces, apilaremos los arreglos bidimensionales de los archivos GeoTIFF listados en `df.href` en un `DataArray` tridimensional. Utilizaremos el identificador `stack` para etiquetar el resultado.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
stack = stack_time_slices(df)
stack.attrs = dict(description=f"OPERA DSWx: B01_WTR", units=None)
stack
```

<!-- #region jupyter={"source_hidden": true} -->
Podemos ver los valores de los pixeles que realmente aparecen en el arreglo `stack` utilizando la función NumPy `unique`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
np.unique(stack)
```

<!-- #region jupyter={"source_hidden": true} -->
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
<!-- #endregion -->

```python jupyter={"source_hidden": true}
stack, relabel = relabel_pixels(stack, values=[0,1,2,252,253,255], replace_null=False)
```

<!-- #region jupyter={"source_hidden": true} -->
Podemos ejecutar `np.unique` de nuevo para asegurarnos de que los datos se modificaron como queríamos.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
np.unique(stack)
```

<!-- #region jupyter={"source_hidden": true} -->
Ahora asignemos un mapa de colores para ayudar a visualizar las imágenes ráster. En este caso, el mapa de colores utiliza varios colores distintos con opacidad total y píxeles negros parcialmente transparentes para indicar los datos que faltan.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
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

<!-- #region jupyter={"source_hidden": true} -->
Podemo, entonces, visualizar los datos.

- Definimos las opciones adecuadas en los diccionarios `image_opts` y `layout_opts`.
- Construimos un objeto `view` que consiste en cortes extraídos del `stack` por submuestreo de cada píxel `steps` (reduce los `steps` a `1` o `None` para ver los rásteres a resolución completa).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
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

```python jupyter={"source_hidden": true}
steps = 100
subset = slice(0,None,steps)
view = stack.isel(longitude=subset, latitude=subset)
view.hvplot.image(**image_opts, **layout_opts)
```

<!-- #region jupyter={"source_hidden": true} -->
La visualización anterior puede tardar un poco en actualizarse (según la elección de `steps`). Esta permite ver la acumulación de agua a lo largo de un año. Hay algunos cortes en los que faltan muchos datos, así que debemos tener cuidado al interpretarlos.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

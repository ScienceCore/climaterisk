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

# Plantilla para el uso de del servicio cloud ofrecido por Earthdata

## Esquema de los pasos para el análisis

<!-- #region jupyter={"source_hidden": true} -->
- Identificación de los parámetros de búsqueda
  - Área de interés (AOI, por las siglas en inglés de _area of interest_) y ventana temporal
  - _Endpoint_, proveedor, identificador del catálogo ("nombre corto")
- Obtención de los resultados de la búsqueda
  - Exploracion, análisis para identificar características, bandas de interés
  - Almacenar los resultados en un DataFrame para facilitar la exploración
- Explorar y refinar los resultados de la búsqueda
  - Identificar los gránulos de mayor valor
  - Filtrar los gránulos atípicos con mínima contribución
  - Combinar los gránulos filtrados relevantes en un DataFrame
  - Identificar el tipo de salida a generar
- Procesar los datos para obtener resultados relevantes
  - Descargar los gránulos relevantes en Xarray DataArray, apilados adecuadamente
  - Realizar los cálculos intermedios necesarios
  - Combinar los datos relevantes en una visualización
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### Importación preliminar de librerías

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

### Funciones prácticas

<!-- #region jupyter={"source_hidden": true} -->
Estas funciones podrían incluirse en archivos de módulos para proyectos de investigación más evolucionados. Para fines didácticos, se incluyen en este cuaderno computacional.
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

```python

```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Identificación de los parámetros de búsqueda

```python jupyter={"source_hidden": true}
AOI = ...
DATE_RANGE = ...
```

```python jupyter={"source_hidden": true}
# Optionally plot the AOI
```

```python jupyter={"source_hidden": true}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Obtención de los resultados de la búsqueda

```python jupyter={"source_hidden": true}
ENDPOINT = ...
PROVIDER = ...
COLLECTIONS = ...
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```python jupyter={"source_hidden": true}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

```python
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->
Limpiar el DataFrame `df` de forma que tenga sentido (por ejemplo, eliminando columnas/filas innecesarias, convirtiendo columnas en tipos de datos fijos, estableciendo un índice, etc.).
<!-- #endregion -->

```python

```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Exploración y refinamiento de los resultados de la búsqueda

<!-- #region jupyter={"source_hidden": true} -->
Consiste en filtrar filas o columnas adecuadamente para limitar los resultados de la búsqueda a los archivos de datos ráster más relevantes para el análisis y/o la visualización. Esto puede significar enfocarse en determinadas regiones geográficos, bandas específicas del producto de datos, determinadas fechas o períodos, etc.
<!-- #endregion -->

```python

```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Procesamiento de los datos para obtener resultados relevantes

<!-- #region jupyter={"source_hidden": true} -->
Esto puede incluir apilar matrices bidimensionales en una matriz tridimensional, combinar imágenes ráster de mosaicos adyacentes en uno solo, etc.
<!-- #endregion -->

```python

```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

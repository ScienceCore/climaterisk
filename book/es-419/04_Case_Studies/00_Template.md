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

# Plantilla para el uso de la nube EarthData

## Esquema de los pasos para el análisis

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
  - Reunir los gránulos filtrados relevantes en un DataFrame
  - Identificar el tipo de resultado que se quiere generar
- Procesamiento de los datos para generar resultados relevantes
  - Descargar los gránulos relevantes en Xarray DataArray, apilados adecuadamente
  - Llevar a cabo los cálculos intermedios necesarios
  - Ensamblar los fragmentos de datos relevantes en la visualización

<!-- #endregion -->

---

### Importaciones preliminares

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

### Utilidades prácticas

Estas funciones podrían colocarse en archivos de módulos para proyectos de investigación más desarrollados. Para fines didácticos, se incluyen en este cuaderno.

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

```python jupyter={"source_hidden": true}
# utility to process DataFrame of search results & return DataArray of stacked raster images
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

---

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

---

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

Limpiar el DataFrame `df` de forma que tenga sentido (por ejemplo, eliminando columnas/filas innecesarias, convirtiendo columnas en tipos de datos fijos, estableciendo el índice, etc.).

```python
```

---

## Explorar y refinar los resultados de la búsqueda

<!-- #region jupyter={"source_hidden": true} -->

Consiste en filtrar filas o columnas adecuadamente para limitar los resultados de la búsqueda a los archivos de datos ráster más adecuados para el análisis y/o la visualización. Esto puede significar enfocarse en determinados mosaicos geográficos, bandas específicas del producto de datos, determinadas fechas/marcas de tiempo, etc.

<!-- #endregion -->

```python
```

---

## Procesamiento de los datos para generar resultados relevantes

Esto puede incluir apilar matrices bidimensionales en una matriz tridimensional, mosaico de imágenes ráster de mosaicos adyacentes en un solo mosaico, etc.

```python
```

---

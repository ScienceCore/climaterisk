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

# Incendios forestales en Grecia

<!-- #region jupyter={"source_hidden": false} -->

En este ejemplo, recuperaremos los datos asociados a los [incendios forestales en Grecia en el 2023](https://es.wikipedia.org/wiki/Incendios_forestales_en_Grecia_de_2023) para comprender su evolución y extensión. Generaremos una serie temporal asociada a estos datos y dos visualizaciones del evento.

En particular, analizaremos la zona que está alrededor de la ciudad de [Alexandroupolis](https://es.wikipedia.org/wiki/Alejandr%C3%B3polis), que se vio gravemente afectada por incendios forestales, con la consiguiente pérdida de vidas, propiedades y zonas boscosas.

---

<!-- #endregion -->

## Esquema de las etapas del análisis

<!-- #region jupyter={"source_hidden": false} -->

- Identificación de los parámetros de búsqueda
  - AOI, ventana temporal
  - _Endpoint_, proveedor, identificador del catálogo ("nombre corto")
- Obtención de los resultados de la búsqueda
  - Inspección, análisis para identificar características, bandas de interés
  - Almacenamos los resultados en un DataFrame para facilitar la exploración
- Exploración y refinamiento de los resultados de la búsqueda
  - Identificar los gránulos de mayor valor
  - Filtrar los gránulos extraños con una contribución mínima
  - Integrar los gránulos filtrados en un DataFrame
  - Identificar el tipo de resultado que se quiere generar
- Procesamiento de los datos para generar resultados relevantes
  - Descargar los gránulos relevantes en Xarray DataArray, apilados adecuadamente
  - Llevar a cabo los cálculos intermedios necesarios
  - Unir los fragmentos de datos relevantes en la visualización

---

<!-- #endregion -->

### Importación preliminar

```{code-cell} python jupyter={"source_hidden": false}
from warnings import filterwarnings
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
```

```{code-cell} python jupyter={"source_hidden": false}
# Imports for plotting
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```{code-cell} python jupyter={"source_hidden": false}
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

```{code-cell} python jupyter={"source_hidden": false}
# simple utility to make a rectangle with given center of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding-box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

```{code-cell} python jupyter={"source_hidden": false}
# simple utility to plot an AOI or bounding-box
def plot_bbox(bbox):
    '''Given bounding-box, returns GeoViews plot of Rectangle & Point at center
    + bbox: bounding-box specified as (lon_min, lat_min, lon_max, lat_max)
    Assume longitude-latitude coordinates.
    '''
    # These plot options are fixed but can be over-ridden
    point_opts = opts.Points(size=12, alpha=0.25, color='blue')
    rect_opts = opts.Rectangles(line_width=2, alpha=0.1, color='red')
    lon_lat = (0.5*sum(bbox[::2]), 0.5*sum(bbox[1::2]))
    return (gv.Points([lon_lat]) * gv.Rectangles([bbox])).opts(point_opts, rect_opts)
```

```{code-cell} python jupyter={"source_hidden": false}
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

<!-- #region jupyter={"source_hidden": false} -->

Estas funciones podrían incluirse en archivos modular para proyectos de investigación más evolucionados. Para fines didácticos, se incluyen en este cuaderno computacional.

---

<!-- #endregion -->

## Identificación de los parámetros de búsqueda

```{code-cell} python jupyter={"source_hidden": false}
dadia_forest = (26.18, 41.08)
AOI = make_bbox(dadia_forest, 0.1, 0.1)
DATE_RANGE = '2023-08-01/2023-09-30'.split('/')
```

```{code-cell} python jupyter={"source_hidden": false}
# Optionally plot the AOI
basemap = gv.tile_sources.ESRI(width=500, height=500, padding=0.1, alpha=0.25)
plot_bbox(AOI) * basemap
```

```{code-cell} python jupyter={"source_hidden": false}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

---

## Obtención de los resultados de búsqueda

```{code-cell} python jupyter={"source_hidden": false}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = 'LPCLOUD'
COLLECTIONS = ["OPERA_L3_DIST-ALERT-HLS_V1_1"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```{code-cell} python jupyter={"source_hidden": false}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

<!-- #region jupyter={"source_hidden": false} -->

Como de costumbre, codificaremos el resultado de la búsqueda en un Pandas `DataFrame`, analizaremos los resultados, y haremos algunas transformaciones para limpiarlos.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
%%time
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": false} -->

Limpiaremos el `DataFrame` `df` de las formas típicas:

- convertiendo la columna `datetime` en `DatetimeIndex`,
- eliminando columnas de tipo `datetime` extrañas,
- renombrando la columna `eo:cloud_cover` como `cloud_cover`,
- convirtiendo la columna `cloud_cover` en valores de punto flotante, y
- convertiendo las columnas restantes en cadenas de caracteres, y
- estableciendo la columna `datetime` como `Index`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df = df.drop(['end_datetime', 'start_datetime'], axis=1)
df.datetime = pd.DatetimeIndex(df.datetime)
df = df.rename(columns={'eo:cloud_cover':'cloud_cover'})
df['cloud_cover'] = df['cloud_cover'].astype(np.float16)
for col in ['asset', 'href', 'tile_id']:
    df[col] = df[col].astype(pd.StringDtype())
df = df.set_index('datetime').sort_index()
df.info()
```

---

## Exploración y refinamiento de los resultados de la búsqueda

<!-- #region jupyter={"source_hidden": false} -->

Examinemos el `DataFrame` `df` para comprender mejor los resultados de la búsqueda. En primer lugar, veamos cuántos mosaicos geográficos diferentes aparecen en los resultados de la búsqueda.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.tile_id.value_counts() 
```

<!-- #region jupyter={"source_hidden": false} -->

Entonces, el AOI se encuentra estrictamente dentro de un único mosaico geográfico MGRS llamado `T35TMF`. Analicemos la columna `asset`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.asset.value_counts().sort_values(ascending=False)
```

<!-- #region jupyter={"source_hidden": false} -->

Algunos de los nombres de estos activos no son tan simples y ordenados como los que encontramos con los productos de datos DIST-ALERT. Sin embargo, podemos identificar fácilmente las subcadenas de caracteres útiles. En este caso, elegimos sólo las filas en las que la columna `asset` incluye `'VEG-DIST-STATUS'` como subcadena de caracteres.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
idx_veg_dist_status = df.asset.str.contains('VEG-DIST-STATUS')
idx_veg_dist_status
```

<!-- #region jupyter={"source_hidden": false} -->

Podemos utilizar esta `Series` booleana con el método de acceso `.loc` de Pandas para filtrar solo las filas que queremos (por ejemplo, las que se conectan a archivos de datos ráster que almacenan la banda `VEG-DIST-STATUS`). Posteriormente podemos eliminar la columna `asset` (que ya no es necesaria).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
veg_dist_status = df.loc[idx_veg_dist_status]
veg_dist_status = veg_dist_status.drop('asset', axis=1)
veg_dist_status
```

```{code-cell} python jupyter={"source_hidden": false}
print(len(veg_dist_status))
```

<!-- #region jupyter={"source_hidden": false} -->

Observe que algunas de las filas tienen la misma fecha pero horas diferentes (lo cual corresponde a varias observaciones en el mismo día del calendario UTC). Podemos agregar las URL en listas _remuestreando_ la serie temporal por día. Posteriormente podremos visualizar el resultado.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
by_day = veg_dist_status.resample('1d').href.apply(list)
display(by_day)
by_day.map(len).hvplot.scatter(grid=True).opts(title='# of observations')
```

<!-- #region jupyter={"source_hidden": false} -->

Limpiemos la `Series` `by_day` filtrando las filas que tienen listas vacías (es decir, fechas en las que no se adquirieron datos).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
by_day = by_day.loc[by_day.map(bool)]
by_day.map(len).hvplot.scatter(ylim=(0,2.1), grid=True).opts(title="# of observations")
```

<!-- #region jupyter={"source_hidden": false} -->

Ahora podemos utilizar la serie `by_day` remuestreada para extraer datos ráster para su análisis.

---

<!-- #endregion -->

## Procesamiento de los datos

<!-- #region jupyter={"source_hidden": false} -->

El incendio forestal cerca de Alexandroupolis comenzó alrededor del 21 de agosto y se propagó rápidamente, afectando en particular al cercano bosque de Dadia. En primer lugar, vamos a ensamblar un "cubo de datos" (por ejemplo, un arreglo apilado de rásters) a partir de los archivos remotos indexados en la serie Pandas `by_day`. Empezaremos seleccionando y cargando uno de los archivos GeoTIFF remotos para extraer los metadatos que se aplican a todos los rásteres asociados con este evento y este mosaico MGRS.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
href = by_day[0][0]
data = rio.open_rasterio(href).rename(dict(x='longitude', y='latitude'))
crs = data.rio.crs
shape = data.shape
```

<!-- #region jupyter={"source_hidden": false} -->

Antes de construir un `DataArray` apilado dentro de un bucle, definiremos un diccionario de Python llamado `template` que se utilizará para instanciar los cortes del arreglo. El diccionario `template` almacenará los metadatos extraídos del archivo GeoTIFF, especialmente las coordenadas.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
template = dict()
template['coords'] = data.coords.copy()
del template['coords']['band']
template['coords'].update({'time': by_day.index.values})
template['dims'] = ['time', 'longitude', 'latitude']
template['attrs'] = dict(description=f"OPERA DSWX: VEG-DIST-STATUS", units=None)

print(template)
```

<!-- #region jupyter={"source_hidden": false} -->

Utilizaremos un bucle para construir un arreglo apilado de rásteres a partir de la serie Pandas `by_day` (cuyas entradas son listas de cadenas de caracteres, es decir, URIs). Si la lista tiene un único elemento, la URL se puede leer directamente utilizando `rasterio.open`; de lo contrario, la función [`rasterio.merge.merge`](https://rasterio.readthedocs.io/en/latest/api/rasterio.merge.html) combina varios archivos de datos ráster adquiridos el mismo día en una única imagen ráster.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import rasterio
from rasterio.merge import merge
```

```{code-cell} python jupyter={"source_hidden": false}
%%time
rasters = []
for date, hrefs in by_day.items():
    n_files = len(hrefs)
    if n_files > 1:
        print(f"Merging {n_files} files for {date.strftime('%Y-%m-%d')}...")
        raster, _ = merge(hrefs)
    else:
        print(f"Opening {n_files} file  for {date.strftime('%Y-%m-%d')}...")
        with rasterio.open(hrefs[0]) as ds:
            raster = ds.read()
    rasters.append(np.reshape(raster, newshape=shape))
```

<!-- #region jupyter={"source_hidden": false} -->

Los datos acumulados en la lista de `rasters` se almacenan como arreglos de NumPy. Así, en vez de llamar a `xarray.concat`, realizamos una llamada a `numpy.concatenate` dentro de una llamada al constructor `xarray.DataArray`. Vinculamos el objeto creado al identificador `stack`, asegurándonos de incluir también la información CRS.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack = xr.DataArray(data=np.concatenate(rasters, axis=0), **template)
stack.rio.write_crs(crs, inplace=True)
stack
```

<!-- #region jupyter={"source_hidden": false} -->

La pila `DataArray` `stack` tiene `time`, `longitude` y `latitude` como principales dimensiones de coordenadas. Podemos utilizarla para hacer algunos cálculos y generar visualizaciones.

---

<!-- #endregion -->

### Visualización del área dañada

<!-- #region jupyter={"source_hidden": false} -->

Para empezar, utilicemos los datos en `stack` para calcular la superficie total dañada. Los datos en `stack` provienen de la banda `VEG-DIST-STATUS` del producto DIST-ALERT. Interpretamos los valores de los píxeles en esta banda de la siguiente manera:

- **0:** Sin alteración
- **1:** La primera detección de alteraciones con cambio en la cobertura vegetal $<50\%$
- **2:** Detección provisional de alteraciones con cambio en la cobertura vegetal $<50\%$
- **3:** Detección confirmada de alteraciones con cambio en la cobertura vegetal $<50\%$
- **4:** La primera detección de alteraciones con cambio en la cobertura vegetal $\ge50\%$
- **5:** Detección provisional de alteraciones con cambio en la cobertura vegetal $\ge50\%$
- **6:** Detección confirmada de alteraciones con cambio en la cobertura vegetal $\ge50\%$
- **7:** Detección finalizada de alteraciones con cambio en la cobertura vegetal $<50\%$
- **8:** Detección finalizada de alteraciones con cambio en la cobertura vegetal $\ge50\%$

El valor del píxel particular que queremos marcar es 6, es decir, un píxel en el que se confirmó que por lo menos el 50% de la cubierta vegetal está dañada y en el que la alteración continúa activamente. Podemos utilizar el método `.sum` para sumar todos los píxeles con valor `6` y el método `.to_series` para representar la suma como una serie de Pandas indexada en el tiempo. También definimos `conversion_factor` que toma en cuenta el área de cada píxel en $\mathrm{km}^2$ (recordemos que cada píxel tiene un área de $30\mathrm{m}\times30\mathrm{m}$).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
pixel_val = 6
conversion_factor = (30/1_000)**2 / pixel_val
damage_area = stack.where(stack==pixel_val, other=0).sum(axis=(1,2)) 
damage_area = damage_area.to_series() * conversion_factor
damage_area
```

```{code-cell} python jupyter={"source_hidden": false}
plot_title = 'Damaged Area (km²)'
line_plot_opts = dict(title=plot_title, grid=True, color='r')
damage_area.hvplot.line(**line_plot_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Observando el gráfico anterior, parece que los incendios forestales comenzaron alrededor del 21 de agosto y se propagaron rápidamente.

---

<!-- #endregion -->

### Visualización de fragmentos temporales seleccionados

<!-- #region jupyter={"source_hidden": false} -->

El bosque cercano de Dadia se vio especialmente afectado por los incendios. Para comprobarlo, trazaremos los datos ráster para ver la distribución espacial de los píxeles dañados en tres fechas concretas: 2 de agosto, 26 de agosto y 18 de septiembre. Una vez más, resaltaremos solamente los píxeles que tengan valor 6 en los datos ráster. Podemos extraer fácilmente esas fechas específicas de la serie temporal `by_day` utilizando una lista de fechas (por ejemplo, `dates_of_interest` en la siguiente celda).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
dates_of_interest = ['2023-08-01', '2023-08-26', '2023-09-18']
print(dates_of_interest)
snapshots = stack.sel(time=dates_of_interest)
snapshots
```

<!-- #region jupyter={"source_hidden": false} -->

Vamos a hacer una secuencia estática de los gráficos. Empezaremos definiendo algunas opciones estándar almacenadas en diccionarios.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(
                    x='longitude', 
                    y='latitude',
                    rasterize=True, 
                    dynamic=True,
                    crs=crs,
                    shared_axes=False,
                    colorbar=False,
                    aspect='equal',
                 )
layout_opts = dict(xlabel='Longitude', ylabel="Latitude")
```

<!-- #region jupyter={"source_hidden": false} -->

Construiremos un mapa de colores utilizando un diccionario de valores RGBA (por ejemplo, tuplas con tres entradas enteras entre 0 y 255, y una cuarta entrada de punto flotante entre 0.0 y 1.0 para la transparencia).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
COLORS = { k:(0,0,0,0.0) for k in range(256) }
COLORS.update({6: (255,0,0,1.0)})
image_opts.update(cmap=list(COLORS.values()))
```

<!-- #region jupyter={"source_hidden": false} -->

Como siempre, empezaremos por cortar imágenes más pequeñas para asegurarnos de que
`hvplot.image` funciona correctamente. Podemos reducir el valor del parámetro `steps` a `1` o `None` para obtener las imágenes renderizadas en resolución completa.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 100
subset = slice(0,None, steps)
view = snapshots.isel(longitude=subset, latitude=subset)
(view.hvplot.image(**image_opts).opts(**layout_opts) * basemap).layout()
```

<!-- #region jupyter={"source_hidden": false} -->

Si eliminamos la llamada a `.layout`, podemos producir un desplazamiento interactivo que muestre el progreso del incendio forestal utilizando todos los rásteres en `stack`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 100
subset = slice(0,None, steps)
view = stack.isel(longitude=subset, latitude=subset,)
(view.hvplot.image(**image_opts).opts(**layout_opts) * basemap)
```

---

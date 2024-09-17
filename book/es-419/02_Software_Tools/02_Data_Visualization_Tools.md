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

# Visualización de datos

<!-- #region jupyter={"source_hidden": true} -->

Las herramientas primarias que usaremos para la trazado vienen de la familia [Holoviz](https://holoviz.org/) de bibliotecas de Python, principalmente [GeoViews](https://geoviews.org/) y [hvPlot](https://hvplot.holoviz.org/). Estos están construidos en gran medida sobre [HoloViews](https://holoviews.org/) y soportan múltiples backends para renderizar gráficos (especialmente [Bokeh](http://bokeh. ydata.org/) para la visualización interactiva y [Matplotlib](http://matplotlib.org/) para gráficos estáticos de publicación-calidad).

<!-- #endregion -->

## [GeoViews](https://geoviews.org/)

<!-- #region jupyter={"source_hidden": true} -->

Desde la [documentación de GeoViews](https://geoviews.org/index.html):

> GeoViews es un [Python](http://python. rg/) biblioteca que hace fácil explorar y visualizar geográficos, meteorológicos, y conjuntos de datos oceanográficos, como los utilizados en la investigación meteorológica, climática y teledetección.
>
> GeoViews está construido en la biblioteca [HoloViews](http://holoviews.org/) para construir visualizaciones flexibles de datos multidimensionales. GeoViews añade una familia de tipos de gráficos geográficos basados en la biblioteca [Cartopy](http://scitools.org.uk/cartopy), trazada usando los paquetes [Matplotlib](http://matplotlib.org/) o [Bokeh](http://bokeh.pydata.org/). Con GeoViews, ahora puede trabajar fácil y naturalmente con grandes conjuntos de datos geográficos multidimensionales, visualizando instantáneamente cualquier subconjunto o combinación de los mismos, siendo siempre capaz de acceder a los datos crudos subyacentes a cualquier parcela.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

import geoviews as gv
gv.extension('bokeh')
from geoviews import opts
```

### Mostrar un mapa base

<!-- #region jupyter={"source_hidden": true} -->

Una _capa base_ o _capa de azulejos_ es útil cuando se muestran datos vectoriales o raster porque nos permite superponer los datos geoespaciales relevantes en un mapa geográfico familiar como fondo. La utilidad principal es que usaremos es `gv.tile_sources`. Podemos usar el método `opts` para especificar configuraciones de confirmación adicionales. A continuación, utilizamos el Servicio de Tiles de Mapa Web _Open Street Map (OSM)_ para crear el objeto `basemap`. Cuando mostramos el repr de este objeto en la célula, el menú Bokeh a la derecha permite la exploración interactiva.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
basemap = gv.tile_sources.OSM.opts(width=600, height=400)
basemap # When displayed, this basemap can be zoomed & panned using the menu at the right
```

### Puntuación de puntos

<!-- #region jupyter={"source_hidden": true} -->

Para empezar, definamos una tupla de Python para las coordenadas longitud-latitud de Tokyo, Japón.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
tokyo_lonlat = (139.692222, 35.689722)
print(tokyo_lonlat)
```

<!-- #region jupyter={"source_hidden": true} -->

La clase `geoviews.Points` acepta una lista de tuplas (cada una de las formas `(x, y)`) y construye un objeto `Points` que puede ser mostrado. Podemos superponer el punto creado en las baldosas OpenStreetMap de `basemap` usando el operador `*` en Holoviews. También podemos usar `geoviews.opts` para establecer varias preferencias de visualización para estos puntos.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
tokyo_point   = gv.Points([tokyo_lonlat])
point_opts = opts.Points(
                          size=48,
                          alpha=0.5,
                          color='red'
                        )
print(type(tokyo_point))
```

```python jupyter={"source_hidden": true}
# Use Holoviews * operator to overlay plot on basemap
# Note: zoom out to see basemap (starts zoomed "all the way in")
(basemap * tokyo_point).opts(point_opts)
```

```python jupyter={"source_hidden": true}
# to avoid starting zoomed all the way in, this zooms "all the way out"
(basemap * tokyo_point).opts(point_opts, opts.Overlay(global_extent=True))
```

### Trazar rectángulos

<!-- #region jupyter={"source_hidden": true} -->

- Forma estándar para representar el rectángulo con las esquinas
  $$(x_{\mathrm{min}},y_{\mathrm{min}}), (x_{\mathrm{min}},y_{\mathrm{max}}), (x_{\mathrm{max}},y_{\mathrm{min}}), (x_{\mathrm{max}}, _{\mathrm{max}})$$
  (asumiendo $x_{\mathrm{max}}>x_{\mathrm{min}}$ & $y_{\mathrm{max}}>y_{\mathrm{min}}$) es como una única 4-tupla
  $$(x_{\mathrm{min}}, _{\mathrm{min}},x_{\mathrm{max}},y_{\mathrm{max}}),$$
  i.e., las coordenadas de la esquina inferior, izquierda seguidas de las coordenadas de la esquina superior derecha.

  Vamos a crear una función simple para generar un rectángulo de un ancho y altura dados, dada la coordenada central.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
# simple utility to make a rectangle centered at pt of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding-box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

<!-- #region jupyter={"source_hidden": true} -->

Podemos probar la función anterior utilizando las coordenadas longitud-latitud de Marrakesh, Marruecos.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Verify that the function bounds works as intended
marrakesh_lonlat = (-7.93, 31.67)
dlon, dlat = 0.5, 0.25
marrakesh_bbox = make_bbox(marrakesh_lonlat, dlon, dlat)
print(marrakesh_bbox)
```

<!-- #region jupyter={"source_hidden": true} -->

`geoviews.Rectangles` acepta una lista de cajas de límites (cada una descrita por una tupla de la forma `(x_min, y_min, x_max, y_max)`) para dibujar. Podemos usar de nuevo `geoviews.opts` para adaptar el rectángulo según sea necesario.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
rectangle = gv.Rectangles([marrakesh_bbox])
rect_opts = opts.Rectangles(
                                line_width=0,
                                alpha=0.1,
                                color='red'
                            )
```

<!-- #region jupyter={"source_hidden": true} -->

Podemos trazar un punto para Marrakesh como antes de usar `geoviews.Points` (personalizado usando `geoviews.opts`).

<!-- #endregion -->

```python jupyter={"source_hidden": true}
marrakesh_point   = gv.Points([marrakesh_lonlat])
point_opts = opts.Points(
                          size=48,
                          alpha=0.25,
                          color='blue'
                        )
```

<!-- #region jupyter={"source_hidden": true} -->

Finalmente, podemos superponer todas estas características en el mapa base con las opciones aplicadas.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
(basemap * rectangle * marrakesh_point).opts( rect_opts, point_opts )
```

<!-- #region jupyter={"source_hidden": true} -->

Utilizaremos el método anterior para visualizar _Áreas de Interés (AOIs)_ al construir consultas de búsqueda para productos EarthData de la NASA. En particular, la convención de representar una caja delimitadora por ordenadas (izquierda, inferior, derecha, superior) también se utiliza en la API [PySTAC](https://pystac.readthedocs.io/en/stable/).

---

<!-- #endregion -->

## [hvPlot](https://hvplot.holoviz.org/)

<!-- #region jupyter={"source_hidden": true} -->

- [hvPlot](https://hvplot.holoviz.org/) está diseñado para extender la API `.plot` de Pandas DataFrames.
- Funciona para Pandas DataFrames y Xarray DataArrays/Datasets.

<!-- #endregion -->

### Trazar desde un DataFrame con hvplot.pandas

<!-- #region jupyter={"source_hidden": true} -->

El código siguiente carga un Pandas DataFrame de datos de temperatura.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
import pandas as pd, numpy as np
from pathlib import Path
LOCAL_PATH = Path().cwd() / '..' / 'assets' / 'temperature.csv'
```

```python jupyter={"source_hidden": true}
df = pd.read_csv(LOCAL_PATH, index_col=0, parse_dates=[0])
df.head()
```

#### Revisando la API de Pandas DataFrame.plot

<!-- #region jupyter={"source_hidden": true} -->

Vamos a extraer un subconjunto de columnas de este DataFrame y generar un gráfico.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
west_coast = df[['Vancouver', 'Portland', 'San Francisco', 'Seattle', 'Los Angeles']]
west_coast.head()
```

<!-- #region jupyter={"source_hidden": true} -->

La API `.plot` de Pandas DataFrame proporciona acceso a varios métodos de trazado. Aquí, usaremos `.plot.line`, pero hay un rango de otras opciones disponibles (por ejemplo, `.plot.area`, `.plot.bar`, `.plot.nb`, `.plot.scatter`, etc.). Esta API se ha repetido en varias librerías debido a su conveniencia.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
west_coast.plot.line(); # This produces a static Matplotlib plot
```

#### Usando la API de hvPlot DataFrame.hvplot

<!-- #region jupyter={"source_hidden": true} -->

Importando `hvplot.pandas`, se puede generar una parcela interactiva similar. La API para `.hvplot` imita que para `.plot`. Por ejemplo, podemos generar la gráfica de línea anterior usando `.hvplot.line`. En este caso, el backend de trazado por defecto es Bokeh, así que el plot es _interactivo_.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
import hvplot.pandas
west_coast.hvplot.line() # This produces an interactive Bokeh plot
```

<!-- #region jupyter={"source_hidden": true} -->

Es posible modificar la parcela para hacerla más limpia.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
west_coast.hvplot.line(width=600, height=300, grid=True)
```

<!-- #region jupyter={"source_hidden": true} -->

La API `hvplot` también funciona cuando está encadenada junto con otras llamadas de método DataFrame. Por ejemplo, podemos volver a mostrar los datos de temperatura y calcular un medio para suavizarlo.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
smoothed = west_coast.resample('2d').mean()
smoothed.hvplot.line(width=600, height=300, grid=True)
```

### Trazar desde un DataFrame con hvplot.xarray

<!-- #region jupyter={"source_hidden": true} -->

La API `.plot` de Pandas también se extendió a Xarray, es decir, para Xarray `DataArray`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
import xarray as xr
import hvplot.xarray
import rioxarray as rio
```

<!-- #region jupyter={"source_hidden": true} -->

Para empezar, carga un archivo GeoTIFF local usando `rioxarray` en una estructura Zarray `DataArray`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
LOCAL_PATH = Path('..') / 'assets' / 'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'
```

```python jupyter={"source_hidden": true}
data = rio.open_rasterio(LOCAL_PATH)
data
```

<!-- #region jupyter={"source_hidden": true} -->

Hacemos algunos reformateos menores al `DataArray`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
data = data.squeeze() # to reduce 3D array with singleton dimension to 2D array
data = data.rename({'x':'easting', 'y':'northing'})
data
```

#### Revisando la API de Pandas DataFrame.plot

<!-- #region jupyter={"source_hidden": true} -->

La API `DataArray.plot` por defecto usa el `pcolormesh` de Matplotlib's para mostrar una matriz 2D almacenada dentro de un `DataArray`. Esto toma un poco de tiempo para renderizar esta imagen moderadamente de alta resolución.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
data.plot(); # by default, uses pcolormesh
```

#### Usando la API de hvPlot DataFrame.hvplot

<!-- #region jupyter={"source_hidden": true} -->

De nuevo, la API `DataArray.hvplot` imita la API `DataArray.plot`; de forma predeterminada, utiliza una subclase derivada de `holoviews.element.raster.Image`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
plot = data.hvplot() # by default uses Image class
print(f'{type(plot)=}')
plot
```

<!-- #region jupyter={"source_hidden": true} -->

El resultado anterior es una trama interactiva, procesada usando Bokeh.It's un poco lento, pero podemos añadir algunas opciones para acelerar la renderización. También requiere limpieza; por ejemplo, la imagen no es cuadrada, el mapa de colores no resalta características útiles, los ejes son transpuestos, etc.

<!-- #endregion -->

#### Creando opciones incrementalmente para mejorar las parcelas

<!-- #region jupyter={"source_hidden": true} -->

Añadamos opciones para mejorar la imagen. Para hacer esto, iniciaremos un diccionario de Python `image_opts` para usar dentro de la llamada al método `image`. Utilizaremos el método `dict.update` para agregar pares clave-valor al diccionario incrementalmente, cada vez que mejore la imagen de salida.

<!-- #endregion -->

```python
image_opts = dict(rasterize=True, dynamic=True)
```

<!-- #region jupyter={"source_hidden": true} -->

Para empezar, hagamos la llamada a `hvplot.image` explícita y especifiquemos la secuencia de ejes. Y aplicar las opciones del diccionario `image_opts`. Utilizaremos la operación dict-unpacking `**image_opts` cada vez que invocemos `data.hvplot.image`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->

A continuación, vamos a corregir la relación de aspecto y las dimensiones de la imagen.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts.update(frame_width=500, frame_height=500, aspect='equal')

plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->

El mapa de colores de la imagen es un poco desagradable; vamos a cambiarlo y usar transparencia (`alpha`).

<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts.update( cmap='hot_r', clim=(0,100), alpha=0.8 )
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->

Antes de añadir un mapa de base, tenemos que tener en cuenta el sistema de coordenadas. Esto se almacena en el archivo GeoTIFF y, cuando se lee usando `rioxarray.open_rasterio`, está disponible utilizando el atributo `data.rio.crs`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
crs = data.rio.crs
crs
```

<!-- #region jupyter={"source_hidden": true} -->

Podemos usar el CRS recuperado arriba como un argumento opcional a `hvplot.image`. Tenga en cuenta que las coordenadas han cambiado en los ejes, pero las etiquetas están equivocadas. Podemos arreglarlo en breve.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts.update(crs=crs)

plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

Ahora vamos a corregir las etiquetas. Utilizaremos el sistema Holoviews/GeoViews `opts` para especificar estas opciones.

```python jupyter={"source_hidden": true}
label_opts = dict(title='VEG_ANOM_MAX', xlabel='Longitude (degrees)', ylabel='Latitude (degrees)')
plot = data.hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->

Vamos a sobreponer la imagen en un mapa base para que podamos ver el terreno debajo.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
base = gv.tile_sources.ESRI
base * plot
```

<!-- #region jupyter={"source_hidden": true} -->

Finalmente, los píxeles blancos son distraídos; vamos a filtrarlos utilizando el método `DataArray` `where`.

<!-- #endregion -->

```python jupyter={"source_hidden": true}
plot = data.where(data>0).hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot * base
```

<!-- #region jupyter={"source_hidden": true} -->

En este cuaderno aplicamos algunas estrategias comunes para generar parcelas. Los usaremos extensamente en el resto del tutorial.

<!-- #endregion -->

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

# Visualización de datos con GeoViews y HvPlot

<!-- #region jupyter={"source_hidden": false} -->

Las principales herramientas que utilizaremos para la visualización de datos provienen de la familia [Holoviz](https://holoviz.org/) de librerías Python, principalmente [GeoViews](https://geoviews.org/) y [hvPlot](https://hvplot.holoviz.org/). Estas están construidas en gran parte sobre [HoloViews](https://holoviews.org/) y soportan múltiples _backends_ para la representación de gráficos ([Bokeh](http://bokeh.pydata.org/) para visualización interactiva y [Matplotlib](http://matplotlib.org/) para gráficos estáticos con calidad de publicación.

<!-- #endregion -->

***

## [GeoViews](https://geoviews.org/)

<!-- #region jupyter={"source_hidden": false} -->

<center><img src="https://geoviews.org/_static/logo_horizontal.png"></center>

De la [documentación de GeoViews](https://geoviews.org/index.html):

> GeoViews es una librería de [Python](http://python.org/) que facilita la exploración y visualización de conjuntos de datos geográficos, meteorológicos y oceanográficos, como los que se utilizan en la investigación meteorológica, climática y de teledetección.
>
> GeoViews se basa en la biblioteca [HoloViews](http://holoviews.org/) y permite crear visualizaciones flexibles de datos multidimensionales. GeoViews agrega una familia de tipos de gráficos geográficos basados en la librería [Cartopy](http://scitools.org.uk/cartopy), trazados con los paquetes [Matplotlib](http://matplotlib.org/) o [Bokeh](http://bokeh.pydata.org/). Con GeoViews, puedes trabajar de forma fácil y natural con grandes conjuntos de datos geográficos multidimensionales, visualizando al instante cualquier subconjunto o combinación de ellos. Al mismo tiempo, podrás acceder siempre a los datos crudos subyacentes a cualquier gráfico.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
from pprint import pprint

import geoviews as gv
gv.extension('bokeh')
from geoviews import opts

FILE_STEM = Path.cwd().parent if 'book' == Path.cwd().parent.stem else 'book'
```

***

### Visualización de un mapa base

<!-- #region jupyter={"source_hidden": false} -->

Un _mapa base_ o _capa de mosaico_ es útil cuando se muestran datos vectoriales o ráster porque nos permite superponer los datos geoespaciales relevantes sobre un mapa geográfico conocido como fondo. La principal funcionalidad que utilizaremos es `gv.tile_sources`. Podemos utilizar el método `opts` para especificar parámetros de configuración adicionales. A continuación, utilizaremos el servicio de mapas web _Open Street Map (OSM)_ (en español, Mapas de Calles Abiertos) para crear el objeto `basemap`. Cuando mostramos la representación de este objeto en la celda del cuaderno computacional, el menú de Bokeh que está a la derecha permite la exploración interactiva.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
basemap = gv.tile_sources.OSM.opts(width=600, height=400)
basemap # When displayed, this basemap can be zoomed & panned using the menu at the right
```

***

### Gráficos de puntos

<!-- #region jupyter={"source_hidden": false} -->

Para empezar, vamos a definir una tupla regular en Python para las coordenadas de longitud y latitud de Tokio, Japón.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
tokyo_lonlat = (139.692222, 35.689722)
print(tokyo_lonlat)
```

<!-- #region jupyter={"source_hidden": false} -->

La clase `geoviews.Points` acepta una lista de tuplas (cada una de la forma `(x, y)`) y construye un objeto `Points` que puede ser visualizado. Podemos superponer el punto creado en los mosaicos _Open Street Map_ de `basemap` utilizando el operador `*` en Holoviews. También podemos utilizar `geoviews.opts` para establecer varias preferencias de visualización para estos puntos.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
tokyo_point   = gv.Points([tokyo_lonlat])
point_opts = opts.Points(
                          size=48,
                          alpha=0.5,
                          color='red'
                        )
print(type(tokyo_point))
```

```{code-cell} python jupyter={"source_hidden": false}
# Use Holoviews * operator to overlay plot on basemap
# Note: zoom out to see basemap (starts zoomed "all the way in")
(basemap * tokyo_point).opts(point_opts)
```

```{code-cell} python jupyter={"source_hidden": false}
# to avoid starting zoomed all the way in, this zooms "all the way out"
(basemap * tokyo_point).opts(point_opts, opts.Overlay(global_extent=True))
```

***

### Gráficos de rectángulos

<!-- #region jupyter={"source_hidden": false} -->

- Forma estándar de representar un rectángulo (también llamado caja delimitadora) con vértices $$(x_{\mathrm{min}},y_{\mathrm{min}}), (x_{\mathrm{min}},y_{\mathrm{max}}), (x_{\mathrm{max}},y_{\mathrm{min}}), (x_{\mathrm{max}},y_{\mathrm{max}})$$
  (suponiendo que $x_{\mathrm{max}}>x_{\mathrm{min}}$ & $y_{\mathrm{max}}>y_{\mathrm{min}}$) es como única cuadrupla
  $$(x_{\mathrm{min}},y_{\mathrm{min}},x_{\mathrm{max}},y_{\mathrm{max}})$$,
  es decir, las coordenadas de la esquina inferior izquierda seguidas de las coordenadas de la esquina superior derecha.

  Vamos a crear una función sencilla para generar un rectángulo de un ancho y altura dados, según la coordenada central.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
# simple utility to make a rectangle centered at pt of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

<!-- #region jupyter={"source_hidden": false} -->

Podemos probar la función anterior utilizando las coordenadas de longitud y latitud de Marruecos.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
# Verify that the function bounds works as intended
marrakesh_lonlat = (-7.93, 31.67)
dlon, dlat = 0.5, 0.25
marrakesh_bbox = make_bbox(marrakesh_lonlat, dlon, dlat)
print(marrakesh_bbox)
```

<!-- #region jupyter={"source_hidden": false} -->

La función `geoviews.Rectangles` acepta una lista de cajas delimitadoras (cada uno descrito por una tupla de la forma `(x_min, y_min, x_max, y_max)`) para el trazado. También podemos utilizar `geoviews.opts` para adaptar el rectángulo a nuestras necesidades.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
rectangle = gv.Rectangles([marrakesh_bbox])
rect_opts = opts.Rectangles(
                                line_width=0,
                                alpha=0.1,
                                color='red'
                            )
```

<!-- #region jupyter={"source_hidden": false} -->

Podemos graficar un punto para Marruecos al igual que antes utilizando `geoviews.Points` (personalizado utilizando `geoviews.opts`).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
marrakesh_point   = gv.Points([marrakesh_lonlat])
point_opts = opts.Points(
                          size=48,
                          alpha=0.25,
                          color='blue'
                        )
```

<!-- #region jupyter={"source_hidden": false} -->

Por último, podemos superponer todas estas características en el mapa base con las opciones aplicadas.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
(basemap * rectangle * marrakesh_point).opts( rect_opts, point_opts )
```

<!-- #region jupyter={"source_hidden": false} -->

Utilizaremos el método anterior para visualizar _(AOIs)_ al construir consultas de búsqueda para los productos EarthData de la NASA. En particular, la convención de representar una caja delimitadora por ordenadas (izquierda, inferior, derecha, superior) también se utiliza en la API [PySTAC](https://pystac.readthedocs.io/en/stable/).

<!-- #endregion -->

***

## [hvPlot](https://hvplot.holoviz.org/)

<!-- #region jupyter={"source_hidden": false} -->

<center><img src="https://hvplot.holoviz.org/_images/diagram.svg"></center>

- [hvPlot](https://hvplot.holoviz.org/) está diseñado para extender la API `.plot` de `DataFrames` de Pandas.
- Funciona para `DataFrames` de Pandas y `DataArrays`/`Datasets` de Xarray.

<!-- #endregion -->

***

### Graficar desde un DataFrame con hvplot.pandas

<!-- #region jupyter={"source_hidden": false} -->

El siguiente código carga un `DataFrame` de Pandas con datos de temperatura.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import pandas as pd, numpy as np
from pathlib import Path
LOCAL_PATH = Path(FILE_STEM, 'assets/temperature.csv')
```

```{code-cell} python jupyter={"source_hidden": false}
df = pd.read_csv(LOCAL_PATH, index_col=0, parse_dates=[0])
df.head()
```

***

#### Revisando la API de `DataFrame.plot` de Pandas

<!-- #region jupyter={"source_hidden": false} -->

Vamos a extraer un subconjunto de columnas de este `DataFrame` y generar un gráfico.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
west_coast = df[['Vancouver', 'Portland', 'San Francisco', 'Seattle', 'Los Angeles']]
west_coast.head()
```

<!-- #region jupyter={"source_hidden": false} -->

La API de `.plot` de `DataFrame` de Pandas proporciona acceso a varios métodos de visualización. Aquí usaremos `.plot.line`, pero hay otras opciones disponibles (por ejemplo, `.plot.area`, `.plot.bar`, `.plot.nb`, `.plot.scatter`, etc.). Esta API se ha utilizado en varias librerías debido a su conveniencia.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
west_coast.plot.line(); # This produces a static Matplotlib plot
```

***

#### Usando la API de hvPlot `DataFrame.hvplot`

<!-- #region jupyter={"source_hidden": false} -->

Importando `hvplot.pandas`, se puede generar un gráfico interactivo similar. La API para `.hvplot` imita esto para `.plot`. Por ejemplo, podemos generar la gráfica de línea anterior usando `.hvplot.line`. En este caso, el _backend_ para los gráficos por defecto es Bokeh, así que el gráfico es _interactivo_.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import hvplot.pandas
west_coast.hvplot.line() # This produces an interactive Bokeh plot
```

<!-- #region jupyter={"source_hidden": false} -->

La API `.plot`  de DataFrame de Pandas proporciona acceso a una serie de métodos de visualización.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
west_coast.hvplot.line(width=600, height=300, grid=True)
```

<!-- #region jupyter={"source_hidden": false} -->

La API `hvplot` también funciona cuando está enlazada junto con otras llamadas del método `DataFrame`. Por ejemplo, podemos muestrear los datos de temperatura y calcular la media para suavizarlos.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
smoothed = west_coast.resample('2d').mean()
smoothed.hvplot.line(width=600, height=300, grid=True)
```

***

### Graficar desde un `DataArray` con `hvplot.xarray`

<!-- #region jupyter={"source_hidden": false} -->

La API `.plot` de Pandas también se extendió a Xarray, es decir, para `DataArray`. de Xarray

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import xarray as xr
import hvplot.xarray
import rioxarray as rio
```

<!-- #region jupyter={"source_hidden": false} -->

Para empezar, carga un archivo GeoTIFF local usando `rioxarray` en una estructura Zarray de `DataArray`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
LOCAL_PATH = Path(FILE_STEM, 'assets/OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif')
```

```{code-cell} python jupyter={"source_hidden": false}
data = rio.open_rasterio(LOCAL_PATH)
data
```

<!-- #region jupyter={"source_hidden": false} -->

Hacemos algunos cambios menores al `DataArray`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data = data.squeeze() # to reduce 3D array with singleton dimension to 2D array
data = data.rename({'x':'easting', 'y':'northing'})
data
```

***

#### Revisando la API `DataFrame.plot` de Pandas

<!-- #region jupyter={"source_hidden": false} -->

La API `DataArray.plot` por defecto usa el `pcolormesh` de Matplotlib para mostrar un arreglo de 2D almacenado dentro de un `DataArray`. La renderización de esta imagen que es de moderadamente de alta resolución, lleva un poco de tiempo.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data.plot(); # by default, uses pcolormesh
```

***

#### Usando la API de hvPlot `DataFrame.hvplot`

<!-- #region jupyter={"source_hidden": false} -->

De nuevo, la API `DataArray.hvplot` imita la API `DataArray.plot`; de forma predeterminada, utiliza una subclase derivada de `holoviews.element.raster.Image`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
plot = data.hvplot() # by default uses Image class
print(f'{type(plot)=}')
plot
```

<!-- #region jupyter={"source_hidden": false} -->

El resultado anterior es una visualización interactiva, procesada usando Bokeh. Esto es un poco lento, pero podemos añadir algunas opciones para acelerar la renderización. También se requiere una manipulación de la misma; por ejemplo, la imagen no es cuadrada, el mapa de colores no resalta características útiles, los ejes son transpuestos, etc.

<!-- #endregion -->

***

#### Creando opciones para mejorar los gráficos de manera incremental

<!-- #region jupyter={"source_hidden": false} -->

Añadamos opciones para mejorar la imagen. Para hacer esto, iniciaremos un diccionario de Python `image_opts` para usar dentro de la llamada al método `image`. Creando opciones para mejorar los gráficos de manera incremental.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(rasterize=True, dynamic=True)
pprint(image_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Para empezar, hagamos la llamada explícita a `hvplot.image` y especifiquemos la secuencia de ejes. Y apliquemos las opciones del diccionario `image_opts`. Utilizaremos la operación `dict-unpacking` `**image_opts` cada vez que invoquemos a `data.hvplot.image`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->

A continuación, vamos a corregir  el ratio y las dimensiones de la imagen.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts.update(frame_width=500, frame_height=500, aspect='equal')
pprint(image_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->

El mapa de colores de la imagen es un poco desagradable; vamos a cambiarlo y usar transparencia (`alpha`).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts.update( cmap='hot_r', clim=(0,100), alpha=0.8 )
pprint(image_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->

Antes de añadir un mapa de base, tenemos que tener en cuenta el sistema de coordenadas. Esto se almacena en el archivo GeoTIFF y, cuando se lee usando `rioxarray.open_rasterio`, se disponibilizada mediante el atributo `data.rio.crs`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
crs = data.rio.crs
crs
```

<!-- #region jupyter={"source_hidden": false} -->

Podemos usar el CRS recuperado arriba como un argumento opcional para `hvplot.image`. Ten en cuenta que las coordenadas han cambiado en los ejes, pero las etiquetas no son las correctas. Podemos arreglarlo.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts.update(crs=crs)
pprint(image_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->

Ahora vamos a corregir las etiquetas. Utilizaremos el sistema Holoviews/GeoViews `opts` para especificar estas opciones.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
label_opts = dict(title='VEG_ANOM_MAX', xlabel='Longitude (degrees)', ylabel='Latitude (degrees)')
pprint(image_opts)
pprint(label_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->

Vamos a superponer la imagen en un mapa base para que podamos ver el terreno debajo.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
base = gv.tile_sources.ESRI
base * plot
```

<!-- #region jupyter={"source_hidden": false} -->

Finalmente, como los píxeles blancos distraen vamos a filtrarlos utilizando el método `DataArray` `where`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
plot = data.where(data>0).hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot * base
```

<!-- #region jupyter={"source_hidden": false} -->

En este cuaderno computacional aplicamos algunas estrategias comunes para generar gráficos. Los usaremos extensamente en el resto del tutorial.

<!-- #endregion -->

***

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

# Construyendo visualizaciones avanzadas

<!-- #region jupyter={"source_hidden": false} -->

Vamos a aplicar algunas de las herramientas que hemos visto hasta ahora para obtener algunas visualizaciones más sofisticadas. Estas incluirán el uso de datos vectoriales de un `GeoDataFrame` de _GeoPandas_, se construirán gráficos estáticos y dinámicos a partir de un arreglo 3D y se combinarán datos vectoriales y datos ráster.

Como contexto, los archivos que examinaremos se basan en [el incendio McKinney que ocurrió en el 2022](https://en.wikipedia.org/wiki/McKinney_Fire), en el Bosque Nacional Klamath (al oeste del condado de Siskiyou, California). Los datos vectoriales representan una instantánea del límite de un incendio forestal. Los datos ráster corresponden a la alteración que se observó en la cobertura de la vegetación (esto se explicará con mayor detalle más adelante).

<!-- #endregion -->

## Importación preliminar y direcciones de los archivos

<!-- #region jupyter={"source_hidden": false} -->

Para empezar, se necesitan algunas importaciones de paquetes. También definiremos algunas direcciones a archivos locales que contienen datos geoespaciales relevantes.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
from warnings import filterwarnings
filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
import geopandas as gpd
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
FILE_STEM = Path.cwd().parent if 'book' == Path.cwd().parent.stem else 'book'
ASSET_PATH = Path(FILE_STEM, 'assets')
SHAPE_FILE = ASSET_PATH / 'shapefiles' / 'mckinney' / 'McKinney_NIFC.shp'
RASTER_FILES = list(ASSET_PATH.glob('OPERA*VEG*.tif'))
RASTER_FILE = RASTER_FILES[0]
```

***

## Graficar datos vectoriales desde un `GeoDataFrame`

<!-- #region jupyter={"source_hidden": false} -->

<center><img src="https://geopandas.org/en/latest/_images/geopandas_logo.png" width=360px></center>

El paquete [GeoPandas](https://geopandas.org/en/stable/index.html) contiene muchas herramientas útiles para trabajar con datos geoespaciales vectoriales. En particular, el [`GeoDataFrame` de GeoPandas](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html) es una subclase del `DataFrame` de Pandas que está específicamente diseñado, por ejemplo, para datos vectoriales almacenados en _shapefiles_.

Como ejemplo, vamos a cargar algunos datos vectoriales desde la ruta local `SHAPEFILE` (tal como se definió anteriormente).

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shape_df = gpd.read_file(SHAPE_FILE)
shape_df
```

<!-- #region jupyter={"source_hidden": false} -->

El objeto `shape_df` es un [`GeoDataFrame`](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html) que tiene más de dos docenas de columnas de metadatos en una sola fila. La columna principal que nos interesa es la de `geometry`. Esta columna almacena las coordenadas de los vértices de un `MULTIPOLYGON`, es decir, un conjunto de polígonos.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shape_df.geometry 
```

<!-- #region jupyter={"source_hidden": false} -->

Los vértices de los polígonos parecen expresarse como pares de `(longitude, latitude)`. Podemos determinar qué sistema de coordenadas específico se utiliza examinando el atributo `crs` del `GeoDataFrame`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(shape_df.crs)
```

<!-- #region jupyter={"source_hidden": false} -->

Utilicemos `hvplot` para generar un gráfico de este conjunto de datos vectoriales.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shape_df.hvplot()
```

<!-- #region jupyter={"source_hidden": false} -->

La proyección en este gráfico es un poco extraña. La documentación de HoloViz incluye una [discusión sobre las consideraciones cuando se visualizan datos geográficos](https://hvplot.holoviz.org/user_guide/Geographic_Data.html). El punto importante a recordar en este contexto es que la opción `geo=True` es útil.

Vamos a crear dos diccionarios de Python, `shapeplot_opts` y `layout_opts`, y construiremos una visualización.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts= dict(geo=True)
layout_opts = dict(xlabel='Longitude', ylabel="Latitude")
print(f"{shapeplot_opts=}")
print(f"{layout_opts=}")

shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

La documentación de HoloViz incluye una [discusión sobre las consideraciones cuando se grafican datos geográficos](https://hvplot.holoviz.org/user_guide/Geographic_Data.html). Es importante recordar que la opción `geo=True` es útil.

- Definir `color=None` significa que los polígonos no se rellenarán.
- Al especificar `line_width` y `line_color` se modifica la apariencia de los límites de los polígonos.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts.update( color=None ,
                       line_width=2,
                       line_color='red')
print(shapeplot_opts)

shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Rellenemos los polígonos con color naranja utilizando la opción `color=orange` y hagamos que el área rellenada sea parcialmente transparente especificando un valor para `alpha` entre cero y uno.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts.update(color='orange', alpha=0.25)
print(shapeplot_opts)

shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

### Agregado de un mapa base

<!-- #region jupyter={"source_hidden": false} -->

A continuación, proporcionemos un mapa base y superpongamos los polígonos trazados utilizando el operador `*`. Observa el uso de paréntesis para aplicar el método `opts` a la salida del operador `*`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
basemap = gv.tile_sources.ESRI(height=500, width=500, padding=0.1)

(shape_df.hvplot(**shapeplot_opts) * basemap).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

El mapa base no necesita ser superpuesto como un objeto separado, puede especificarse utilizando la palabra clave `tiles`. Por ejemplo, al establecer `tiles='OSM'` se utilizan los mosaicos de [_Open Street Map_](ttps://www.openstreetmap.org). Observa que las dimensiones de la imagen renderizada probablemente no sean las mismas que las de la imagen anterior con los mosaicos [ESRI](https://www.esri.com), ya que antes especificamos explícitamente la altura de 500, con la opción `height=500`, y el ancho de 500, con la opción `width=500`, en la definición del `basemap`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts.update(tiles='OSM')
shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Vamos a eliminar la opción `tiles` de `shapeplot_opts` y a vincular el objeto del gráfico resultante al identificador `shapeplot`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
del shapeplot_opts['tiles']
print(shapeplot_opts)

shapeplot = shape_df.hvplot(**shapeplot_opts)
shapeplot
```

### Combinación de datos vectoriales con datos ráster en un gráfico estático

<!-- #region jupyter={"source_hidden": false} -->

Combinemos estos datos vectoriales con algunos datos ráster. Cargaremos los datos raster desde un archivo local utilizando la función `rioxarray.open_rasterio`. Por practicidad, usaremos el encadenamiento de métodos para reetiquetar las coordenadas del `DataArray` cargado y usaremos el método `squeeze` para convertir el arreglo tridimensional que se cargó en uno bidimensional.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster = (
          rio.open_rasterio(RASTER_FILE)
            .rename(dict(x='longitude', y='latitude'))
            .squeeze()
         )
raster
```

<!-- #region jupyter={"source_hidden": false} -->

Utilizaremos un diccionario de Python `image_opts` para almacenar argumentos útiles y pasarlos a `hvplot.image`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(
                    x='longitude',
                    y='latitude',                   
                    rasterize=True, 
                    dynamic=True,
                    cmap='hot_r', 
                    clim=(0, 100), 
                    alpha=0.8,
                    project=True,
                 )

raster.hvplot.image(**image_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Podemos superponer `shapeplot` con los datos ráster graficados utilizando el operador `*`. Podemos utilizar las herramientas `Pan`, `Wheel Zoom` y `Box Zoom` en la barra de herramientas de Bokeh a la derecha del gráfico para hacer _zoom_ y comprobar que los datos vectoriales fueron trazados encima de los datos ráster.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster.hvplot.image(**image_opts) * shapeplot
```

<!-- #region jupyter={"source_hidden": false} -->

Además, podemos superponer los datos vectoriales y ráster en mosaicos ESRI utilizando `basemap`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster.hvplot.image(**image_opts) * shapeplot * basemap
```

<!-- #region jupyter={"source_hidden": false} -->

Observa que muchos de los píxeles blancos oscurecen el gráfico. Resulta que estos píxeles corresponden a ceros en los datos ráster, los cuales pueden ser ignorados sin problema. Podemos filtrarlos utilizando el método `where`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster = raster.where((raster!=0))
layout_opts.update(title="McKinney 2022 Wildfires")

(raster.hvplot.image(**image_opts) * shapeplot * basemap).opts(**layout_opts)
```

***

## Construcción de gráficos estáticos a partir de un arreglo 3D

<!-- #region jupyter={"source_hidden": false} -->

Vamos a cargar una secuencia de archivos ráster en un arreglo tridimensional y generaremos algunos gráficos. Para empezar, construiremos un bucle para leer `DataArrays` de los archivos `RASTER_FILES` y utilizaremos `xarray.concat` para generar un único arreglo de rásters tridimensional (es decir, tres rásters de $3,600\times3,600$ apilados verticalmente).  Aprenderemos las interpretaciones específicas asociadas con el conjunto de datos ráster en un cuaderno computacional posterior. Por el momento, los trataremos como datos sin procesar con los que experimentaremos.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack = []
for path in RASTER_FILES:
    data = rio.open_rasterio(path).rename(dict(x='longitude', y='latitude'))
    band_name = path.stem.split('_')[-1]
    data.coords.update({'band': [band_name]})
    data.attrs = dict(description=f"OPERA DIST product", units=None)
    stack.append(data)

stack = xr.concat(stack, dim='band')
stack = stack.where(stack!=0)
```

<!-- #region jupyter={"source_hidden": false} -->

Renombramos los ejes `longitude` y `latitude` y filtramos los píxeles con valor cero para simplificar la visualización posterior.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack
```

<!-- #region jupyter={"source_hidden": false} -->

Una vez que el `stack` de `DataArray` esté construido, podemos enfocarnos en la visualización.

Si queremos generar un gráfico estático con varias imágenes, podemos utilizar `hvplot.image` junto con el método `.layout`. Para ver cómo funciona, empecemos por redefinir los diccionarios `image_opts` y `layout_opts`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(  x='longitude', 
                    y='latitude',
                    rasterize=True, 
                    dynamic=True,
                    cmap='hot_r',
                    crs=stack.rio.crs,
                    alpha=0.8,
                    project=True, 
                    aspect='equal',
                    shared_axes=False,
                    colorbar=True,
                    tiles='ESRI',
                    padding=0.1)
layout_opts = dict(xlabel='Longitude', ylabel="Latitude")
```

<!-- #region jupyter={"source_hidden": false} -->

Para acelerar el renderizado, construiremos inicialmente un objeto `view` que seleccione subconjuntos de píxeles. Definimos inicialmente el parámetro `steps=200` para restringir la vista a cada 200 píxeles en cualquier dirección. Si reducimos los `steps`, se tarda más en renderizar. Establecer `steps=1` o `steps=None` equivale a seleccionar todos los píxeles.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 200
subset = slice(0, None, steps)
layout_opts.update(frame_width=250, frame_height=250)


view = stack.isel(latitude=subset, longitude=subset)
view.hvplot.image(**image_opts).opts(**layout_opts).layout()
```

<!-- #region jupyter={"source_hidden": false} -->

El método `layout` traza de manera predeterminada cada uno de los tres rásteres seleccionados a lo largo del eje `band` horizontalmente.

<!-- #endregion -->

***

## Construcción de una vista dinámica a partir de un arreglo 3D

<!-- #region jupyter={"source_hidden": false} -->

Otra forma de visualizar un arreglo tridimensional es asociar un _widget_ de selección a uno de los ejes. Si llamamos a `hvplot.image` sin agregar el método `.layout` el resultado es un _mapa dinámico_. En este caso, el _widget_ de selección nos permite elegir cortes a lo largo del eje `band`.

Una vez más, aumentar el valor del parámetro `steps` reduce el tiempo de renderizado. Reducirlo a `1` o a `None` renderiza a resolución completa.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 200
subset = slice(0, None, steps)
layout_opts.update(frame_height=400, frame_width=400)

view = stack.isel(latitude=subset, longitude=subset)
view.hvplot.image(**image_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Más adelante apilaremos muchos rásters con distintas marcas temporales a lo largo de un eje `time`. Cuando haya muchos cortes, el _widget_ de selección se renderizará como un deslizador en vez de como un menú desplegable. Podemos controlar la ubicación del _widget_ utilizando una opción de palabra clave `widget_location`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
view.hvplot.image(widget_location='bottom_left', **image_opts, **layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Observa que agregar la opción `widget_location` modifica ligeramente la secuencia en la que se especifican las opciones. Es decir, si seteamos:

```python
view.hvplot.image(widget_location='top_left', **image_opts).opts(**layout_opts)
```

se genera una excepción (de ahí la invocación en la celda de código anterior). Hay algunas dificultades sutiles en la elaboración de la secuencia correcta para aplicar opciones al personalizar objetos HoloViz/Hvplot (principalmente debido a las formas en que los espacios de los nombres se superponen con Bokeh u otros _backends_ de renderizado). La mejor estrategia es empezar con el menor número de opciones posible y experimentar añadiendo opciones de forma incremental hasta que obtengamos la visualización final que deseamos.

<!-- #endregion -->

***

### Combinación de datos vectoriales con datos ráster en una vista dinámica.

<!-- #region jupyter={"source_hidden": false} -->

Por último, vamos a superponer nuestros datos vectoriales anteriores, los límites del incendio forestal, con la vista dinámica de este arreglo tridimensional de rásteres. Podemos utilizar el operador `*` para combinar la salida de `hvplot.image` con `shapeplot`, la vista renderizada de los datos vectoriales.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 200
subset = slice(0, None, steps)
view = stack.isel(latitude=subset, longitude=subset)

image_opts.update(colorbar=False)
layout_opts.update(frame_height=500, frame_width=500)
(view.hvplot.image(**image_opts) * shapeplot).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->

Una vez más, la correcta especificación de las opciones puede requerir un poco de experimentación. Las ideas importantes que se deben tomar en cuenta aquí son:

- cómo cargar conjuntos de datos con `geopandas` and `rioxarray`, y
- cómo utilizar `hvplot` de forma interactiva e incremental para generar visualizaciones atractivas.

<!-- #endregion -->

***

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

# Manipulación de arreglos con [Xarray](https://docs.xarray.dev/en/stable/index.html)

<!-- #region jupyter={"source_hidden": false} -->

Hay numerosas formas de trabajar con datos geoespaciales, así que elegir una herramienta puede ser difícil. La principal librería que utilizaremos es [_Xarray_](https://docs.xarray.dev/en/stable/index.html) por sus estructuras de datos `DataArray` y `Dataset`, y sus utilidades asociadas, así como [NumPy](https://numpy.org) y [Pandas](https://pandas.pydata.org) para manipular arreglos numéricos homogéneos y datos tabulares, respectivamente.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
from warnings import filterwarnings
filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio

FILE_STEM = Path.cwd().parent if 'book' == Path.cwd().parent.stem else 'book'
```

***

<!-- #region jupyter={"source_hidden": false} -->

<center><img src="https://docs.xarray.dev/en/stable/_static/Xarray_Logo_RGB_Final.svg" width=360px></center>

La principal estructura de datos de Xarray es [`DataArray`](https://docs.xarray.dev/en/stable/user-guide/data-structures.html), que ofrece soporte para arreglos multidimensionales etiquetados. El [Projecto Pythia](https://foundations.projectpythia.org/core/xarray.html) proporciona una amplia introducción a este paquete. Nos enfocaremos principalmente en las partes específicas del API Xarray que utilizaremos para nuestros análisis geoespaciales particulares.

Vamos a cargar una estructura de datos `xarray.DataArray` de ejemplo desde un archivo cuya ubicación viene determinada por `LOCAL_PATH`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
LOCAL_PATH = Path(FILE_STEM, 'assets/OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif')
data = rio.open_rasterio(LOCAL_PATH)
```

***

## Análisis de la `repr` enriquecida de `DataArray`

<!-- #region jupyter={"source_hidden": false} -->

Cuando se utiliza un Jupyter Notebook, los datos Xarray `DataArray` `data` se pueden analizar de forma interactiva.

- La celda de salida contiene un Jupyter Notebook `repr` enriquecido para la clase `DataArray`.
- Los triángulos situados junto a los encabezados "Coordinates", "Indexes" y "Attributes" pueden pulsarse con el mouse para mostrar una vista ampliada.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(f'{type(data)=}\n')
data
```

***

## Análisis de los atributos de `DataArray` mediante programación

<!-- #region jupyter={"source_hidden": false} -->

Por supuesto, aunque esta vista gráfica es práctica, también es posible acceder a varios atributos de `DataArray` mediante programación. Esto nos permite escribir una lógica programatica para manipular los `DataArray` condicionalmente según sea necesario. Por ejemplo:

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(data.coords)
```

<!-- #region jupyter={"source_hidden": false} -->

Las dimensiones `data.dims` son las cadenas de caracteres/etiquetas asociadas a los ejes del `DataArray`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data.dims
```

<!-- #region jupyter={"source_hidden": false} -->

Podemos extraer las coordenadas como arreglos NumPy unidimensionales (homogéneas) utilizando los atributos `coords` y `.values`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(data.coords['x'].values)
```

<!-- #region jupyter={"source_hidden": false} -->

`data.attrs` es un diccionario que contiene otros metadatos analizados a partir de las etiquetas GeoTIFF (los "Atributos" en la vista gráfica). Una vez más, esta es la razón por la que `rioxarray` es útil. Es posible escribir código que cargue datos de varios formatos de archivo en Xarray `DataArray`, pero este paquete encapsula mucho del código desordenado que, por ejemplo, rellenaría `data.attrs`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data.attrs
```

***

## Uso del método de acceso `rio` de `DataArray`

<!-- #region jupyter={"source_hidden": false} -->

Tal como se mencionó, `rioxarray` extiende la clase `xarray.DataArray` con un método de acceso llamado `rio`. El método de acceso `rio` agrega efectivamente un espacio de nombres con una variedad de atributos. Podemos usar una lista de comprensión de Python para mostrar los que no empiezan con guión bajo (los llamados métodos/atributos "private" y "dunder").

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
[name for name in dir(data.rio) if not name.startswith('_')]
```

<!-- #region jupyter={"source_hidden": false} -->

El atributo `data.rio.crs` es importante para nuestros propósitos. Proporciona acceso al sistema de referencia de coordenadas asociado a este conjunto de datos ráster.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(type(data.rio.crs))
print(data.rio.crs)
```

<!-- #region jupyter={"source_hidden": false} -->

El atributo `.rio.crs` es una estructura de datos de la clase `CRS` del proyecto [pyproj](https://pyproj4.github.io/pyproj/stable/index.html). La `repr` de Python para esta clase devuelve una cadena como `EPSG:32610`. Este número se refiere al [conjunto de datos de parámetros geodésicos EPGS](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset).

De [Wikipedia](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset):

> El [conjunto de datos de parámetros geodésicos EPGS](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset) es un registro público de [datums geodésicos](https://es.wikipedia.org/wiki/Sistema_de_referencia_geod%C3%A9sico), [sistemas de referencia espacial](https://es.wikipedia.org/wiki/Sistema_de_referencia_espacial), [elipsoides terrestres](https://es.wikipedia.org/wiki/Elipsoide_de_referencia), transformaciones de coordenadas y [unidades de medida](https://es.wikipedia.org/wiki/Unidad_de_medida) relacionadas, originados por un miembro del [EPGS](https://en.wikipedia.org/wiki/European_Petroleum_Survey_Group) en 1985. A cada entidad se le asigna un código EPSG comprendido entre 1024 y 32767, junto con una representación estándar de [texto conocido (WKT)](https://en.wikipedia.org/wiki/Well-known_text_representation_of_coordinate_reference_systems) legible por máquina. El mantenimiento del conjunto de datos corre a cargo del Comité de Geomática [IOGP](https://en.wikipedia.org/wiki/International_Association_of_Oil_%26_Gas_Producers).

<!-- #endregion -->

***

## Manipulación de los datos en un `DataArray`

<!-- #region jupyter={"source_hidden": false} -->

Estos datos se almacenan utilizando un CRS [UTM](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system) particular. Las etiquetas de las coordenadas serían convencionalmente _este_ y _norte_. Sin embargo, a la hora de hacer el trazo, será conveniente utilizar _longitud_ y _latitud_ en su lugar. Reetiquetaremos las coordenadas para reflejar esto, es decir, la coordenada llamada `x` se reetiquetará como `longitude` y la coordenada llamada `y` se reetiquetará como `latitude`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data = data.rename({'x':'longitude', 'y':'latitude'})
```

```{code-cell} python jupyter={"source_hidden": false}
print(data.coords)
```

<!-- #region jupyter={"source_hidden": false} -->

Una vez más, aunque los valores numéricos almacenados en los arreglos de coordenadas no tienen sentido estrictamente como valores (longitud, latitud), aplicaremos estas etiquetas ahora para simplificar el trazado más adelante.

Los objetos Xarray `DataArray` permiten extraer subconjuntos de forma muy similar a las listas de Python. Las  siguientes celdas extraen el mismo subarreglo mediante dos llamadas a métodos diferentes.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data.isel(longitude=slice(0,2))
```

```{code-cell} python jupyter={"source_hidden": false}
data.sel(longitude=[499_995, 500_025])
```

<!-- #region jupyter={"source_hidden": false} -->

En vez de utilizar paréntesis para cortar secciones de arreglos (como en NumPy), para `DataArray`, podemos utilizar los métodos `sel` o `isel` para seleccionar subconjuntos por valores de coordenadas continuas o por posiciones enteras (es decir, coordenadas de "píxel") respectivamente. Esto es similar al uso de `.loc` and `.iloc` en Pandas para extraer entradas de una Pandas `Series` o `DataFrame`.

Si tomamos un subconjunto en 2D de los `DataArray` `data` 3D, podemos graficarlo usando el método de acceso `.plot` (hablaremos al respecto más adelante).

<!-- #endregion -->

```python jupyter={"source_hidden": false}
data.isel(band=0).plot();
```

<!-- #region jupyter={"source_hidden": false} -->

Este gráfico tarda un poco en procesarse porque el arreglo representado tiene $3,600\times3,600$ píxeles. Podemos utilizar la función `slice` de Python para extraer, por ejemplo, cada 100 píxeles en cualquier dirección para trazar una imagen de menor resolución mucho más rápido.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 100
subset = slice(0,None,steps)
view = data.isel(longitude=subset, latitude=subset, band=0)
view.plot();
```

<!-- #region jupyter={"source_hidden": false} -->

El gráfico producido es bastante oscuro (lo que refleja que la mayoría de las entradas son cero según la leyenda). Observa que los ejes se etiquetan automáticamente utilizando las `coords` que renombramos antes.

<!-- #endregion -->

***

## Extracción de datos `DataArray` a NumPy, Pandas

<!-- #region jupyter={"source_hidden": false} -->

Observa que un `DataArray` encapsula de un arreglo NumPy. Ese arreglo NumPy se puede recuperar usando el atributo `.values`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
array = data.values
print(f'{type(array)=}')
print(f'{array.shape=}')
print(f'{array.dtype=}')
print(f'{array.nbytes=}')
```

<!-- #region jupyter={"source_hidden": false} -->

Estos datos ráster se almacenan como datos enteros sin signo de 8 bits, es decir, un byte por cada píxel. Un entero de 8 bits sin signo puede representar valores enteros entre 0 y 255. En un arreglo con algo más de trece millones de elementos, eso significa que hay muchos valores repetidos. Podemos verlo poniendo los valores de los píxeles en una Pandas `Series` y usando el método `.value_counts`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
s_flat = pd.Series(array.flatten()).value_counts()
s_flat.sort_index()
```

<!-- #region jupyter={"source_hidden": false} -->

La mayoría de las entradas de este arreglo ráster son cero. Los valores numéricos varían entre 0 y 100 con la excepción de unos 1,700 píxeles con el valor 255. Esto tendrá más sentido cuando hablemos de la especificación del producto de datos DIST.

<!-- #endregion -->

***

## Apilamiento y concatenación de una secuencia de `DataArrays`

<!-- #region jupyter={"source_hidden": false} -->

A menudo es conveniente apilar múltiples arreglos bidimensionales de datos ráster en un único arreglo tridimensional. En NumPy, esto se hace típicamente con la función [`numpy.concatenate`](https://numpy.org/doc/stable/reference/generated/numpy.concatenate.html). Hay una funcionalidad similar en Xarray—[`xarray.concat`](https://docs.xarray.dev/en/stable/generated/xarray.concat.html) (que es similar en diseño a la función [`pandas.concat`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html)). La principal diferencia entre `numpy.concatenate` y `xarray.concat` es que esta última función debe tener en cuenta las _coordenadas etiquetadas_, mientras que la primera no. Esto es importante cuando, por ejemplo, los ejes de coordenadas de dos rásters se superponen pero no están perfectamente alineados.

Para ver cómo funciona el apilamiento de rásteres, empezaremos haciendo una lista de tres archivos GeoTIFF (almacenados localmente), inicializando una lista de `stack` vacía, y después construyendo una lista de `DataArrays` en un bucle.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
RASTER_FILES = list((Path(FILE_STEM, 'assets').glob('OPERA*VEG*.tif')))

stack = []
for path in RASTER_FILES:
    print(f"Stacking {path.name}..")
    data = rio.open_rasterio(path).rename(dict(x='longitude', y='latitude'))
    band_name = path.stem.split('_')[-1]
    data.coords.update({'band': [band_name]})
    data.attrs = dict(description=f"OPERA DIST product", units=None)
    stack.append(data)
```

<!-- #region jupyter={"source_hidden": false} -->

He aquí algunas observaciones importantes sobre el bucle de código anterior:

- El uso de `rioxarray.open_rasterio` para cargar un Xarray `DataArray` en memoria hace mucho trabajo por nosotros. En particular, se asegura de que las coordenadas continuas están alineadas con las coordenadas de píxeles subyacentes.
- De manera predeterminada, `data.coords` tiene las claves `x` y `y` que elegimos reetiquetar como `longitude` y `latitude` respectivamente. Técnicamente, los valores de las coordenadas continuas que se cargaron desde este archivo GeoTIFF en particular se expresan en coordenadas UTM (es decir, este y norte), pero, posteriormente, al trazar, las etiquetas `longitude` y `latitude` serán más convenientes.
- `data.coords['band']`, tal como se cargó desde el archivo, tiene el valor `1`. Elegimos sobrescribir ese valor con el nombre de la banda (que extraemos del nombre del archivo como `band_name`).
- De manera predeterminada, `rioxarray.open_rasterio` completa `data.attrs` con pares clave-valor extraídos de las etiquetas TIFF. Para diferentes bandas/capas, estos diccionarios de atributos podrían tener claves o valores conflictivos. Puede ser aconsejable conservar estos metadatos en algunas circunstancias. Simplemente elegimos descartarlos en este contexto para evitar posibles conflictos. El diccionario mínimo de atributos de la estructura de datos final tendrá como únicas claves `description` y `units`.

Dado que construimos una lista de `DataArray` en la lista `stack`, podemos ensamblar un `DataArray` tridimensional utilizando `xarray.concat`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack = xr.concat(stack, dim='band')
```

<!-- #region jupyter={"source_hidden": false} -->

La función `xarray.concat` acepta una secuencia de objetos `xarray.DataArray` con dimensiones conformes y los _concatena_ a lo largo de una dimensión especificada. Para este ejemplo, apilamos rásteres bidimensionales que corresponden a diferentes bandas o capas. Por eso utilizamos la opción `dim='band'` en la llamada a `xarray.concat`. Más adelante, en cambio, apilaremos rásteres bidimensionales a lo largo de un eje _temporal_ (esto implica un código ligeramente diferente para garantizar el etiquetado y la alineación correctos).

Examinemos `stack` mediante su `repr`en este Jupyter Notebook.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack
```

<!-- #region jupyter={"source_hidden": false} -->

Observa que `stack` tiene un CRS asociado que fue analizado por `rioxarray.open_rasterio`.

<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack.rio.crs
```

<!-- #region jupyter={"source_hidden": false} -->

Este proceso es muy útil para el análisis (suponiendo que haya suficiente memoria disponible para almacenar toda la colección de rásteres). Más adelante, utilizaremos este enfoque varias veces para manipular colecciones de rásteres de dimensiones conformes. El apilamiento se puede utilizar para producir una visualización dinámica con un control deslizante o, alternativamente, para producir un gráfico estático.

<!-- #endregion -->

***

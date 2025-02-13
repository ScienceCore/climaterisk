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

# Utilización del producto OPERA DSWx

<!-- #region editable=true slideshow={"slide_type": ""} -->

<center>
    <img src="https://d2pn8kiwq2w21t.cloudfront.net/original_images/Opera-Hero-Overview-Infographic-v6.jpg" width="50%">
</center>

Del proyecto [OPERA](https://www.jpl.nasa.gov/go/opera):

> Iniciado en abril del 2021, el proyecto OPERA del JPL recopila datos de instrumentos satelitales ópticos y de radar para generar seis conjuntos de productos:
>
> - un conjunto de productos sobre la extensión del agua de la superficie terrestre a escala casi mundial
> - un conjunto de productos de Alteraciones de la Superficie terrestre a escala casi mundial
> - un producto con corrección radiométrica del terreno a escala casi mundial
> - un conjunto de productos _Coregistered Single Look Complex_ para Norteamérica
> - un conjunto de productos de desplazamiento para Norteamérica
> - un conjunto de productos de movimiento vertical del terreno en Norteamérica

Es decir, OPERA es una iniciativa de la NASA que toma, por ejemplo, datos de teledetección óptica o radar recopilados desde satélites, y genera una variedad de conjuntos de datos preprocesados para uso público. Los productos de OPERA no son imágenes de satélite sin procesar, sino el resultado de una clasificación algorítmica para determinar, por ejemplo, qué regiones terrestres contienen agua o dónde se ha desplazado la vegetación. Las imágenes de satélite sin procesar se recopilan a partir de mediciones realizadas por los instrumentos a bordo de las misiones de los satélites Sentinel-1 A/B, Sentinel-2 A/B y Landsat-8/9.

<!-- #endregion -->

---

## El producto OPERA DSWx

<!-- #region editable=true slideshow={"slide_type": ""} -->

Ya vimos la familia DIST (es decir, alteración de la superficie terrestre) con productos de datos OPERA. En este cuaderno computacional, analizaremos otro producto de datos OPERA: el producto _Dynamic Surface Water Extent (DSWx)_ (en español, Extensión de Aguas Superficiales Dinámicas). Este producto de datos resume la extensión de las aguas continentales (es decir, el agua en las masas de tierra en contraposición a la parte de un océano) que se puede utilizar para hacer un seguimiento de las inundaciones y las sequías. El producto DSWx se describe detalladamente en la [especificación del producto OPERA DSWx HLS](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf).

Los productos de datos DSWx se generan a partir de las mediciones de reflectancia de superficie del HLS, específicamente, estas son efectuadas por elinstrumento OLI a bordo del satélite Landsat 8, el OLI-2 a bordo del satélite Landsat 9, y el MSI a bordo de los satélites Sentinel-2A/B. Al igual que los productos DIST, los productos DSWx consisten en datos ráster almacenados en formato GeoTIFF que utilizan el [MGRS](https://en.wikipedia.org/wiki/Military_Grid_Reference_System)  (los detalles se describen en la especificación del [producto DSWx](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf). De nuevo, los productos OPERA DSWx se distribuyen como [GeoTIFF optimizados para la nube](https://www.cogeo.org/) que almacenan diferentes bandas/capas en archivos TIFF distintos.

<!-- #endregion -->

---

<!-- #region editable=true slideshow={"slide_type": ""} -->

## Banda 1: Clasificación del agua (WTR)

<!-- #endregion -->

Hay diez bandas o capas asociadas al producto de datos DSWx. En este tutorial, nos enfocaremos estrictamente en la primera banda&mdash;la capa de _clasificación del agua_ (WTR, por las abreviación en inglés de la palabra _Water_)\*&mdash;pero los detalles de todas las bandas se dan en la [especificación del producto DSWx](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf). Por ejemplo, la banda 3 es la _Capa de Confianza (CONF)_ que proporciona, para cada píxel, valores cuantitativos que describen el grado de confianza en las categorías dadas en la banda 1 (la Capa de clasificación del agua). La banda 4 es una capa de _Diagnóstico (DIAG)_ que codifica, para cada píxel, cuál de las cinco pruebas resultó positiva para obtener el valor del píxel correspondiente en la capa CONF.

La capa de clasificación del agua consiste en datos ráster enteros de 8 bits sin signo (UInt8) que representan si un píxel contiene aguas continentales (por ejemplo, parte de un embalse, un lago, un río, etc., pero no agua asociada con el mar abierto). Los valores de esta capa ráster se calculan a partir de las imágenes crudas adquiridas por el satélite, asignando a los píxeles uno de los 7 valores enteros positivos que analizaremos a continuación.

---

### Ejemplo de análisis de una capa WTR

Comencemos importando las librerías necesarias y cargando un archivo adecuado en un Xarray `DataArray`. El archivo en cuestión contiene datos ráster relativos al [embalse del lago Powelr](https://es.wikipedia.org/wiki/Lago_Powell), en el río Colorado, en los Estados Unidos.

```{code-cell} python
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
```

```{code-cell} python
import hvplot.pandas, hvplot.xarray
import geoviews as gv
gv.extension('bokeh')
from bokeh.models import FixedTicker
```

```{code-cell} python
FILE_STEM = Path.cwd().parent if 'book' == Path.cwd().parent.stem else 'book'
LOCAL_PATH = Path(FILE_STEM, 'assets/OPERA_L3_DSWx-HLS_T12SVG_20230411T180222Z_20230414T030945Z_L8_30_v1.0_B01_WTR.tif')
b01_wtr = rio.open_rasterio(LOCAL_PATH).rename({'x':'longitude', 'y':'latitude'}).squeeze()
```

Recuerda que usar el `repr` para `b01_wtr` en este Jupyter Notebook es bastante conveniente.

- Al desplegar la pestaña `Attributes`, podemos ver todos los metadatos asociados a los datos adquiridos.
- Al desplegar la pestaña `Coordinates`, podemos analizar todos los arreglos asociados a esos valores de coordenadas.

```{code-cell} python
# Examine data
b01_wtr
```

Vamos a examinar la distribución de los valores del píxel en `b01_wtr` utilizando el método Pandas `Series.value_counts`.

```{code-cell} python
counts = pd.Series(b01_wtr.values.flatten()).value_counts().sort_index()
display(counts)
```

Estos valores de píxel son _datos categóricos_. En específico, los valores de píxel válidos y sus significados&mdash;según la [especificación del producto DSWx](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf) &mdash;son los siguientes:

- **0**: Sin agua&mdash;cualquier área con datos de reflectancia válidos que no sea de una de las otras categorías permitidas (agua abierta, agua superficial parcial, nieve/hielo, nube/sombra de nube, o océano enmascarado).
- **1**: Agua abierta&mdash;cualquier píxel que sea completamente agua sin obstrucciones para el sensor, incluyendo obstrucciones por vegetación, terreno y edificios.
- **2**: Agua parcialmente superficial&mdash;un área que es por lo menos 50% y menos de 100% agua abierta (por ejemplo, sumideros inundados, vegetación flotante, y píxeles bisecados por líneas costeras).
- **252**: Nieve/Hielo.
- **253**: Nube o sombra de nube&mdash;un área oscurecida por, o adyacente a, una nube o sombra de nube.
- **254**: Océano enmascarado&mdash;un área identificada como océano utilizando una base de datos de la línea costera con un margen añadido.
- **255**: Valor de relleno (datos faltantes).

---

### Realización de una primera visualización

Hagamos un primer gráfico aproximado de los datos ráster utilizando `hvplot.image`. Como de costumbre, instanciamos un objeto `view` que corta un subconjunto más pequeño de píxeles para hacer que la imagen se renderice rápidamente.

```{code-cell} python
image_opts = dict(
                    x='longitude',
                    y='latitude',                   
                    rasterize=True, 
                    dynamic=True,
                    project=True
                 )
layout_opts = dict(
                    xlabel='Longitude',
                    ylabel='Latitude',
                    aspect='equal',
                  )

steps = 100
subset = slice(0, None, steps)
view = b01_wtr.isel(longitude=subset, latitude=subset)
view.hvplot.image(**image_opts).opts(**layout_opts)
```

El mapa de colores predeterminado no revela muy bien las características ráster. Además, observa que el eje de la barra de colores cubre el rango numérico de 0 a 255 (aproximadamente), aunque la mayoría de esos valores de los píxeles (es decir, de `3` a `251`) no aparecen realmente en los datos. Anotar una imagen ráster de datos categóricos con una leyenda puede tener más sentido que utilizar una barra de colores. Sin embargo, actualmente, `hvplot.image` no soporta el uso de una leyenda. Por lo tanto, para este tutorial, nos limitaremos a utilizar una barra de colores. Antes de asignar un mapa de colores y etiquetas apropiadas para la barra de colores, tiene sentido limpiar los valores de los píxeles.

---

### Reasignación de los valores de los píxeles

Queremos reasignar los valores ráster de los píxeles a un rango más estrecho (por ejemplo, de `0` a `5` en vez de `0` a `255`) para crear una barra de color sensible. Para ello, empezaremos copiando los valores del `DataArray` `b01_wtr` en otro llamado `new_data`, y creando un arreglo llamado `values` para contener el rango completo de valores de píxel permitidos.

```{code-cell} python
new_data = b01_wtr.copy(deep=True)
values = np.array([0, 1, 2, 252, 253, 254, 255], dtype=np.uint8)
print(values)
```

Primero debemos decidir cómo tratar los datos que faltan, es decir, los píxeles con el valor `255` en este ráster. Vamos a elegir tratar los píxeles de datos que faltan igual que los píxeles `"Sin agua"`. Podemos utilizar el método `DataArray.where` para reasignar los píxeles con valor `null_val` (por ejemplo, 255 en la celda de código siguiente) al valor de reemplazo `transparent_val` (por ejemplo, `0` en este caso). Anticipando que incluiremos este código en una función más adelante, incluimos el cálculo en un bloque `if` condicionado a un valor booleano `replace_null`.

```{code-cell} python
null_val = 255
transparent_val = 0
replace_null = True
if replace_null:
    new_data = new_data.where(new_data!=null_val, other=transparent_val)
    values = values[np.where(values!=null_val)]

print(np.unique(new_data.values))
```

Observa que `values` ya no incluye `null_val`. A continuación, instanciamos un arreglo `new_values` para almacenar los valores de píxel de reemplazo.

```{code-cell} python
n_values = len(values)
start_val = 0
new_values = np.arange(start=start_val, stop=start_val+n_values, dtype=values.dtype)
assert transparent_val in new_values, f"{transparent_val=} not in {new_values}"
print(values)
print(new_values)
```

Ahora combinamos `values` y `new_values` en un diccionario `relabel`, y usamos el diccionario para modificar las entradas de `new_data`.

```{code-cell} python
relabel = dict(zip(values, new_values))
for old, new in relabel.items():
    if new==old: continue
    new_data = new_data.where(new_data!=old, other=new)
```

Podemos encapsular la lógica de las celdas anteriores en una función de utilidad `relabel_pixels` que condensa un amplio rango de valores categóricos de píxeles en uno más ajustado que se mostrará mejor con un mapa de colores.

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

Apliquemos la función que acabamos de definir a `b01_wtr` y comprobemos que los valores de los píxeles cambiaron como queríamos.

```{code-cell} python
values = [0, 1, 2, 252, 253, 254, 255]
print(f"Before applying relabel_pixels: {np.unique(b01_wtr.values)}")
print(f"Original pixel values expected: {values}")
b01_wtr, relabel = relabel_pixels(b01_wtr, values=values)
print(f"After applying relabel_pixels: {np.unique(b01_wtr.values)}")
```

Observe que el valor de píxel `5` no aparece en el arreglo reetiquetada porque el valor de píxel `254` (para los píxeles de "Océano enmascarado") no aparece en el archivo GeoTIFF original. Esto está bien. El código escrito a continuación seguirá produciendo toda la variedad de posibles valores para los píxeles (y colores) en su barra de colores.

---

### Definición de un mapa de color y trazado con una barra de color

Ahora estamos listos para definir un mapa de colores. Definimos el diccionario `COLORS` de forma que las etiquetas de píxel de `new_values` sean las claves del diccionario y algunas tuplas de color _Red Green Blue Alpha_ (RGBA) (en español, rojo verde azul alfa) utilizadas frecuentemente para este tipo de datos sean los valores del diccionario. Utilizaremos variantes del código de la siguiente celda para actualizar `layout_opts` de forma que los gráficos generados para varias capas/bandas de los productos de datos DSWx tengan leyendas adecuadas.

```{code-cell} python
COLORS = {
0: (255, 255, 255, 0.0),  # No Water
1:  (0,   0, 255, 1.0),   # Open Water
2:  (180, 213, 244, 1.0), # Partial Surface Water
3: (  0, 255, 255, 1.0),  # Snow/Ice
4: (175, 175, 175, 1.0),  # Cloud/Cloud Shadow
5: ( 0,   0, 127, 0.5),   # Ocean Masked
}

c_labels = ["No Water", "Open Water", "Partial Surface Water", "Snow/Ice", "Cloud/Cloud Shadow", "Ocean Masked"]
c_ticks = list(COLORS.keys())
limits = (c_ticks[0]-0.5, c_ticks[-1]+0.5)

print(c_ticks)
print(c_labels)
```

Para utilizar este mapa de colores, estas marcas y estas etiquetas en una barra de colores, creamos un diccionario `c_bar_opts` que contiene los objetos que hay que pasar al motor de renderizado Bokeh.

```{code-cell} python editable=true slideshow={"slide_type": ""}
c_bar_opts = dict( ticker=FixedTicker(ticks=c_ticks),
                   major_label_overrides=dict(zip(c_ticks, c_labels)),
                   major_tick_line_width=0, )
```

Debemos actualizar los diccionarios `image_opts` y `layout_opts` para incluir los datos relevantes para el mapa de colores.

```{code-cell} python editable=true slideshow={"slide_type": ""}
image_opts.update({ 'cmap': list(COLORS.values()),
                    'clim': limits,
                    'colorbar': True
                  })

layout_opts.update(dict(title='B01_WTR', colorbar_opts=c_bar_opts))
```

Finalmente, podemos renderizar un gráfico rápido para asegurarnos de que la barra de colores se produce con etiquetas adecuadas.

```{code-cell} python
steps = 100
subset = slice(0, None, steps)
view = b01_wtr.isel(longitude=subset, latitude=subset)
view.hvplot.image( **image_opts).opts(frame_width=500, frame_height=500, **layout_opts)
```

Por último, podemos definir un mapa base, esta vez utilizando mosaicos de [ESRI](https://www.esri.com). Esta vez, graficaremos el ráster a resolución completa (es decir, no nos molestaremos en utilizar `isel` para seleccionar primero un corte de menor resolución del ráster).

```{code-cell} python editable=true slideshow={"slide_type": ""}
# Creates basemap
base = gv.tile_sources.EsriTerrain.opts(padding=0.1, alpha=0.25)
b01_wtr.hvplot(**image_opts).opts(**layout_opts) * base
```

<!-- #region editable=true slideshow={"slide_type": ""} -->

Este cuaderno computacional proporciona una visión general de cómo visualizar datos extraídos de productos de datos OPERA DSWx almacenados localmente. Ahora estamos listos para automatizar la búsqueda de dichos productos en la nube utilizando la API PySTAC.

----

<!-- #endregion -->

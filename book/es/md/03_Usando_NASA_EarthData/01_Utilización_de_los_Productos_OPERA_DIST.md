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

# Utilización de los productos OPERA DIST

## El proyecto OPERA

<!-- #region jupyter={"source_hidden": true} -->
<center>
    <img src="https://d2pn8kiwq2w21t.cloudfront.net/original_images/Opera-Hero-Overview-Infographic-v6.jpg" width="50%">
</center>

Del proyecto [Observational Products for End-Users from Remote Sensing Analysis (OPERA)](https://www.jpl.nasa.gov/go/opera) (en español, Productos de Observación para Usuarios Finales a partir del Analisis por Teledetección):

> Iniciado en abril del 2021, el proyecto OPERA del _Jet Propulsion Laboratory_ (JPL) (en español, Laboratorio de Propulsión a Chorro) recopila datos satelitales ópticos y de radar para generar seis conjuntos de productos:
>
> - un conjunto de productos sobre la extensión de las aguas de la superficie terrestre a escala casi mundial
> - un conjunto de productos de Alteraciones de la Superficie terrestre a escala casi mundial
> - un producto con Corrección Radiométrica del Terreno a escala casi mundial
> - un conjunto de productos _Coregistered Single Look Complex_ para Norteamérica
> - un conjunto de productos de Desplazamiento para Norteamérica
> - un conjunto de productos de Movimiento Vertical del Terreno en Norteamérica

Es decir, OPERA es una iniciativa de la National Aeronautics and Space Administration (NASA, en español, Administración Nacional de Aeronáutica y del Espacio) que toma, por ejemplo, datos de teledetección óptica o radar recopilados desde satélites, y genera una variedad de conjuntos de datos preprocesados para uso público. Los productos de OPERA no son imágenes de satélite sin procesar, sino el resultado de una clasificación algorítmica para determinar, por ejemplo, qué regiones terrestres contienen agua o dónde se ha modificado la vegetación. Las imágenes de satélite sin procesar se recopilan a partir de mediciones realizadas por los instrumentos a bordo de las misiones de los satélites Sentinel-1 A/B, Sentinel-2 A/B y Landsat-8/9 (de ahí el término _Harmonized Landsat-Sentinel_" (HLS) (en español, Landsat-Sentinel Armonizadas) para en numerosas descripciones de productos).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## El producto OPERA _Land Surface Disturbance_ (DIST) (en español, Perturbación de la superficie terrestre)

<!-- #region jupyter={"source_hidden": true} -->
Uno de estos productos de datos de OPERA es el producto DIST (descrito con más detalle en la especificación del producto [OPERA DIST HLS](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DIST_HLS_Product_Specification_V1.pdf)).
Los productos DIST mapean la _perturbación de la vegetación_ (en concreto, la pérdida de cubierta vegetal por píxel HLS siempre que haya una disminución indicada) a partir de escenas armonizadas Landsat-8 y Sentinel-2 A/B (HLS). Una de las aplicaciones de estos datos es cuantificar los daños causados por los _incendios forestales_. El producto DIST_ALERT se publica a intervalos regulares (al igual que las imágenes HLS, aproximadamente cada 12 días en un determinado mosaico/región). El producto DIST_ANN resume las mediciones de las alteraciones a lo largo de un año.

Los productos DIST cuantifican los datos de reflectancia de la superficie (RS) (en inglés, Surface Reflectance, SR) adquiridos a partir de imágenes terrestres operacionales _Operational Land Imager_ (OLI) (en español, Generador de Imágenes Terrestres Operacional) a bordo del satélite de teledetección Landsat-8 y del _Multi-Spectral Instrument_ (MSI) (en español, Instrumento Multiespectral) a bordo del satélite de teledetección Sentinel-2 A/B. Los productos de datos HLS DIST son archivos de tipo ráster, cada uno de ellos asociado a mosaicos de la superficie terrestre. Cada mosaico se representa mediante coordenadas cartográficas proyectadas alineadas con el [Sistema de Referencia de Cuadrículas Militares (MGRS, por sus siglas en inglés de _Military Grid Reference System_)](https://en.wikipedia.org/wiki/Military_Grid_Reference_System). Cada mosaico se divide en 3,660 filas y 3,660 columnas con un espaciado de píxeles de 30 metros (así que un mosaico es de $109.8\,\mathrm{km}$ largo en cada lado). Los mosaicos vecinos se solapan 4.900 metros en cada dirección (los detalles se describen detalladamente en la [especificación de producto DIST](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DIST_HLS_Product_Specification_V1.pdf)).

Los productos OPERA DIST se distribuyen como [GeoTIFFs optimizados para la nube](https://www.cogeo.org/); en la práctica, esto significa que las diferentes bandas se almacenan en archivos de formato TIFFs (TIFF, por sus siglas en inglés, _Tagged Image File Format_) distintos. La especificación TIFF permite el almacenamiento de matrices multidimensionales en un único archivo. El almacenamiento de bandas distintas en diferentes archivos TIFF permite que estos se descarguen de forma independiente.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Banda 1: Valor máximo de la anomalía de pérdida de vegetación (VEG_ANOM_MAX)

<!-- #region jupyter={"source_hidden": true} -->
Examina un archivo local con un ejemplo de datos DIST-ALERT. El archivo contiene la primera banda de datos de alteración: la _anomalía de pérdida máxima de vegetación_. Para cada píxel, se trata de un valor entre 0% y 100% que representa la diferencia porcentual entre la cobertura vegetal que se observa actualmente y un valor de referencia histórico. Es decir, un valor de 100 corresponde a una pérdida total de vegetación en un píxel y un valor de 0 corresponde a que no hubo pérdida de vegetación. Los valores de los píxeles se almacenan como enteros sin signo de 8 bits (UInt8) porque los valores de los píxeles solo deben oscilar entre 0 y 100. Un valor del píxel de 255 indica que faltan datos, es decir, que los datos HLS no pudieron determinar un valor máximo de anomalía en la vegetación para ese píxel. Por supuesto, el uso de datos enteros sin signo de 8 bits es mucho más eficiente para el almacenamiento y para la transmisión de datos a través de una red (en comparación con, por ejemplo, datos de punto flotante de 32 o 64 bits).

Empieza importando las librerías necesarias. Observa que también estamos importando la clase `FixedTicker` de la librería Bokeh para hacer que los gráficos interactivos sean un poco más atractivos.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Notebook dependencies
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import rioxarray as rio
import geoviews as gv
gv.extension('bokeh')
import hvplot.xarray
from bokeh.models import FixedTicker

FILE_STEM = Path.cwd().parent.parent.parent if 'book' == Path.cwd().parent.parent.parent.stem else 'book'
```

<!-- #region jupyter={"source_hidden": true} -->
Lee los datos de un archivo local `'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'`. Antes de cargarlo, analiza los metadatos incluídos en el nombre del archivo.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
LOCAL_PATH = FILE_STEM / 'assets' / 'data' / 'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'
filename = LOCAL_PATH.name
print(filename)
```

<!-- #region jupyter={"source_hidden": true} -->
Este nombre de archivo bastante largo incluye varios campos separados por caracteres de guión bajo (`_`). Podemos utilizar el método `str.split` de Python para ver más fácilmente los distintos campos.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
filename.split('_') # Use the Python str.split method to view the distinct fields more easily.
```

<!-- #region jupyter={"source_hidden": true} -->
Los archivos de los productos OPERA tienen un esquema de nombres particular (como se describe en la [especificación de producto DIST](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DIST_HLS_Product_Specification_V1.pdf)). En la salida anterior, puedes extraer ciertos metadatos para este ejemplo:

1. _Product_: `OPERA`;
2. _Level_: `L3` ;
3. _ProductType_: `DIST-ALERT-HLS` ;
4. _TileID_: `T10TEM` (cadena de caracteres que hace referencia a un mosaico del [MGRS](https://en.wikipedia.org/wiki/Military_Grid_Reference_System));
5. _AcquisitionDateTime_: `20220815T185931Z` (cadena que representa una marca de tiempo GMT para la adquisición de los datos);
6. _ProductionDateTime_ : `20220817T153514Z` (cadena que representa una marca de tiempo GMT para cuando se generó el producto de los datos);
7. _Sensor_: `S2A` (identificador del satélite que adquirió los datos sin procesar: `L8` (Landsat-8), `S2A` (Sentinel-2 A) o `S2B` (Sentinel-2 B);
8. _Resolution_: `30` (por ejemplo, píxeles de longitud lateral $30\mathrm{m}$);
9. _ProductVersion_: `v0.1` (versión del producto); y
10. _LayerName_: `VEG-ANOM-MAX`

Ten en cuenta que la NASA utiliza nomenclaturas convencionales como [Earthdata Search](https://search.earthdata.nasa.gov) para extraer datos significativos de los [_SpatioTemporal Asset Catalogs_ (STACs)](https://stacspec.org/) (en español, Catálogos de Activos Espaciales y Temporales). Más adelante se utilizarán estos campo&mdash; en particular _TileID_ y _LayerName_; para filtrar los resultados de la búsqueda antes de recuperar los datos remotos.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
Sube los datos de este archivo local en un `DataArray`, que es un tipo de dato de Xarray, utilizando `rioxarray.open_rasterio`. Reetiqueta las coordenadas adecuadamente y extrae el CRS (sistema de referencia de coordenadas).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data = rio.open_rasterio(LOCAL_PATH)
crs = data.rio.crs
data = data.rename({'x':'longitude', 'y':'latitude', 'band':'band'}).squeeze()
```

```python jupyter={"source_hidden": true}
data
```

```python jupyter={"source_hidden": true}
crs
```

<!-- #region jupyter={"source_hidden": true} -->
Antes de generar un gráfico, crea un mapa base utilizando mosaicos [ESRI](https://es.wikipedia.org/wiki/Esri).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Creates basemap
base = gv.tile_sources.ESRI.opts(width=750, height=750, padding=0.1)
```

<!-- #region jupyter={"source_hidden": true} -->
También utiliza diccionarios para capturar la mayor parte de las opciones de trazado que utilizarás más adelante junto con `.hvplot.image`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts = dict(
                    x='longitude',
                    y='latitude',                   
                    rasterize=True, 
                    dynamic=True,
                    frame_width=500, 
                    frame_height=500,
                    aspect='equal',
                    cmap='hot_r', 
                    clim=(0, 100), 
                    alpha=0.8
                 )
layout_opts = dict(
                    xlabel='Longitude',
                    ylabel='Latitude'
                  )
```

<!-- #region jupyter={"source_hidden": true} -->
Por último, usa el método `DataArray.where` para filtrar los píxeles que faltan y los que no vieron ningún cambio en la vegetación; estos valores de píxeles serán reasignados como `nan` por lo que serán transparentes cuando el raster sea visualizado. También modifica ligeramente las opciones de `image_opts` y `layout_opts`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
veg_anom_max = data.where((data>0) & (data!=255))
image_opts.update(crs=data.rio.crs)
layout_opts.update(title=f"VEG_ANOM_MAX")
```

<!-- #region jupyter={"source_hidden": true} -->
Estos cambios permiten generar una visualización útil.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
veg_anom_max.hvplot.image(**image_opts).opts(**layout_opts) * base
```

<!-- #region jupyter={"source_hidden": true} -->
En el gráfico resultante, los píxeles blancos y amarillos corresponden a regiones en las que se ha producido cierta deforestación, pero no mucha. Por el contrario, los píxeles oscuros y negros corresponden a regiones que han perdido casi toda la vegetación.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Banda 2: Fecha de alteración inicial de la vegetación (VEG_DIST_DATE)

<!-- #region jupyter={"source_hidden": true} -->
Los productos DIST-ALERT contienen varias bandas (tal como se resume en la [ especificación de productos DIST](https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DIST_HLS_Product_Specification_V1.pdf)). La segunda banda que se analiza es la _fecha de alteración inicial de la vegetación_ en el último año. Esta se almacena como un número entero de 16 bits (Int16).

El archivo `OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-DIST-DATE.tif` se almacena localmente. La [especificación de productos DIST](\(https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DIST_HLS_Product_Specification_V1.pdf\)) describe cómo utilizar las convenciones para la denominación de archivos. Aquí destaca la _fecha y hora de adquisición_ `20220815T185931`, por ejemplo, casi las 7 p.m. (UTC) del 15 de agosto del 2022.

Cargar y reetiqueta el `DataArray` como antes.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
LOCAL_PATH = FILE_STEM / 'assets' / 'data' / 'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-DIST-DATE.tif'
data = rio.open_rasterio(LOCAL_PATH)
data = data.rename({'x':'longitude', 'y':'latitude', 'band':'band'}).squeeze()
```

<!-- #region jupyter={"source_hidden": true} -->
En esta banda en particular, el valor 0 indica que no ha habido alteraciones en el último año y -1 es un valor que indica que faltan datos. Cualquier valor positivo es el número de días desde el 31 de diciembre del 2020 en los que se midió la primera alteración en ese píxel. Filtrar los valores no positivos y conserva estos valores significativos utilizando `DataArray.where`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
veg_dist_date = data.where(data>0)
```

<!-- #region jupyter={"source_hidden": true} -->
Examina el rango de valores numéricos en `veg_dist_date` utilizando DataArray.min`and`DataArray.max`. Ambos métodos ignorarán los píxeles que contengan `nan\` (por sus siglas en inglés de _Not-a-Number_) al calcular el mínimo y el máximo.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
d_min, d_max = int(veg_dist_date.min().item()), int(veg_dist_date.max().item())
print(f'{d_min=}\t{d_max=}')
```

<!-- #region jupyter={"source_hidden": true} -->
En este caso, los datos relevantes se encuentran entre 247 y 592. Recuerda que se trata del número de días transcurridos desde el 31 de diciembre del 2020, cuando se observó la primera alteración en el último año. Dado que estos datos se adquirieron el 15 de agosto del 2022, los únicos valores posibles estarían entre 227 y 592 días. Así que debes recalibrar los colores en la visualización.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts.update(
                   clim=(d_min,d_max),
                   crs=data.rio.crs
                 )
layout_opts.update(title=f"VEG_DIST_DATE")
```

```python jupyter={"source_hidden": true}
veg_dist_date.hvplot.image(**image_opts).opts(**layout_opts) * base
```

<!-- #region jupyter={"source_hidden": true} -->
Con este mapa de colores, los píxeles más claros mostraron algunos signos de deforestación hace cerca de un año. Por el contrario, los píxeles negros mostraron deforestación por primera vez cerca del momento de adquisición de los datos. Por tanto, esta banda es útil para seguir el avance de los incendios forestales a medida que arrasan los bosques.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Banda 3: Estado de alteración de la vegetación (VEG_DIST_STATUS)

<!-- #region jupyter={"source_hidden": true} -->
Por último, se analiza una tercera banda de la familia de productos DIST-ALERT denominada _estado de alteración de la vegetación_. Estos valores de píxel se almacenan como enteros de 8 bits sin signo. Solo hay 6 valores distintos almacenados:

- **0:** Sin alteración
- **1:** Alteración provisional (**primera detección**) con cambio en la cubierta vegetal < 50%
- **2:** Alteración confirmada (**detección recurrente**) con cambio en la cubierta vegetal < 50%
- **3:** Alteración provisional con cambio en la cobertura vegetal ≥ 50%
- **4:** Alteración confirmada con cambio en la cobertura vegetal ≥ 50%
- **255**: Datos no disponibles

El valor de un píxel se marca como cambiado provisionalmente cuando la pérdida de la cobertura vegetal (alteración) es observada por primera vez por un satélite. Si el cambio se vuelve a notar en posteriores adquisiciones HLS sobre dicho píxel, entonces el píxel se marca como confirmado.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
Se puede usar un archivo local como ejemplo de esta capa/banda particular de los datos DIST-ALERT. El código es el mismo que el anterior, pero observa que:

- los datos filtrados reflejan los valores de píxel significativos para esta capa (por ejemplo, `data>0` and `data<5`), y
- los valores del mapa de colores se reasignan en consecuencia (es decir, de 0 a 4).

Observa el uso de `FixedTicker` en la definición de una barra de colores más adecuada para un mapa de color discreto (es decir, categórico).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
LOCAL_PATH = FILE_STEM / 'assets' / 'data' / 'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-DIST-STATUS.tif'
data = rio.open_rasterio(LOCAL_PATH)
data = data.rename({'x':'longitude', 'y':'latitude', 'band':'band'}).squeeze()
```

```python jupyter={"source_hidden": true}
veg_dist_status = data.where((data>0)&(data<5))
image_opts.update(crs=data.rio.crs)
```

```python jupyter={"source_hidden": true}
layout_opts.update(
                    title=f"VEG_DIST_STATUS",
                    clim=(0,4),
                    colorbar_opts={'ticker': FixedTicker(ticks=[0, 1, 2, 3, 4])}
                  )
```

```python jupyter={"source_hidden": true}
veg_dist_status.hvplot.image(**image_opts).opts(**layout_opts) * base
```

<!-- #region jupyter={"source_hidden": true} -->
Este mapa de colores continuo no resalta correctamente las características de este gráfico. Una mejor opción sería un mapa de colores _categórico_. Se mostrará como hacerlo en el próximo cuaderno computacional (con los productos de datos OPERA DSWx).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

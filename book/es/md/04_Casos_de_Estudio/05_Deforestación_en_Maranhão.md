---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.2
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Deforestación en Maranhão

<!-- #region jupyter={"source_hidden": true} -->
La Amazonía es una de las regiones más biodiversas del planeta y un componente clave del sistema climático global que además sostiene múltiples comunidades indígenas. En particular el estado de Maranhão, en Brasil, es uno de los focos más críticos de deforestación en el país. Se estima que el 76 % de la cobertura original de bosque amazónico en este estado ha sido destruida. Según Global Forest Watch, Maranhão ha registrado una de las tasas más altas de pérdida de cobertura boscosa en Brasil en los últimos años, impulsada por incendios, expansión agropecuaria y tala ilegal. Estos procesos están estrechamente ligados a la fragmentación ecológica, la pérdida de biodiversidad y la violencia hacia comunidades indígenas. Frente a este escenario, el monitoreo sistemático de los cambios en la cobertura vegetal es fundamental. Los productos OPERA DIST-HLS, derivados principalmente de Landsat (NASA/USGS) y Sentinel-2 (ESA), ofrecen una herramienta poderosa para detectar disturbios recientes y aportar evidencia clave para la conservación y la formulación de políticas públicas basadas en datos.

<figure style="text-align: center;">
  <img src="https://tse3.mm.bing.net/th/id/OIP.sSfdF5nBFUWbh3UImdbyVgHaE7?pid=Api" alt="Buriticupu - erosión" style="max-width: 100%; height: auto;">
  <figcaption style="font-size: 0.9em; color: #555;">Foto: AFP / El País (2023)</figcaption>
</figure>
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Ruta de trabajo

<!-- #region jupyter={"source_hidden": true} -->
Nuestro objetivo es evaluar la deforestación en un area cercana a la ciudad de Buriticupu en el estado Maranhao. 
Para eso en esta notebook vamos a :

1. Filtrar y seleccionar los productos OPERA DIST-ALERT desde la nube
2. Visualizar y explorar los subproductos VEG_DIST_STATUS
3. Gráficar la evolución del disturbio a lo largo del tiempo.
4. Generar un mapa de disturbios
5. Explorar subproducto VEG_DIST_DATE
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### Antes de empezar - Importar librerías que vamos a utilizar

```python jupyter={"source_hidden": true}
#librerias para manipulación de datos
from warnings import filterwarnings #suprime los warning
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
import rasterio
```

```python jupyter={"source_hidden": true}
#librerias para visualización
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```python jupyter={"source_hidden": true}
#configuración de acceso a datos geoespaciales desde la nube
from pystac_client import Client
from osgeo import gdal
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### 1. FILTRAR Y SELECCIONAR LOS PRODUCTOS OPERA DESDE LA NUBE

<!-- #region jupyter={"source_hidden": false} -->
#### 1.a Seleccionar el area de estudio 
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# PASOS PARA SELECCIONAR EL ÁREA DE ESTUDIO (AOI) 
# Usar la herramienta online: https://boundingbox.klokantech.com/
# 1. Buscar la zona de interés y dibujar un rectángulo sobre el mapa.
# 2. En la sección "Copy & Paste", seleccionar el formato "CSV".
# 3. Copiar las coordenadas 
# Estas coordenadas están en el orden correcto requerido por STAC:
# bbox = [xmin, ymin, xmax, ymax] = [long_oeste, lat_sur, long_este, lat_norte]
```

<!-- #region jupyter={"source_hidden": true} -->
Coordenadas copiadas de boundingbox
-46.52993,-4.383815,-46.363075,-4.243793
<!-- #endregion -->

```python jupyter={"source_hidden": true}
#Definir el AOI con las coordenadas 
AOI = [-46.52993,-4.383815,-46.363075,-4.243793]
rango_fechas = "2022-01-01/2024-03-31"
```

<!-- #region jupyter={"source_hidden": false} -->
#### 1.b Explorar y buscar los productos OPERA DIST-ALERT
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Realizamos la búsqueda de productos OPERA DIST-ALERT para ver fechas disponibles
from pystac_client import Client

#parámetros de búsqueda
search_params = {
    "bbox": AOI,
    "datetime": rango_fechas,
    "collections": ["OPERA_L3_DIST-ALERT-HLS_V1_1"]
}

client = Client.open("https://cmr.earthdata.nasa.gov/stac/LPCLOUD/")
items = list(client.search(**search_params).get_items())

# Extraemos fechas disponibles
fechas = sorted({item.datetime.date() for item in items})
print(f"Fechas disponibles ({len(fechas)}):")
print(fechas)
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
**Cada item OPERA DIST-ALERT incluye varios assets `.tif`, y cada uno representa una capa de información distinta:**

- **VEG-DIST-STATUS.tif**: detección de disturbio 
- **VEG-DIST-CONF.tif**: nivel de confianza de la detección
- **VEG-DIST-DATE.tif**: fecha en que se detectó el disturbio
- **VEG-ANOM.tif**: anomalía de la vegetación
- **VEG-IND.tif**: índice de vegetación
- **VEG-LAST-DATE.tif**: última fecha sin disturbio detectado
- **VEG-DIST-DUR.tif**: duración acumulada del disturbio
- **VEG-DIST-COUNT.tif**: número de disturbios detectados
<!-- #endregion -->

```python jupyter={"source_hidden": true}
#Imprimimos los archivos que se encuentran dentro de 1 item
item = items[0]  

print(f"Item - Fecha: {item.datetime.date()}")
for asset_key, asset in item.assets.items():
    print(f"  Asset: {asset_key} → {asset.href}")
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
#### 1.c Filtramos los asset VEG_DIST-STATUS con baja nubosidad
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Recorremos todos los productos encontrados y seleccionamos solo los archivos .tif
# correspondientes al asset 'VEG-DIST-STATUS'
# Guardamos la fecha del producto y el link al archivo 

veg_status_assets = []

for item in items:
    for key, asset in item.assets.items():
        if "VEG-DIST-STATUS" in key and asset.href.endswith(".tif"):
            veg_status_assets.append({
                "fecha": item.datetime.date(),
                "url": asset.href
            })

print(f"Se encontraron {len(veg_status_assets)} archivos VEG-DIST-STATUS.")

#imprimimos los primeros 10
for registro in veg_status_assets[:10]:
    print(f"  {registro['fecha']} → {registro['url']}")
```

```python jupyter={"source_hidden": true}
# Imprimimos cloud_cover de los items con asset VEG-DIST-STATUS
for item in items:
    if any("VEG-DIST-STATUS" in k for k in item.assets):
        print(f"{item.datetime.date()} → Cloud cover: {item.properties.get('eo:cloud_cover', 'No disponible')}")
```

```python jupyter={"source_hidden": true}
filtrados = []

for item in items:
    cloud = item.properties.get('eo:cloud_cover', None)
    if cloud is not None and cloud < 40:
        for key, asset in item.assets.items():
            if (
                "VEG-DIST-STATUS" in key and 
                asset.href.endswith(".tif") and 
                asset.href.startswith("https")
            ):
                filtrados.append({
                    "fecha": item.datetime.date(),
                    "url": asset.href,
                    "nubes": cloud
                })
print(f"Se encontraron {len(filtrados)} archivos con menos de 40% de nubes.")
for registro in filtrados[:10]:
    print(f"{registro['fecha']} → Cloud cover: {registro['nubes']} → {registro['url']}")
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### 2. VISUALIZAR Y EXPLORAR Productos VEG_DIST_STATUS

```python jupyter={"source_hidden": true}
#Visualizar productos VEG_DIST_STATUS en el area de interes.

#convertir a shp las coordenadas del area de interes (AOI)
from shapely.geometry import box
import geopandas as gpd

# AOI definido como bounding box
aoi_coords = [-46.78, -4.61, -46.58, -4.41]  # xmin, ymin, xmax, ymax
aoi_geom = box(*aoi_coords)
AOI = gpd.GeoDataFrame(geometry=[aoi_geom], crs="EPSG:4326")
```

```python jupyter={"source_hidden": true}
#Visualizar la primer y ultima fecha del los productos filtrados
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
import rioxarray

# Crear colormap personalizado
white_to_red = mcolors.LinearSegmentedColormap.from_list("white_to_red", ["white", "red"])

# URLs de los dos productos
urls = [
    ("2023/06/26", "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/OPERA_L3_DIST-ALERT-HLS_V1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230626T133151Z_20231221T083621Z_S2A_30_v1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230626T133151Z_20231221T083621Z_S2A_30_v1_VEG-DIST-STATUS.tif"),
    ("2023/09/18", "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/OPERA_L3_DIST-ALERT-HLS_V1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230918T131723Z_20231221T085043Z_L8_30_v1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230918T131723Z_20231221T085043Z_L8_30_v1_VEG-DIST-STATUS.tif")
]

# Crear figura
fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)

for ax, (label, url) in zip(axes, urls):
    da = rioxarray.open_rasterio(url, masked=True).squeeze()
    # Reproyectar AOI al CRS del raster
    aoi_proj = AOI.to_crs(da.rio.crs)
    # Recorte
    da_clip = da.rio.clip(aoi_proj.geometry, aoi_proj.crs)
    # Plot
    img = da_clip.plot(
        ax=ax,
        cmap=white_to_red,
        vmin=0,
        vmax=8,
        add_colorbar=False
    )
    aoi_proj.boundary.plot(ax=ax, edgecolor="black", linewidth=0.5)
    ax.set_title(f"Disturbios detectados\n{label}")
    ax.axis("off")

# Agregar colorbar común
cbar = fig.colorbar(img, ax=axes.ravel().tolist(), shrink=0.6, label="Vegetation_disturbance_status")
plt.show()
```

<!-- #region jupyter={"source_hidden": true} -->
Valores del producto `VEG-DIST-STATUS`:

- **0:** Sin alteración
- **1:** Primera detección de alteraciones con cambios en la cobertura vegetal <50%
- **2:** Detección provisional de alteraciones con cambios en la cobertura vegetal <50%
- **3:** Detección confirmada de alteraciones con cambios en la cobertura vegetal < 50%
- **4:** Primera detección de alteraciones con cambios en la cobertura vegetal ≥50%
- **5:** Detección provisional de alteraciones con cambios en la cobertura vegetal ≥50%
- **6:** Detección confirmada de alteraciones con cambios en la cobertura vegetal ≥50%
- **7:** Detección finalizada de alteraciones con cambios en la cobertura vegetal <50%
- **8:** Detección finalizada de alteraciones con cambios en lacobertura vegetal ≥50%
- **255** Datos faltantes
<!-- #endregion -->



```python jupyter={"source_hidden": true}
#Graficar la distribución de los valores de disturbios en dos subproductos DIST-VEG-ALERT

import matplotlib.pyplot as plt
import numpy as np
import rioxarray

# URLs de los dos productos
urls = [
    ("2023/06/26", "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/OPERA_L3_DIST-ALERT-HLS_V1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230626T133151Z_20231221T083621Z_S2A_30_v1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230626T133151Z_20231221T083621Z_S2A_30_v1_VEG-DIST-STATUS.tif"),
    ("2023/09/18", "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/OPERA_L3_DIST-ALERT-HLS_V1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230918T131723Z_20231221T085043Z_L8_30_v1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230918T131723Z_20231221T085043Z_L8_30_v1_VEG-DIST-STATUS.tif")
]

# Leer y calcular frecuencias primero
frecuencias = []
for label, url in urls:
    da = rioxarray.open_rasterio(url, masked=True).squeeze()
    aoi_proj = AOI.to_crs(da.rio.crs)
    da_clip = da.rio.clip(aoi_proj.geometry, aoi_proj.crs)
    vals = da_clip.values.flatten()
    vals = vals[(vals > 0) & (~np.isnan(vals))]
    hist, _ = np.histogram(vals, bins=np.arange(0.5, 9.5, 1))
    frecuencias.append((label, hist))

# Encontrar el máximo para escalar ambos plots
ymax = max(hist.max() for _, hist in frecuencias)

# Gráfico
fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
for ax, (label, hist) in zip(axes, frecuencias):
    ax.bar(range(1, 9), hist, color='crimson', edgecolor='black', alpha=0.7)
    ax.set_xticks(range(1, 9))
    ax.set_ylim(0, ymax + ymax * 0.1)
    ax.set_title(f"Histograma - {label}")
    ax.set_xlabel("Clase de disturbio")
    ax.set_ylabel("Frecuencia")

plt.suptitle("Distribución de clases de disturbio detectadas", fontsize=14)
plt.show()
```
<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### 3. EVOLUCIÓN DEL DISTURBIO A LO LARGO DEL TIEMPO 

```python jupyter={"source_hidden": true}
# Stack de los 12 subproductos VEG-DIST-STATUS

from rioxarray import open_rasterio
import xarray as xr
import numpy as np
import pandas as pd

# Recortar cada raster al AOI y luego apilar
raster_list = []
fechas = []

for f in filtrados:    
    da = open_rasterio(f["url"], masked=True).squeeze()
    aoi_proj = AOI.to_crs(da.rio.crs)
    da_clip = da.rio.clip(aoi_proj.geometry, aoi_proj.crs)
    
    raster_list.append(da_clip)
    fechas.append(pd.Timestamp(f["fecha"]))

# Crear el stack recortado
stack = xr.concat(raster_list, dim="time")
stack["time"] = fechas
```

```python jupyter={"source_hidden": true}
stack
```

```python jupyter={"source_hidden": true}
#Graficar el area disturbada acumulada en el area de estudio

import matplotlib.pyplot as plt

#ordenaar el stack por fecha
stack_sorted = stack.sortby("time")

# Crear máscara booleana donde el valor sea 6 (disturbio confirmado)
disturbios = stack_sorted == 6

# Sumar la cantidad de píxeles por fecha
pixeles_por_fecha = disturbios.sum(dim=["x", "y"])

# Convertir a km² (cada píxel es de 30m x 30m = 900 m² = 0.0009 km²)
km2_por_fecha = pixeles_por_fecha * 0.0009

# Graficar
plt.figure(figsize=(8, 5))
km2_por_fecha.to_series().plot(marker='o')
plt.title("Evolución de disturbios confirmados (valor 6)")
plt.ylabel("Área acumulada (km²)")
plt.xlabel("Fecha")
plt.grid(True)
plt.tight_layout()
plt.show()
```

<!-- #region jupyter={"source_hidden": true} -->
¿Hay algo raro en los graficos?
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Convertir a DataFrame 
df_filtrados = pd.DataFrame(filtrados)
df_filtrados["fecha"] = pd.to_datetime(df_filtrados["fecha"])

# Ordenar por menor cobertura de nubes 
df_filtrados = df_filtrados.sort_values("nubes")
#Seleccionar el producto con Sentinel

# Eliminar duplicados dejando el que tiene menor nubosidad
df_filtrados = df_filtrados.drop_duplicates(subset="fecha", keep="first")

# Reconstruir la lista filtrada
filtrados_unicos = df_filtrados.to_dict(orient="records")
```

```python jupyter={"source_hidden": true}
#VOLVEMOS A CORRER EL STACK USANDO filtrados_unicos

# Stack de los subproductos VEG-DIST-STATUS

from rioxarray import open_rasterio
import xarray as xr
import numpy as np
import pandas as pd

# Recortar cada raster al AOI y luego apilar
raster_list = []
fechas = []

for f in filtrados_unicos: 
    da = open_rasterio(f["url"], masked=True).squeeze()
    aoi_proj = AOI.to_crs(da.rio.crs)
    da_clip = da.rio.clip(aoi_proj.geometry, aoi_proj.crs)
    
    raster_list.append(da_clip)
    fechas.append(pd.Timestamp(f["fecha"]))

# Crear el stack recortado
stack = xr.concat(raster_list, dim="time")
stack["time"] = fechas
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### 4. GENERAR UN MAPA DE DISTUBIOS

```python jupyter={"source_hidden": true}
import hvplot.xarray
import geoviews as gv
import numpy as np

# Enmascarar valores 0 para que sean transparentes
stack_masked = stack.where(stack != 0)

# Submuestreo para que no sea tan pesado
stack_sub = stack_masked.isel(x=slice(0, None, 4), y=slice(0, None, 4))

# Colormap rojo fuerte
cmap = ["#fff5f5", "#fcbfbf", "#f78787", "#f25454", "#e93232", "#d40000", "#a50000", "#730000"]

# Visualización interactiva
hvplot_map = stack_sub.hvplot(
    x='x',
    y='y',
    groupby='time',
    cmap=cmap,
    clim=(1, 8),
    rasterize=True,
    crs=stack.rio.crs,
    tiles=gv.tile_sources.EsriImagery,
    alpha=0.9,
    frame_width=500,    
    frame_height=500,
    title="Evolución de disturbios detectados",
    widget_location='bottom',   # Deslizador de tiempo abajo
    colorbar=True
)

hvplot_map
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### 5. EXPLORAR SUBPRODUCTO VEG_DIST-DATE

```python jupyter={"source_hidden": true}
from pystac_client import Client
import pandas as pd

# Abrir el catálogo STAC de LP DAAC
catalog = Client.open("https://cmr.earthdata.nasa.gov/stac/LPCLOUD/")

# Parámetros de búsqueda
search_params = {
    "bbox": [-46.78, -4.61, -46.58, -4.41],  # AOI
    "datetime": "2025-01-01/2025-07-26",     # rango de fechas
    "collections": ["OPERA_L3_DIST-ALERT-HLS_V1_1"]
}

# Buscar items en el catálogo
items = list(catalog.search(**search_params).get_items())

# Filtrar solo los assets VEG-DIST-DATE accesibles por HTTPS
filtrado_date = []

for item in items:
    for asset_key, asset in item.assets.items():
        if "VEG-DIST-DATE" in asset_key and asset.href.startswith("https"):
            filtrado_date.append({
                "start_datetime": item.properties.get("start_datetime"),
                "end_datetime": item.properties.get("end_datetime"),
                "datetime": item.datetime,
                "cloud_cover": item.properties.get("eo:cloud_cover"),
                "url": asset.href
            })

# Convertir a DataFrame para explorar
df = pd.DataFrame(filtrado_date)

# Mostrar resumen
print(f"Se encontraron {len(df)} assets únicos con VEG-DIST-DATE vía HTTPS.")
df.head()
```

```python jupyter={"source_hidden": true}
import matplotlib.pyplot as plt

df["cloud_cover"] = pd.to_numeric(df["cloud_cover"], errors='coerce')
df.plot(
   #x="datetime", 
    y="cloud_cover", 
    kind="bar", 
    figsize=(10, 5), 
    color="skyblue", 
    title="Cobertura de nubes por escena"
)
# Ocultar etiquetas del eje X
plt.xticks([])

plt.tight_layout()
plt.show()
```

```python jupyter={"source_hidden": true}
df_bajanubosidad = df[df["cloud_cover"] < 20]

df_bajanubosidad.plot(
   #x="datetime", 
    y="cloud_cover", 
    kind="bar", 
    figsize=(10, 5), 
    color="skyblue", 
    title="Cobertura de nubes por fecha"
);
```

```python jupyter={"source_hidden": true}
# Asegurarse de que la columna de fechas esté como datetime
df_bajanubosidad["end_datetime"] = pd.to_datetime(df_bajanubosidad["end_datetime"])

# Ordenar por fecha final y seleccionar el más reciente
más_reciente_baja_nubosidad = df_bajanubosidad.sort_values("end_datetime", ascending=False).iloc[0]

# Mostrar resultado
print("Producto más reciente con menos de 20% de nubosidad:")
print(más_reciente_baja_nubosidad)
```

```python jupyter={"source_hidden": true}
#seleccionamos la url del producto mas reciente con nubosidad < 20%
url=más_reciente_baja_nubosidad["url"]
```

```python jupyter={"source_hidden": true}
#Visualizar el subproducto VEG_DIST_DATE en comparación con el subproducto VEG_DIST_STATE

import matplotlib.pyplot as plt
import geopandas as gpd
import rioxarray
import numpy as np
from shapely.geometry import box

# AOI
aoi_geom = gpd.GeoDataFrame(geometry=[box(-46.78, -4.61, -46.58, -4.41)], crs="EPSG:4326")

# Subproducto VEG_DIST_DATE
url1 = más_reciente_baja_nubosidad["url"]
da1 = rioxarray.open_rasterio(url1, masked=True).squeeze()
aoi_proj = aoi_geom.to_crs(da1.rio.crs)
da1_clip = da1.rio.clip(aoi_proj.geometry, aoi_proj.crs)
masked1 = np.ma.masked_where(da1_clip <= 0, da1_clip)

# Subproducto VEG_DIST_STATUS
url2= "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/OPERA_L3_DIST-ALERT-HLS_V1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230918T131723Z_20231221T085043Z_L8_30_v1/OPERA_L3_DIST-ALERT-HLS_T23MLR_20230918T131723Z_20231221T085043Z_L8_30_v1_VEG-DIST-STATUS.tif"
da2 = rioxarray.open_rasterio(url2, masked=True).squeeze()
da2_clip = da2.rio.clip(aoi_proj.geometry, aoi_proj.crs)
masked2 = np.ma.masked_where(da2_clip <= 0, da2_clip)

# Gráfico de los 2 subproductos
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Mapa 1
img1 = axes[0].imshow(
    masked1,
    cmap="viridis",
    extent=da1_clip.rio.bounds(),
    interpolation="nearest"
)
axes[0].set_title("VEG_DIST_DATE 17/07/2025")
axes[0].set_frame_on(True)
cbar1 = plt.colorbar(img1, ax=axes[0], shrink=0.7)
cbar1.set_label("Día desde 2020-12-31")

# colormap personalizado
white_to_red = mcolors.LinearSegmentedColormap.from_list("white_to_red", ["white", "red"])
# Mapa 2
img2 = axes[1].imshow(
    masked2,
    cmap= white_to_red,
    extent=da2_clip.rio.bounds(),
    interpolation="nearest"
)
axes[1].set_title("VEG_DIST-STATUS 18/09/2023")
axes[1].set_frame_on(True)
cbar2 = plt.colorbar(img2, ax=axes[1], shrink=0.7)
cbar2.set_label("Valor de disturbio")

plt.tight_layout()
plt.show()
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

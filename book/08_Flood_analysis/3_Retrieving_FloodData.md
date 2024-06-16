---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

## Retrieving OPERA DSWx-HLS data for a flood event

Heavy rains severely impacted Southeast Texas in May 2024 [[1]](https://www.texastribune.org/2024/05/03/texas-floods-weather-harris-county/), resulting in flooding and causing significant damage to property and human life [[2]](https://www.texastribune.org/series/east-texas-floods-2024/). In this notebook, we will retrieve [OPERA DSWx-HLS](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf) data associated to understand the extent of flooding and damage, and visualize data from before, during, and after the event.

```python
import rasterio
import rioxarray
from rasterio.warp import transform_bounds, reproject
from rasterio.crs import CRS
import folium

import hvplot.pandas  # noqa
import hvplot.xarray  # noqa
import xarray as xr
import cartopy.crs as ccrs
import xyzservices.providers as xyz
from matplotlib.colors import ListedColormap
from bokeh.models import CategoricalColorMapper, ColorBar

from shapely.geometry import Point
from osgeo import gdal

from holoviews.plotting.util import process_cmap

import pandas as pd

# Imports for plotting
import geoviews as gv
gv.extension('bokeh')
gv.output(size=1000)

# STAC imports to retrieve cloud data
from pystac_client import Client

from datetime import datetime
import numpy as np

# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')

```

```python
# Let's set up the parameters of our search query

# Flooding in Texas, 2024; 
livingston_tx = Point(-95.09, 30.69).buffer(0.01)

# We will search data around the flooding event at the start of May
start_date = datetime(year=2024, month=4, day=30)
stop_date = datetime(year=2024, month=5, day=31)
date_range = f'{start_date.strftime("%Y-%m-%d")}/{stop_date.strftime("%Y-%m-%d")}'

# We open a client instance to search for data, and retrieve relevant data records
STAC_URL = 'https://cmr.earthdata.nasa.gov/stac'

# Setup PySTAC client
# POCLOUD refers to the PO DAAC cloud environment that hosts earth observation data
catalog = Client.open(f'{STAC_URL}/POCLOUD/') 

# Setup PySTAC client
provider_cat = Client.open(STAC_URL)
catalog = Client.open(f'{STAC_URL}/POCLOUD/')
collections = ["OPERA_L3_DSWX-HLS_V1"]

opts = {
    'bbox' : livingston_tx.bounds, 
    'collections': collections,
    'datetime' : date_range,
}
```


```python
# Execute the search
search = catalog.search(**opts)
results = list(search.items_as_dicts())
print(f"Number of tiles found intersecting given AOI: {len(results)}")
```

```python
# Let's load the search results into a pandas dataframe
layer_name = '0_B01_WTR'

times = pd.DatetimeIndex([result['properties']['datetime'] for result in results]) # parse of timestamp for each result
data = {'hrefs': [value['href'] for result in results for key, value in result['assets'].items() if layer_name in key],  # parse out links only to DIST-STATUS data layer
        'tile_id': [value['href'].split('/')[-1].split('_')[3] for result in results for key, value in result['assets'].items() if layer_name in key]}

# # Construct pandas dataframe to summarize granules from search results
granules = pd.DataFrame(index=times, data=data)
granules.index.name = 'times'
```

```python
granules.head()
```

```python
# We now filter the dataframe to restrict our results to a single tile_id
granules = granules[granules.tile_id == 'T15RTQ']
granules.sort_index(inplace=True)
```

```python
granules
```

```python
def urls_to_dataset(granule_dataframe):
    '''method that takes in a list of OPERA tile URLs and returns an xarray dataset with dimensions
    latitude, longitude and time'''

    dataset_list = []
    
    for i, row in granule_dataframe.iterrows():
        with rasterio.open(row.hrefs) as ds:
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

        lon_grid, lat_grid = np.meshgrid(lon, lat)

        da = xr.DataArray(
            data=img,
            dims=["band", "y", "x"],
            coords=dict(
                lon=(["y", "x"], lon_grid),
                lat=(["y", "x"], lat_grid),
                time=i,
                band=np.arange(img.shape[0])
            ),
            attrs=dict(
                description="OPERA DSWx B01",
                units=None,
            ),
        )
        da.rio.write_crs(crs, inplace=True)

        dataset_list.append(da)
    return xr.concat(dataset_list, dim='time').squeeze()

dataset= urls_to_dataset(granules)
```

```python
COLORS = [(0, 0, 0, 0)]*256
COLORS[1] = (0, 0, 255, 1) # OSW
COLORS[2] = (0, 0, 255, 1) # PSW
COLORS[252] = (0, 0, 255, 1) # ICE
COLORS[253] = (150, 150, 150, 1)
```

```python
img = dataset.hvplot.quadmesh(title = 'DSWx data for May 2024 Texas floods',
                            x='lon', y='lat', 
                            project=True, rasterize=True, frame_width=100,
                            cmap=COLORS, 
                            colorbar=False,
                            widget_location='bottom',
                            tiles = xyz.OpenStreetMap.Mapnik,
                            xlabel='Longitude (degrees)',ylabel='Latitude (degrees)',
                            fontscale=1.25)

img
```

---

## Exercise: Repeat the analysis.

+ Specify a region geographic rectangle (suggestions?).
+ Specify a period in time (i.e., a start date and an end date).
+ Use the PySTAC API to retrieve search results.
+ Make a Pandas DataFrame from the results to identify which dates yield the most granules.
+ Pull the relevant TIF files into the notebook session to make a few plots.
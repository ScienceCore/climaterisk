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

## Retrieving OPERA DSWx-HLS data for a flood event

Heavy rains severely impacted Southeast Texas in May 2024 [[1]](https://www.texastribune.org/2024/05/03/texas-floods-weather-harris-county/), resulting in flooding and causing significant damage to property and human life [[2]](https://www.texastribune.org/series/east-texas-floods-2024/). In this notebook, we will retrieve [OPERA DSWx-HLS](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf) data associated to understand the extent of flooding and damage, and visualize data from before, during, and after the event.

```python
import rasterio
import rioxarray
import folium

import hvplot.xarray  # noqa
import xarray as xr
import xyzservices.providers as xyz

from shapely.geometry import Point
from osgeo import gdal

from holoviews.plotting.util import process_cmap

import pandas as pd

from warnings import filterwarnings
filterwarnings("ignore") # suppress PySTAC warnings

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
livingston_tx = Point(-95.09, 30.69)

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
    'bbox' : livingston_tx.buffer(0.01).bounds, 
    'collections': collections,
    'datetime' : date_range,
}
```


```python
livingston_tx = Point(-95.09, 30.69)
m = folium.Map(location=(livingston_tx.y, livingston_tx.x), control_scale = True, zoom_start=8)
radius = 15000
folium.Circle(
    location=[livingston_tx.y, livingston_tx.x],
    radius=radius,
    color="red",
    stroke=False,
    fill=True,
    fill_opacity=0.6,
    opacity=1,
    popup="{} pixels".format(radius),
    tooltip="Livingston, TX",
    # 
).add_to(m)

m
```

```python
# Execute the search
search = catalog.search(**opts)
results = list(search.items_as_dicts())
print(f"Number of tiles found intersecting given AOI: {len(results)}")
```

```python
def search_to_df(results, layer_name='0_B01_WTR'):
        '''
        Given search results returned from a NASA earthdata query, load and return relevant details and band links as a dataframe
        '''

        times = pd.DatetimeIndex([result['properties']['datetime'] for result in results]) # parse of timestamp for each result
        data = {'hrefs': [value['href'] for result in results for key, value in result['assets'].items() if layer_name in key], 
                'tile_id': [value['href'].split('/')[-1].split('_')[3] for result in results for key, value in result['assets'].items() if layer_name in key]}


        # Construct pandas dataframe to summarize granules from search results
        granules = pd.DataFrame(index=times, data=data)
        granules.index.name = 'times'

        return granules
```

```python
granules = search_to_df(results)
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
type(results[0])

```

```python
def filter_search_by_cc(results, cloud_threshold=10):
    '''
    Given a list of results returned by the NASA Earthdata STAC API for OPERA DSWx data,
    filter them by cloud cover
    '''

    filtered_results = []

    for result in results:
        try:
            cloud_cover = result['properties']['eo:cloud_cover']
        except:
            href = result['assets']['0_B01_WTR']['href']
            with rasterio.open(href) as ds:
                img = ds.read(1).flatten()
                cloud_cover = 100*(np.sum(np.isin(img, 253))/img.size)

        if  cloud_cover <= cloud_threshold:
            filtered_results.append(result)

    return filtered_results
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
COLORS = [(150, 150, 150, 0)]*256
COLORS[0] = (0, 255, 0, 1)
COLORS[1] = (0, 0, 255, 1) # OSW
COLORS[2] = (0, 0, 255, 1) # PSW
COLORS[252] = (0, 0, 255, 1) # ICE
COLORS[253] = (150, 150, 150, 1)
```

```python
img = dataset.hvplot.quadmesh(title = 'DSWx data for May 2024 Texas floods',
                            x='lon', y='lat', 
                            project=True, rasterize=True,
                            cmap=COLORS, 
                            colorbar=False,
                            widget_location='bottom',
                            tiles = xyz.OpenStreetMap.Mapnik,
                            xlabel='Longitude (degrees)',ylabel='Latitude (degrees)',
                            fontscale=1.25, frame_width=1000, frame_height=1000)

img
```

### Vaigai Reservoir

```python
vaigai_reservoir = Point(77.568, 10.054)
```

```python
# Plotting search location in folium as a sanity check
m = folium.Map(location=(vaigai_reservoir.y, vaigai_reservoir.x), control_scale = True, zoom_start=9)
radius = 5000
folium.Circle(
    location=[vaigai_reservoir.y, vaigai_reservoir.x],
    radius=radius,
    color="red",
    stroke=False,
    fill=True,
    fill_opacity=0.6,
    opacity=1,
    popup="{} pixels".format(radius),
    tooltip="50 px radius",
    # 
).add_to(m)

m
```

```python
# We will search data around the flooding event in December
start_date = datetime(year=2023, month=4, day=1)
stop_date = datetime(year=2024, month=4, day=1)
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

# Setup search options
opts = {
    'bbox' : vaigai_reservoir.buffer(0.01).bounds, 
    'collections': collections,
    'datetime' : date_range,
}

# Execute the search
search = catalog.search(**opts)
results = list(search.items_as_dicts())
print(f"Number of tiles found intersecting given AOI: {len(results)}")
```

```python
# let's filter our results so that only scenes with less than 10% cloud cover are returned
results = filter_search_by_cc(results)

print("Number of results containing less than 10% cloud cover: ", len(results))
```

```python
# Load results into dataframe
granules = search_to_df(results)
```

```python
# This may take a while depending on the number of results we are loading
dataset= urls_to_dataset(granules)
```

```python
img = dataset.hvplot.quadmesh(title = 'Vaigai Reservoir, India - water extent over a year',
                            x='lon', y='lat', 
                            project=True, rasterize=True, 
                            cmap=COLORS, 
                            colorbar=False,
                            widget_location='bottom',
                            tiles = xyz.OpenStreetMap.Mapnik,
                            xlabel='Longitude (degrees)',ylabel='Latitude (degrees)',
                            fontscale=1.25, frame_width=1000, frame_height=1000)

img
```

### Lake Mead

```python
lake_mead = Point(-114.348, 36.423)
```

```python
# Plotting search location in folium as a sanity check
m = folium.Map(location=(lake_mead.y, lake_mead.x), control_scale = True, zoom_start=9)
radius = 5000
folium.Circle(
    location=[lake_mead.y, lake_mead.x],
    radius=radius,
    color="red",
    stroke=False,
    fill=True,
    fill_opacity=0.6,
    opacity=1,
    popup="{} pixels".format(radius),
    tooltip="50 px radius",
    # 
).add_to(m)

m
```

```python
# We will search data for a year
start_date = datetime(year=2023, month=3, day=1)
stop_date = datetime(year=2024, month=6, day=15)
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

# Setup search options
opts = {
    'bbox' : lake_mead.buffer(0.01).bounds, 
    'collections': collections,
    'datetime' : date_range,
}

# Execute the search
search = catalog.search(**opts)
results = list(search.items_as_dicts())
print(f"Number of tiles found intersecting given AOI: {len(results)}")
```

```python
# let's filter our results so that only scenes with less than 10% cloud cover are returned
results = filter_search_by_cc(results)

print("Number of results containing less than 10% cloud cover: ", len(results))
```

That's a fairly large number of tiles! Loading the data into an xarray dataset will take a few minutes.

```python
# Load results into dataframe
granules = search_to_df(results)
```

```python
# Let's filter by tile id so that we can study changes over the same spatial extent
granules = granules[granules.tile_id=='T11SQA']
```

```python
# Similarly, loading a year's worth of data will take a few minutes
dataset= urls_to_dataset(granules)
```

```python
img = dataset.hvplot.quadmesh(title = 'Lake Mead, NV USA - water extent over a year',
                            x='lon', y='lat', 
                            project=True, rasterize=True,
                            cmap=COLORS, 
                            colorbar=False,
                            widget_location='bottom',
                            tiles = xyz.OpenStreetMap.Mapnik,
                            xlabel='Longitude (degrees)',ylabel='Latitude (degrees)',
                            fontscale=1.25, frame_width=1000, frame_height=1000)

img
```

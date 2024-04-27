# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: opera_app_dev
#     language: python
#     name: python3
# ---

# ## Retrieving OPERA DSWx-HLS data for a flood event
#
# Heavy rains severly impacted Argentina in March 2024 [[1]](https://www.reuters.com/world/americas/argentina-downpour-drenches-crop-fields-flash-floods-buenos-aires-2024-03-12/). The event resulted in flash floods and impacted crop yields, severely impacting the Buenos Aires metropolitan area, and caused significant damage to property and human life. In this notebook, we will retrieve OPERA DSWx-HLS data associated to understand the extent of flooding and damage, and compare data from before and after the event.

# +
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
from shapely.geometry import box
from osgeo import gdal
from pystac_client import Client
import rioxarray
import geoviews as gv
from rioxarray import merge as rioxarray_merge
from rasterio.merge import merge
import rasterio
import xarray as xr
import numpy as np

# sys.path.append('../../')
# from src.dswx_utils import intersection_percent, colorize, getbasemaps, transform_data_for_folium

# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')

# +
# Define data search parameters

# Define AOI as left, bottom, right and top lat/lon extent
aoi = box(-59.63818, -35.02927, -58.15723, -33.77271)

# We will search data for the month of March 2024
start_date = datetime(year=2024, month=3, day=1)
stop_date = datetime(year=2024, month=3, day=31)

# +
# We open a client instance to search for data, and retrieve relevant data records
STAC_URL = 'https://cmr.earthdata.nasa.gov/stac'

# Setup PySTAC client
provider_cat = Client.open(STAC_URL)
catalog = Client.open(f'{STAC_URL}/POCLOUD/')
collections = ["OPERA_L3_DSWX-HLS_PROVISIONAL_V1"]

# We would like to search data for March 2024
date_range = f"{start_date.strftime("%Y-%m-%d")}/{stop_date.strftime("%Y-%m-%d")}"

opts = {
    'bbox' : aoi.bounds, 
    'collections': collections,
    'datetime' : date_range,
}

search = catalog.search(**opts)

print("Number of tiles found intersecting given polygon: ", len(list(search.items())))
# -

# Let's parse the results and organize them by the date of acquisition

# +
results_dict = defaultdict(list)

for item in search.items():
    item_dict = item.to_dict()
    item_datetime_str = item_dict['properties']['datetime'].split('T')[0]
    results_dict[item_datetime_str].append(item_dict['assets']['0_B01_WTR']['href'])
# -

# Let's get a sense of how many granules are available for each day of the month. Note, we don't know how many of these tiles contain cloud cover obscuring features of interest yet

# +
granule_count = {}
for key, value in results_dict.items():
    granule_count[datetime.strptime(key, "%Y-%m-%d")] = len(results_dict[key])

fig, ax = plt.subplots(1, 1, figsize=(12, 6))
ax.plot(granule_count.keys(), granule_count.values())
ax.set_title('# of DSWx-HLS granules available / day')
ax.set_xlabel('Day of Month')
ax.set_ylabel('Granule count')
ax.set_xlim([datetime(2024, 3, 1), datetime(2024, 3, 31)])
xlabels = ax.get_xticklabels()
ax.set_xticklabels(xlabels, rotation=45, ha='right')


ax.grid()
# -

# The floods primarily occurred between March 11th and 13th. Let us mosaic and visualize the data for these days

len(x_coords), len(y_coords), merged_array.shape

x_coords[0], x_coords[-1], bounds[0], bounds[2]

(409800.0 - 199980.0)/30.

(bounds[3] - bounds[1])/30

merged_array.shape, bounds

# +
# First, generate a list of files that we would like to mosaic
# specify search window
dates_range = [datetime(year=2024, month=3, day=1) + timedelta(days=i) for i in range(10)]

data_arrays, timesteps = [], []

for key in sorted(results_dict.keys()):
    merged_array, transform = merge(results_dict[key])
    x_res, y_res = abs(transform[0]), abs(transform[4])

    bounds = rasterio.transform.array_bounds(merged_array.shape[-2], merged_array.shape[-1], transform)
    
    x_coords = np.arange(bounds[0], bounds[2], x_res)
    y_coords = np.arange(bounds[1], bounds[3], y_res)
    
    current_timestep = datetime.strptime(key, "%Y-%m-%d")
    
    timesteps.append(current_timestep)
    tmp_xr_da = xr.DataArray(np.squeeze(merged_array), coords={'latitude':y_coords, 'longitude':x_coords})
    data_arrays.append(tmp_xr_da)
# -

concat_array = xr.concat(data_arrays, dim='time')

concat_array['time']= timesteps

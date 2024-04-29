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
# GIS imports
from shapely.geometry import box
from osgeo import gdal
from rasterio.merge import merge
import rasterio

# plotting imports
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import contextily as cx
from rasterio.plot import show
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

# data wrangling imports
import numpy as np

# misc imports
from datetime import datetime, timedelta
from collections import defaultdict

# STAC imports to retrieve cloud data
from pystac_client import Client

# Setting up backend for plotting
# gv.extension('matplotlib')
# gv.extension('bokeh')
# gv.output(size=400)

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

# +
data_arrays, timesteps, transform_list, stacked_array = [], [], [], []

for key in sorted(results_dict.keys()):
    if key not in ['2024-03-01', '2024-03-17', '2024-03-28']:
        continue

    merged_array, transform = merge(results_dict[key])
    transform_list.append(transform)
    stacked_array.append(merged_array)

    current_timestep = datetime.strptime(key, "%Y-%m-%d")
    
    timesteps.append(current_timestep)

stacked_array = np.concatenate(stacked_array, axis=0)

# +
# Load up color maps for visualization
# Pick the first file for the first key available in results_dict
with rasterio.open(results_dict[list(results_dict.keys())[0]][0]) as src:
    colormap = src.colormap(1)
    crs = src.crs

for k, v in colormap.items():
    if k in [1, 2, 252]: # 
        colormap[k] = (0, 0, 255, 255)

    # turn off opacity for not-water/no data
    if k in [0, 255]: # 
        colormap[k] = (0, 0, 0, 0)

    # turn the opacity of all other classes to zero
    # else:
    #     v = list(v)
    #     v[3] = 0
    #     colormap[k] = tuple(v)

cmap = ListedColormap([np.array(colormap[key]) / 255 for key in range(256)])

# +
fig, ax = plt.subplots(1, 3, figsize = (30, 10))

for i in range(3):
    show(stacked_array[i], ax=ax[i], cmap=cmap, transform=transform_list[i], interpolation=None)
    cx.add_basemap(ax[i], crs=crs, zoom=10, source=cx.providers.OpenStreetMap.Mapnik)
    show(stacked_array[i], ax=ax[i], cmap=cmap, transform=transform_list[i], interpolation=None)

    scalebar = AnchoredSizeBar(ax[i].transData,
                            5000, '5 km', 'lower right', 
                            color='black',
                            frameon=False,
                            pad = 0.25,
                            sep=5,
                            fontproperties = {'weight':'semibold', 'size':12},
                            size_vertical=300)

    ax[i].add_artist(scalebar)
    ax[i].ticklabel_format(axis='both', style='scientific',scilimits=(0,0),useOffset=False,useMathText=True)
    ax[i].set_xlabel('UTM easting (meters)')
    ax[i].set_ylabel('UTM northing (meters)')
    ax[i].set_title(f"Water extent on: {timesteps[i].strftime('%Y-%m-%d')}")

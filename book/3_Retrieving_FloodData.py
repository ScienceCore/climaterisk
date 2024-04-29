# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
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

import hvplot.xarray, hvplot.pandas

# data wrangling imports
import numpy as np
import pandas as pd
import xarray as xr

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
date_range = f'{start_date.strftime("%Y-%m-%d")}/{stop_date.strftime("%Y-%m-%d")}'

opts = {
    'bbox' : aoi.bounds, 
    'collections': collections,
    'datetime' : date_range,
}

search = catalog.search(**opts)
# -

results = list(search.items_as_dicts())
print(f"Number of tiles found intersecting given polygon: {len(results)}")

# Let's parse the results and organize them by the date of acquisition

# +
# Look at very first item from search as a dict
results[0]['properties']['datetime']

results[0]['assets']['0_B01_WTR']['href']
# -

# Each element of `results` is a nested dictionary; the particular values we want to pick out from a given `result` are:
# + `result['properties']['datetime']` : timestamp associated with a particular granule; and
# + `result['assets']['0_B01_WTR']['href']` : URI associated with a particular granule
#
# Let's extract these into a Pandas DataFrame for convenience.

times = pd.DatetimeIndex([result['properties']['datetime'] for result in results])
hrefs = {'hrefs': [result['assets']['0_B01_WTR']['href'] for result in results]}

# Construct Pandas DataFrame to summarize granules from search results
granules = pd.DataFrame(index=times, data=hrefs)
granules.index.name = 'times'

len(granules.hrefs.unique()) / len(granules) # Make sure all the hrefs are unique

len(granules.index.unique()) / len(granules) # Notice the timestamps are not all unique, i.e., some are repeated

# Let's get a sense of how many granules are available for each day of the month. Note, we don't know how many of these tiles contain cloud cover obscuring features of interest yet

granules_by_day = granules.resample('1d')  # Grouping by day, i.e., "resampling"

granule_counts = granules_by_day.count() # Aggregating counts

# Ignore the days with no associated granules
granule_counts = granule_counts[granule_counts.hrefs > 0]

# Relabel the index & column of the DataFrame
granule_counts.index.name = 'Day of Month'
granule_counts.rename({'hrefs':'Granule count'}, inplace=True, axis=1)

count_title = '# of DSWx-HLS granules available / day'
granule_counts.hvplot.line(title=count_title,grid=True)

granules_by_day # Recall our earlier resampling by day

# Aggregate all granules by day into a list
granules_by_day = granules_by_day['hrefs'].apply(list)

granules_by_day.head().map(len) # Should match granule_counts from earlier

# The floods primarily occurred between March 11th and 13th. Let us mosaic and visualize the data for these days

# Note: these dates do not agree with the text in the Markdown block above; fix?
dates_of_interest = ['2024-03-01', '2024-03-17', '2024-03-28'] 
granules_by_day.loc[dates_of_interest[-1]]

import xarray as xr
da_list, transform_list = [], []
for date in dates_of_interest:
    merged_array, transform = merge(granules_by_day.loc[date])
    dims = merged_array.shape
    da_list.append( xr.DataArray(data=merged_array,
                                       coords=[('t',[date]), ('x', range(dims[1])), ('y', range(dims[2]))]))
    transform_list.append(transform)

da = xr.concat(da_list, dim='t')

da.hvplot.quadmesh(x='x', y='y', rasterize=True) # First attempt at an hvplot

da.isel(t=2).hvplot.quadmesh(x='x', y='y', rasterize=True) # Second attempt at an hvplot

# Pick the first file for the first key available
first_file = granules_by_day.loc[dates_of_interest[0]][0]
# Load up color maps for visualization
with rasterio.open(first_file) as src:
    colormap = pd.Series(src.colormap(1)) # What does the argument "1" mean here?
    crs = src.crs

blue_bands = [1, 2, 252]
black_bands = [0, 255]
for k in blue_bands:
    colormap.loc[k] = (0,0,255,255)
for k in black_bands:
    colormap.loc[k] = (0,0,0,0)

cmap = ListedColormap([np.array(colormap[key]) / 255 for key in range(256)])

# +
fig, ax = plt.subplots(1, 3, figsize = (30, 10))

for i in range(3):
    show(da.isel(t=i).values, ax=ax[i], cmap=cmap, transform=transform_list[i], interpolation=None)
    cx.add_basemap(ax[i], crs=crs, zoom=10, source=cx.providers.OpenStreetMap.Mapnik)
    show(da.isel(t=i).values, ax=ax[i], cmap=cmap, transform=transform_list[i], interpolation=None)

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
    ax[i].set_title(f"Water extent on: {da.coords['t'].values[i]}")

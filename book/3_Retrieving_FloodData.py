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
# Heavy rains severly impacted Argentina in March 2024 [[1]](https://www.reuters.com/world/americas/argentina-downpour-drenches-crop-fields-flash-floods-buenos-aires-2024-03-12/). The event resulted in flash floods and impacted crop yields, severely impacting the Buenos Aires metropolitan area, and caused significant damage to property and human life. In this notebook, we will retrieve [OPERA DSWx-HLS](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf) data associated to understand the extent of flooding and damage, and compare data from before and after the event.

# +
# Imports for plotting
import geoviews as gv
gv.extension('bokeh')
gv.output(size=400)

import hvplot.xarray, hvplot.pandas
import holoviews as hv
from holoviews.plotting.util import process_cmap
hv.extension('bokeh')

# Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import contextily as cx
from rasterio.plot import show
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar


# +
# GIS imports
from shapely.geometry import box
from osgeo import gdal
from rasterio.merge import merge
import rasterio

# data wrangling imports
import numpy as np
import pandas as pd
import xarray as xr

# misc imports
from datetime import datetime, timedelta

# STAC imports to retrieve cloud data
from pystac_client import Client

# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')
# -

# ## Defining AOI

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

print(f'{type(results)=}')
result = results[0]
print(f'{type(result)=}')
print(result.keys())


# The object `results` retrieved from the search is a list of Python dictionaries; each element of `results` is itself contains other other nested dictionaries. Let's use a [custom function](https://www.slingacademy.com/article/python-how-to-pretty-print-a-deeply-nested-dictionary-basic-and-advanced-examples) modelled on the Python `pprint` library to examins the structure of the results.

# from https://www.slingacademy.com/article/python-how-to-pretty-print-a-deeply-nested-dictionary-basic-and-advanced-examples
def custom_pretty_printer(d, indent=0, maxlen=12):
    "Prints a nested dict, truncating entries to maxlen characters"
    for key, value in d.items():
        print(f"{'    ' * indent}{str(key)}:", end='')
        if isinstance(value, dict):
            print()
            custom_pretty_printer(value, indent+1, maxlen)
        else:
            s = str(value)
            s = s if len(s) < maxlen else f'{s[:maxlen]}...'
            print(f' {s}')


custom_pretty_printer(result, maxlen=30)

# Look at specific keys extracted from the 'properties' & 'assets' keys.
print(result['properties']['datetime'])
print(result['assets']['0_B01_WTR']['href'])

# The particular values we want to pick out from a given `result` are:
# + `result['properties']['datetime']` : timestamp associated with a particular granule; and
# + `result['assets']['0_B01_WTR']['href']` : URI associated with a particular granule (pointing to a TIF file).

# ## Summarizing search results in a DataFrame
#
# Let's extract these particular fields into a Pandas DataFrame for convenience.

times = pd.DatetimeIndex([result['properties']['datetime'] for result in results])
hrefs = {'hrefs': [result['assets']['0_B01_WTR']['href'] for result in results]}

# Construct Pandas DataFrame to summarize granules from search results
granules = pd.DataFrame(index=times, data=hrefs)
granules.index.name = 'times'

len(granules.hrefs.unique()) / len(granules) # Make sure all the hrefs are unique

len(granules.index.unique()) / len(granules) # Notice the timestamps are not all unique, i.e., some are repeated

# Let's get a sense of how many granules are available for each day of the month. Note, we don't know how many of these tiles contain cloud cover obscuring features of interest yet.
#
# The next few lines do some manipulations in Pandas of the DataFrame `granules` to yield a line plot showing what dates are associated with the most granules.

granules_by_day = granules.resample('1d')  # Grouping by day, i.e., "resampling"

granule_counts = granules_by_day.count() # Aggregating counts

# Ignore the days with no associated granules
granule_counts = granule_counts[granule_counts.hrefs > 0]

# Relabel the index & column of the DataFrame
granule_counts.index.name = 'Day of Month'
granule_counts.rename({'hrefs':'Granule count'}, inplace=True, axis=1)

count_title = '# of DSWx-HLS granules available / day'
granule_counts.hvplot.line(title=count_title, grid=True, frame_height=100, frame_width=200)

# The floods primarily occurred between March 11th and 13th. Unfortunately, there are few granules associated with those days.

# ## Generating visualizations
# Let us mosaic using data from days with more data available.

granules_by_day # Recall our earlier resampling by day

# Aggregate all granules by day into a list for each day
granules_by_day = granules_by_day['hrefs'].apply(list)

granules_by_day.head(5).map(len) # Should match granule_counts from earlier

# Note: these dates do not agree with the text in the Markdown block above; fix?
dates_of_interest = ['2024-03-01', '2024-03-17', '2024-03-28']

# The Pandas Series granules_by_day returns a list of URIs for each date; these can be merged into images. 
granules_by_day.loc[dates_of_interest[-1]]

# +
# Assemble DataArray from merged data from those three days.
# This could take some time to download TIF files (within the function rasterio.merge.merge)

# Note: the computation below of x_coords & y_coords may be incorrect; the formulas are inferred from https://rasterio.readthedocs.io/en/latest/quickstart.html.
# It is also possible that they can be computed once outside the loop rather than repeatedly.
da_list, transform_list = [], []
for date in dates_of_interest:
    merged_array, transform = merge(granules_by_day.loc[date])
    dims = merged_array.squeeze().shape
    x_min, y_max = transform * (0,0)
    x_max, y_min = transform * dims
    x_coords = np.linspace(x_min, x_max, dims[0])
    y_coords = np.linspace(y_min, y_max, dims[1])
    da_list.append( xr.DataArray(data=merged_array,
                                       coords=[('t',[date]), ('x', x_coords), ('y', y_coords)]) )
    transform_list.append(transform)
# -

da = xr.concat(da_list, dim='t')

# One interesting observation: the images are stored as 8-bit unsigned integers (i.e., values between 0 and 255).
#
# Although there are 256 possible values, there are only a handful of distinct values in the dynamic range of the numerical data (as we can see by extracting the pixel values into a Pandas Series).

pixel_values = pd.Series(da.values.flatten())
pixel_values.value_counts().sort_index() / len(pixel_values) # fewer than a half dozen distinct pixel values.

# The pixel values 1, 2, & 252 correspond to water; the values 0 & 255 correspond either to land or missing data.
#
# To help visualize the data, we first extract the colormap from one of the granules. We then flag the constraints above by assigning the corresponding pixel values blue or white (to be treated as transparent).

# Pick the first file for the first key available
first_file = granules_by_day.loc[dates_of_interest[0]][0]
# Load up color maps for visualization
with rasterio.open(first_file) as src:
    colormap = src.colormap(1)
    crs = src.crs

# Convert colormap from dict to NumPy array while rescaling values to [0,1]
colormap = np.concatenate([ np.array([colormap[k]]) / 255 for k in colormap ], axis=0)

# Assign the
blue_bands, transparent_bands = [1, 2, 252], [0, 255]
colormap[blue_bands,:] = [0,0,1,1]
colormap[transparent_bands,:] = [0,0,0,0]

colormap = ListedColormap(colormap)

# In Matplotlib, these three time slices can be plotted with the code below.

# +
fig, ax = plt.subplots(1, 3, figsize = (30, 10))

for i in range(3):
    show(da.isel(t=i).values, ax=ax[i], cmap=colormap, transform=transform_list[i], interpolation=None)
# -

# The above plots can be improved with some additional code; it's a little tricky to read.

# +
fig, ax = plt.subplots(1, 3, figsize = (30, 10))

for i in range(3):
    show(da.isel(t=i).values, ax=ax[i], cmap=colormap, transform=transform_list[i], interpolation=None)
    cx.add_basemap(ax[i], crs=crs, zoom=10, source=cx.providers.OpenStreetMap.Mapnik)
    show(da.isel(t=i).values, ax=ax[i], cmap=colormap, transform=transform_list[i], interpolation=None)

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
# -

# Alternatively, the Hvplot library provides ways to plot data directly from Pandas DataFrames or Xarray DataArrays.

cmap = process_cmap(colormap) # Convert Matplotlib colormap into form suitable for Holoviz/Geoviews/Hvplot
da.hvplot.quadmesh(x='x', y='y', colorbar=True, cmap=cmap, aspect='equal',  datashade=True,
                 frame_width=150, frame_height=150, dynamic=True,).opts(xlabel='UTM easting', ylabel='UTM northing', alpha=0.5,)

da.hvplot.quadmesh(x='x', y='y', cmap=cmap, aspect='equal', colorbar=False, datashade=True,
                 frame_width=100, frame_height=100, dynamic=True,).opts(xlabel='UTM easting', ylabel='UTM northing', alpha=1,)

# ---
#
# ## Exercise: Repeat the analysis.
#
# + Specify a region geographic rectangle (suggestions?).
# + Specify a period in time (i.e., a start date and an end date).
# + Use the PySTAC API to retrieve search results.
# + Make a Pandas DataFrame from the results to identify which dates yield the most granules.
# + Pull the relevant TIF files into the notebook session to make a few plots.

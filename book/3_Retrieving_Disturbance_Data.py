# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# The [OPERA DIST-HLS data product](https://lpdaac.usgs.gov/documents/1766/OPERA_DIST_HLS_Product_Specification_V1.pdf) can be used to study the impacts and evolution of wildfires at a large scale. In this notebook, we will retrieve data associated with the [2023 Greece wildfires](`https://en.wikipedia.org/wiki/2023_Greece_wildfire`s) to understand its evolution and extent. We will also generate a time series visualization of the event.
#
# In particular, we will be examining the area around the city of [Alexandroupolis](https://en.wikipedia.org/wiki/Alexandroupolis) which was severely impacted by the wildfires, resulting in loss of lives, property, and forested areas.

# +
# Notebook dependencies
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

import hvplot.xarray
import geoviews as gv
import geopandas as gpd
import holoviews as hv
import panel.widgets as pnw
import datetime
from datetime import datetime

from bokeh.models import FixedTicker
hv.extension('bokeh')

import warnings
warnings.filterwarnings('ignore')

import sys

# GIS imports
from shapely.geometry import Point, box
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

from dist_utils import stack_bands, time_and_area_cube
# -

# ---
# ## **Data Information Input**

# In the code cell below, the user should specify the:
# * Start and end days of interest <br>
# * Date iteration step<br>
# * Data directory<br>
# * Band list<br>
# * Anomaly threshold<br><br>
#
# **<font color='red'>Note: The cell below is the only code in the notebook that should be modified. </font>**
#

# +
# Define data search parameters

# Define AOI as left, bottom, right and top lat/lon extent
aoi = box(22.93945, 40.69742,25.57617, 41.68221)

# We will search data for the month of March 2024
start_date = datetime(year=2023, month=8, day=1)
stop_date = datetime(year=2023, month=9, day=30)

# +
# We open a client instance to search for data, and retrieve relevant data records
STAC_URL = 'https://cmr.earthdata.nasa.gov/stac'

# Setup PySTAC client
# LPCLOUD refers to the LP DAAC cloud environment that hosts earth observation data
catalog = Client.open(f'{STAC_URL}/LPCLOUD/') 

collections = ["OPERA_L3_DIST-ALERT-HLS_V1"]

# We would like to search data for August-September 2023
date_range = f'{start_date.strftime("%Y-%m-%d")}/{stop_date.strftime("%Y-%m-%d")}'

opts = {
    'bbox' : aoi.bounds, 
    'collections': collections,
    'datetime' : date_range,
}

search = catalog.search(**opts)
# -

# NOTE: The OPERA DIST data product is hosted on [LP DAAC](https://lpdaac.usgs.gov/news/lp-daac-releases-opera-land-surface-disturbance-alert-version-1-data-product/), and this is specified when setting up the PySTAC client to search their catalog of data products in the above code cell.

results = list(search.items_as_dicts())
print(f"Number of tiles found intersecting given AOI: {len(results)}")

# Let's load the search results into a pandas dataframe

# +
times = pd.DatetimeIndex([result['properties']['datetime'] for result in results]) # parse of timestamp for each result
hrefs = {'hrefs': [value['href'] for result in results for key, value in result['assets'].items() if 'VEG-DIST-STATUS' in key]} # parse out links only to DIST-STATUS data layer

# # Construct pandas dataframe to summarize granules from search results
granules = pd.DataFrame(index=times, data=hrefs)
granules.index.name = 'times'
# -

# **Layer Values:**
# * **0:** No disturbance<br>
# * **1:** Provisional (**first detection**) Disturbance with vegetation cover change <50% <br>
# * **2:** Confirmed (**recurrent detection**) Disturbance with vegetation cover change < 50% <br> 
# * **3:** Provisional Disturbance with vegetation cover change ≥ 50% <br>
# * **4:** Confirmed Disturbance with vegetation cover change ≥ 50%  <br> 

# ---
# ## **Summary** 
# In this Jupyter notebook, we showcase how end-users can leverage the **OPERA Land Surface Disturbance (DIST)** product **to interactively visualize the evolution and calculate the extent of a wildfire**.
# <br>
# ***

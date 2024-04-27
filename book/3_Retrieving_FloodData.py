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
# Heavy rains severly impacted Argentina in March 2024 [1](https://www.reuters.com/world/americas/argentina-downpour-drenches-crop-fields-flash-floods-buenos-aires-2024-03-12/). The event resulted in flash floods and impacted crop yields, severely impacting the Buenos Aires metropolitan area, and caused significant damage to property and human life. In this notebook, we will retrieve OPERA DSWx-HLS data associated to understand the extent of flooding and damage, and compare data from before and after the event.

# +
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from shapely.geometry import box
from osgeo import gdal
from pystac_client import Client

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

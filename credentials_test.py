# minimum test needed to see if credentials are set correctly to download data from NASA Earthdata
# Users need to have a .netrc file in their home directory with valid credentials for this script to work

from pystac_client import Client
from datetime import datetime
from shapely.geometry import Point
import rasterio
from osgeo import gdal
import warnings

# suppress PySTAC warnings
warnings.filterwarnings("ignore")

# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')

STAC_URL = 'https://cmr.earthdata.nasa.gov/stac'

catalog = Client.open(f'{STAC_URL}/POCLOUD/') 

# Setup PySTAC client
provider_cat = Client.open(STAC_URL)
catalog = Client.open(f'{STAC_URL}/POCLOUD/')
collections = ["OPERA_L3_DSWX-HLS_V1"]

start_date = datetime(year=2024, month=4, day=30)
stop_date = datetime(year=2024, month=5, day=31)
livingston_tx = Point(-95.09, 30.69)
date_range = f'{start_date.strftime("%Y-%m-%d")}/{stop_date.strftime("%Y-%m-%d")}'

opts = {
    'bbox' : livingston_tx.buffer(0.01).bounds, 
    'collections': collections,
    'datetime' : date_range,
}

# Execute the search
print("Testing PySTAC search ..")
search = catalog.search(**opts)
results = list(search.items_as_dicts())
print(f"Search succesful, accessing test data ..")

test_href = results[0]['assets']['0_B01_WTR']['href']

try:
    with rasterio.open(test_href) as ds:
        _ = ds.profile
        print("Success! Your credentials file is correctly configured!")
except:
    print("Could not access data, ensure that the .netrc file exists in the user home directory and contains valid NASA Earthdata credentials")
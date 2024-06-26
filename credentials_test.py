# Minimal test to verify NASA Earthdata credentials for downloading data products.
# Requires a .netrc file in home directory containing valid credentials.

import osgeo.gdal, rasterio
from pystac_client import Client
from warnings import filterwarnings
filterwarnings("ignore") # suppress PySTAC warnings

# Mandatory GDAL setup for accessing cloud data
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
osgeo.gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')

# Define AOI (Area-Of-Interest) & time-window
livingston_tx, delta = (-95.09, 30.69), 0.1
aoi = tuple(coord + sgn*delta for sgn in (-1,+1) for coord in livingston_tx)
time_window =  '2024-04-30/2024-05-31'

# Prepare PySTAC client
STAC_URL, collections = 'https://cmr.earthdata.nasa.gov/stac', ["OPERA_L3_DSWX-HLS_V1"]
catalog = Client.open(f'{STAC_URL}/POCLOUD/')

print("Testing PySTAC search...")
opts = dict(bbox=aoi, collections=collections, datetime=time_window)
results = list(catalog.search(**opts).items_as_dicts())
test_uri = results[0]['assets']['0_B01_WTR']['href']

try:
    print(f"Search successful, accessing test data...")
    with rasterio.open(test_uri) as ds: _ = ds.profile
    print("Success! Your credentials file is correctly configured!")
except:
    print(f"Could not access NASA EarthData asset: {test_uri}")
    print("Ensure that a .netrc file containing valid NASA Earthdata credentials exists in the user home directory.")

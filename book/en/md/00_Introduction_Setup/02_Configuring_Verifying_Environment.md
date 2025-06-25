---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Configuring & Verifying the Environment

<!-- #region jupyter={"source_hidden": true} -->
For this notebook, you need to know your NASA Earthdata credentials (i.e., your associated username and password).

+ First, you will construct a file called `.netrc` in your home folder (i.e., `~/.netrc`) that contains those credentials.
+ Next, you will execute a test that verifies the configuration.

The following executable cell defines some Python functions to invoke later (importing relevant Python utilities as needed).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
from pathlib import Path
from getpass import getpass
import osgeo.gdal
import rasterio
from pystac_client import Client
from warnings import filterwarnings
filterwarnings("ignore") # suppress PySTAC warnings
# Mandatory GDAL setup for accessing cloud data
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
osgeo.gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')

def create_netrc(PATH):
    "Creates netrc file at PATH by prompting interactive user input."
    PATH.unlink(missing_ok=True)
    TEMPLATE = " ".join(["machine", "urs.earthdata.nasa.gov", "login",
                     "{USERNAME}", "password", "{PASSWORD}\n"])
    username = input("NASA EarthData login:    ")
    password = getpass(prompt="NASA EarthData password: ")
    print('Writing .netrc file.')
    PATH.write_text(TEMPLATE.format(USERNAME=username, PASSWORD=password))
    PATH.chmod(0o600)
    return None

def define_options():
    "Creates URL & dictionary of options required for executing a PySTAC search."
    # Define AOI (Area-Of-Interest) & time-window
    livingston_tx, delta = (-95.09, 30.69), 0.1
    AOI = tuple(coord + sgn*delta for sgn in (-1,+1) for coord in livingston_tx)
    start, stop = '2024-04-30', '2024-05-05'
    WINDOW = f'{start}/{stop}'
    URL = 'https://cmr.earthdata.nasa.gov/stac'
    PROVIDER = 'POCLOUD'
    COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
    AOI_string = f"({', '.join([f'{coord:.2f}' for coord in AOI])})"
    print(f"\nDefined AOI={AOI_string}\n        {WINDOW=}")
    print(f"        {COLLECTIONS=}\n        {PROVIDER=}\n")
    return URL, PROVIDER, dict(bbox=AOI, collections=COLLECTIONS, datetime=WINDOW)

def execute_search(STAC_URL, PROVIDER, opts):
    "Executes a STAC search using required parameters"
    # Prepare PySTAC client
    catalog = Client.open(f'{STAC_URL}/{PROVIDER}/')
    results = list(catalog.search(**opts).items_as_dicts())
    return results

def process_uri(URI):
    "Given a URI associated with a remote GeoTIFF file, attempt to open & parse it."
    with rasterio.open(URI) as ds:
        _ = ds.profile
    return None

def test_netrc():
    """Minimal test to verify NASA Earthdata credentials for downloading data products.
    Requires a .netrc file in home directory containing valid credentials."""
    STAC_URL, PROVIDER, opts = define_options()
    try:
        results = execute_search(STAC_URL, PROVIDER, opts)
        print(f"Retrieved {len(results)} search results...")
        test_uri = results[0]['assets']['0_B01_WTR']['href']
        print(f"Search successful. Accessing test data...\n")
        process_uri(test_uri)
    except (IndexError, KeyError) as e:
        print(f"{results}\n")
        raise e
    except rasterio.RasterioIOError as e:
        print(e)
        raise e
    return None
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Configuring the Cloud Environment to Access NASA EarthData from Python

<!-- #region jupyter={"source_hidden": true} -->
To access NASA's EarthData products from Python programs or Jupyter notebooks, it is necessary to save your NASA EarthData credentials in a special file called `.netrc`. Executing the cell below creates this file.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
NETRC_PATH = Path('~/.netrc').expanduser()
print("Warning: Executing the rest of this cell will overwrite any pre-existing .netrc file.")
overwrite = input("Confirm that you want to proceed? (Y/N).")
if overwrite.lower() in ['y', 'yes']:
    create_netrc(NETRC_PATH)
else:
    print('Skipping writing of .netrc file.')
```

<!-- #region jupyter={"source_hidden": true} -->
Some caveats:

+ You will be asked whether or not to delete any pre-existing file.
    + If yes, you will be prompted for your *NASA Earthdata* username & then your corresponding password.
    + If no, 

+ Executing the cell above yields a prompt that asks permission to overwrite the file `.netrc` if it exists already. Choose `y` or `yes` only if you are comfortable with deleting any credentials stored within that file.
+ Should you choose to create the `.netrc` file, you will be prompted for your NASA EarthData username & password. Make sure to have these ready before executing the cell above.
+ As an alternative, you could use a text editor to create the file `.netrc` with content as follows:
   ```
   machine urs.earthdata.nasa.gov login USERNAME password PASSWORD
   ```
   Of course, you would replace `USERNAME` and `PASSWORD` in your actual `.netrc` file with your actual NASA EarthData account details.
+ Once the `.netrc` file is saved with your correct credentials, it's good practice to restrict access to the file:
   ```bash
   $ chmod 600 ~/.netrc
   ```
  This is achieved in the second last line of the function `create_netrc` (i.e., `PATH.chmod(0o600)`).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Verifying Access to NASA EarthData Products

<!-- #region jupyter={"source_hidden": true} -->
The file `.netrc` is required to access STACs (Spatio-Temporal Asset Catalogs) within Python programs using [PySTAC](https://pystac.readthedocs.io/en/stable/)).

To make sure everything is working properly, execute the Python cell below:
<!-- #endregion -->

```python jupyter={"source_hidden": true}
if ((not NETRC_PATH.exists()) or (NETRC_PATH.stat().st_size==0)):
    print("Warning: no valid .netrc file exists; re-execute this cell to create one with correct credentials.")
else:
    try:
        test_netrc()
        print("Success! Your credentials file ~/.netrc is correctly configured!\n")
    except Exception as e:
        print(f"TEST FAILED.")
        print("\n\nEnsure that a .netrc file containing valid NASA Earthdata credentials exists in the user home directory.\n")
```

<!-- #region jupyter={"source_hidden": true} -->
If the preceding cell executed smoothly, you will see a message indication success:
```bash
Success! Your credentials file ~/.netrc is correctly configured!
```
In this case, you're done! You now have everything you need to explore NASA's Earth observation data through the EarthData portal!
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
If you see the message 
```bash
Ensure that a .netrc file containing valid NASA Earthdata credentials exists in the user home directory.
```
you will need to enter your correct credentials into the file `~/.netrc`. You can do so by restarting and re-executing this notebook (or by editing the file with a text editor).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

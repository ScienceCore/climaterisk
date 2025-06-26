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

# Configuración y Verificación del Entorno

<!-- #region jupyter={"source_hidden": true} -->
Necesita conocer sus credenciales de NASA Earthdata para usar este cuaderno (es decir, su nombre de usuario y contraseña asociados).

+ Primero, construirá un archivo llamado `.netrc` en la carpeta de inicio (es decir, `~/.netrc`) que contiene esas credenciales.
+ A continuación, ejecutará una prueba que verifica la configuración.

LLa siguiente celda ejecutable define algunas funciones de Python para invocar más adelante (importando utilidades de Python relevantes según sea necesario).
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

## Configuración del entorno en la nube para acceder a NASA EarthData desde Python

<!-- #region jupyter={"source_hidden": true} -->
Para acceder a los productos EarthData de la NASA desde programas Python o cuadernos Jupyter, es necesario guardar sus credenciales de NASA EarthData en un archivo especial llamado `.netrc`. Al ejecutar la celda de abajo, se crea este archivo.
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
Algunas advertencias:

+ Se le preguntará si desea eliminar o no cualquier archivo preexistente.
    + En caso afirmativo, se le pedirá su nombre de usuario de *NASA Earthdata* y luego su contraseña correspondiente.
    + Si la respuesta es no, no se realiza ninguna acción.
+ Al ejecutar la celda de arriba, se produce un mensaje que pide permiso para sobrescribir el archivo `.netrc` si ya existe. Elija `y` o `yes` solo si se siente cómodo con la eliminación de las credenciales almacenadas en ese archivo.
+ Si elige crear el archivo `.netrc`, se le solicitará su nombre de usuario y contraseña de NASA EarthData. Asegúrese de tenerlos listos antes de ejecutar la celda de arriba.
+ Como alternativa, puede utilizar un editor de texto para crear el archivo`.netrc` con el siguiente contenido:
   ```
   machine urs.earthdata.nasa.gov login USERNAME password PASSWORD
   ```
   Por supuesto, reemplazaría `USERNAME` y `PASSWORD` en su archivo `.netrc` real con los detalles de su cuenta de NASA EarthData.
+ Una vez que el archivo `.netrc` se guarda con sus credenciales correctas, es una buena práctica restringir el acceso al archivo:
   ```bash
   $ chmod 600 ~/.netrc
   ```
   Esto se logra en la penúltima línea de la función `create_netrc` (es decir, `PATH.chmod(0o600)`).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Verificación del Acceso a los Productos de NASA EarthData

<!-- #region jupyter={"source_hidden": true} -->
El archivo `.netrc` es necesario para acceder a los STAC (Catálogos de Activos Espacio-Temporales) dentro de los programas de Python que utilizan [PySTAC](https://pystac.readthedocs.io/en/stable/)).

Para asegurarse de que todo funciona correctamente, ejecute la siguiente celda de Python:
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
Si la celda anterior se ejecutó sin problemas, verá un mensaje que indica que se ha realizado correctamente:
```bash
Success! Your credentials file ~/.netrc is correctly configured!
```
En este caso, ¡ya está! ¡Ahora tienes todo lo que necesitas para explorar los datos de observación de la Tierra de la NASA a través del portal EarthData!
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
Si ve el mensaje
```bash
Ensure that a .netrc file containing valid NASA Earthdata credentials exists in the user home directory.
```
deberá ingresar sus credenciales correctas en el archivo `~/.netrc`. Puede hacerlo reiniciando y volviendo a ejecutar este bloc de notas (o editando el archivo con un editor de texto).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

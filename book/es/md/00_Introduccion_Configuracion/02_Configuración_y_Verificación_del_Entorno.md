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
Necesitas conocer tus credenciales de NASA Earthdata para usar este cuaderno computacional (es decir, tu nombre de usuario y contraseña asociados).

Ejecutar esta notebook te permitirá:
+ Primero, construir un archivo llamado `.netrc` en la carpeta de inicio (es decir, `~/.netrc`) que contiene esas credenciales.
+ Segundo, ejecutar una prueba que verifica que la configuración se haya realizado de forma correcta.

La siguiente celda ejecutable define algunas funciones de Python que se utilizaran más adelante para importar las utilidades necesarias.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
from pathlib import Path
from getpass import getpass
import osgeo.gdal
import rasterio
from pystac_client import Client
from warnings import filterwarnings
filterwarnings("ignore") # suprimir advertencias de PySTAC
NETRC_PATH = Path('~/.netrc').expanduser()

# Configuración obligatoria de GDAL para acceder a datos en la nube
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.gdal_cookies.txt')
osgeo.gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
osgeo.gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')

def create_netrc(PATH):
    """Genera un archivo netrc en la ruta indicada (PATH) solicitando al
    usuario que ingrese sus credenciales de forma interactiva."""
    PATH.unlink(missing_ok=True)
    TEMPLATE = " ".join(["machine", "urs.earthdata.nasa.gov", "login",
                     "{USERNAME}", "password", "{PASSWORD}\n"])
    username = input("NASA Earthdata login:    ")
    password = getpass(prompt="NASA Earthdata password: ")
    print('Escribir archivo .netrc')
    PATH.write_text(TEMPLATE.format(USERNAME=username, PASSWORD=password))
    PATH.chmod(0o600)
    return None

def define_options():
    "Crea una URL y un diccionario de opciones necesarios para ejecutar una búsqueda con PySTAC."
    # Definir el área de interés (AOI) y el rango temporal
    livingston_tx, delta = (-95.09, 30.69), 0.1
    AOI = tuple(coord + sgn*delta for sgn in (-1,+1) for coord in livingston_tx)
    start, stop = '2024-04-30', '2024-05-05'
    WINDOW = f'{start}/{stop}'
    URL = 'https://cmr.earthdata.nasa.gov/stac'
    PROVIDER = 'POCLOUD'
    COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
    AOI_string = f"({', '.join([f'{coord:.2f}' for coord in AOI])})"
    print(f"\nCriterios de búsqueda:\nAOI={AOI_string}\n{WINDOW=}")
    print(f"{COLLECTIONS=}\n{PROVIDER=}\n")
    return URL, PROVIDER, dict(bbox=AOI, collections=COLLECTIONS, datetime=WINDOW)

def execute_search(STAC_URL, PROVIDER, opts):
    "Ejecuta una búsqueda STAC utilizando los parámetros requeridos"
    # Preparar el cliente de PySTAC
    catalog = Client.open(f'{STAC_URL}/{PROVIDER}/')
    results = list(catalog.search(**opts).items_as_dicts())
    return results

def process_uri(URI):
    "Dada una URI asociada a un archivo GeoTIFF remoto, intenta abrirlo y analizar su contenido."
    with rasterio.open(URI) as ds:
        _ = ds.profile
    return None

def test_netrc():
    """Prueba mínima para verificar las credenciales de NASA Earthdata necesarias
    para descargar productos de datos. Requiere un archivo .netrc en el directorio
    personal con credenciales válidas."""
    STAC_URL, PROVIDER, opts = define_options()
    try:
        results = execute_search(STAC_URL, PROVIDER, opts)
        print(f"Identificados {len(results)} resultados de búsqueda...")
        test_uri = results[0]['assets']['0_B01_WTR']['href']
        print(f"Intentar acceder a un archivo remoto...\n")
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

## Configuración del entorno en la nube para acceder a NASA Earthdata desde Python

<!-- #region jupyter={"source_hidden": true} -->
Para acceder a los productos Earthdata de la NASA desde programas Python o cuadernos computacionales Jupyter, es necesario guardar tus credenciales de NASA Earthdata en un archivo especial llamado `.netrc`. 

Al ejecutar la celda de abajo:
+ Se te mostrará una advertencia indicando que ejecutar el resto de esta celda sobrescribirá cualquier archivo .netrc existente.
+ Se te pedirá que confirmes si deseas continuar:
    + En caso afirmativo, escribe `s` o `si`: se te pedirá tu nombre de usuario de *NASA Earthdata* y luego tu contraseña. Asegúrate de tenerlos listos antes de ejecutar la celda.
    + Si la respuesta es no, no se realizará ninguna acción.

**¡Importante!**
+ Elige `s` o `si` solo si te sientes cómodo con la eliminación de las credenciales almacenadas en el archivo `.netrc`. Recuerda tener disponible tu nombre de usuario y tu contraseña de NASA Earthdata. 
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print("Advertencia: Ejecutar el resto de esta celda sobrescribirá cualquier archivo .netrc existente.")
overwrite = input("¿Confirmás que querés continuar? (S/N).")
if overwrite.lower() in ['s', 'si', 'sí']:
    create_netrc(NETRC_PATH)
else:
    print('Se omite la escritura del archivo .netrc.')
```

<!-- #region jupyter={"source_hidden": true} -->
Como alternativa, puede utilizar un editor de texto para crear el archivo`.netrc` con el siguiente contenido:
```
machine urs.earthdata.nasa.gov login USERNAME password PASSWORD
```
Por supuesto, debes reemplazar `USERNAME` y `PASSWORD` en tu archivo `.netrc` real con los detalles de tu cuenta de NASA Earthdata.
   
Una vez que el archivo `.netrc` se guarda con sus credenciales correctas, es una buena práctica restringir el acceso al mismo:
```bash
$ chmod 600 ~/.netrc
```
Esto se logra en la penúltima línea de la función `create_netrc` (es decir, `PATH.chmod(0o600)`).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Verificación del Acceso a los Productos de NASA Earthdata

<!-- #region jupyter={"source_hidden": true} -->
El archivo `.netrc` es necesario para acceder a los STAC (Catálogos de Activos Espacio-Temporales) dentro de los programas de Python que utilizan [PySTAC](https://pystac.readthedocs.io/en/stable/)).

Para asegurarte de que todo funciona correctamente, ejecuta la siguiente celda de Python. Si la celda se ejecuta sin problemas, verás un mensaje que indica que las credenciales se han configurado correctamente:

```bash
¡Éxito! ¡Tu archivo de credenciales ~/.netrc está configurado correctamente!
```
En este caso, ¡ya está! ¡Ahora tienes todo lo que necesitas para explorar los datos de observación de la Tierra provistos por la NASA a través del portal Earthdata!

<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
Si, en cambio, ves el mensaje:

```bash
Asegurate que el archivo .netrc contiene credenciales de NASA Earthdata que existen en el directorio de inicio del usuario.
```
deberás ingresar tus credenciales correctas en el archivo `~/.netrc`. Puedes hacerlo reiniciando y volviendo a ejecutar este cuaderno computacional o editando el archivo con un editor de texto.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
Entonces, ejecuta la siguiente celda para verificar la creación del archivo `~/.netrc` con las credenciales correctas:
<!-- #endregion -->

```python jupyter={"source_hidden": true}
if ((not NETRC_PATH.exists()) or (NETRC_PATH.stat().st_size==0)):
    print("Advertencia: no existe un archivo .netrc válido; ejecuta esta celda nuevamente para crear uno con credenciales correctas.")
else:
    try:
        test_netrc()
        print("¡Éxito! ¡Tu archivo de credenciales ~/.netrc está configurado correctamente!\n")
    except Exception as e:
        print(f"LA PRUEBA FALLÓ")
        print("\n\nAsegurate que el archivo .netrc contiene credenciales de NASA Earthdata que existen en el directorio de inicio del usuario.\n")
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

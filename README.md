# [EN] NASA TOPS-T Reproducibly Analyzing Wildfire, Drought, and Flood Risk with NASA Earthdata Cloud

![banner](book/assets/img/banner.jpg)

Using NASA Earthdata Cloud data to assess the risk of wildfire, drought, and flood.

## Usage

### Building the book

If you'd like to develop and/or build the NASA TOPS-T Reproducibly Analyzing Wildfire, Drought, and Flood Risk with NASA Earthdata Cloud book, then in a terminal you should:

1. Clone this repository
1. Run `pip install -r requirements.txt` (it is recommended you do this within a virtual environment)
1. (Optional) Edit the books source files located in the `book/` directory
1. Change to the `book` directory with `cd book/`
1. Run `myst start` to remove any existing builds
1. Run `myst build --html` to build HTML version of book

A fully-rendered HTML version of the book will be built in `book/_build/html/`.

### Hosting the book

Please see the [MyST documentation](https://mystmd.org/guide/deployment) to discover options for deploying a book online using services such as GitHub.

## Contributors

We welcome and recognize all contributions. You can see a list of current contributors in the [contributors tab](https://github.com/ScienceCore/climaterisk/graphs/contributors).

## Credits

This project is created using the excellent open source [MyST MD](https://mystmd.org) and is funded by NASA Transform to Open Science Training or “TOPST”, Research Opportunities in Space and Earth Science [(ROSES) solicitation F.14](https://nspires.nasaprs.com/external/viewrepositorydocument/cmdocumentid=860824/solicitationId=%7BAB776446-03A8-4C24-845D-2E5A2ADA2D5A%7D/viewSolicitationDocument=1/F.14_TOPST_Amend46.pdf).

---------------------------

# [ES] NASA TOPS-T: Análisis reproducible del riesgo de incendios forestales, sequía e inundaciones con NASA Earthdata Cloud

Uso de datos de NASA Earthdata Cloud para evaluar el riesgo de incendios forestales, sequías e inundaciones.

## Uso

### Para compilar el libro

Si quieres desarrollar y/o compilar el libro **NASA TOPS-T: Análisis reproducible del riesgo de incendios forestales, sequía e inundaciones con NASA Earthdata Cloud**, abre una terminal y:

1. Clona este repositorio
1. Ejecuta `pip install -r requirements.txt` (se recomienda hacerlo dentro de un entorno virtual)
1. (Opcional) Edita los archivos fuente del libro ubicados en el directorio `book/`
1. Navega al directorio `book` con `cd book/`
1. Ejecuta `myst start` para eliminar cualquier build previo
1. Ejecuta `myst build --html` para generar lla versión HTML del libro

Una versión HTML completamente renderizada del libro se generará en `book/_build/html/`.

#### Publicar el libro

Consultá la documentación de [MyST documentation](https://mystmd.org/guide/deployment) para conocer las opciones de publicar en línea (por ejemplo, con GitHub).

### Para ejecutar las notebooks de forma local

Usa esta sección si quieres ejecutar los cuadernos computacionales (notebooks) en tu máquina para explorar los ejemplos de forma interactiva.  
Requiere tener Git, Anaconda/Miniconda y Jupyter instalados. También requiere crear una cuenta en [NASA Earthdata](https://urs.earthdata.nasa.gov/) y tener las credenciales (usuario y contraseña) a mano.

1. Abre una terminal (ej. Bash o Anaconda Prompt).
2. Clona el repositorio y navega hasta el.

```bash
git clone https://github.com/ScienceCore/climaterisk.git
cd climaterisk
```

3. Crea y activa el entorno.

```bash
conda env create -f environment.yml -n climaterisk
conda activate climaterisk
```

4. (Opcional) Si te encuentras con un problema de memoria o del solucionador (solver), prueba:

```bash
conda update -n base -c conda-forge conda
conda config --set solver libmamba
conda env create -f environment.yml -n climaterisk
```

5. Abre JupyterLab

```bash
jupyter lab
```
En JupyterLab, abre la notebook `startup.ipynb` ubicada en la carpeta `book` y ejecuta todas las celdas para generar las notebooks reestantes.

6. Credenciales de NASA Earthdata para los casos de estudio

Para trabajar con las notebooks que usan datos de NASA Earthdata Cloud, ejecuta todas las celdas de la notebook `02_Configuración_y_Verificación_del_Entorno.md` ubicada en `book/es/ipynb/00_Introduccion_Configuracion/`.
Acepta sobrescribir el archivo `.netrc` e ingresá tu `usuario` y `contraseña` de [NASA Earthdata](https://urs.earthdata.nasa.gov/) cuando se solicite.

### Personas colaboradoras

Agradecemos y reconocemos todas las contribuciones. Podés ver la lista de personas colaboradoras actuales en la [pestaña de colaboradores](https://github.com/ScienceCore/climaterisk/graphs/contributors).

Créditos

Este proyecto fue creado con el software de código abierto [MyST MD](https://mystmd.org) y cuenta con financiamiento del programa Transform to Open Science Training (TOPST) de la NASA, en el marco de Research Opportunities in Space and Earth Science [(ROSES) solicitation F.14](https://nspires.nasaprs.com/external/viewrepositorydocument/cmdocumentid=860824/solicitationId=%7BAB776446-03A8-4C24-845D-2E5A2ADA2D5A%7D/viewSolicitationDocument=1/F.14_TOPST_Amend46.pdf).

# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: base
#     language: python
#     name: python3
# ---

# + [markdown] slideshow={"slide_type": "slide"}
# # Primeros pasos
# ## Configuración del Hub de 2i2c y las credenciales de EarthData
#
# <div style="display: flex; align-items: center;">
#     <img src="TOPS.png" alt="Image" style="width: 100px; height: auto; margin-right: 10px;">
#     <h3>ScienceCore:<br>Climate Risk</h3>
# </div>
#
#
#

# + [markdown] slideshow={"slide_type": "notes"}
# En esta sección, encontrarás información sobre como configurar tu cuenta del Hub de 2i2c y tus credenciales de EarthData. Ambas cosas son necesarias para poder completar los siguientes módulos. 

# + [markdown] slideshow={"slide_type": "slide"}
# ## Conectate al Hub de 2i2c
#
# - Servicio colaborativo en la nube para comunidades en investigación y educación. 
# - Conectate al Hub siguiendo este link: https://showcase.2i2c.cloud/hub/login
#

# + [markdown] slideshow={"slide_type": "notes"}
# El Hub de 2i2c es un servicio en la nube colaborativo para comunidades en investigación y educación. 
# Las clases que encontrarás en los módulos de este Jupyter book, están pensadas para ejecutarse en el hub de 2i2c. 
#

# + [markdown] slideshow={"slide_type": "slide"}
# ## NASA EarthData
#
# - Plataforma diseñada para facilitar el acceso y uso de datos de ciencias de la Tierra (imágenes, observaciones satelitales, datos climáticos y mediciones ambientales).
# - Acceso abierto y gratuito. 
#

# + [markdown] slideshow={"slide_type": "notes"}
# El programa de Sistemas de Datos de Ciencias de la Tierra de la NASA supervisa el ciclo de vida de los datos de ciencias de la Tierra de la NASA de todas sus misiones de Observación de la Tierra — desde la adquisición hasta el procesamiento y la distribución.
#
# La plataforma Earthdata está diseñada para facilitar el descubrimiento, acceso y uso de datos de ciencias de la Tierra para fines de investigación, aplicaciones y toma de decisiones. Proporciona datos en varios formatos, incluidas imágenes, observaciones satelitales, datos climáticos y mediciones ambientales, entre otros.
#
# El sitio web de NASA Earthdata es el punto de partida para el acceso completo y abierto a las colecciones de datos de ciencias de la Tierra de la NASA, que se proporcionan de forma gratuita para acelerar el avance científico en beneficio de la sociedad. 

# + [markdown] slideshow={"slide_type": "slide"}
# ## Crea las credenciales de EarthData
#
# - Página para registrarte: https://urs.earthdata.nasa.gov/home
# - Tutorial: https://urs.earthdata.nasa.gov/documentation/for_users/how_to_register
# - ¡Importante! Recuerda guardar tu **usuario** y **contraseña**, ¡lo necesitarás más adelante! 

# + [markdown] slideshow={"slide_type": "notes"}
# Para acceder a los datos a través de este portal, se requiere que los usuarios configuren credenciales de inicio de sesión.
# Debes registrarte en este link: https://urs.earthdata.nasa.gov/home
# Puedes encontrar un tutorial sobre como hacerlo en este link: https://urs.earthdata.nasa.gov/documentation/for_users/how_to_register
# Asegúrate de recordar el nombre de usuario y la contraseña que configures en este paso, ya que los necesitarás en el paso siguiente. 
#
#

# + [markdown] slideshow={"slide_type": "slide"}
# ## Accede a EarthData desde Python
#
# - Almacena las credenciales creadas en un archivo. 
# - Utiliza el archivo `.netrc` provisto en este repositorio, incluyendo tus datos en la siguiente línea:
#
# machine urs.earthdata.nasa.gov login **{username}** password **{password}**
#
# - Guarda los cambios y cierra el archivo. 

# + [markdown] slideshow={"slide_type": "notes"}
# Para acceder con éxito a los datos de la NASA utilizando Python y Jupyter notebooks, necesitas almacenar las credenciales de inicio de sesión en un archivo. 
# En el repositorio de este proyecto, se proporciona un archivo .netrc donde los usuarios puedes ingresar tus credenciales.
#
# Abre el archivo .netrc y edita donde dice usuario y contraseña, reemplazándolos por el usuario y la contraseña que creaste el paso anterior. 
#
# Guarda los cambios y cierra el archivo. ¡Ahora estás listo para acceder a los datos de Observación de la Tierra a través del portal de Earthdata!
#
#

# + [markdown] slideshow={"slide_type": "slide"}
# ## Actividad 1
#
# Ejecuta la notebook `1_Getting_Started.ipynb` para obtener la siguiente imagen:
#
# ![Setup1](SETUP1.png)

# + [markdown] slideshow={"slide_type": "slide"}
# ## Live coding: Vamos a la notebook `1_Getting_Started.ipynb`

# + [markdown] slideshow={"slide_type": "notes"}
# Para asegurarte de que tus credenciales estén configuradas correctamente y funcionando, puedes ejecutar la Jupyter notebook titulada 1_Getting_Started.ipynb. 

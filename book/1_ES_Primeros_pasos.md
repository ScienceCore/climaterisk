# Primeros pasos

## ¿Cómo utilizar el hub de 2i2c?

Para acceder al 2i2c Hub seguí estos sencillos pasos:
* Accede al [Hub de 2i2c](https://showcase.2i2c.cloud/hub/login)
* Introduce tus credenciales: Ingresa tu nombre de usuario y contraseña del 2i2c Hub

## ¿Cómo acceder a los datos disponibles en el sitio Earthdata de la NASA?

El programa **Earth Science Data Systems (ESDS)**, **Programa de Sistemas de Datos de Ciencias de la Tierra** de la NASA, supervisa el ciclo de vida de los datos científicos de la Tierra de todas sus misiones de observación de la Tierra, desde su adquisición hasta su procesamiento y distribución.

A los efectos de esta guía, el sitio web Earthdata de la NASA es el punto de entrada que permite acceder de manera completa, gratuita y abierta a las colecciones de datos de ciencias de la Tierra de la NASA, con el fin de acelerar el avance científico en beneficio de la sociedad. Para acceder a los datos a través de este portal, los usuarios deben definir primero sus credenciales de acceso.

 Para crear una cuenta en EarthData, sigue el siguiente[tutorial], el cual te guíara paso a paso. Como sugerencia, elige un *nombre de usuario* y *contraseña* que recuerdes bien, ya que los necesitarás más adelante.
Ahora viene la parte técnica: para acceder a los datos desde programas de Python y Jupyter notebooks, es necesario guardar las credenciales (de EarthData) en un archivo especial.  En este repositorio encontrarás un archivo llamado "`.netrc`" con un ejemplo (puedes pensar en él como una plantilla). Abre ese archivo y edita la siguiente línea:

`machine urs.earthdata.nasa.gov login {tu_nombre_de_usuario} password {tu_contraseña}`

Reemplaza "`{tu_nombre_de_usuario`}" y "`{tu_contraseña}`" con los datos de tu cuenta. Luego, guarda el archivo y ¡listo!  Ya tienes todo lo necesario para acceder a los datos de observación de la Tierra a través del portal de EarthData. ️
Por último, para asegurarte de que todo funciona correctamente, abre la notebook titulada "1_primeros_pasos.ipynb" y sigue las indicaciones. ¡Con esto ya podrás explorar el mundo de los datos de la NASA!





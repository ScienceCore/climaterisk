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

# Uso del Hub de 2i2c

<!-- #region jupyter={"source_hidden": true} -->
Este cuaderno computacional contiene las instrucciones para iniciar sesión en la nube con ([JupyterHub](https://jupyter.org/hub)) plataforma proporcionada por [2i2c](https://2i2c.org) para este tutorial.

**No podrás completar este paso hasta el día que inicie el tutorial (ese día recibirás la contraseña).**
<!-- #endregion -->

## 1. Iniciar sesión en el Hub de 2i2c

<!-- #region jupyter={"source_hidden": true} -->
Para iniciar sesión en el JupyterHub proporcionado por 2i2c, sigue estos pasos:
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
1. **Navega hasta el Hub de 2i2c:** Tu navegador web debe apuntar a [este enlace] (https://climaterisk.opensci.2i2c.cloud).

2. **Inicia sesión con tus credenciales:**

- **Nombre de usuario:** Puedes elegir cualquier nombre de usuario que desees.  Sugerimos que utilices tu nombre de usuario de GitHub para evitar conflictos.
- **Contraseña:** _Recibirás la contraseña el día que inicie el tutorial_.

![2i2c\_login](../../assets/img/2i2c_login.png) (2i2c_inicio_de_sesión)

3. **Inicio de sesión:**

El proceso de inicio de sesión puede tardar unos minutos, especialmente si es necesario crear un nuevo espacio de trabajo virtual solo para ti.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
![iniciar\_servidor2](../../assets/img/start_server_2i2c.png)
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
- **Qué esperar:**

De manera predeterminada, al iniciar sesión en [`https://climaterisk.opensci.2i2c.cloud`](https://climaterisk.opensci.2i2c.cloud) se clonará automáticamente un repositorio para trabajar. Si el inicio de sesión es exitoso, verás la siguiente pantalla y estarás listo para empezar a trabajar.

![entorno\_de\_trabajo\_jupyter\_lab](../../assets/img/work_environment_jupyter_lab.png)

**Notas:** Cualquier archivo en el que trabajes se mantendrá entre sesiones siempre y cuando uses el mismo nombre de usuario al iniciar sesión.
<!-- #endregion -->

## 2. Configuración del entorno en la nube para acceder a NASA EarthData desde Python

<!-- #region jupyter={"source_hidden": true} -->
Para acceder a los productos de NASA EarthData desde programas de Python o cuadernos computacionales de Jupyter, es necesario que guardes tus credenciales de NASA EarthData en un archivo especial llamado .netrc en tu directorio de inicio.

- Puedes crear este archivo ejecutando en una terminal el script llamado `make_netrc.py`:

  ```bash
  $ python make_netrc.py
  ```

  También puedes ejecutar este script dentro de este cuaderno de Jupyter ejecutando la celda Python siguiente (utilizando el comando mágico %run).

  Algunas advertencias:
  - El script no se ejecutará si ~/.netrc ya existe. Puedes borrar ese archivo o renombrarlo si quieres conservar las credenciales que contiene.
  - El script solicitará tu nombre de usuario y contraseña de NASA EarthData, así que está atento si lo ejecutas desde un cuaderno de Jupyter.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%run make_netrc.py
```

<!-- #region jupyter={"source_hidden": true} -->
- De manera alternativa, puedes crear un archivo que se llame .netrc en tu carpeta de inicio (es decir, ~/.netrc) con el siguiente contenido:
  ```
  machine urs.earthdata.nasa.gov login USERNAME password PASSWORD
  ```
  Por supuesto, debes reemplazar el `USERNAME` y la `PASSWORD` en el archivo .netrc con los datos reales de tu cuenta NASA EarthData. Una vez que hayas guardado el archivo `.netrc` con tus credenciales correctas, es una buena práctica restringir el acceso al archivo:
  ```bash
  $ chmod 600 ~/.netrc
  ```
<!-- #endregion -->

## 3. Verificando el acceso a los productos de NASA EarthData

<!-- #region jupyter={"source_hidden": true} -->
Para asegurarte de que todo funciona correctamente, ejecuta el script `test_netrc.py`:

```bash
$ python test_netrc.py
```

Una vez más, puedes ejecutarlo directamente desde un cuaderno computacional utilizando la celda de Python que se muestra a continuación:
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%run test_netrc.py
```

<!-- #region jupyter={"source_hidden": true} -->
Si funcionó sin problemas, ¡ya está todo listo! ¡Ahora tienes todo lo que necesitas para explorar los datos de observación de la Tierra de la NASA mediante el portal EarthData!
<!-- #endregion -->

---


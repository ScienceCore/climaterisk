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

# Sistemas de referencia de coordenadas

<!-- #region jupyter={"source_hidden": true} -->
Más adelante en este tutorial, extraeremos y analizaremos conjuntos de datos geoespaciales de los _catálogos de activos espacio-temporales_ (generalmente llamados _STAC_). En concreto, esto significa que tenemos que especificar con precisión una región geográfica&mdash; normalmente denominada _área de interés_ (AOI por las siglas en inglés de _area of interest_)&mdash; y una _ventana temporal_ que describan respectivamente dónde y cuándo se produjo un evento relevante (por ejemplo, una inundación, un incendio forestal, etc.). Es decir, tanto la ubicación espacial como el período de interés deben expresarse sin ambigüedades para buscar datos relevantes.

Los conjuntos de datos geoespaciales&mdash;  ya sean datos ráster o datos vectoriales (como se describen en los siguientes cuadernos computacionales)&mdash; deben ser representados utilizando un Sistema de Referencia  de Coordenadas (CRS, por las siglas en inglés de _Coordinate Reference Systems_). En el contexto de los [_Sistemas de Información Geográfica (SIG)_](https://es.wikipedia.org/wiki/Sistema_de_informaci%C3%B3n_geogr%C3%A1fica), un CRS es un marco matemático que define cómo las características geográficas y las ubicaciones en la superficie de la Tierra se asocian con coordenadas numéricas (tuplas de dos o tres dimensiones). Se necesita una representación de coordenadas para calcular las cantidades geométricas (por ejemplo, distancias/longitud, ángulos, áreas, volúmenes, etc.) de manera precisa para el análisis geoespacial.

El presente cuaderno computacional resume el marco principal que utilizaremos: el [Sistema de Referencia de Cuadrículas Militares (MGRS, por las siglas en inglés de _Military Grid Reference System_)](https://en.wikipedia.org/wiki/Military_Grid_Reference_System). Este sistema se construye utilizando el [_sistema de coordenadas universal transversal de Mercator_ (UTM, por las siglas en inglés de _Universal Transverse Mercator_)](https://es.wikipedia.org/wiki/Sistema_de_coordenadas_universal_transversal_de_Mercator), un [_sistema de referencia de coordenadas proyectado_](https://en.wikipedia.org/wiki/Projected_coordinate_system). Para entender todas estas piezas, también necesitamos conocer algunos datos básicos sobre el [_Sistema de Coordenadas Geográficas_ (GCS)](https://es.wikipedia.org/wiki/Coordenadas_geogr%C3%A1ficas) que emplea coordenadas de latitud-longitud.
<!-- #endregion -->

---

## Relativo a las marcas de tiempo

<!-- #region jupyter={"source_hidden": true} -->
Consideremos primero el problema de especificar un intervalo de tiempo sin ambigüedades. Encontramos desafíos haciéndolo en contextos ordinarios (por ejemplo, si tratamos de programar una llamada entre personas que residen en diferentes zonas horarias). Las personas científicas que estudian la Tierra generalmente utilizan el [tiempo universal coordinado (UTC, por las siglas en inglés de _coordinated universal time_)](https://es.wikipedia.org/wiki/Tiempo_universal_coordinado) al grabar marcas de tiempo asociadas a mediciones u observaciones para evitar problemas con la zona horaria. Este es el caso de todos los productos de información de la NASA con los que trabajaremos. Hay preguntas sutiles sobre el grado de precisión con que se da una marca de tiempo (por ejemplo, en días, horas, minutos, segundos, milisegundos, etc). Sin embargo, utilizar UTC es una forma estándar de representar puntos en el tiempo (o una ventana de tiempo entre dos marcas de tiempo) sin ambigüedades.
<!-- #endregion -->

---

## Sistemas de coordenadas geográficas

<!-- #region jupyter={"source_hidden": true} -->
La mayoría de las personas están familiarizadas con el [Sistema de Posicionamiento Global (GPS, por las siglas en inglés de _Global Positioning System_)](https://es.wikipedia.org/wiki/GPS) que utiliza un [_Sistema de Coordenadas Geográficas_ (GCS, por las siglas en inglés de _Geographic Coordinate System_)](https://es.wikipedia.org/wiki/Coordenadas_geogr%C3%A1ficas) para representar ubicaciones en la superficie de la Tierra. Los sistemas de coordenadas geográficas se basan implícitamente en el [sistemas de coordenadas esféricas](https://es.wikipedia.org/wiki/Coordenadas_esf%C3%A9ricas), donde los puntos de la superficie de una esfera están determinados por dos valores angulares llamados _latitud_ y _longitud_. Por supuesto, la Tierra no es realmente esférica. Su forma se define mejor como un [_elipsoide_](https://es.wikipedia.org/wiki/Elipsoide) o un [_esferoide achatado por los polos_](https://es.wikipedia.org/wiki/Esferoide), (aunque todavía se deben hacer correcciones para tomar en cuenta la topografía y otras características de la superficie). El [_Sistema Geodésico Mundial_](https://es.wikipedia.org/wiki/Sistema_Geod%C3%A9sico_Mundial) es un modelo estándar de la Tierra que se utiliza para aplicaciones geodésicas, cartográficas y de navegación por satélite. La versión actual de este estándar es el _WGS84_, el cual que incluye un _datum geodésico_ (una descripción matemática de un elipsoide de referencia, junto con un punto de referencia en la superficie y un sistema de coordenadas orientado, centrado en la Tierra y fijo en la Tierra), un [_Modelo Gravitacional de la Tierra_ (EGM, por las siglas en inglés de _Earth Gravitational Model_)](https://en.wikipedia.org/wiki/Earth_Gravitational_Model) asociado y un [_Modelo Magnético Mundial_ (WMM, por las siglas en inglés de _World Magnetic Model_](https://es.wikipedia.org/wiki/Modelo_magn%C3%A9tico_mundial). No es necesario que nos ocupemos de los detalles del estándar WGS84, más allá de reconocer que esta norma subyace a cualquier GCS que utilice coordenadas de latitud-longitud.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
![](../../assets/img/geographic_crs.png)
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
Estos son algunos datos relevantes sobre las coordenadas de latitud-longitud del GCS en los que nos basaremos a lo largo de este tutorial:

- La _latitud_ ($\phi$) de un punto $P$ de la superficie de una esfera representa el ángulo entre el plano ecuatorial y un segmento de recta entre $P$ y $O$, el centro de la esfera. Así, la latitud de cualquier punto del ecuador es $0^\circ$, la latitud del polo superior (norte) es $+90^\circ$ y la latitud del polo inferior (sur) es $-90^\circ$.
- La _longitud_ ($\lambda$) de un punto $P$ en la superficie de una esfera es el ángulo extendido entre dos planos: el primer plano contiene ambos polos y un _punto de anclaje_ en la superficie de la esfera, y el segundo plano contiene el punto _P_ y ambos polos. La elección típica de un punto de anclaje en la superficie terrestre que se utiliza en el GCS es Greenwich, Inglaterra. El gran círculo que pasa por Greenwich y los polos se denomina _meridiano principal_. Los puntos situados estrictamente al oeste de Greenwich tienen valores de longitud negativos (entre 180 $^\circ$ y 0 $^\circ$), mientras que los puntos situados estrictamente al este de Greenwich tienen valores de longitud positivos (entre 0 $^\circ$ y 180 $^\circ$).
- Las coordenadas de latitud y longitud suelen expresarse en unidades angulares de _grados_ (denominadas ${}^\circ$). Cuando se requiere más precisión, un grado se divide en 60 _minutos_ (denominados ${}'$), cada uno de los cuales puede dividirse a su vez en 60 _segundos_ (denominados ${}"$). Las representaciones decimales de los pares latitud-longitud se utilizan en muchos lugares, pero podemos encontrar ambas convenciones para representar coordenadas.
- Los grandes círculos que pasan por los polos se denominan _meridianos_. Los meridianos tienen un valor de longitud fijo.
- Los círculos en planos paralelos al ecuatoriano se denominan _paralelos_. Los paralelos tienen un valor de latitud fijo.
- En el ecuador terrestre, un segundo de longitud corresponde aproximadamente a 30 metros. Sin embargo, hay una relación no lineal entre las diferencias de coordenadas latitud-longitud y las distancias en la superficie terrestre (y, por lo tanto, distorsiones en otras propiedades geométricas). Por ejemplo, consideremos dos regiones angulares de "ancho" $1^\circ$ en longitud y "altura" $1^\circ$ en latitud (alineadas con los ejes latitud-longitud). En un mapa que utilice coordenadas GCS, esas dos regiones tendrían la misma superficie; sin embargo, las áreas correspondientes en la superficie terrestre serían diferentes. En particular, la zona más cercana al ecuador tendría una superficie mayor. Concretamente, más cerca de los polos, las líneas de longitud y latitud constantes están más juntas, por lo que las áreas se comprimen (es una característica de cualquier GCS).
<!-- #endregion -->

---

## Sistemas de referencia de coordenadas proyectadas

<!-- #region jupyter={"source_hidden": true} -->
Los cartógrafos y geógrafos prefieren trabajar con mapas en los que las distancias medidas entre los puntos del mapa sean aproximadamente proporcionales a las distancias físicas reales. Este no es el caso de los mapas que utilizan las coordenadas de latitud-longitud del GCS.

Un enfoque más práctico para fines geográficos es utilizar en su lugar un [_sistema de referencia de coordenadas proyectado_](https://en.wikipedia.org/wiki/Projected_coordinate_system). Es decir, utilizar un CRS cuyas coordenadas se obtengan mediante una [proyección cartográfica](https://es.wikipedia.org/wiki/Proyecci%C3%B3n_cartogr%C3%A1fica) que proyecte los puntos de una región fija de la superficie curva de la Tierra en un plano bidimensional. Esta transformación distorsiona necesariamente la superficie curva de la Tierra, pero localmente las distancias geométricas entre los puntos del plano son aproximadamente proporcionales a las distancias reales. Así, las coordenadas de un sistema de coordenadas proyectadas suelen expresarse en unidades de longitud (por ejemplo, metros). Las proyecciones implican compromisos en el sentido de que diferentes proyecciones representan con mayor fiabilidad ciertas propiedades geométricas&mdash; forma, área, distancia, etc.&mdash; con mayor precisión.
<!-- #endregion -->

### Coordenadas Universal Transversal de Mercator (UTM)

<!-- #region jupyter={"source_hidden": true} -->
El sistema de [_Coordenadas Universal Transversal de Mercator_ (UTM, por las siglas en inglés de Universal Transverse Mercator)](hhttps://es.wikipedia.org/wiki/Sistema_de_coordenadas_universal_transversal_de_Mercator) es un caso particular de referencia de coordenadas proyectadas. Los valores de estas coordenadas se denominan típicamente _dirección al este_ y _dirección al norte_ (en referencia a las distancias este y norte, respectivamente, desde el origen en algún plano aplanado localmente).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
![utm\_zones](https://gisgeography.com/wp-content/uploads/2016/05/UTM-Zones-Globe-2-500x485.png)
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
- El CRS UTM divide el mapa del mundo en 60 zonas de un ancho de $6^\circ$ en longitud que se extienden entre $-80^\circ$ & $+84^\circ$ de latitud. Las zonas UTM están numeradas del 1 al 60, comenzando en el antimeridiano (es decir, la zona 1 a 180 $^\circ$ de longitud) y progresando hacia el este hasta el antemeridiano (es decir, la zona 60 a 180 $^\circ$ de longitud).
- El origen dentro de cada zona UTM está en el ecuador, es decir, en el meridiano central de la zona.
- Existen fórmulas para convertir coordenadas GCS de [latitud-longitud en coordenadas UTM de este-noroeste](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system#From_latitude,_longitude_\(%CF%86,_%CE%BB\)_to_UTM_coordinates_\(E,_N\)), así como [fórmulas para hacer lo contrario](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system#From_UTM_coordinates_\(E,_N,_Zone,_Hemi\)). Aparte de saber que las rutinas de software implementan esas fórmulas para efectuar esas transformaciones no es necesario que nos ocupemos de esos detalles en este tutorial.
- La posición de un punto en coordenadas UTM usualmente implica la especificación de dos valores positivos para las coordenadas este y norte, así como el número de la zona UTM. El valor del este es el número de metros al este del meridiano central de la zona y el valor del norte es el número de metros al norte del ecuador. Para evitar el uso de coordenadas negativas, se agrega un _falso valor del norte_ de $10,000,000\,\mathrm{m}$ a la coordenada norte y un _falso valor del este_ de $500,000\,\mathrm{m}$ a la coordenada este.
<!-- #endregion -->

---

### Nota sobre los sistemas de referencia de coordenadas

<!-- #region jupyter={"source_hidden": true} -->
En principio, hay infinitos sistemas de referencia de coordenadas que asocian ubicaciones en la superficie terrestre con tuplas bidimensionales o tridimensionales de números (coordenadas). Para caracterizar de forma concisa una serie de CRS prácticos, el [Grupo Europeo de Estudios del Petróleo](https://en.wikipedia.org/wiki/European_Petroleum_Survey_Group) (EPSG) mantiene el [registro EPSG](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset). A cada CRS se le asigna un código comprendido entre 1024 y 32767 junto con una representación estándar de texto conocido legible por máquina [(WKT, por las siglas en inglés de _Well Known Text_)](https://en.wikipedia.org/wiki/Well-known_text_representation_of_coordinate_reference_systems).
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
Estos son algunos ejemplos importantes de códigos EPSG CRS:

- **EPSG:4326** es el CRS que utiliza coordenadas estándar de latitud-longitud basadas en el modelo geodésico WGS84 utilizado para GPS y navegación.
- **EPSG:3857** es el CRS proyectado por _Web Mercator_ que se utiliza, por ejemplo, en Google Maps y OpenStreetMaps debido a su comodidad para la representación y la navegación en línea recta. Distorsiona considerablemente las distancias cercanas a los polos.
- **EPSG:32610** es un UTM CRS proyectado particular. Los CRS similares proyectados en UTM tienen un código de la forma _EPSG:326XY_. Los dígitos `326` indican un CRS proyectada UTM válida en el hemisferio norte. Los dos últimos dígitos, `10` en este caso, identifican una zona UTM concreta comprendida entre `01` y `60`.
- **EPSG:32710** también es un CRS UTM proyectado particular. Los dígitos `327` indican un CRS UTM proyectado válido en el hemisferio sur y los dos últimos dígitos, de nuevo, `10` en este caso, identifican una zona UTM concreta comprendida entre `01` y `60`.

Desde un punto de vista matemático, un código EPSG es un identificador compacto que relaciona conjuntos normalizados de ecuaciones, parámetros y reglas.
<!-- #endregion -->

---

## Sistema de Referencia de Cuadrículas Militares (MGRS)

<!-- #region jupyter={"source_hidden": true} -->
La última convención que debemos conocer es el [_Sistema de Referencia de Cuadrículas Militares_](https://en.wikipedia.org/wiki/Military_Grid_Reference_System) (MGRS, por las siglas en inglés de _Military Grid Reference System_). El MGRS es utilizado principalmente por los ejércitos de la Organización del Tratado del Atlántico Norte (OTAN, por las siglas en inglés de _North Atlantic Treaty Organization_) para identificar ubicaciones terrestres. El MGRS no es un CRS, sino un _estándar de geocoordenadas_ superpuesto a otros CRS. Lejos de la región polar, el MGRS utiliza el sistema de coordenadas UTM, cerca de los polos, utiliza el sistema de coordenadas Estereográfica Polar Universal (UPS, por las siglas en inglés de _Universal Polar Stereographic_). En ambos casos, el MGRS se basa en coordenadas CRS proyectadas basadas en el modelo WGS84 para obtener representaciones espaciales precisas.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
![MGRS tiles](../../assets/img/utm_zones.png)
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
El sistema MGRS utiliza zonas UTM como base para su cuadrícula. Recordemos que el sistema UTM divide la superficie terrestre en 60 zonas, cada una de ellas con un ancho de $6^{\circ}$ de longitud, que se extienden desde $-80^\circ$ to $+84^\circ$. Cada zona UTM se divide en 20 bandas horizontales de latitud, cada una de ellas de una altura de $8^\circ$ de latitud. Estas bandas de latitud se etiquetan de la `C` a la `X` (excluyendo las letras `I` y `O` para evitar confusiones con `1` y `0` respectivamente). Estas dos primeras etiquetas constituyen un _designador de zona de cuadrícula_ (GZD, por las siglas en inglés de _grid-zone designator_ ).  Estas 1,200 zonas cuadriculadas MGRS se subdividen a su vez en mosaicos de área $(100\,\mathrm{km}\times100\,\mathrm{km})$; los cuales se etiquetan por columna y fila dentro de cada GZD. Por ejemplo, el identificador del mosaico `10TEM` indica que el mosaico en cuestión está en la zona UTM `10` en la banda horizontal `T`. Dentro de ese GZD, hay una cuadrícula de mosaicos y la que tiene el índice de columna `E` y el índice de fila `M` es el mosaico en cuestión. Estas etiquetas ayudan a identificar las coordenadas de las esquinas de una región cuadrada asociada a una imagen de satélite, así como el sistema de coordenadas proyectadas utilizado para asignar puntos de la superficie terrestre a las coordenadas de las regiones proyectadas.

En esencia, el MGRS es un perfeccionamiento del sistema de coordenadas UTM, diseñado para facilitar la legibilidad y la comunicación en aplicaciones militares y de navegación. La estructura jerárquica del sistema, desde la zona UTM a la banda de latitud, pasando por cuadrículas de 100 km y, finalmente, hasta coordenadas precisas de este y norte, permite una referenciación eficaz sin necesidad de tener coordenadas numéricas grandes.
<!-- #endregion -->

---

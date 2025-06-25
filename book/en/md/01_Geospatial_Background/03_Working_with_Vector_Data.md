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

# Working with Vector Data

<!-- #region jupyter={"source_hidden": true} -->
Certain physical properties of interest in GIS are not conveniently captured by raster data on discrete grids. For instance, geometric features of a landscape like roads, rivers and boundaries between regions are better described using lines or curves in a suitable projected coordinate system. *Vector data*, in the context of GIS, refers to geometric representations of such aspects of a landscape.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Understanding Vector Data

<!-- #region jupyter={"source_hidden": true} -->
*Vector data* consists of ordered sequences of *vertices*, i.e., pairs of numbers of the form $(x,y)$. The continuous coordinates of each vertex are associated with a physical spatial location in some projected *CRS* (*Coordinate Reference System*).

+ *Point data*: Isolated vertices represent discrete zero-dimensional features (e.g., trees, street lamps, etc.).
+ *Line data*: Any ordered sequence of at least two vertices constitutes a *"polyline"* that can be visualized by drawing straight lines between adjacent vertices. Line data is suitable for representing one-dimensional features like roads, trails, and rivers.
+ *Polygon data*: Any ordered sequence of at least three vertices in which the first and last vertex are the same constitutes a *polygon* (i.e., a closed shape). Polygon data is suitable for describing two-dimensional regions like a lake or the boundary of a forest. A common use of polygon data is to represent borders between political constituencies (e.g., countries).

A single vector dataset georeferenced with a particular CRS typically contains any number of points, lines, or polygons.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
![points-lines-polygons-vector-data-types](../../../assets/img/points-lines-polygons-vector-data-types.png)

<p style="text-align: center;">This image shows the three vector types: points, lines and polygons. Source: National Ecological Observatory Network.
</p>
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
![points](../../../assets/img/points.png)

<p style="text-align: center;">(Left image) Overhead view of a landscape; (right image) Point vector representations of salient features.<br>Source: *Sistemas de Información Geográfica* by Victor Olaya.
</p>

![lines](../../../assets/img/lines.png)

<p style="text-align: center;">(Left image) Overhead view of a river; (right image) Line vector representation of the river.<br>Source: *Sistemas de Información Geográfica* by Victor Olaya.
</p>

![polygon](../../../assets/img/polygon.png)

<p style="text-align: center;">(Left image) Overhead view of a lake; (right image) Polygon vector representation of the lake<br>Source: *Sistemas de Información Geográfica* by Victor Olaya.
</p>
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
As with raster data, vector data representations are usually bundled with metadata to store various attributes associated with the dataset. Vector data is generally specified at a higher level of precision than the resolution than most raster grids allow. Moreover, geographic features represented as vector data enables computations that raster data does not. For instance, it is possible to determine various geometric or topological relationships:

+ Does a point lie within the boundary of a geographic region?
+ Do two roads intersect?
+ What is the nearest point on a road to another region?

Other geometric quantities like the length of a river or the surface area of a lake are available by applying techniques from computational geometry to vector data representations.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Using GeoJSON

<!-- #region jupyter={"source_hidden": true} -->
[GeoJSON](https://geojson.org/) is a subset of [JSON (JavaScript object notation)](https://www.json.org). It was developed in the early 2000s to represent simple geographical features together with non-spatial attributes. The core idea is to provide a specification for encoding geospatial data that can be decoded by any JSON decoder.

The GIS developers responsible for GeoJSON designed it with the intention that any web developer should be able to write a custom GeoJSON parser, allowing for many possible ways to use geospatial data beyond standard GIS software. The technical details of the GeoJSON format are described in the standards document [RFC7946](https://datatracker.ietf.org/doc/html/rfc7946).

Let's see how to parse and plot GeoJSON files using [GeoPandas](https://geopandas.org/en/stable/). The local file `cables.geojson` stores line vector data representing underwater cables connecting different land masses.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
import geopandas as gpd
from pathlib import Path
from warnings import filterwarnings
filterwarnings('ignore')

FILE_STEM = Path.cwd().parent.parent.parent if 'book' == Path.cwd().parent.parent.parent.stem else 'book'
GEOJSON = FILE_STEM / 'assets' / 'data' /'cables.geojson'
```

```python jupyter={"source_hidden": true}
with open(GEOJSON) as f:
    text = f.read()
print(text[:1500])
```

<!-- #region jupyter={"source_hidden": true} -->
Trying to read the GeoJSON output above is tricky but predictable. JSON files are generically intended for machine consumption and are hence not very readable.

Let's use the `geopandas.read_file` function to load the vector data into a `GeoDataFrame`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
gdf = gpd.read_file(GEOJSON)
display(gdf.head())
gdf.info()
```

<!-- #region jupyter={"source_hidden": true} -->
There are 530 rows each of which corresponds to line data (a connected sequence of line segments). We can use the `GeoDataFrame` column `color` as an option within a call to `.plot` to make a plot of these cables.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
gdf.geometry.plot(color=gdf.color, alpha=0.25);
```

<!-- #region jupyter={"source_hidden": true} -->
Let's use a remote file to create another `GeoDataFrame`, this time containing polygon data.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
URL = "http://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_land.geojson"
gdf = gpd.read_file(URL)

gdf
```

<!-- #region jupyter={"source_hidden": true} -->
This time, the plot shows filled polygons corresponding to the countries of the world.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
gdf.plot(color='green', alpha=0.25) ;
```

<!-- #region jupyter={"source_hidden": true} -->
The `GeoDataFrame.loc` accessor allows us to plot particular subsets of countries.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
gdf.loc[15:90].plot(color='green', alpha=0.25) ;
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Using Shapefiles

<!-- #region jupyter={"source_hidden": true} -->
The [shapefile](https://en.wikipedia.org/wiki/Shapefile) standard is a digital format for distributing geospatial vector data and its associated attributes. The standard—first developed by [ESRI](https://en.wikipedia.org/wiki/Esri) roughly 30 years ago—is supported by most modern GIS software tools. The name "shapefile" is a bit misleading because a "shapefile" typically consists of a bundle of several files (some mandatory, some optional) stored in a common directory with a common filename prefix.

From [Wikipedia](https://en.wikipedia.org/wiki/Shapefile):

> The shapefile format stores the geometry as primitive geometric shapes like points, lines, and polygons. These shapes, together with data attributes that are linked to each shape, create the representation of the geographic data. The term "shapefile" is quite common, but the format consists of a collection of files with a common filename prefix, stored in the same directory. The three mandatory files have filename extensions .shp, .shx, and .dbf. The actual shapefile relates specifically to the .shp file, but alone is incomplete for distribution as the other supporting files are required. Legacy GIS software may expect that the filename prefix be limited to eight characters to conform to the DOS 8.3 filename convention, though modern software applications accept files with longer names.

Shapefiles use the [*Well-Known Binary (WKB)*](https://libgeos.org/specifications/wkb/) format for encoding geometries. This is a compact tabular format, i.e., row and column numbers ass value is significant. Some minor limitations of this format include the restriction of attribute field names to 10 characters or fewer and poor Unicode support; as a result, text is often abbreviated and encoded in ASCII.

You can refer to the [ESRI Shapefile Technical Whitepaper](https://www.esri.com/content/dam/esrisites/sitecore-archive/Files/Pdfs/library/whitepapers/pdfs/shapefile.pdf) to find out more about shapefiles.
<!-- #endregion -->

#### Mandatory files

<!-- #region jupyter={"source_hidden": true} -->
- Main File (`.shp`): shape format, i.e., the spatial vector data (points, lines, and polygons) representing feature geometry.
- Index File (`.shx`): shape index positions (to enable retrieval of feature geometry).
- dBASE File (`.dbf`): standard database file storing attribute format (columnar attributes for each shape in dBase IV format, typically readable by, e.g., Microsoft Access or Excel).

Records correspond in sequence in each of these files , i.e., attributes in record $k$ of the `dbf` file describe the feature in record $k$ of the associated `shp` file.
<!-- #endregion -->

#### Optional files

<!-- #region jupyter={"source_hidden": true} -->
- Projection File (`.prj`): description of relevant coordinate reference system using a [*well-known text (WKT or WKT-CRS)*  representation](https://en.wikipedia.org/wiki/Well-known_text_representation_of_coordinate_reference_systems).
- Extensible Markup Language File (`.xml`): [geospatial metadata](https://en.wikipedia.org/wiki/Geospatial_metadata) in [XML](https://en.wikipedia.org/wiki/XML) format.
- Code Page File (`.cpg`): plain text files to describe the encoding applied to create the shapefile. If your shapefile doesn’t have a .cpg file, then it has the system´s default encoding.
- Spatial Index Files (`.sbn` and `.sbx`): encoded index files to speed up loading times.

There are numerous other optional files; see the [whitepaper](https://www.esri.com/content/dam/esrisites/sitecore-archive/Files/Pdfs/library/whitepapers/pdfs/shapefile.pdf).

As with GeoJSON files, shapefiles can be read directly using `geopandas.read_file` to load the `.shp` file. We'll do this now using an example shapefile that shows the boundary of a wildfire.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
SHAPEFILE = FILE_STEM / 'assets' / 'data' / 'shapefiles' / 'mckinney' / 'McKinney_NIFC.shp'
gdf = gpd.read_file(SHAPEFILE)
gdf.info()
gdf.head()
```

```python jupyter={"source_hidden": true}
gdf.plot(color='red', alpha=0.5);
```

<!-- #region jupyter={"source_hidden": true} -->
We'll use this particular shapefile again in later notebooks and explain what it represents in greater detail then.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

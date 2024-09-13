# Geospatial data formats


There are numerous standard file formats used for sharing scientific data (e.g., [*HDF*](https://en.wikipedia.org/wiki/Hierarchical_Data_Format), [*Parquet*](https://parquet.apache.org/), [*CSV*](https://en.wikipedia.org/wiki/Comma-separated_values), etc.). Moreover, there are [dozens of file formats](https://www.spatialpost.com/list-common-gis-file-format/) available for [*Geographic Information Systems (GIS)*](https://en.wikipedia.org/wiki/Geographic_information_system) e.g., DRG, [*NetCDF*](https://docs.unidata.ucar.edu/nug/current/), USGS DEM, DXF, DWG, SVG, and so on.

For this tutorial, we focus on only three specific formats.


## GeoTIFF(for raster data)


[GeoTIFF](https://en.wikipedia.org/wiki/GeoTIFF) is a public domain metadata standard designed to work within [*TIFF (Tagged Image File Format)*)](https://en.wikipedia.org/wiki/TIFF) files. The GeoTIFF format enables georeferencing information to be embedded as geospatial metadata within image files. GIS applications use GeoTIFFs for aerial photography, satellite imagery, and digitized maps. The GeoTIFF data format is described in detail in the [OGC GeoTIFF Standard](https://www.ogc.org/standard/geotiff/) document.

A GeoTIFF file extension contains geographic metadata that describes the actual location in space that each pixel in an image represents. In creating a GeoTIFF file, spatial information is included in the `.tif` file as embedded tags, which can include raster image metadata such as:
* horizontal and vertical datums 
* spatial extent, i.e. the area that the dataset covers
* the coordinate reference system (CRS) used to store the data
* spatial resolution, measured in the number of independent pixel values per unit length
* the number of layers in the .tif file
* ellipsoids and geoids (i.e., estimated models of the Earth’s shape)
* mathematical rules for map projection to transform data for a three-dimensional space into a two-dimensional display.


## Shapefiles (for vector data)


The [shapefile](https://en.wikipedia.org/wiki/Shapefile) standard is a digital format for distributing geospatial vector data and its associated attributes. The standard—first developed by [ESRI](https://en.wikipedia.org/wiki/Esri) roughly 30 years ago—is supported by most modern GIS software tools. The name "shapefile" is a bit misleading because a "shapefile" typically consists of a bundle of several files (some mandatory, some optional) stored in a common directory with a common filename prefix.

From [Wikipedia](https://en.wikipedia.org/wiki/Shapefile):

> The shapefile format stores the geometry as primitive geometric shapes like points, lines, and polygons. These shapes, together with data attributes that are linked to each shape, create the representation of the geographic data. The term "shapefile" is quite common, but the format consists of a collection of files with a common filename prefix, stored in the same directory. The three mandatory files have filename extensions .shp, .shx, and .dbf. The actual shapefile relates specifically to the .shp file, but alone is incomplete for distribution as the other supporting files are required. Legacy GIS software may expect that the filename prefix be limited to eight characters to conform to the DOS 8.3 filename convention, though modern software applications accept files with longer names.

Shapefiles use the [*Well-Known Binary (WKB)*](https://libgeos.org/specifications/wkb/) format for encoding geometries. This is a compact tabular format, i.e., row and column numbers ass value is significant. Some minor limitations of this format include the restirction of attribute field names to 10 characters or fewer and poor Unicode support; as a result, text is often abbreviated and encoded in ASCII.^3^

You can refer to the [ESRI Shapefile Technical Whitepaper](https://www.esri.com/content/dam/esrisites/sitecore-archive/Files/Pdfs/library/whitepapers/pdfs/shapefile.pdf) to find out more about shapefiles.


#### Mandatory files


- Main File (`.shp`): shape format, i.e., the spatial vector data (points, lines, and polygons) representing feature geometry.
- Index File (`.shx`): shape index positions (to enable retrieval of feature geometry).
- dBASE File (`.dbf`): standard database file storing attribute format (columnar attributes for each shape in dBase IV format, typically readable by, e.g., Microsoft Access or Excel).

Records correspond in sequence in each of these files , i.e., attributes in record $k$ of the `dbf` file describe the feature in record $k$ of the associated `shp` file.


#### Optional files


- Projection File (`.prj`): description of relevant coordinate reference system using a [*well-known text (WKT or WKT-CRS)*  representation](https://en.wikipedia.org/wiki/Well-known_text_representation_of_coordinate_reference_systems).
- Extensible Markup Language File (`.xml`): [geospatial metadata](https://en.wikipedia.org/wiki/Geospatial_metadata) in [XML](https://en.wikipedia.org/wiki/XML) format.
- Code Page File (`.cpg`): plain text files to describe the encoding applied to create the shapefile. If your shapefile doesn’t have a .cpg file, then it has the system´s default encoding.
- Spatial Index Files (`.sbn` and `.sbx`): encoded index files to speed up loading times.
- etc. (there are numerous other optional files; see the [whitepaper](https://www.esri.com/content/dam/esrisites/sitecore-archive/Files/Pdfs/library/whitepapers/pdfs/shapefile.pdf)).


## GeoJSON (for vector data)


[GeoJSON](https://geojson.org/) is a subset of [JSON (JavaScript object notation)](https://www.json.org) developed in the early 2000s to represent simple geographical features together with non-spatial attributes. The core idea is to provide a specification for encoding geospatial data that can be decoded by any JSON decoder.

![json_example](../assets/json_example.PNG)

<p style="text-align: center;">This image shows an example of a GeoJson file. Source: https://gist.githubusercontent.com/wavded.
</p>

The GIS developers responsible for GeoJSON designed it with the intention that any web developer should be able to write a custom GeoJSON parser, allowing for many possible ways to use geospatial data beyond standard GIS software. The technical details of the GeoJSON format are described in the standards document [RFC7946](https://datatracker.ietf.org/doc/html/rfc7946).

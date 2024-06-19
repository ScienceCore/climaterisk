# Geospatial data formats

## Vector data formats

In this tutorial we will be using the following vector data formats:

### 1. SHP

Shapefile is the most widely known format for distributing geospatial data. It is a standard first developed by ESRI almost 30 years ago, which is considered ancient in software development.^3^ 

The Shapefile consists of several files: in addition to one file with the actual geometry data, another file for defining the coordinate reference system is needed, as well as a file for defining the attributes and a file to index the geometries. This makes operating Shapefiles slightly clunky and confusing. However, Shapefile has been around for so long that any GIS software supports handling it.<sup>3</sup>

Internally, Shapefile uses Well-known binary (WKB) for encoding the geometries. This is a compact format that is based on tabular thinking, i.e. the row and column number of a value is significant. A minor nuisance is the limitation of the attribute field names to 10 characters and poor Unicode support, so some abbreviations and forcing to ASCII may have to be used.^3^

For more details about the shapefiles you can refer to the [ESRI Shapefile Technical Description](https://www.esri.com/content/dam/esrisites/sitecore-archive/Files/Pdfs/library/whitepapers/pdfs/shapefile.pdf)

### 2. GeoJSON

GeoJSON is a subset of JSON (JavaScript object notation). It was developed 10 years ago by a group of enthusiastic GIS developers. The core idea is to provide a specification for encoding geospatial data while remaining decodable by any JSON decoder.^3^

Being a subset of the immensely popular JSON, the parsing support is on a different level than with Shapefile. In addition to support from most GIS software, any web developer will be able to write a custom GeoJSON parser, opening new possibilities for integrating the data.^3^

Being designed as one blob of data instead of a small "text database" means it is simpler to handle but is essentially designed to be loaded to memory in full at once.^3^ 

For more information about GeoJSON data formats, you can refer to [https://geojson.org/](https://geojson.org/).

## Raster data formats


In this tutorial we will be using the following raster data format:

### 1. GeoTiffs

GeoTIFF is a public domain metadata standard that enables georeferencing information to be embedded within an image file. The GeoTIFF format embeds geospatial metadata into image files such as aerial photography, satellite imagery, and digitized maps so that they can be used in GIS applications.^2^

A GeoTIFF file extension contains geographic metadata that describes the actual location in space that each pixel in an image represents. In creating a GeoTIFF file, spatial information is included in the .tif file as embedded tags, which can include raster image metadata such as:
* horizontal and vertical datums 
* spatial extent, i.e. the area that the dataset covers
* the coordinate reference system (CRS) used to store the data
* spatial resolution, measured in the number of independent pixel values per unit length
* the number of layers in the .tif file
* ellipsoids and geoids - estimated models of the Earth’s shape
* mathematical rules for map projection to transform data for a three-dimensional space into a two-dimensional display.

Geodata is drawn from vector formats on a map, and the geodata is converted to the specified output projection of the map if the projection in the source file differs. Some of the vector and raster formats typically supported by a GeoTIFF online viewer include asc, gml, gpx, json, kml, kmz, mid, mif, osm, tif, tab, map, id, dat, gdbtable, and gdbtablx.^2^

For more details about GeoTiff data format, you can refer to [OGC GeoTIFF Standard](https://www.ogc.org/standard/geotiff/).

## References

1. https://www.geographyrealm.com/geodatabases-explored-vector-and-raster-data/
2. https://www.heavy.ai/technical-glossary/geotiff
3. https://feed.terramonitor.com/shapefile-vs-geopackage-vs-geojson/

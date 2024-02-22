# Selecting an Area of Interest (AOI) for data analysis
An `AOI` refers to the geographical extent of our study area, expressed in a specific co-ordinate reference system [(CRS)](https://docs.qgis.org/3.28/en/docs/gentle_gis_introduction/coordinate_reference_systems.html#coordinate-reference-system-crs-in-detail).

An AOI can be expressed in various formats, for example we can express an area covering the Yellowstone National Park in the United States as:
```
x_min = -111.0529, y_min = 44.3587, x_max = -109.7877, y_max = 45.0159
```
where the values are expressed in WGS84 (using latitude and longitude).

The same information can also be conveyed as a geoJSON. This would look like:
```
{
  "type": "Feature",
  "properties": {},
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [-111.0529, 45.0159],
        [-109.7877, 45.0159],
        [-109.7877, 44.3587],
        [-111.0529, 44.3587],
        [-111.0529, 45.0159]
      ]
    ]
  }
}
```
In this case, the Polygon is specified by a list of coordinates corresponding to the vertices of our shape. We will visualize this shape in the Jupyter notebook.

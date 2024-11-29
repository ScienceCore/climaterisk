# Coordinate Reference Systems


The following summary was made using:
+ the [QGIS documentation](https://docs.qgis.org/3.34/en/docs/gentle_gis_introduction/coordinate_reference_systems.html)
+ the book [*Sistemas de Información Geográfica*](https://volaya.github.io/libro-sig/) by Victor Olaya

With the help of coordinate reference systems (CRS), every location on the earth can be specified by a set of two numbers, called *coordinates*. There are two commonly-used categories of CRS: *geographic* coordinate reference systems and *projected* coordinate reference systems (also called *rectangular* coordinate reference systems).


## Geographic Coordinate Systems


The geographic coordinate system is a spherical coordinate system by which a point is located with two angular values:

- Lines of **longitude** run perpendicular to the equator and converge at the poles. The reference line for longitude (the prime meridian) runs from the North pole to the South pole through Greenwich, England. Subsequent lines of longitude are measured from zero to 180 degrees East or West of the prime meridian. Note that values West of the prime meridian are assigned negative values for use in digital mapping applications. At the equator, and only at the equator, the distance represented by one line of longitude is equal to the distance represented by one degree of latitude. As you move towards the poles, the distance between lines of longitude becomes progressively less, until, at the exact location of the pole, all 360° of longitude are represented by a single point that you could put your finger on (you probably would want to wear gloves though).

- Lines of **latitude** run parallel to the equator and divide the earth into 180 equally spaced sections from North to South (or South to North). The reference line for latitude is the equator and each hemisphere is divided into ninety sections, each representing one degree of latitude. In the northern hemisphere, degrees of latitude are measured from zero at the equator to ninety at the north pole. In the southern hemisphere, degrees of latitude are measured from zero at the equator to ninety degrees at the south pole. To simplify the digitization of maps, degrees of latitude in the southern hemisphere are often assigned negative values (0 to -90°). Wherever you are on the earth’s surface, the distance between the lines of latitude is the same (60 nautical miles).

![geographic_crs](../assets/geographic_crs.png)

<p style="text-align: center;">Geographic coordinate system with lines of latitude parallel to the equator and lines of longitude with the prime meridian through Greenwich. Source: QGIS Documentation.
</p>


Using the geographic coordinate system, we have a grid of lines dividing the earth into squares that cover approximately 12363.365 square kilometers at the equator — a good start, but not very useful for determining the location of anything within that square. To be truly useful, a map grid must be divided into small enough sections so that they can be used to describe (with an acceptable level of accuracy) the location of a point on the map. To accomplish this, degrees are divided into minutes (') and seconds ("). There are sixty minutes in a degree, and sixty seconds in a minute (3600 seconds in a degree). So, at the equator, one second of latitude or longitude = 30.87624 meters.


## Projected coordinate reference systems


A [*projected coordinate reference system*](https://en.wikipedia.org/wiki/Projected_coordinate_system) uses a [map projection](https://en.wikipedia.org/wiki/Map_projection) to identify pairs of spatial coordinates $(X,Y)$ with points on the surface of the Earth. These coordinate values are typically referred to as "easting" and "northing" (referring to distances east and north respectively to the origin in some locally flattened $XY$-plane). Unlike angular longitude-latitude pairs, the spatial easting-northing coordinates in a projected coordinate system have units of length (e.g., metres).
 
Projected coordinate reference systems in the southern hemisphere (south of the equator) normally assign the origin on the equator at a specific longitude. This means that the $Y$-values increase southwards and the $X$-values increase westwards. In the northern hemisphere (north of the equator) the origin is also the equator at a specific Longitude. However, now the Y-values increase northwards and the X-values increase to the East.


### Universal Transverse Mercator (UTM) coordinates


The [*Universal Transverse Mercator (UTM)*](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system) coordinate reference system has its origin on the equator at a specific Longitude. Now the $Y$-values increase southwards and the X-values increase to the West. The UTM CRS is a global map projection. This means it is generally used all over the world. To avoid excessive distortion, the world is divided into 60 equal zones that are all 6 degrees wide in longitude from East to West. The UTM zones are numbered 1 to 60, starting at the antimeridian (zone 1 at 180 degrees West longitude) and progressing East back to the antemeridian (zone 60 at 180 degrees East longitude).

![utm_zones](../assets/utm_zones.png)

<p style="text-align: center;">The Universal Transverse Mercator zones. Source: QGIS Documentation.
</p>


The position of a coordinate in UTM south of the equator must be indicated with the zone number and with its northing ($Y$) value and easting ($X$) value in meters. The northing value is the distance of the position from the equator in meters. The easting value is the distance from the central meridian (longitude) of the used UTM zone. Furthermore, in UTM zones that are south of the equator, a so-called false northing value of 10,000,000 m to the northing ($Y$) value to avoid negative values. Similarly, in some UTM zones, a false easting value of 500,000 m is added to the easting ($X$) value.

---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.2
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Data Visualization with GeoViews & HvPlot

<!-- #region jupyter={"source_hidden": false} -->
The primary tools we'll use for plotting come from the [Holoviz](https://holoviz.org/) family of Python libraries, principally [GeoViews](https://geoviews.org/) and [hvPlot](https://hvplot.holoviz.org/). These are largely built on top of [HoloViews](https://holoviews.org/) and support multiple backends for rendering plots (notably [Bokeh](http://bokeh.pydata.org/) for interactive visualization and [Matplotlib](http://matplotlib.org/) for static, publication-quality plots).
<!-- #endregion -->

***


## [GeoViews](https://geoviews.org/)

<!-- #region jupyter={"source_hidden": false} -->
<center><img src="https://geoviews.org/_static/logo_horizontal.png"></img>
</center>

From the [GeoViews documentation](https://geoviews.org/index.html):

> GeoViews is a [Python](http://python.org/) library that makes it easy to explore and visualize geographical, meteorological, and oceanographic datasets, such as those used in weather, climate, and remote sensing research.
>
> GeoViews is built on the [HoloViews](http://holoviews.org/) library for building flexible visualizations of multidimensional data. GeoViews adds a family of geographic plot types based on the [Cartopy](http://scitools.org.uk/cartopy) library, plotted using either the [Matplotlib](http://matplotlib.org/) or [Bokeh](http://bokeh.pydata.org/) packages. With GeoViews, you can now work easily and naturally with large, multidimensional geographic datasets, instantly visualizing any subset or combination of them, while always being able to access the raw data underlying any plot.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
from pprint import pprint

import geoviews as gv
gv.extension('bokeh')
from geoviews import opts

FILE_STEM = Path.cwd().parent if 'book' == Path.cwd().parent.stem else 'book'
```

***


### Displaying a basemap

<!-- #region jupyter={"source_hidden": false} -->
A *basemap* or *tile layer* is useful when displaying vector or raster data because it allows us to overlay the relevant geospatial data on a familar gepgraphical map as a background. The principal utility is we'll use is `gv.tile_sources`. We can use the method `opts` to specify additional confirguration settings. Below, we use the *Open Street Map (OSM)* Web Map Tile Service to create the object `basemap`. When we display the repr for this object in the notebook cell, the Bokeh menu at right enables interactive exploration.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
basemap = gv.tile_sources.OSM.opts(width=600, height=400)
basemap # When displayed, this basemap can be zoomed & panned using the menu at the right
```

***


### Plotting points

<!-- #region jupyter={"source_hidden": false} -->
To get started, let's define a regular Python tuple for the longitude-latitude coordinates of Tokyo, Japan.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
tokyo_lonlat = (139.692222, 35.689722)
print(tokyo_lonlat)
```

<!-- #region jupyter={"source_hidden": false} -->
The class `geoviews.Points` accepts a list of tuples (each of the form `(x, y)`)  & constructs a `Points` object that can be displayed. We can overlay the point created in the OpenStreetMap tiles from `basemap` using the `*` operator in Holoviews. We can also use `geoviews.opts` to set various display preferences for these points.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
tokyo_point   = gv.Points([tokyo_lonlat])
point_opts = opts.Points(
                          size=48,
                          alpha=0.5,
                          color='red'
                        )
print(type(tokyo_point))
```

```{code-cell} python jupyter={"source_hidden": false}
# Use Holoviews * operator to overlay plot on basemap
# Note: zoom out to see basemap (starts zoomed "all the way in")
(basemap * tokyo_point).opts(point_opts)
```

```{code-cell} python jupyter={"source_hidden": false}
# to avoid starting zoomed all the way in, this zooms "all the way out"
(basemap * tokyo_point).opts(point_opts, opts.Overlay(global_extent=True))
```

***


### Plotting rectangles

<!-- #region jupyter={"source_hidden": false} -->
+ Standard way to represent rectangle (also called a *bounding box*) with corners
  $$(x_{\mathrm{min}},y_{\mathrm{min}}), (x_{\mathrm{min}},y_{\mathrm{max}}), (x_{\mathrm{max}},y_{\mathrm{min}}), (x_{\mathrm{max}},y_{\mathrm{max}})$$
  (assuming $x_{\mathrm{max}}>x_{\mathrm{min}}$ & $y_{\mathrm{max}}>y_{\mathrm{min}}$) is as a single 4-tuple
  $$(x_{\mathrm{min}},y_{\mathrm{min}},x_{\mathrm{max}},y_{\mathrm{max}}),$$
  i.e., the lower,left corner coordinates followed by the upper, right corner coordinates.

  Let's create a simple function to generate a rectangle of a given width & height given the centre coordinate.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
# simple utility to make a rectangle centered at pt of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

<!-- #region jupyter={"source_hidden": false} -->
We can test the preceding function using the longitude-latitude coordinates of Marrakesh, Morocco.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
# Verify that the function bounds works as intended
marrakesh_lonlat = (-7.93, 31.67)
dlon, dlat = 0.5, 0.25
marrakesh_bbox = make_bbox(marrakesh_lonlat, dlon, dlat)
print(marrakesh_bbox)
```

<!-- #region jupyter={"source_hidden": false} -->
The utility `geoviews.Rectangles` accepts a list of bounding boxes (each described by a tuple of the form `(x_min, y_min, x_max, y_max)`) to plot. We can again use `geoviews.opts` to tailor the rectangle as needed.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
rectangle = gv.Rectangles([marrakesh_bbox])
rect_opts = opts.Rectangles(
                                line_width=0,
                                alpha=0.1,
                                color='red'
                            )
```

<!-- #region jupyter={"source_hidden": false} -->
We can plot a point for Marrakesh as before using `geoviews.Points` (customized using `geoviews.opts`).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
marrakesh_point   = gv.Points([marrakesh_lonlat])
point_opts = opts.Points(
                          size=48,
                          alpha=0.25,
                          color='blue'
                        )
```

<!-- #region jupyter={"source_hidden": false} -->
Finally, we can overlay all these features on the basemap with the options applied.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
(basemap * rectangle * marrakesh_point).opts( rect_opts, point_opts )
```

<!-- #region jupyter={"source_hidden": false} -->
We'll use the approach above to visualize *Areas of Interest (AOIs)* when constructing search queries for NASA EarthData products. In particular, the convention of representing a bounding box by (left, lower, right, upper) ordinates is also used in the [PySTAC](https://pystac.readthedocs.io/en/stable/) API.
<!-- #endregion -->

***


## [hvPlot](https://hvplot.holoviz.org/)

<!-- #region jupyter={"source_hidden": false} -->
<center><img src="https://hvplot.holoviz.org/_images/diagram.svg"></img>
</center>

+ [hvPlot](https://hvplot.holoviz.org/) is designed to extend the `.plot` API from Pandas DataFrames.
+ It works for Pandas DataFrames and Xarray DataArrays/Datasets.
<!-- #endregion -->

***


### Plotting from a DataFrame with hvplot.pandas

<!-- #region jupyter={"source_hidden": false} -->
The code below loads a Pandas DataFrame of temperature data.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import pandas as pd, numpy as np
from pathlib import Path
LOCAL_PATH = Path(FILE_STEM, 'assets/temperature.csv')
```

```{code-cell} python jupyter={"source_hidden": false}
df = pd.read_csv(LOCAL_PATH, index_col=0, parse_dates=[0])
df.head()
```

***


#### Reviewing the Pandas DataFrame.plot API

<!-- #region jupyter={"source_hidden": false} -->
Let's extract a subset of columns from this DataFrame and generate a plot.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
west_coast = df[['Vancouver', 'Portland', 'San Francisco', 'Seattle', 'Los Angeles']]
west_coast.head()
```

<!-- #region jupyter={"source_hidden": false} -->
The Pandas DataFrame `.plot` API provides access to a number of plotting methods. Here, we'll use `.plot.line`, but a range of other options are available (e.g., `.plot.area`, `.plot.bar`, `.plot.hist`, `.plot.scatter`, etc.). This API has been repeated in several libraries due to its convenience.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
west_coast.plot.line(); # This produces a static Matplotlib plot
```

***


#### Using the hvPlot DataFrame.hvplot API

<!-- #region jupyter={"source_hidden": false} -->
By importing `hvplot.pandas`, a similar interactive plot can be generated. The API for `.hvplot` mimics that for `.plot`. For instance, we can generate the line plot above using `.hvplot.line`. In this case, the default plotting backend is Bokeh, so the plot is *interactive*.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import hvplot.pandas
west_coast.hvplot.line() # This produces an interactive Bokeh plot
```

<!-- #region jupyter={"source_hidden": false} -->
It is possible to modify the plot to make it cleaner.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
west_coast.hvplot.line(width=600, height=300, grid=True)
```

<!-- #region jupyter={"source_hidden": false} -->
The `hvplot` API also works when chained together with other DataFrame method calls. For instance, we can resample the temperature data and compute a mean to smooth it out.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
smoothed = west_coast.resample('2d').mean()
smoothed.hvplot.line(width=600, height=300, grid=True)
```

***


### Plotting from a DataArray with hvplot.xarray

<!-- #region jupyter={"source_hidden": false} -->
The Pandas `.plot` API was also extended to Xarray, i.e., for Xarray `DataArray`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import xarray as xr
import hvplot.xarray
import rioxarray as rio
```

<!-- #region jupyter={"source_hidden": false} -->
To start, load a local GeoTIFF file using `rioxarray` into an Zarray `DataArray` structure.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
LOCAL_PATH = Path(FILE_STEM, 'assets/OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif')
```

```{code-cell} python jupyter={"source_hidden": false}
data = rio.open_rasterio(LOCAL_PATH)
data
```

<!-- #region jupyter={"source_hidden": false} -->
We do some minor reformatting to the `DataArray`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data = data.squeeze() # to reduce 3D array with singleton dimension to 2D array
data = data.rename({'x':'easting', 'y':'northing'})
data
```

***


#### Reviewing the Xarray DataArray.plot API

<!-- #region jupyter={"source_hidden": false} -->
The `DataArray.plot` API by default uses Matplotlib's `pcolormesh` to display a 2D array stored within a `DataArray`. This takes a little time to render for this moderately high-resolution image.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
data.plot(); # by default, uses pcolormesh
```

***


#### Using the hvPlot DataArray.hvplot API

<!-- #region jupyter={"source_hidden": false} -->
Again, the `DataArray.hvplot` API mimics the `DataArray.plot` API; by default, it uses a subclass derived from `holoviews.element.raster.Image`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
plot = data.hvplot() # by default uses Image class
print(f'{type(plot)=}')
plot
```

<!-- #region jupyter={"source_hidden": false} -->
The result above is an interactive plot, rendered using Bokeh.It's a bit slow, but we can add some options to speed up rendering. It also requires cleaning up; for instance, the image is not square, the colormap does not highlight useful features, the axes are transposed, and so on.
<!-- #endregion -->

***


#### Building up options incrementally to improve plots

<!-- #region jupyter={"source_hidden": false} -->
Let's add options to improve the image. To do this, we'll initialize a Python dictionary `image_opts` to use within the call to the `image` method. We'll use the `dict.update` method to add key-value pairs to the dictionary incrementally, each time improving the output image.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(rasterize=True, dynamic=True)
pprint(image_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
To start, let's make the call to `hvplot.image` explicit & specify the sequence of axes. & apply the options from the dictionary `image_opts`. We'll use the dict-unpacking operation `**image_opts` each time we invoke `data.hvplot.image`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->
Next, let's fix the aspect ratio and image dimensions.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts.update(frame_width=500, frame_height=500, aspect='equal')
pprint(image_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->
The image colormap is a bit unpleasant; let's change it and use transparency (`alpha`).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts.update( cmap='hot_r', clim=(0,100), alpha=0.8 )
pprint(image_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->
Before adding a basemap, we need to account for the coordinate system. This is stored in the GeoTIFF file and, when read using `rioxarray.open_rasterio`, it is available by using the attribute `data.rio.crs`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
crs = data.rio.crs
crs
```

<!-- #region jupyter={"source_hidden": false} -->
We can use the CRS recovered above as an optional argument to `hvplot.image`. Notice the coordinates have changed on the axes, but the labels are wrong. We can fix that shortly.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts.update(crs=crs)
pprint(image_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->
Let's now fix the labels. We'll use the Holoviews/GeoViews `opts` system to specify these options.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
label_opts = dict(title='VEG_ANOM_MAX', xlabel='Longitude (degrees)', ylabel='Latitude (degrees)')
pprint(image_opts)
pprint(label_opts)
plot = data.hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot
```

<!-- #region jupyter={"source_hidden": false} -->
Let's overlay the image on a basemap so we can see the terrain underneath.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
base = gv.tile_sources.ESRI
base * plot
```

<!-- #region jupyter={"source_hidden": false} -->
Finally, the white pixels are distracting; let's filter them out using the `DataArray` method `where`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
plot = data.where(data>0).hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot * base
```

<!-- #region jupyter={"source_hidden": false} -->
In this notebook, we applied some common strategies to generate plots. We'll use these extensively in the rest of the tutorial.
<!-- #endregion -->

***

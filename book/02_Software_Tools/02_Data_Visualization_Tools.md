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

# Data Visualization

<!-- #region jupyter={"source_hidden": true} -->
The primary tools we'll use for plotting come from the [Holoviz](https://holoviz.org/) family of Python libraries, principally [GeoViews](https://geoviews.org/) and [hvPlot](https://hvplot.holoviz.org/). These are largely built on top of [HoloViews](https://holoviews.org/) and support multiple backends for rendering plots (notably [Bokeh](http://bokeh.pydata.org/) for interactive visualization and [Matplotlib](http://matplotlib.org/) for static, publication-quality plots).
<!-- #endregion -->

## [GeoViews](https://geoviews.org/)

<!-- #region jupyter={"source_hidden": true} -->
From the [GeoViews documentation](https://geoviews.org/index.html):

> GeoViews is a [Python](http://python.org/) library that makes it easy to explore and visualize geographical, meteorological, and oceanographic datasets, such as those used in weather, climate, and remote sensing research.
>
> GeoViews is built on the [HoloViews](http://holoviews.org/) library for building flexible visualizations of multidimensional data. GeoViews adds a family of geographic plot types based on the [Cartopy](http://scitools.org.uk/cartopy) library, plotted using either the [Matplotlib](http://matplotlib.org/) or [Bokeh](http://bokeh.pydata.org/) packages. With GeoViews, you can now work easily and naturally with large, multidimensional geographic datasets, instantly visualizing any subset or combination of them, while always being able to access the raw data underlying any plot.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

import geoviews as gv
gv.extension('bokeh')
from geoviews import opts
```

### Displaying a basemap

<!-- #region jupyter={"source_hidden": true} -->
- Principal utility is `gv.tile_sources`
- Use the method `opts` to specify optional settings
- Bokeh menu at right enables interactive exploration
<!-- #endregion -->

```python jupyter={"source_hidden": true}
basemap = gv.tile_sources.OSM.opts(width=600, height=400)
basemap
```

### Plotting points

<!-- #region jupyter={"source_hidden": true} -->
To get started, let's define a regular Python tuple for the longitude-latitude coordinates of Tokyo, Japan.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
tokyo_lonlat = (139.692222, 35.689722)
print(tokyo_lonlat)
```

<!-- #region jupyter={"source_hidden": true} -->
+ `geoviews.Points` accepts a list of tuples (each of the form `(x, y)`) to plot.
+ Use the OpenStreetMap tiles from `gv.tile_sources.OSM` as a basemap.
+ Overlay using the Holoviews operator `*`
+ Define the options using `geoviews.opts`
+ ? find a way to initialize the zoom level sensibly?
<!-- #endregion -->

```python jupyter={"source_hidden": true}
tokyo_point   = gv.Points([tokyo_lonlat])
point_opts = opts.Points(
                          size=48,
                          alpha=0.5,
                          color='red'
                        )
```

```python jupyter={"source_hidden": true}
# Use Holoviews * operator to overlay plot on basemap
# Note: zoom out to see basemap (starts zoomed "all the way in")
(basemap * tokyo_point).opts(point_opts)
```

```python jupyter={"source_hidden": true}
# to avoid starting zoomed all the way in, this zooms "all the way out"
(basemap * tokyo_point).opts(point_opts, opts.Overlay(global_extent=True))
```

### Plotting rectangles

<!-- #region jupyter={"source_hidden": true} -->
+ Standard way to represent rectangle with corners
  $$(x_{\mathrm{min}},y_{\mathrm{min}}), (x_{\mathrm{min}},y_{\mathrm{max}}), (x_{\mathrm{max}},y_{\mathrm{min}}), (x_{\mathrm{max}},y_{\mathrm{max}})$$
  (assuming $x_{\mathrm{max}}>x_{\mathrm{min}}$ & $y_{\mathrm{max}}>y_{\mathrm{min}}$) is as a single 4-tuple
  $$(x_{\mathrm{min}},y_{\mathrm{min}},x_{\mathrm{max}},y_{\mathrm{max}}),$$
  i.e., the lower,left corner coordinates followed by the upper, right corner coordinates.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# simple utility to make a rectangle of "half-width" dx & "half-height" dy & centred pt
def bounds(pt,dx,dy):
    '''Returns rectangle represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), half-width & half-height dx & dy respectively,
    where x_lo = x-dx, x_hi=x+dx, y_lo = y-dy, y_hi = y+dy.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx,dy)))
```

```python jupyter={"source_hidden": true}
# Verify that the function bounds works as intended
marrakesh_lonlat = (-7.93, 31.67)
dlon, dlat = 0.25, 0.25
marrakesh_rect = bounds(marrakesh_lonlat, dlon, dlat)
print(marrakesh_rect)
```

<!-- #region jupyter={"source_hidden": true} -->
+ `geoviews.Rectangles` accepts a list of bounding boxes (each described by a tuple of the form `(x_min, y_min, x_max, y_max)`) to plot.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
rect_opts = opts.Rectangles(
                                line_width=0,
                                alpha=0.25,
                                color='red'
                            )
```

```python jupyter={"source_hidden": true}
rectangle = gv.Rectangles([marrakesh_rect])
(basemap * rectangle).opts( rect_opts )
```

<!-- #region jupyter={"source_hidden": true} -->
We'll use the approach above to visualize *Areas of Interest (AOIs)* when constructing search queries for NASA EarthData products. In particular, the convention of representing a bounding box by (left, lower, right, upper) ordinates is also used in the [PySTAC](https://pystac.readthedocs.io/en/stable/) API.

---
<!-- #endregion -->

## [hvPlot](https://hvplot.holoviz.org/)

<!-- #region jupyter={"source_hidden": true} -->
+ [hvPlot](https://hvplot.holoviz.org/) is designed to extend the `.plot` API from Pandas DataFrames.
+ It works for Pandas DataFrames and Xarray DataArrays/Datasets.
<!-- #endregion -->

### Plotting from a DataFrame with hvplot.pandas

<!-- #region jupyter={"source_hidden": true} -->
The code below loads a Pandas DataFrame of temperature data.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
import pandas as pd, numpy as np
from pathlib import Path
LOCAL_PATH = Path().cwd() / '..' / 'assets' / 'temperature.csv'
```

```python jupyter={"source_hidden": true}
df = pd.read_csv(LOCAL_PATH, index_col=0, parse_dates=[0])
df.head()
```

#### Reviewing the Pandas DataFrame.plot API

<!-- #region jupyter={"source_hidden": true} -->
Let's extract a subset of columns from this DataFrame and generate a plot.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
west_coast = df[['Vancouver', 'Portland', 'San Francisco', 'Seattle', 'Los Angeles']]
west_coast.head()
```

<!-- #region jupyter={"source_hidden": true} -->
The Pandas DataFrame `.plot` API provides access to a number of plotting methods. Here, we'll use `.plot.line`, but a range of other options are available (e.g., `.plot.area`, `.plot.bar`, `.plot.hist`, `.plot.scatter`, etc.). This API has been repeated in several libraries due to its convenience.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
west_coast.plot.line(); # This produces a static Matplotlib plot
```

#### Using the hvPlot DataFrame.hvplot API

<!-- #region jupyter={"source_hidden": true} -->
By importing `hvplot.pandas`, a similar interactive plot can be generated. The API for `.hvplot` mimics that for `.plot`. For instance, we can generate the line plot above using `.hvplot.line`. In this case, the default plotting backend is Bokeh, so the plot is *interactive*.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
import hvplot.pandas
west_coast.hvplot.line() # This produces an interactive Bokeh plot
```

<!-- #region jupyter={"source_hidden": true} -->
It is possible to modify the plot to make it cleaner.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
west_coast.hvplot.line(width=600, height=300, grid=True)
```

<!-- #region jupyter={"source_hidden": true} -->
The `hvplot` API also works when chained together with other DataFrame method calls. For instance, we can resample the temperature data and compute a mean to smooth it out.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
smoothed = west_coast.resample('2d').mean()
smoothed.hvplot.line(width=600, height=300, grid=True)
```

### Plotting from a DataArray with hvplot.xarray

<!-- #region jupyter={"source_hidden": true} -->
The Pandas `.plot` API was also extended to Xarray, i.e., for Xarray `DataArray`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
import xarray as xr
import hvplot.xarray
import rioxarray as rio
```

<!-- #region jupyter={"source_hidden": true} -->
To start, load a local GeoTIFF file using `rioxarray` into an Zarray `DataArray` structure.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
LOCAL_PATH = Path('..') / 'assets' / 'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'
```

```python jupyter={"source_hidden": true}
data = rio.open_rasterio(LOCAL_PATH)
data
```

<!-- #region jupyter={"source_hidden": true} -->
We do some minor reformatting to the `DataArray`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data = data.squeeze() # to reduce 3D array with singleton dimension to 2D array
data = data.rename({'x':'easting', 'y':'northing'})
data
```

#### Reviewing the Xarray DataArray.plot API

<!-- #region jupyter={"source_hidden": true} -->
The `DataArray.plot` API by default uses Matplotlib's `pcolormesh` to display a 2D array stored within a `DataArray`. This takes a little time to render for this moderately high-resolution image.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data.plot(); # by default, uses pcolormesh
```

#### Using the hvPlot DataArray.hvplot API

<!-- #region jupyter={"source_hidden": true} -->
Again, the `DataArray.hvplot` API mimics the `DataArray.plot` API; by default, it uses a subclass derived from `holoviews.element.raster.Image`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
plot = data.hvplot() # by default uses Image class
print(f'{type(plot)=}')
plot
```

<!-- #region jupyter={"source_hidden": true} -->
The result above is an interactive plot, rendered using Bokeh.It's a bit slow, but we can add some options to speed up rendering. It also requires cleaning up; for instance, the image is not square, the colormap does not highlight useful features, the axes are transposed, and so on.
<!-- #endregion -->

#### Building up options incrementally to improve plots

<!-- #region jupyter={"source_hidden": true} -->
Let's add options to improve the image. To do this, we'll initialize a Python dictionary `image_opts` to use within the call to the `image` method. We'll use the `dict.update` method to add key-value pairs to the dictionary incrementally, each time improving the output image.
<!-- #endregion -->

```python
image_opts = dict(rasterize=True, dynamic=True)
```

<!-- #region jupyter={"source_hidden": true} -->
To start, let's make the call to `hvplot.image` explicit & specify the sequence of axes. & apply the options from the dictionary `image_opts`. We'll use the dict-unpacking operation `**image_opts` each time we invoke `data.hvplot.image`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->
Next, let's fix the aspect ratio and image dimensions.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts.update(frame_width=500, frame_height=500, aspect='equal')

plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->
The image colormap is a bit unpleasant; let's change it and use transparency (`alpha`).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts.update( cmap='hot_r', clim=(0,100), alpha=0.8 )
plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->
Before adding a basemap, we need to account for the coordinate system. This is stored in the GeoTIFF file and, when read using `rioxarray.open_rasterio`, it is available by using the attribute `data.rio.crs`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
crs = data.rio.crs
crs
```

<!-- #region jupyter={"source_hidden": true} -->
We can use the CRS recovered above as an optional argument to `hvplot.image`. Notice the coordinates have changed on the axes, but the labels are wrong. We can fix that shortly.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts.update(crs=crs)

plot = data.hvplot.image(x='easting', y='northing', **image_opts)
plot
```

Let's now fix the labels. We'll use the Holoviews/GeoViews `opts` system to specify these options.

```python jupyter={"source_hidden": true}
label_opts = dict(title='VEG_ANOM_MAX', xlabel='Longitude (degrees)', ylabel='Latitude (degrees)')
plot = data.hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot
```

<!-- #region jupyter={"source_hidden": true} -->
Let's overlay the image on a basemap so we can see the terrain underneath.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
base = gv.tile_sources.ESRI
base * plot
```

<!-- #region jupyter={"source_hidden": true} -->
Finally, the white pixels are distracting; let's filter them out using the `DataArray` method `where`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
plot = data.where(data>0).hvplot.image(x='easting', y='northing', **image_opts).opts(**label_opts)
plot * base
```

<!-- #region jupyter={"source_hidden": true} -->
In this notebook, we applied some common strategies to generate plots. We'll use these extensively in the rest of the tutorial.
<!-- #endregion -->

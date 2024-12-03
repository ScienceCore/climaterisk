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

# Constructing Advanced Visualizations

<!-- #region jupyter={"source_hidden": false} -->
Let's apply some of the tools we've seen so far to make some more sophisticated visualizations. These will include using vector data from a *GeoPandas* `GeoDataFrame`, constructing both static plots and dynamic views from a 3D array, and combining vector data and raster data.

As context, the files we'll examine are based on [the 2022 McKinney widfire](https://en.wikipedia.org/wiki/McKinney_Fire) in Klamath National Forest (western Siskiyou County, California). The vector data is a snapshot of the boundary of a wildfire; the raster data corresponds to the  observed *land surface disturbance*  of vegetation (this will be explained in greater detail later).
<!-- #endregion -->

## Preliminary imports and file paths

<!-- #region jupyter={"source_hidden": false} -->
To begin, some typical package imports are needed. We'll also define some paths to local files containing relevant geospatial data.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
from warnings import filterwarnings
filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
import geopandas as gpd
import rioxarray as rio
```

```{code-cell} python jupyter={"source_hidden": false}
# Imports for plotting
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```{code-cell} python jupyter={"source_hidden": false}
FILE_STEM = Path.cwd().parent if 'book' == Path.cwd().parent.stem else 'book'
ASSET_PATH = Path(FILE_STEM, 'assets')
SHAPE_FILE = ASSET_PATH / 'shapefiles' / 'mckinney' / 'McKinney_NIFC.shp'
RASTER_FILES = list(ASSET_PATH.glob('OPERA*VEG*.tif'))
RASTER_FILE = RASTER_FILES[0]
```

***


## Plotting vector data from a `GeoDataFrame`

<!-- #region jupyter={"source_hidden": false} -->
<img src="https://geopandas.org/en/latest/_images/geopandas_logo.png" width=360px></img>

The [GeoPandas](https://geopandas.org/en/stable/index.html) package contains many useful tools for working with vector geospatial data. In particular, the [GeoPandas `GeoDataFrame`](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html) is a subclass of the Pandas DataFrame that is specifically tailored for vector data stored in, e.g.,  *shapefiles*.

As an example, let's load some vector data from the local path `SHAPEFILE` (as defined above).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shape_df = gpd.read_file(SHAPE_FILE)
shape_df
```

<!-- #region jupyter={"source_hidden": false} -->
The object `shape_df` is a [`GeoDataFrame`]((https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html)) that has over two dozen columns of metadata in a single row. The main column that concerns us is the `geometry` column; this column stores the coordinates of the vertices of a `MULTIPOLYGON`, i.e., a set of polygons.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shape_df.geometry 
```

<!-- #region jupyter={"source_hidden": false} -->
The vertices of the polygons seem to be expressed as `(longitude, latitude)` pairs. We can verify what specific coordinate system is used by examining the `GeoDataFrame`'s `crs` attribute.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(shape_df.crs)
```

<!-- #region jupyter={"source_hidden": false} -->
Let's use `hvplot` to generate a plot of this vector dataset.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shape_df.hvplot()
```

<!-- #region jupyter={"source_hidden": false} -->
The projection in this plot is a bit strange. The HoloViz documentation includes a [discussion of considerations when plotting geographic data](https://hvplot.holoviz.org/user_guide/Geographic_Data.html); the salient point to remember in this immediate context is that the option `geo=True` is useful.

Let's create two Python dictionaries—`shapeplot_opts` & `layout_opts`—and build up a visualization.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts= dict(geo=True)
layout_opts = dict(xlabel='Longitude', ylabel="Latitude")
print(f"{shapeplot_opts=}")
print(f"{layout_opts=}")

shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
We can augment the plot by updating `shapeplot_opts`.
+ Specifying `color=None` means that the polygons will not be filled.
+ Specifying `line_width` and `line_color` modifies the appearance of the boundaries of the polygons.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts.update( color=None ,
                       line_width=2,
                       line_color='red')
print(shapeplot_opts)

shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
Let's fill the polygons with, say, `color=orange`  and make the filled area partially transparent by specifying an `alpha` value between zero and one.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts.update(color='orange', alpha=0.25)
print(shapeplot_opts)

shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

### Adding a basemap

<!-- #region jupyter={"source_hidden": false} -->
Next, let's provide a basemap and overlay the plotted polygons using the `*` operator. Notice the use of parentheses to apply the `opts` method to the output of the `*` operator.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
basemap = gv.tile_sources.ESRI(height=500, width=500, padding=0.1)

(shape_df.hvplot(**shapeplot_opts) * basemap).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
The basemap does not need to be overlayed as as separate object; it can be specified using the `tiles` keyword. For instance, setting `tiles='OSM'` uses [OpenStreetMap](ttps://www.openstreetmap.org) tiles instead. Notice the dimensions of the image rendered are likely not the same as the previous image with the [ESRI](https://www.esri.com) tiles because we explicitly specified `height=500` & `width=500` in defining `basemap` earlier.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
shapeplot_opts.update(tiles='OSM')
shape_df.hvplot(**shapeplot_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
Let's remove the `tiles` option from `shapeplot_opts` and bind the resulting plot object to the identifier `shapeplot`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
del shapeplot_opts['tiles']
print(shapeplot_opts)

shapeplot = shape_df.hvplot(**shapeplot_opts)
shapeplot
```

### Combining vector data with raster data in a static plot

<!-- #region jupyter={"source_hidden": false} -->
Let's combine this vector data with some raster data. We'll load raster data from a local file using the function `rioxarray.open_rasterio`. For convenience, we'll use method-chaining to relabel the coordinates of the `DataArray` loaded and use the `squeeze` method to convert the three-dimensional array loaded into a two-dimensional array.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster = (
          rio.open_rasterio(RASTER_FILE)
            .rename(dict(x='longitude', y='latitude'))
            .squeeze()
         )
raster
```

<!-- #region jupyter={"source_hidden": false} -->
We'll use a Python dictionary `image_opts` to store useful keyord arguments to pass to `hvplot.image`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(
                    x='longitude',
                    y='latitude',                   
                    rasterize=True, 
                    dynamic=True,
                    cmap='hot_r', 
                    clim=(0, 100), 
                    alpha=0.8,
                    project=True,
                 )

raster.hvplot.image(**image_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
We can overlay `shapeplot` with the plotted raster data using the `*` operator. We can use the `Pan`, `Wheel Zoom`, and `Box Zoom` tools in the Bokeh toolbar to the right of the plot to zoom in and verify that the vector data has in fact been plotted on top of the raster data.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster.hvplot.image(**image_opts) * shapeplot
```

<!-- #region jupyter={"source_hidden": false} -->
We can additionally overlay the vector & raster data onto ESRI tiles using `basemap`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster.hvplot.image(**image_opts) * shapeplot * basemap
```

<!-- #region jupyter={"source_hidden": false} -->
Notice many of the white pixels are obscuring the plot. It turns out that these pixels correspond to zeros in the raster data that can safely be ignored. We can filter those out using the `where` method.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster = raster.where((raster!=0))
layout_opts.update(title="McKinney 2022 Wildfires")

(raster.hvplot.image(**image_opts) * shapeplot * basemap).opts(**layout_opts)
```

***


## Constructing static plots from a 3D array

<!-- #region jupyter={"source_hidden": false} -->
Let's load a sequence of raster files into a three-dimensional array and produce some plots. To start, we'll construct a loop to read `DataArrays` from the files `RASTER_FILES` and we'll use `xarray.concat` to produce a single three-dimensional array of rasters (i.e., three $3,600\times3,600$ rasters stacked vertically).  We'll learn the specific interpretations associated with the raster dataset in a later notebook; for now, let's just treat them as raw data to experiment with.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack = []
for path in RASTER_FILES:
    data = rio.open_rasterio(path).rename(dict(x='longitude', y='latitude'))
    band_name = path.stem.split('_')[-1]
    data.coords.update({'band': [band_name]})
    data.attrs = dict(description=f"OPERA DIST product", units=None)
    stack.append(data)

stack = xr.concat(stack, dim='band')
stack = stack.where(stack!=0)
```

<!-- #region jupyter={"source_hidden": false} -->
We relabel the axes `longitude` & `latitude` and we filter out pixels with value zero to make plotting simpler later.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack
```

<!-- #region jupyter={"source_hidden": false} -->
Having built the `DataArray` `stack`, we can focus on visualization.

If we want to generate a static plot with several images laid out, we can use `hvplot.image` together with the `.layout` method. To see how this works, let's start by redefining dictionaries `image_opts` and `layout_opts`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(  x='longitude', 
                    y='latitude',
                    rasterize=True, 
                    dynamic=True,
                    cmap='hot_r',
                    crs=stack.rio.crs,
                    alpha=0.8,
                    project=True, 
                    aspect='equal',
                    shared_axes=False,
                    colorbar=True,
                    tiles='ESRI',
                    padding=0.1)
layout_opts = dict(xlabel='Longitude', ylabel="Latitude")
```

<!-- #region jupyter={"source_hidden": false} -->
To speed up rendering, we'll initially construct an object `view` that selects subsets of pixels; we initially define the parameter `steps=200` to restrict the view to every 200th pixel in either direction. If we reduce `steps`, it takes longer to render. Setting `steps=1` or `steps=None` is equivalent to selecting all pixels.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 200
subset = slice(0, None, steps)
layout_opts.update(frame_width=250, frame_height=250)


view = stack.isel(latitude=subset, longitude=subset)
view.hvplot.image(**image_opts).opts(**layout_opts).layout()
```

<!-- #region jupyter={"source_hidden": false} -->
The `layout` method by default plotted each of the three rasters selected along the `band` axis horizontally.
<!-- #endregion -->

***


## Constructing a dynamic view from a 3D array

<!-- #region jupyter={"source_hidden": false} -->
Another way to visualize a three-dimensional array is to associate a selection widget with one of the axes. If we call `hvplot.image` without appending the `.layout` method, the result is a *dynamic map*. In this instance, the selection widget allows us to choose slices from along the `band` axis.

Again, increasing the parameter `steps` reduces the rendering time. Decreasing it to `1` or `None` renders at full resolution.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 200
subset = slice(0, None, steps)
layout_opts.update(frame_height=400, frame_width=400)

view = stack.isel(latitude=subset, longitude=subset)
view.hvplot.image(**image_opts).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
Later, we'll stack many rasters with distinct timestamps along a `time` axis; when there are many slices, the selection widget will be rendered as a slider rather than as a drop-down menu. We can control the location of the widget using a keyword option `widget_location`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
view.hvplot.image(widget_location='bottom_left', **image_opts, **layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
Notice adding the `widget_location` option does slightly modify the sequence in which options are specified. That is, if we invoke something like
```python
view.hvplot.image(widget_location='top_left', **image_opts).opts(**layout_opts)
```
an exception is raised (hence the invocation in the code cell above). There are some subtle difficulties in working out the correct sequence to apply options when customizing HoloViz/Hvplot objects (mainly due to the ways in which namespaces overlap with Bokeh or other rendering back-ends). The best strategy is to start with as few options as possible and to experiment by incrementally adding options until we get the final visualization we want.
<!-- #endregion -->

***


### Combining vector data with raster data in a dynamic view

<!-- #region jupyter={"source_hidden": false} -->
Finally, let's overlay our vector data from before—the boundary of the wildfire—with the dynamic view of this three-dimensional array of rasters. We can use the `*` operator to combine the output of `hvplot.image` with `shapeplot`, the rendered view of the vector data.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 200
subset = slice(0, None, steps)
view = stack.isel(latitude=subset, longitude=subset)

image_opts.update(colorbar=False)
layout_opts.update(frame_height=500, frame_width=500)
(view.hvplot.image(**image_opts) * shapeplot).opts(**layout_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
Again, getting the options specified correctly can take a bit of experimentation. The important ideas to take away here are:
+ how to load relevant datasets with `geopandas` and `rioxarray`; and
+ how to use `hvplot` interactively & incrementally to produce compelling visualizations.
<!-- #endregion -->

***

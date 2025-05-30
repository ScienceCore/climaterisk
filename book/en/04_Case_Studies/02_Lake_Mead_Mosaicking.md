---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Generating a Mosaicked Image of Lake Mead

<!-- #region jupyter={"source_hidden": false} -->
[Lake Mead](https://en.wikipedia.org/wiki/Lake_Mead) is a water reservoir in southwestern United States and is significant for irrigation in neighboring states. The lake has experienced significant drought over the past decade and particularly between 2020 & 2023. In this notebook, we'll find GeoTIFF data related to this lake and synthesize several raster files to produce a plot.

***
<!-- #endregion -->

## Outline of steps for analysis

<!-- #region jupyter={"source_hidden": false} -->
+ Identifying search parameters
    + AOI, time-window
    + Endpoint, Provider, catalog identifier ("short name")
+ Obtaining search results
    + Instrospect, examine to identify features, bands of interest
    + Wrap results into a DataFrame for easier exploration
+ Exploring & refining search results
    + Identify granules of highest value
    + Filter extraneous granules with minimal contribution
    + Assemble relevant filtered granules into DataFrame
    + Identify kind of output to generate
+ Data-wrangling to produce relevant output
    + Download relevant granules into Xarray DataArray, stacked appropriately
    + Do intermediate computations as necessary
    + Assemble relevant data slices into visualization
<!-- #endregion -->

***


### Preliminary imports

```{code-cell} python jupyter={"source_hidden": false}
from warnings import filterwarnings
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
```

```{code-cell} python jupyter={"source_hidden": false}
# Imports for plotting
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
from bokeh.models import FixedTicker
```

```{code-cell} python jupyter={"source_hidden": false}
# STAC imports to retrieve cloud data
from pystac_client import Client
from osgeo import gdal
# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')
```

### Convenient utilities

<!-- #region jupyter={"source_hidden": false} -->
These functions could be placed in module files for more developed research projects. For learning purposes, they are embedded within this notebook.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
# simple utility to make a rectangle with given center of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding-box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

```{code-cell} python jupyter={"source_hidden": false}
# simple utility to plot an AOI or bounding-box
def plot_bbox(bbox):
    '''Given bounding-box, returns GeoViews plot of Rectangle & Point at center
    + bbox: bounding-box specified as (lon_min, lat_min, lon_max, lat_max)
    Assume longitude-latitude coordinates.
    '''
    # These plot options are fixed but can be over-ridden
    point_opts = opts.Points(size=12, alpha=0.25, color='blue')
    rect_opts = opts.Rectangles(line_width=0, alpha=0.1, color='red')
    lon_lat = (0.5*sum(bbox[::2]), 0.5*sum(bbox[1::2]))
    return (gv.Points([lon_lat]) * gv.Rectangles([bbox])).opts(point_opts, rect_opts)
```

```{code-cell} python jupyter={"source_hidden": false}
# utility to extract search results into a Pandas DataFrame
def search_to_dataframe(search):
    '''Constructs Pandas DataFrame from PySTAC Earthdata search results.
    DataFrame columns are determined from search item properties and assets.
    'asset': string identifying an Asset type associated with a granule
    'href': data URL for file associated with the Asset in a given row.'''
    granules = list(search.items())
    assert granules, "Error: empty list of search results"
    props = list({prop for g in granules for prop in g.properties.keys()})
    tile_ids = map(lambda granule: granule.id.split('_')[3], granules)
    rows = (([g.properties.get(k, None) for k in props] + [a, g.assets[a].href, t])
                for g, t in zip(granules,tile_ids) for a in g.assets )
    df = pd.concat(map(lambda x: pd.DataFrame(x, index=props+['asset','href', 'tile_id']).T, rows),
                   axis=0, ignore_index=True)
    assert len(df), "Empty DataFrame"
    return df
```

```{code-cell} python jupyter={"source_hidden": false}
# utility to remap pixel values to a sequence of contiguous integers
def relabel_pixels(data, values, null_val=255, transparent_val=0, replace_null=True, start=0):
    """
    This function accepts a DataArray with a finite number of categorical values as entries.
    It reassigns the pixel labels to a sequence of consecutive integers starting from start.
    data:            Xarray DataArray with finitely many categories in its array of values.
    null_val:        (default 255) Pixel value used to flag missing data and/or exceptions.
    transparent_val: (default 0) Pixel value that will be fully transparent when rendered.
    replace_null:    (default True) Maps null_value->transparent_value everywhere in data.
    start:           (default 0) starting range of consecutive integer values for new labels.
    The values returned are:
    new_data:        Xarray DataArray containing pixels with new values
    relabel:         dictionary associating old pixel values with new pixel values
    """
    new_data = data.copy(deep=True)
    if values:
        values = np.sort(np.array(values, dtype=np.uint8))
    else:
        values = np.sort(np.unique(data.values.flatten()))
    if replace_null:
        new_data = new_data.where(new_data!=null_val, other=transparent_val)
        values = values[np.where(values!=null_val)]
    n_values = len(values)
    new_values = np.arange(start=start, stop=start+n_values, dtype=values.dtype)
    assert transparent_val in new_values, f"{transparent_val=} not in {new_values}"
    relabel = dict(zip(values, new_values))
    for old, new in relabel.items():
        if new==old: continue
        new_data = new_data.where(new_data!=old, other=new)
    return new_data, relabel
```

***


## Identifying search parameters

<!-- #region jupyter={"source_hidden": false} -->
We'll identify a geographic point near the north shore of [Lake Mead](https://en.wikipedia.org/wiki/Lake_Mead), make a bounding box, and choose a date range that covers Marh and part of April 2023.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
lake_mead = (-114.754, 36.131)
AOI = make_bbox(lake_mead, 0.1, 0.1)
DATE_RANGE = "2023-03-01/2023-04-15"
```

```{code-cell} python jupyter={"source_hidden": false}
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(width=500, height=500, padding=0.1)
plot_bbox(AOI) * basemap
```

```{code-cell} python jupyter={"source_hidden": false}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

***


## Obtaining search results

<!-- #region jupyter={"source_hidden": false} -->
As usual, we'll specify the search endpoint, provider, & catalog. For the DSWx family of data products these are as follows.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = 'POCLOUD'
COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```{code-cell} python jupyter={"source_hidden": false}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

<!-- #region jupyter={"source_hidden": false} -->
We convert the search results to a `DataFrame` for easier perusal.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df = search_to_dataframe(search_results)
display(df.head())
df.info()
```

<!-- #region jupyter={"source_hidden": false} -->
We'll clean the DataFrame `df` in standard ways by:
+ dropping the `start_datetime` & `end_datetime` columns;
+ renaming the `eo:cloud_cover` column;
+ converting the columns to suitable datatypes; and
+ assigning the `datetime` column as the index.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.datetime = pd.DatetimeIndex(df.datetime)
df = df.drop(['start_datetime', 'end_datetime'], axis=1)
df = df.rename({'eo:cloud_cover':'cloud_cover'}, axis=1)
df['cloud_cover'] = df['cloud_cover'].astype(np.float16)
for col in ['asset', 'href', 'tile_id']:
    df[col] = df[col].astype(pd.StringDtype())
df = df.set_index('datetime').sort_index()
```

```{code-cell} python jupyter={"source_hidden": false}
display(df.head())
df.info()
```

***


## Exploring & refining search results

<!-- #region jupyter={"source_hidden": false} -->
We can look at the `assets` column to see which different bands are available in the results returned.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.asset.value_counts()
```

<!-- #region jupyter={"source_hidden": false} -->
The `0_B01_WTR` band is the one that we want to work with later.

We can also see how much cloud cover there is in our search results.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.cloud_cover.agg(['min','mean','median','max'])
```

<!-- #region jupyter={"source_hidden": false} -->
We can extract selected rows from the `DataFrame` using boolean `Series`. Specifically, we'll select the rows that have less than 10% cloud cover and in which the `asset` is the `0_B01_WTR` band.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
c1 = (df.cloud_cover <= 10)
c2 = (df.asset.str.contains('B01_WTR'))
b01_wtr = df.loc[c1 & c2].drop(['asset', 'cloud_cover'], axis=1)
b01_wtr
```

<!-- #region jupyter={"source_hidden": false} -->
Finally, we can see how many different MGRS tiles intersect our AOI.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
b01_wtr.tile_id.value_counts()
```

<!-- #region jupyter={"source_hidden": false} -->
There are four distinct geographic tiles that intersect this particular AOI.

***
<!-- #endregion -->

## Data-wrangling to produce relevant output

<!-- #region jupyter={"source_hidden": false} -->
This time, we'll use a technique called *mosaicking* to combine raster data from adjacent tiles into a single raster data set. This requires the `rasterio.merge.merge` function as before. We'll also need the function `rasterio.transform.array_bounds` to get the coordinates aligned properly.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import rasterio
from rasterio.merge import merge
from rasterio.transform import array_bounds
```

<!-- #region jupyter={"source_hidden": false} -->
We've used the function `merge` before to combine distinct raster data sets associated with a single MGRS tile. This time, the raster data merged will come from adjacent MGRS tiles. In calling the `merge` function in the next code cell, the column `b01_wtr.href` will be treated as a list of URLs ([Uniform Resource Locators](https://en.wikipedia.org/wiki/Uniform_Resource_Locator)). For each URL in that list, a GeoTIFF file will be downloaded and processed. The net result is a mosaicked image, i.e., a merged raster that contains a combination of all the rasters. The specifics of the merging algorithm are described in the [`rasterio.merge` module documentation](https://rasterio.readthedocs.io/en/latest/api/rasterio.merge.html).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
%%time
mosaicked_img, mosaic_transform = merge(b01_wtr.href)
```

<!-- #region jupyter={"source_hidden": false} -->
The output again consists of a NumPy array and coordinate transformation. 
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(f"{type(mosaicked_img)=}\n")
print(f"{mosaicked_img.shape=}\n")
print(f"{type(mosaic_transform)=}\n")
print(f"{mosaic_transform=}\n")
```

<!-- #region jupyter={"source_hidden": false} -->
The entries of `mosaic_transform` describe an [*affine transformation*](https://en.wikipedia.org/wiki/Affine_transformation) from pixel coordinates to continuous UTM coordinates. In particular:

+ the entry `mosaic_transform[0]` is the horizontal width of each pixel in metres; and
+ the entry `mosaic_transform[4]` is the vertical height of each pixel in metres.
  
Notice also that, in this instance, `mosaic_transform[4]` is a negative value (i.e., `mosaic_transform[4]==-30.0`). This tells us that the orientation of the continuous coordinate vertical axis opposes the orientation of the vertical pixel coordinate axis, i.e., the vertical continuous coordinate decreases in a downwards direction unlike the vertical pixel coordinate.

When we pass the object `mosaic_transform` into the `rasterio.transform.array_bounds` function, the value returned is a bounding-box, i.e., a tuple of the form `(x_min, y_min, x_max, y_max)` describing the lower-left and upper-right corners of the resulting mosaicked image in continuous UTM coordinates. 
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
bounds = array_bounds(*mosaicked_img.shape[1:], mosaic_transform)

bounds
```

<!-- #region jupyter={"source_hidden": false} -->
Combining all the preceding information allows us to reconstruct the continuous UTM coordinates associated with each pixel. We'll compute arrays for these continuous coordinates and label them `longitude` and `latitude`. These coordinates would more accurately be called `easting` and `northing`, but we'll use the labels `longitude` and `latitude` respectively when we attach the coordinate arrays to an Xarray `DataArray`. We choose these labels because, when the raster data is plotted with `hvplot.image`, the output will use longitude-latitude coordinates.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
longitude = np.arange(bounds[0], bounds[2], mosaic_transform[0])
latitude = np.arange(bounds[3], bounds[1], mosaic_transform[4])
```

<!-- #region jupyter={"source_hidden": false} -->
We'll wrap the mosaicked image and the relevant metadata into an Xarray `DataArray`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster = xr.DataArray(
        data=mosaicked_img,
        dims=["band", "latitude", "longitude"],
        coords=dict(
            longitude=(["longitude"], longitude),
            latitude=(["latitude"], latitude),
        ),
        attrs=dict(
            description="OPERA DSWx B01",
            units=None,
        ),
    )
raster
```

<!-- #region jupyter={"source_hidden": false} -->
We need to attach a CRS object to the `raster` object. To do so, we'll use `rasterio.open` to load the relevant metadata from one of the granules associated with `b01_wtr` (these should be the same for all these particular files).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
with rasterio.open(b01_wtr.href[0]) as ds:
    crs = ds.crs

raster.rio.write_crs(crs, inplace=True)
print(raster.rio.crs)
```

<!-- #region jupyter={"source_hidden": false} -->
In research code, we could bundle the preceding commands within a function and save that to a module. We won't do that here because, for the purposes of this tutorial, it's preferable to make sure that we can examine the output of various lines of code interactively.

With all the preceding steps completed, we're ready to produce a plot of the mosaicked raster. We'll relabel the pixel values so that the colorboar in the final result will be tidier.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
raster, relabel = relabel_pixels(raster, values=[0,1,2,253,254,255])
```

<!-- #region jupyter={"source_hidden": false} -->
We'll define image options, layout options, & a colormap in dictionaries as we've done previously to produce a single plot.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(
                    x='longitude',
                    y='latitude',                   
                    rasterize=True, 
                    dynamic=True,
                    crs=raster.rio.crs
                 )
layout_opts = dict(
                    xlabel='Longitude',
                    ylabel='Latitude',
                  )
```

```{code-cell} python jupyter={"source_hidden": false}
# Define a colormap using RGBA values; these need to be written manually here...
COLORS = {
0: (255, 255, 255, 0.0),  # No Water
1:  (0,   0, 255, 1.0),   # Open Water
2:  (180, 213, 244, 1.0), # Partial Surface Water
3: (  0, 255, 255, 1.0),  # Snow/Ice
4: (175, 175, 175, 1.0),  # Cloud/Cloud Shadow
5: ( 0,   0, 127, 0.5),   # Ocean Masked
}

c_labels = ["Not water", "Open water", "Partial Surface Water", "Snow/Ice",
            "Cloud/Cloud Shadow", "Ocean Masked"]
c_ticks = list(COLORS.keys())
limits = (c_ticks[0]-0.5, c_ticks[-1]+0.5)

c_bar_opts = dict( ticker=FixedTicker(ticks=c_ticks),
                   major_label_overrides=dict(zip(c_ticks, c_labels)),
                   major_tick_line_width=0, )

image_opts.update({ 'cmap': list(COLORS.values()),
                    'clim': limits,
                  })

layout_opts.update(dict(colorbar_opts=c_bar_opts))
```

<!-- #region jupyter={"source_hidden": false} -->
We'll define the basemap as a separate object to overlay using the `*` operator.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
basemap = gv.tile_sources.ESRI(frame_width=500, frame_height=500, padding=0.05, alpha=0.25)
```

<!-- #region jupyter={"source_hidden": false} -->
Finally, we can use the builtin Python `slice` function to extract downsampled images quickly before trying to view the entire image. Remember, reducing the value `steps` to `1` (or `None`) plots the raster at full resolution.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
%%time
steps = 1
view = raster.isel(longitude=slice(0,None,steps), latitude=slice(0,None,steps)).squeeze()

view.hvplot.image(**image_opts).opts(**layout_opts) * basemap
```

<!-- #region jupyter={"source_hidden": false} -->
This raster is much larger than ones we've previously examined (requiring roughly 4 times the storage). This process could be iterated to make a slider showing the merged results from neighboring tiles at different times. This, of course, requires that there is enough memory available.

***
<!-- #endregion -->

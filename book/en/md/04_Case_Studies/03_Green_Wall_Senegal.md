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

# The Great Green Wall in Senegal

<!-- #region jupyter={"source_hidden": true} -->
[The Great Green Wall](https://en.wikipedia.org/wiki/Great_Green_Wall_(Africa)) is an effort to combat the spread of the Sahara desert by growing vegetation in a systematic and scientific manner. The [OPERA DIST-ALERT data product](https://lpdaac.usgs.gov/documents/1766/OPERA_DIST_HLS_Product_Specification_V1.pdf) can also be used to identify changes in the growth of vegetation (implying natural or, in this case, anthropogenic causes).

<center>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Sahara_satellite_hires.jpg/800px-Sahara_satellite_hires.jpg"></img>
</center>
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Outline of steps for analysis

<!-- #region jupyter={"source_hidden": true} -->
+ Identifying search parameters (AOI, time-window, endpoint, etc.)
+ Obtaining search results in a `DataFrame`
+ Exploring & refining search results
+ Data-wrangling to produce relevant output

In this case, we'll assemble a DataFrame to summarize search results, trim down the results to a manageable size, and make an interactive slider to examine the data retrieved.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

### Preliminary imports

```python jupyter={"source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
import rasterio
```

```python jupyter={"source_hidden": true}
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```python jupyter={"source_hidden": true}
from pystac_client import Client
from osgeo import gdal
# GDAL setup for accessing cloud data
gdal.SetConfigOption('GDAL_HTTP_COOKIEFILE','~/.cookies.txt')
gdal.SetConfigOption('GDAL_HTTP_COOKIEJAR', '~/.cookies.txt')
gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN','EMPTY_DIR')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS','TIF, TIFF')
```

### Convenient utilities

```python jupyter={"source_hidden": true}
# simple utility to make a rectangle with given center of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding-box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

```python jupyter={"source_hidden": true}
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

```python jupyter={"source_hidden": true}
# utility to extract search results into a Pandas DataFrame
def search_to_dataframe(search_results):
    '''Constructs Pandas DataFrame from PySTAC Earthdata search results.
    DataFrame columns are determined from search item properties and assets.'''
    # Extract granules into a list of searh items
    granules = list(search_results.items())
    assert granules, "Error: empty list of search results"
    # Determine column labels from unique properties from all granules
    properties = sorted(list({prop for g in granules for prop in g.properties.keys()}))
    # Assemble blocks of rows from each granule
    blocks = []
    for g in granules:
        # Leftmost columns determined from properties
        left = pd.Series(index=properties)
        for p in properties:
            left.loc[p] = g.properties.get(p, None)
        tile_id = g.id.split('_')[3]
        left.loc['tile_id'] = tile_id
        left = pd.DataFrame(left).T
        right = []
        for a in sorted(g.assets.keys()):
            href = g.assets[a].href
            # Ignore hrefs using Amazon s3 (not currently working with rasterio)
            if href.startswith('s3://'):
                continue
            right.append(pd.DataFrame(data=dict(asset=a, href=href), index=[0]))
        # Use outer join to create block from left row and right block
        blocks.append(left.join(pd.concat(right, axis=0, ignore_index=True), how='outer'))
    # Stack blocks into final dataframe, forward-filling as needed
    df = pd.concat(blocks, axis=0, ignore_index=True).ffill(axis=0)
    assert len(df), "Empty DataFrame"
    return df
```

```python jupyter={"source_hidden": true}
# utility to process DataFrame of search results & return DataArray of stacked raster images
def stack_time_slices(granule_dataframe):
    '''This function returns a three-dimensional Xarray DataArray comprising time slices read from GeoTIFF files.
    - Input: a DataFrame of granules (i.e., a DataFrame with a DateTimeIndex and a column 'href' of URIs).
    - Output: a stacked DataArray with dimensions ('time', 'longitude', 'latitude')
    - GeoTIFF data are assumed to have been acquired over the same MGRS tile (NOT verified within).
    - Note CRS explicitly embedded into DataArray stack as extracted from GeoTIFF file.
    - DataArray is constructed using np.datetime64 time axis to simplify visualization.'''
    slices, timestamps = list(), list()
    for timestamp_, row_ in granule_dataframe.iterrows():
        da_ = rio.open_rasterio(row_['href'])
        # Preserve coordinate arrays from last GeoTIFF file parsed
        x, y = da_.coords['x'].values, da_.coords['y'].values
        slices.append(da_.values)
        timestamps.append(np.datetime64(timestamp_,'s'))
    # Construct time axis from accumulated timestamps
    time = np.array(timestamps)
    # Construct DataArray stack from accumulated slices & coordinates
    slices = np.concatenate(slices, axis=0)
    coords = dict(time=time, longitude=x, latitude=y)
    stack = xr.DataArray(data=slices, coords=coords, dims=['time', 'latitude', 'longitude'])
    # Preserve coordinate reference system (CRS) in DataArray stack
    crs = da_.rio.crs
    stack.rio.write_crs(crs, inplace=True)
    return stack
```

<!-- #region jupyter={"source_hidden": true} -->
These functions could be placed in module files for more developed research projects. For learning purposes, they are embedded within this notebook.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Obtaining search results

<!-- #region jupyter={"source_hidden": true} -->
The Great Green Wall spans the African continent; we'll choose an area-of-interest centered at the geographic coordinates $(-16.0913^{\circ}, 16.528^{\circ})$ in Senegal. We'll look at as much data as is available from January 2022 until the end of March 2024. We'll use the identifiers `AOI` and `DATE_RANGE` to eventually be used in a PySTAC search query.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
AOI = make_bbox((-16.0913, 16.528), 0.1, 0.1)
DATE_RANGE = "2022-01-01/2024-03-31"
```

<!-- #region jupyter={"source_hidden": true} -->
The plot generated below illustrates the AOI; the Bokeh Zoom tools are useful to examine the box on several length scales.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(padding=0.1, alpha=0.25)
plot_bbox(AOI) * basemap
```

```python jupyter={"source_hidden": true}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

<!-- #region jupyter={"source_hidden": true} -->
To execute the search, we define the endpoint URI and instantiate a `Client` object.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = 'LPCLOUD'
COLLECTIONS = ["OPERA_L3_DIST-ALERT-HLS_V1_1"]
search_params.update(collections=COLLECTIONS)
print(search_params)

catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

<!-- #region jupyter={"source_hidden": true} -->
The search itself is quite fast and yields a few thousand results that can be more easily examined in a Pandas DataFrame.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
df = search_to_dataframe(search_results)
df.info()
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->
We clean the `DataFrame` `df` in typical ways that make sense:

+ renaming the `eo:cloud_cover` column as `cloud_cover`;
+ dropping extraneous `datetime` columns;
+ casting columns to sensible datatypes;
+ casting the `datetime` column as `DatetimeIndex`; and
+ setting the `datetime` column as the `Index`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df = df.rename(columns={'eo:cloud_cover':'cloud_cover'})
df.cloud_cover = df.cloud_cover.astype(np.float16)
df = df.drop(['start_datetime', 'end_datetime'], axis=1)
df = df.convert_dtypes()
df.datetime = pd.DatetimeIndex(df.datetime)
df = df.set_index('datetime').sort_index()
```

```python jupyter={"source_hidden": true}
df.info()
```

<!-- #region jupyter={"source_hidden": true} -->
The next step is to identify a smaller set of rows from the search results that we can work with more easily.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Exploring & refining search results

<!-- #region jupyter={"source_hidden": true} -->
The `VEG-DIST-STATUS` band of the DIST-ALERT data is what we want, so we need to extract only those rows from `df` that are associated with that particular band. To do so, we can construct a boolean series `c1` that is `True` whenever the string in the `asset` column includes `VEG-DIST-STATUS` as a sub-string. We can also construct a boolean series `c2` to filter out rows for which the `cloud_cover` exceeds 20%.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
c1 = df.asset.str.contains('VEG-DIST-STATUS')
```

```python jupyter={"source_hidden": true}
c2 = df.cloud_cover<20
```

<!-- #region jupyter={"source_hidden": true} -->
If we examine the `tile_id` column, we can see that a single MGRS tile contains the AOI we specified. As such, all the data indexed in `df` corresponds to distinct measurements taken from a fixed geographic tile at different times.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df.tile_id.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->
We can combine the information above to reduce the `DataFrame` to a much shorter sequence of rows. We can also drop the `asset` and `tile_id` columns because they will be the same in every row after filtering. We can also drop the `cloud_cover` as we really only need the `href` column going forward.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df = df.loc[c1 & c2].drop(['asset', 'tile_id', 'cloud_cover'], axis=1)
df.info()
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Data-wrangling to produce relevant output

<!-- #region jupyter={"source_hidden": true} -->
We can examine the resulting `DataFrame` to see what information remains.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df
```

<!-- #region jupyter={"source_hidden": true} -->
There are almost eighty rows, each of which is associated with a distinct granule (in this context, a GeoTIFF file produced from an observation made at a given timestamp). We'll use a loop to assemble a stacked `DataArray` from the remote files using `xarray.concat`. Given that a few dozen files need to be retrieved from a remote source, this can take a few minutes and the result will require some memory (about 12 MiB for each row since each GeoTIFF corresponds to a $3,660\times3,660$ array of 8-bit unsigned integers).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
stack = stack_time_slices(df)
stack.attrs = dict(description=f"OPERA DIST: VEG-DIST-STATUS", units=None)
stack
```

<!-- #region jupyter={"source_hidden": true} -->
As a reminder, for the `VEG-DIST-STATUS` band, we interpret the raster values as follows:

* **0:** No disturbance
* **1:** First detection of disturbance with vegetation cover change <50%
* **2:** Provisional detection of disturbance with vegetation cover change <50%
* **3:** Confirmed detection of disturbance with vegetation cover change <50%
* **4:** First detection of disturbance with vegetation cover change ≥50%
* **5:** Provisional detection of disturbance with vegetation cover change ≥50%
* **6:** Confirmed detection of disturbance with vegetation cover change ≥50%
* **7:** Finished detection of disturbance with vegetation cover change <50%
* **8:** Finished detection of disturbance with vegetation cover change ≥50%
* **255** Missing data

By applying `np.unique` to the stack of rasters, we see that all these 10 distinct values occur somewhere in the data.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
np.unique(stack)
```

<!-- #region jupyter={"source_hidden": true} -->
We'll treat the pixels with missing values (i.e., value `255`) the same as pixels with no disturbance (i.e., value `0`). We could reassign the value `nan` to those pixels, but that converts all the data to `float32` or `float64` and hence increases the amount of memory required. That is, reassigning `255->0` allows us to ignore the missing values without using more memory.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
stack = stack.where(stack!=255, other=0)

np.unique(stack)
```

<!-- #region jupyter={"source_hidden": true} -->
We'll define a colormap to identify pixels showing signs of disturbance. Rather than assigning different colors to each of the 8 disturbance categories, we'll use [RGBA](https://en.wikipedia.org/wiki/RGBA_color_model) values to assign colors with a transparency value. With the colormap defined in the next cell, most of the pixels will be fully transparent. The remaining pixels are red with strictly positive `alpha` values. The values we really want to see are `3`, `6`, `7`, & `8` (indicating confirmed ongoing disturbance or confirmed disturbance that has finished).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Define a colormap using RGBA values; these need to be written manually here...
COLORS = [
            (255, 255, 255, 0.0),   # No disturbance
            (255,   0,   0, 0.25),  # <50% disturbance, first detection
            (255,   0,   0, 0.25),  # <50% disturbance, provisional
            (255,   0,   0, 0.50),  # <50% disturbance, confirmed, ongoing
            (255,   0,   0, 0.50),  # ≥50% disturbance, first detection
            (255,   0,   0, 0.50),  # ≥50% disturbance, provisional
            (255,   0,   0, 1.00),  # ≥50% disturbance, confirmed, ongoing
            (255,   0,   0, 0.75),  # <50% disturbance, finished
            (255,   0,   0, 1.00),  # ≥50% disturbance, finished
         ]
```

<!-- #region jupyter={"source_hidden": true} -->
Finally, we're ready to produce visualizations using the array `stack`.

+ We define `view` as a subset of `stack` that skips `steps` pixels in each direction to speed rendering (change to `steps=1` or `steps=None` when ready to plot at full resolution).
+ We define dictionaries `image_opts` and `layout_opts` to control arguments to pass to `hvplot.image`.
+ The result, when plotted, is an interactive plot with a slider that allows us to view specific time slices of the data.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts = dict(
                    x='longitude',
                    y='latitude',
                    cmap=COLORS,
                    colorbar=False,
                    clim=(-0.5,8.5),
                    crs = stack.rio.crs,
                    tiles=gv.tile_sources.ESRI,
                    tiles_opts=dict(alpha=0.1, padding=0.1),
                    project=True,
                    rasterize=True,
                    widget_location='bottom',
                 )
```

```python jupyter={"source_hidden": true}
layout_opts = dict(
                    title = 'Great Green Wall, Sahel Region, Africa\nDisturbance Alerts',
                    xlabel='Longitude (°)',ylabel='Latitude (°)',
                    fontscale=1.25,
                    frame_width=500,
                    frame_height=500,
                  )
```

```python jupyter={"source_hidden": true}
steps = 100
subset=slice(0,None,steps)
view = stack.isel(longitude=subset, latitude=subset)
view.hvplot.image(**image_opts, **layout_opts)
```

<!-- #region jupyter={"source_hidden": true} -->
It can be difficult to see the red pixels with the entire region in view; the box zoom and wheel zoom tools are useful here. There is also some latency when using the slider as it takes some time to render a new slice.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

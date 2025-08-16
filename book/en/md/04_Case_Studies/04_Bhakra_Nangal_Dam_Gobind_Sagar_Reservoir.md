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

# The Bhakra Nangal Dam & Gobind Sagar Reservoir

<!-- #region jupyter={"source_hidden": true} -->
The [Bhakra Nangal dam](https://en.wikipedia.org/wiki/Bhakra_Dam) was opened in 1963 in India. The dam forms the Gobind Sagar reservoir and provides irrigation to 10 million acres in the neighboring states of Punjab, Haryana, and Rajasthan. We can use OPERA DSWx data to observe fluctuations in water levels over long time periods.

<center>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bhakra_Dam_Aug_15_2008.JPG/440px-Bhakra_Dam_Aug_15_2008.JPG"></img>
</center>
<!-- #endregion -->

## Outline of steps for analysis

<!-- #region jupyter={"source_hidden": true} -->
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
# Imports for plotting
import hvplot.pandas, hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```python jupyter={"source_hidden": true}
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

```python jupyter={"source_hidden": true}
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

<!-- #region jupyter={"source_hidden": true} -->
These functions could be placed in module files for more developed research projects. For learning purposes, they are embedded within this notebook.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Identifying search parameters

<!-- #region jupyter={"source_hidden": true} -->
For coordinates of the dam, we'll use $(76.46^{\circ}, 31.42^{\circ})$. We'll also look for a full calendar year's worth of data between April 1, 2023 and April 1, 2024.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
AOI = make_bbox((76.46, 31.42), 0.2, 0.2)
DATE_RANGE = "2023-04-01/2024-04-01"
```

```python jupyter={"source_hidden": true}
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(alpha=0.5, padding=0.1)
plot_bbox(AOI) * basemap
```

```python jupyter={"source_hidden": true}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Obtaining search results

<!-- #region jupyter={"source_hidden": true} -->
We're going to look for OPERA DSWx data products, so we define the `ENDPOINT`, `PROVIDER`, and `COLLECTIONS` as follows (these values are occasionally modified, so some searching through NASA's [Earthdata Search website](https://search.earthdata.nasa.gov) may be necessary).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = "POCLOUD"
COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```python jupyter={"source_hidden": true}
%%time
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

<!-- #region jupyter={"source_hidden": true} -->
Having executed the search, the results can be perused in a `DataFrame`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->
We'll clean the `DataFrame` `df` by renaming the `eo:cloud_cover` column, dropping the extra datetime columns, converting the datatypes sensibly, and setting the index.
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
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->
At this stage, the `DataFrame` of search results has over two thousand rows. Let's trim that down.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Exploring & refining search results

<!-- #region jupyter={"source_hidden": true} -->
We'll filter the rows of `df` to capture only granules captured with less than 10% cloud cover and the `B01_WTR` band of the DSWx data.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
c1 = df.cloud_cover<10
c2 = df.asset.str.contains('B01_WTR')
```

```python jupyter={"source_hidden": true}
df = df.loc[c1 & c2]
df.info()
```

<!-- #region jupyter={"source_hidden": true} -->
We can count all the distinct entries of the `tile_id` column and. find that there's only one (`T43RFQ`). This means that the AOI specified lies strictly inside a single MGRS tile and that all granules found will be associated with that particular geographic tile.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
df.tile_id.value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->
We've reduced the total number of granules to a little over fifty. Let's use these to produce a visualization.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

## Data-wrangling to produce relevant output

<!-- #region jupyter={"source_hidden": true} -->
As we've seen several times now, we'll stack the two-dimensional arrays from the GeoTIFF files listed in `df.href` into a three-dimensional `DataArray`; we'll use the identifier `stack` to label the result.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
stack = stack_time_slices(df)
stack.attrs = dict(description=f"OPERA DSWx: B01_WTR", units=None)
stack
```

<!-- #region jupyter={"source_hidden": true} -->
We can see the pixel values that actually occur in the array `stack` using the NumPy `unique` function.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
np.unique(stack)
```

<!-- #region jupyter={"source_hidden": true} -->
As a reminder, according to the [DSWx product specification](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf), the meanings of the raster values are as follows:

+ **0**: Not Water&mdash;any area with valid reflectance data that is not from one of the other allowable categories (open water, partial surface water, snow/ice, cloud/cloud shadow, or ocean masked).
+ **1**: Open Water&mdash;any pixel that is entirely water unobstructed to the sensor, including obstructions by vegetation, terrain, and buildings.
+ **2**: Partial Surface Water&mdash;an area that is at least 50% and less than 100% open water (e.g., inundated sinkholes, floating vegetation, and pixels bisected by coastlines).
+ **252**: Snow/Ice.
+ **253**: Cloud or Cloud Shadow&mdash;an area obscured by or adjacent to cloud or cloud shadow.
+ **254**: Ocean Masked&mdash;an area identified as ocean using a shoreline database with an added margin.
+ **255**: Fill value (missing data).

Notice that the value `254`&mdash;ocean masked&mdash;does not occur in this particular collection of rasters because this particular region is far away from the coast.

To clean up the data (in case we want to use a colormap), let's reassign the pixel values with our utility function `relabel_pixels`. This time, let's keep the "no data" (`255`) values so we can see where data is missing.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
stack, relabel = relabel_pixels(stack, values=[0,1,2,252,253,255], replace_null=False)
```

<!-- #region jupyter={"source_hidden": true} -->
We can execute `np.unique` again to ensure that the data has been modified as intended.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
np.unique(stack)
```

<!-- #region jupyter={"source_hidden": true} -->
Let's now assign a colormap to help visualize the raster images. In this instance, the colormap uses several distinct colors with full opacity and black, partially transparent pixels to indicate missing data.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Define a colormap using RGBA values; these need to be written manually here...
COLORS = {
0: (255, 255, 255, 0.0),  # Not Water
1: (  0,   0, 255, 1.0),  # Open Water
2: (180, 213, 244, 1.0),  # Partial Surface Water
3: (  0, 255, 255, 1.0),  # Snow/Ice
4: (175, 175, 175, 1.0),  # Cloud/Cloud Shadow
5: (  0,   0, 0, 0.5),    # Missing
}
```

<!-- #region jupyter={"source_hidden": true} -->
We're ready to plot the data.

+ We define suitable options in the dictionaries `image_opts` and `layout_opts`.
+ We construct an object `view` that consists of slices extracted from `stack` by subsampling every `steps` pixels (reduce `steps` to `1` or `None` to view the rasters at full resolution).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
image_opts = dict(  
                    x='longitude',
                    y='latitude',
                    cmap = list(COLORS.values()),
                    colorbar=False,
                    tiles = gv.tile_sources.OSM,
                    tiles_opts=dict(padding=0.05, alpha=0.25),
                    project=True,
                    rasterize=True, 
                    framewise=False,
                    widget_location='bottom',
                 )

layout_opts = dict(
                    title = 'Bhakra Nangal Dam, India - water extent over a year',
                    xlabel='Longitude (degrees)',
                    ylabel='Latitude (degrees)',
                    fontscale=1.25,
                    frame_width=500, 
                    frame_height=500
                   )
```

```python jupyter={"source_hidden": true}
steps = 100
subset = slice(0,None,steps)
view = stack.isel(longitude=subset, latitude=subset)
view.hvplot.image(**image_opts, **layout_opts)
```

<!-- #region jupyter={"source_hidden": true} -->
The visualization above may take a while to update (depending on the choice of `steps`). It does provide a way to see the water accumulation over a period of a year. There are a number of slices in which a lot of data is missing, so some care is required to interpret those time slices.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": false} -->
---
<!-- #endregion -->

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

# Greece Wildfires

<!-- #region jupyter={"source_hidden": false} -->
In this example, we will retrieve data associated with the [2023 Greece wildfires](https://en.wikipedia.org/wiki/2023_Greece_wildfires) to understand their evolution and extent. We will generate a time series associated with this data and two visualizations of the event.

In particular, we will examine the area around the city of [Alexandroupolis](https://en.wikipedia.org/wiki/Alexandroupolis) which was severely impacted by the wildfires, resulting in loss of lives, property, and forested areas.

---
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

---
<!-- #endregion -->

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
    rect_opts = opts.Rectangles(line_width=2, alpha=0.1, color='red')
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

<!-- #region jupyter={"source_hidden": false} -->
These functions could be placed in module files for more developed research projects. For learning purposes, they are embedded within this notebook.

---
<!-- #endregion -->

## Identifying search parameters

```{code-cell} python jupyter={"source_hidden": false}
dadia_forest = (26.18, 41.08)
AOI = make_bbox(dadia_forest, 0.1, 0.1)
DATE_RANGE = '2023-08-01/2023-09-30'.split('/')
```

```{code-cell} python jupyter={"source_hidden": false}
# Optionally plot the AOI
basemap = gv.tile_sources.ESRI(width=500, height=500, padding=0.1, alpha=0.25)
plot_bbox(AOI) * basemap
```

```{code-cell} python jupyter={"source_hidden": false}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

---


## Obtaining search results

```{code-cell} python jupyter={"source_hidden": false}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = 'LPCLOUD'
COLLECTIONS = ["OPERA_L3_DIST-ALERT-HLS_V1_1"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```{code-cell} python jupyter={"source_hidden": false}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

<!-- #region jupyter={"source_hidden": false} -->
As usual, let's encode the search result into a Pandas `DataFrame`, examine the results, and make a few transformations to clean up the results.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
%%time
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": false} -->
We clean the `DataFrame` `df` in typical ways that make sense:
+ casting the `datetime` column as `DatetimeIndex`;
+ dropping extraneous `datetime` columns;
+ renaming the `eo:cloud_cover` column as `cloud_cover`;
+ casting the `cloud_cover` column as floating-point values; and
+ casting the remaining columns as strings; and
+ setting the `datetime` column as the `Index`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df = df.drop(['end_datetime', 'start_datetime'], axis=1)
df.datetime = pd.DatetimeIndex(df.datetime)
df = df.rename(columns={'eo:cloud_cover':'cloud_cover'})
df['cloud_cover'] = df['cloud_cover'].astype(np.float16)
for col in ['asset', 'href', 'tile_id']:
    df[col] = df[col].astype(pd.StringDtype())
df = df.set_index('datetime').sort_index()
df.info()
```

---


## Exploring & refining search results

<!-- #region jupyter={"source_hidden": false} -->
Let's examine the `DataFrame` `df` to better understand the search results. First, let's see how many different geographic tiles occur in the search results.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.tile_id.value_counts() 
```

<!-- #region jupyter={"source_hidden": false} -->
So the AOI lies strictly within a single MGRS geographic tile, namely `T35TMF`. Let's examine the `asset` column.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.asset.value_counts().sort_values(ascending=False)
```

<!-- #region jupyter={"source_hidden": false} -->
Some of these `asset` names are not as simple and tidy as the ones we encountered with the DIST-ALERT data products. We can, however, easily identify useful substrings. Here, we choose only those rows in which the `asset` column includes `'VEG-DIST-STATUS'` as a sub-string.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
idx_veg_dist_status = df.asset.str.contains('VEG-DIST-STATUS')
idx_veg_dist_status
```

<!-- #region jupyter={"source_hidden": false} -->
We can use this boolean `Series` with the Pandas `.loc` accessor to filter out only the rows we want (i.e., that connect to raster data files storing the `VEG-DIST-STATUS` band). We can subsequently drop the `asset` column (it is no longer required).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
veg_dist_status = df.loc[idx_veg_dist_status]
veg_dist_status = veg_dist_status.drop('asset', axis=1)
veg_dist_status
```

```{code-cell} python jupyter={"source_hidden": false}
print(len(veg_dist_status))
```

<!-- #region jupyter={"source_hidden": false} -->
Notice some of the rows have the same date but different times (corresponding to multiple observations in the same UTC calendar day). We can aggregate the URLs into lists by *resampling* the time series by day; we can subsequently visualize the result.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
by_day = veg_dist_status.resample('1d').href.apply(list)
display(by_day)
by_day.map(len).hvplot.scatter(grid=True).opts(title='# of observations')
```

<!-- #region jupyter={"source_hidden": false} -->
Let's clean up the `Series` `by_day` by filtering out the rows that have empty lists (i.e., dates on which no data was acquired).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
by_day = by_day.loc[by_day.map(bool)]
by_day.map(len).hvplot.scatter(ylim=(0,2.1), grid=True).opts(title="# of observations")
```

<!-- #region jupyter={"source_hidden": false} -->
We can now use the resampled series `by_day` to extract raster data for analysis.

---
<!-- #endregion -->

## Data-wrangling to produce relevant output

<!-- #region jupyter={"source_hidden": false} -->
The wildfire near Alexandroupolis started around August 21st and rapidly spread, particularly affecting the nearby Dadia Forest. Let's first assemble a "data cube" (i.e., a stacked array of rasters) from the remote files indexed in the Pandas series `by_day`. We'll start by selecting and loading one of the remote GeoTIFF files to extract metadata that applies to all the rasters associated with this event and this MGRS tile.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
href = by_day[0][0]
data = rio.open_rasterio(href).rename(dict(x='longitude', y='latitude'))
crs = data.rio.crs
shape = data.shape
```

<!-- #region jupyter={"source_hidden": false} -->
Before we build a stacked `DataArray` within a loop, we'll define a Python dictionary called  `template` that will be used to instantiate the slices of the array. The dictionary `template` will store metadata extracted from the GeoTIFF file, notably the coordinates.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
template = dict()
template['coords'] = data.coords.copy()
del template['coords']['band']
template['coords'].update({'time': by_day.index.values})
template['dims'] = ['time', 'longitude', 'latitude']
template['attrs'] = dict(description=f"OPERA DSWX: VEG-DIST-STATUS", units=None)

print(template)
```

<!-- #region jupyter={"source_hidden": false} -->
We'll use a loop to build a stacked array of rasters from the Pandas series `by_day` (whose entries are lists of string, i.e., URIs). If the list has a singleton element, the URI can be read directly using `rasterio.open`; otherwise, the function [`rasterio.merge.merge`](https://rasterio.readthedocs.io/en/latest/api/rasterio.merge.html) combines multiple raster data files acquired on the same day into a single raster image.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
import rasterio
from rasterio.merge import merge
```

```{code-cell} python jupyter={"source_hidden": false}
%%time
rasters = []
for date, hrefs in by_day.items():
    n_files = len(hrefs)
    if n_files > 1:
        print(f"Merging {n_files} files for {date.strftime('%Y-%m-%d')}...")
        raster, _ = merge(hrefs)
    else:
        print(f"Opening {n_files} file  for {date.strftime('%Y-%m-%d')}...")
        with rasterio.open(hrefs[0]) as ds:
            raster = ds.read()
    rasters.append(np.reshape(raster, newshape=shape))
```

<!-- #region jupyter={"source_hidden": false} -->
The data accumulated within the list `rasters` are all stored as NumPy arrays. Thus, rather than calling `xarray.concat`, we wrap a call to `numpy.concatenate` within a call to the `xarray.DataArray` constructor. We bind the object created to the identifier `stack`, making sure to also include the CRS information.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
stack = xr.DataArray(data=np.concatenate(rasters, axis=0), **template)
stack.rio.write_crs(crs, inplace=True)
stack
```

<!-- #region jupyter={"source_hidden": false} -->
The `DataArray` `stack` has `time`, `longitude`, and `latitude` as its main coordinate dimensions. We can use this to perform some computations and produce relevant visualizations.

---
<!-- #endregion -->

### Plotting the area damaged

<!-- #region jupyter={"source_hidden": false} -->
To begin, let's use the data in `stack` to compute the total surface area damaged. The data in `stack` comes from `VEG-DIST-STATUS`  band of the DIST-ALERT product. We interpret the pixel values in this band as follows:

* **0:** No disturbance
* **1:** First detection of disturbance with vegetation cover change $<50\%$
* **2:** Provisional detection of disturbance with vegetation cover change $<50\%$
* **3:** Confirmed detection of disturbance with vegetation cover change $<50\%$
* **4:** First detection of disturbance with vegetation cover change $\ge50\%$
* **5:** Provisional detection of disturbance with vegetation cover change $\ge50\%$
* **6:** Confirmed detection of disturbance with vegetation cover change $\ge50\%$
* **7:** Finished detection of disturbance with vegetation cover change $<50\%$
* **8:** Finished detection of disturbance with vegetation cover change $\ge50\%$

The particular pixel value we want to flag, then, is 6, i.e., a pixel in which at least 50% of the vegetation cover has been confirmed to be damaged and in which the disturbance is actively ongoing. We can use the `.sum` method to add up all the pixels with value `6` and the `.to_series` method to represent the sum as a time-indexed Pandas series. We also define `conversion_factor` that accounts for the area of each pixel in $\mathrm{km}^2$ (recall each pixel has area $30\mathrm{m}\times30\mathrm{m}$).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
pixel_val = 6
conversion_factor = (30/1_000)**2 / pixel_val
damage_area = stack.where(stack==pixel_val, other=0).sum(axis=(1,2)) 
damage_area = damage_area.to_series() * conversion_factor
damage_area
```

```{code-cell} python jupyter={"source_hidden": false}
plot_title = 'Damaged Area (km²)'
line_plot_opts = dict(title=plot_title, grid=True, color='r')
damage_area.hvplot.line(**line_plot_opts)
```

<!-- #region jupyter={"source_hidden": false} -->
Looking at the preceding plot, it seems the wildfires started around August 21 and spread rapidly.

---
<!-- #endregion -->

### Viewing selected time slices

<!-- #region jupyter={"source_hidden": false} -->
The nearby Dadia Forest was particularly affected by the wildfires. To see this, let's plot the raster data to see the spatial distribution of damaged pixels on three particular dates:  August 2, August 26th, and September 18th. Again, we'll highlight only those pixels with value 6 from the raster data. We can extract those specific dates easily from the Time series `by_day` using a list of dates (i.e., `dates_of_interest` in the cell below).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
dates_of_interest = ['2023-08-01', '2023-08-26', '2023-09-18']
print(dates_of_interest)
snapshots = stack.sel(time=dates_of_interest)
snapshots
```

<!-- #region jupyter={"source_hidden": false} -->
Let's make a static sequence of plots. We start by defining some standard options stored in dictionaries.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(
                    x='longitude', 
                    y='latitude',
                    rasterize=True, 
                    dynamic=True,
                    crs=crs,
                    shared_axes=False,
                    colorbar=False,
                    aspect='equal',
                 )
layout_opts = dict(xlabel='Longitude', ylabel="Latitude")
```

<!-- #region jupyter={"source_hidden": false} -->
We'll construct a colormap using a dictionary of RGBA values (i.e., tuples with three integer entries between 0 and 255 and a fourth floating-point entry between 0.0 and 1.0 for transparency).
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
COLORS = { k:(0,0,0,0.0) for k in range(256) }
COLORS.update({6: (255,0,0,1.0)})
image_opts.update(cmap=list(COLORS.values()))
```

<!-- #region jupyter={"source_hidden": false} -->
As usual, we'll start by slicing smaller images to make sure the call to `hvplot.image` works as intended. We can reduce the value of the parameter `steps` to `1` or `None` to get the images rendered at full resolution.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 100
subset = slice(0,None, steps)
view = snapshots.isel(longitude=subset, latitude=subset)
(view.hvplot.image(**image_opts).opts(**layout_opts) * basemap).layout()
```

<!-- #region jupyter={"source_hidden": false} -->
If we remove the call to `.layout`, we can produce an interactive slider that shows the progress of the wildfire using all the rasters in `stack`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
steps = 100
subset = slice(0,None, steps)
view = stack.isel(longitude=subset, latitude=subset,)
(view.hvplot.image(**image_opts).opts(**layout_opts) * basemap)
```

---

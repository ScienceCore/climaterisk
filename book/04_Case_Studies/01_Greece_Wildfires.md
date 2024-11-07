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


## 2023 Greece wildfires

<!-- #region jupyter={"source_hidden": true} -->
In this example, we will retrieve data associated with the [2023 Greece wildfires](https://en.wikipedia.org/wiki/2023_Greece_wildfires) to understand its evolution and extent. We will generate a time series visualization of the event.

In particular, we will be examining the area around the city of [Alexandroupolis](https://en.wikipedia.org/wiki/Alexandroupolis) which was severely impacted by the wildfires, resulting in loss of lives, property, and forested areas.
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

---


### Preliminary imports

```python jupyter={"outputs_hidden": true, "source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')
# data wrangling imports
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rio
import rasterio
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
# Imports for plotting
import hvplot.pandas
import hvplot.xarray
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
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

<!-- #region jupyter={"source_hidden": true} -->
These functions could be placed in module files for more developed research projects. For learning purposes, they are embedded within this notebook.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
# simple utility to make a rectangle with given center of width dx & height dy
def make_bbox(pt,dx,dy):
    '''Returns bounding-box represented as tuple (x_lo, y_lo, x_hi, y_hi)
    given inputs pt=(x, y), width & height dx & dy respectively,
    where x_lo = x-dx/2, x_hi=x+dx/2, y_lo = y-dy/2, y_hi = y+dy/2.
    '''
    return tuple(coord+sgn*delta for sgn in (-1,+1) for coord,delta in zip(pt, (dx/2,dy/2)))
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
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

```python jupyter={"outputs_hidden": true, "source_hidden": true}
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

---


## Identifying search parameters

```python jupyter={"outputs_hidden": true, "source_hidden": true}
dadia_forest = (26.18, 41.08)
AOI = make_bbox(dadia_forest, 0.1, 0.1)
DATE_RANGE = '2023-08-01/2023-09-30'
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
# Optionally plot the AOI
basemap = gv.tile_sources.OSM(width=500, height=500, padding=0.1)
plot_bbox(AOI) * basemap
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

---


## Obtaining search results

```python jupyter={"outputs_hidden": true, "source_hidden": true}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac'
PROVIDER = 'LPCLOUD'
COLLECTIONS = ["OPERA_L3_DIST-ALERT-HLS_V1_1"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
%%time
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": true} -->
Clean DataFrame `df` in ways that make sense (e.g., dropping unneeded columns/rows, casting columns as fixed datatypes, setting the index, etc.).
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
df = df.drop(['end_datetime', 'start_datetime'], axis=1)
df.datetime = pd.DatetimeIndex(df.datetime)
df['eo:cloud_cover'] = df['eo:cloud_cover'].astype(np.float16)
df = df.set_index('datetime').sort_index()
df.info()
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
for col in ['asset', 'href', 'tile_id']:
    df[col] = df[col].astype(pd.StringDtype())
```

---


## Exploring & refining search results

<!-- #region jupyter={"source_hidden": true} -->
Let's examine the `DataFrame` `df` to better understand the search results. First, let's see how many different geographic tiles occur in the search results.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
df.tile_id.value_counts() 
```

<!-- #region jupyter={"source_hidden": true} -->
Let's examine the `asset` column.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
df.asset.value_counts().sort_values(ascending=False)
```

<!-- #region jupyter={"source_hidden": true} -->
These `asset` names are not as simple and tidy as the ones we had with the DIST-ALERT data products. We can identify eseful substrings.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
df.asset.str.contains('VEG-DIST-STATUS')
```

<!-- #region jupyter={"source_hidden": true} -->
We can use this boolean `Series` with the Pandas `.loc` accessor to filter out only the rows we want (i.e., that connect to raster data files storing the `VEG-DIST-STATUS` band). We can subsequently drop the `asset` column (it is no longer required).
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
veg_dist_status = df.loc[df.asset.str.contains('VEG-DIST-STATUS')]
veg_dist_status = veg_dist_status.drop('asset', axis=1)
veg_dist_status
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
print(len(veg_dist_status))
```

<!-- #region jupyter={"source_hidden": true} -->
We can aggregate the URLs into lists by *resampling* the time series and visualizing the result.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
by_day = veg_dist_status.resample('1d').href.apply(list)
# by_day = by_day.loc[by_day.href] # logical filtering out empty lists; CHECK
display(by_day)
by_day.map(len).hvplot.line()
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
by_day = by_day.loc[by_day.map(bool)] # Filter out empty lists
by_day.map(len).hvplot.line()
```

---


## Data-wrangling to produce relevant output

<!-- #region jupyter={"source_hidden": true} -->
The wildfire near Alexandroupolis started on August 21st and rapidly spread, particularly affecting the nearby Dadia Forest. Let's first calculate the area affected over time.

As the lists in the `Series` `by_day` can contain one or more files, we can use the `merge` function to combine multiple raster data files acquired on the same day into a single raster image.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
from rasterio.merge import merge
```

<!-- #region jupyter={"source_hidden": true} -->
Remember, values in the `VEG-DIST-STATUS`  band of the DIST-ALERT product are interpreted as follows:

* **0:** No disturbance
* **1:** First detection of disturbance with vegetation cover change <50%
* **2:** Provisional detection of disturbance with vegetation cover change <50%
* **3:** Confirmed detection of disturbance with vegetation cover change <50%
* **4:** First detection of disturbance with vegetation cover change >50%
* **5:** Provisional detection of disturbance with vegetation cover change >50%
* **6:** Confirmed detection of disturbance with vegetation cover change >50%
* **7:** Finished detection of disturbance with vegetation cover change <50%
* **8:** Finished detection of disturbance with vegetation cover change >50%

The value we want to flag, then, is 6, i.e., only those pixels where at least 50% of the area was affected.

The cell below will take a few minutes to run as we need to retrieve datw files for all the rows of `by_day`.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
%%time
damage_area = []
conversion_factor = (30/1_000)**2 # to convert pixel count to area in km²; each pixel is 30x30m²

for date, hrefs in by_day.items():
    n_files = len(hrefs)
    if n_files > 1:
        print(f"Merging {n_files} files for {date}...")
        raster, _ = merge(hrefs)
    else:
        print(f"Opening {n_files} file  for {date}...")
        with rasterio.open(hrefs[0]) as ds:
            raster = ds.read()
    damage_area.append(np.sum(raster==6)*conversion_factor)
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
damaged_area = pd.Series(index=by_day.index, data=damage_area,)
damaged_area.index.name = 'Date'
plot_title = 'Damaged Area (km²)'
damaged_area.hvplot.line(title=plot_title, grid=True, color='r')
```

<!-- #region jupyter={"source_hidden": true} -->
Looking at the preceding plot, it seems the wildfires started around August 21 and spread rapidly, particularly affecting the nearby Dadia Forest. To see this, let's plot. the raster data to see the spatial distribution of those pixels on three dates:  August 1st, August 25th, and September 19th. Again, we'll highlight only those pixels with value 6 from the raster data. We can extract those specific dates easily from the Time series `by_day` using a list.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
dates_of_interest = ['2023-08-01', '2023-08-25', '2023-09-19']
print(dates_of_interest)
snapshots = by_day.loc[dates_of_interest]

snapshots
```

<!-- #region jupyter={"source_hidden": true} -->
Finally, let's make a more sophisticated static sequence of plots using Matplotlib. This is a bit more complicated, requiring imports from other packages.
<!-- #endregion -->

```python jupyter={"outputs_hidden": true, "source_hidden": true}
# Some additional imports needed
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from rasterio.plot import show
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import contextily as cx
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
# Define color map to generate plot (Red, Green, Blue, Alpha)
colors = [(1, 1, 1, 0) for _ in range(256)]  # Initial set all values to white, with zero opacity
colors[6] = (1, 0, 0, 1)                     # Set class 6 to Red with 100% opacity
cmap = ListedColormap(colors)
```

```python jupyter={"outputs_hidden": true, "source_hidden": true}
%%time
fig, ax = plt.subplots(1, 3, figsize = (30, 10))
crs = None

for k, (date, hrefs) in enumerate(snapshots.items()):
    # Read the crs to be used to generate basemaps
    if crs is None:
        with rasterio.open(hrefs[0]) as ds:
            crs = ds.crs;

    if len(hrefs) == 1:
        with rasterio.open(hrefs[0]) as ds:
            raster = ds.read()
            transform = ds.transform
    else:
        raster, transform = merge(hrefs)

    show(raster, ax=ax[k], transform=transform, interpolation='none')
    cx.add_basemap(ax[k], crs=crs, zoom=9, source=cx.providers.OpenStreetMap.Mapnik)
    show(raster, ax=ax[k], transform=transform, interpolation='none', cmap=cmap)

    scalebar = AnchoredSizeBar(ax[k].transData,
                            10000 , '10 km', 'lower right', 
                            color='black',
                            frameon=False,
                            pad = 0.25,
                            sep=5,
                            fontproperties = {'weight':'semibold', 'size':12},
                            size_vertical=300)

    ax[k].add_artist(scalebar)
    ax[k].ticklabel_format(axis='both', style='scientific',scilimits=(0,0),useOffset=False,useMathText=True)
    ax[k].set_xlabel('UTM easting (meters)')
    ax[k].set_ylabel('UTM northing (meters)')
    ax[k].set_title(f"Disturbance extent on: {date.strftime('%Y-%m-%d')}")
```

<!-- #region jupyter={"source_hidden": true} -->
The above code is inefficient; we're making repeated calls to `merge` that download the same cloud data more tha once. With some refactoring, we can be more efficient. But notice how the use of DataFrames, Series, and related data structures interactively shapes our analysis.
<!-- #endregion -->

---

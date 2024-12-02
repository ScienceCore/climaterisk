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

# Using the PySTAC API

<!-- #region jupyter={"source_hidden": false} -->
There is an abundance of data searchable through NASA's [Earthdata Search website](https://search.earthdata.nasa.gov). The preceding link connects to a GUI for searching [SpatioTemporal Asset Catalogs (STACs)](https://stacspec.org/) by specifying an *Area of Interest (AOI)* and a *time-window* or *range of dates*.

For the sake of reproducibility, we want to be able to search asset catalogs programmatically. This is where the [PySTAC](https://pystac.readthedocs.io/en/stable/) library comes in.
<!-- #endregion -->

***


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


## Identifying search parameters


### Defining AOI & range of dates

<!-- #region jupyter={"source_hidden": false} -->
We'll start by considering a particular example. [Heavy rains severely impacted Southeast Texas in May 2024](https://www.texastribune.org/2024/05/03/texas-floods-weather-harris-county/), resulting in [flooding and causing significant damage to property and human life](https://www.texastribune.org/series/east-texas-floods-2024/).
 
As usual, certain relevant imports are required. The first two cells are familiar (related to data analysis & visualization tools examined already). The third cell includes imports from the `pystac_client` library and `gdal` library followed by some settings required for using [GDAL (the Geospatial Data Abstraction Library)](https://gdal.org). These configuration details enable your notbook sessions to interact with remote sources of geospatial data smoothly.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
from warnings import filterwarnings
filterwarnings('ignore')
# data wrangling imports
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rio
import rasterio
```

```{code-cell} python jupyter={"source_hidden": false}
# Imports for plotting
import hvplot.pandas
import hvplot.xarray
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

<!-- #region jupyter={"source_hidden": false} -->
Next, let's define geographic search parameters so we can retrieve data pertinent to that flooding event. This involves specifying an *area of interest (AOI)* and a *range of dates*.
+ The AOI is specified as a rectangle of longitude-latitude coordinates in a single 4-tuple of the form
  $$({\mathtt{longitude}}_{\mathrm{min}},{\mathtt{latitude}}_{\mathrm{min}},{\mathtt{longitude}}_{\mathrm{max}},{\mathtt{latitude}}_{\mathrm{max}}),$$
  i.e., the lower,left corner coordinates followed by the upper, right corner coordinates.
+ The range of dates is specified as a string of the form
  $$ {\mathtt{date}_{\mathrm{start}}}/{\mathtt{date}_{\mathrm{end}}}, $$
  where dates are specified in standard ISO 8601 format `YYYY-MM-DD`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
# Center of the AOI
livingston_tx_lonlat = (-95.09,30.69) # (lon, lat) form
```

<!-- #region jupyter={"source_hidden": false} -->
We'll write a few short functions to encapsulate the logic of our generic workflows. For research code, these would be placed in Python module files. For convenience, we'll embed the functions in this notebook and others so they can execute correctly with minimal dependencies.
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
AOI = make_bbox(livingston_tx_lonlat, 0.5, 0.25)
basemap = gv.tile_sources.OSM.opts(width=500, height=500)
plot_bbox(AOI) * basemap
```

<!-- #region jupyter={"source_hidden": false} -->
Let's add a date range. The flooding happened primarily between April 30th & May 2nd; we'll set a longer time window covering the months of April & May.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
start_date, stop_date = '2024-04-01', '2024-05-31'
DATE_RANGE = f'{start_date}/{stop_date}'
```

<!-- #region jupyter={"source_hidden": false} -->
Finally, let's create a dictionary `search_params` that stores the AOI and the range of dates. This dictionary will be used to search for data in STACs.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
search_params = dict(bbox=AOI, datetime=DATE_RANGE)
print(search_params)
```

***


## Obtaining search results


### Executing a search with the PySTAC API

<!-- #region jupyter={"source_hidden": false} -->
Three other pieces of information are required to initiate a search for data: the *Endpoint* (a URL), the *Provider* (a string representing a path extending the Endpoint), & the *Collection identifiers* (a list of strings referring to specific catalogs). We generally need to experiment with NASA's [Earthdata Search website](https://search.earthdata.nasa.gov) to determine these values correctly for the specific data products we want to retrieve. The [NASA CMR STAC GitHub repository also monitors issues](https://github.com/nasa/cmr-stac/issues) related to the API for EarthData Cloud search queries.


For the search for DSWx data products that we want to execute, these parameters are as defined in the next code cell.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
ENDPOINT = 'https://cmr.earthdata.nasa.gov/stac' # base URL for the STAC to search
PROVIDER = 'POCLOUD'
COLLECTIONS = ["OPERA_L3_DSWX-HLS_V1_1.0"]
# Update the dictionary opts with list of collections to search
search_params.update(collections=COLLECTIONS)
print(search_params)
```

<!-- #region jupyter={"source_hidden": false} -->
Having defined the search parameters in the Python dictionary `search_params`, we can instantiate a `Client` and search the spatio-temporal asset catalog using the `Client.search` method.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
catalog = Client.open(f'{ENDPOINT}/{PROVIDER}/')
search_results = catalog.search(**search_params)
print(f'{type(search_results)=}\n',search_results)
```

<!-- #region jupyter={"source_hidden": false} -->
The object `search_results` returned by calling the `search` method is of type `ItemSearch`. To retrieve the results, we invoke the `items` method and cast the result as a Python `list` we'll bind to the identifier `granules`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
%%time
granules = list(search_results.items())
print(f"Number of granules found with tiles overlapping given AOI: {len(granules)}")
```

<!-- #region jupyter={"source_hidden": false} -->
Let's examine the contents of the list `granules`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
granule = granules[0]
print(f'{type(granule)=}')
```

```{code-cell} python jupyter={"source_hidden": false}
granule
```

<!-- #region jupyter={"source_hidden": false} -->
The object `granule` has a rich output representation in this Jupyter notebook. We can expand the attributes in the output cell by clicking the triangles.

![](../assets/granule_output_repr.png)

The term *granule* refers to a collection of data files (raster data in this case) all associated with raw data acquired by a particular satellite at a fixed timestamp over a particular geographic tile. There are a number of interesting attributes associated with this granule.
+ `properties['datetime']`: a string representing the time of data acquisition for the raster data files in this granule;
+ `properties['eo:cloud_cover']`: the percentage of pixels obscured by cloud and cloud shadow in this granule's raster data files; and
+ `assets`: a Python `dict` whose values summarize the bands or levels of raster data associated with this granule.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(f"{type(granule.properties)=}\n")
print(f"{granule.properties['datetime']=}\n")
print(f"{granule.properties['eo:cloud_cover']=}\n")
print(f"{type(granule.assets)=}\n")
print(f"{granule.assets.keys()=}\n")
```

<!-- #region jupyter={"source_hidden": false} -->
Each object in `granule.assets` is an instance of the `Asset` class that has an attribute `href`. It is the `href` attribute that tells us where to locate a GeoTiff file associated with this asset of this granule.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
for a in granule.assets:
    print(f"{a=}\t{type(granule.assets[a])=}")
    print(f"{granule.assets[a].href=}\n\n")
```

<!-- #region jupyter={"source_hidden": false} -->
In addition, the `Item` has an `.id` attribute that stores a string. As with the filenames associated with OPERA products, this `.id` string contains the identifier for an MGRS geographic tile. We can extract that identifier applying Python string manipulations to the granule `.id` attribute. Let's do that and store the result in `tile_id`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
print(granule.id)
tile_id = granule.id.split('_')[3]
print(f"{tile_id=}")
```

***


### Summarizing search results in a DataFrame

<!-- #region jupyter={"source_hidden": false} -->
The details of the search results are complicated to parse in this manner. Let's extract a few particular fields from the granules obtained into a Pandas `DataFrame` using a convenient Python function. We'll define the function here and re-use it in later notebooks.
<!-- #endregion -->

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
Invoking `search_to_dataframe` on `search_results` encodes most of the important information from the search as a Pandas `DataFrame` as below.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df = search_to_dataframe(search_results)
df.head()
```

<!-- #region jupyter={"source_hidden": false} -->
The `DataFrame.info` method allows us to examine the schema of this DataFrame.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df.info()
```

<!-- #region jupyter={"source_hidden": false} -->
Let's clean up the DataFrame of search results. This could be embedded in a function, but, it's worth knowing how to do this interactiely with Pandas. 

First, for these results, only one `Datetime` column is necessary; we can drop the others.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df = df.drop(['start_datetime', 'end_datetime'], axis=1)
df.info()
```

<!-- #region jupyter={"source_hidden": false} -->
Next, let's fix the schema of the `DataFrame` `df` by casting the columns as sensible data types. It will also be convenient to use the acquisition timestamp as the DataFrame index. Let's do so using the `DataFrame.set_index` method.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df['datetime'] = pd.DatetimeIndex(df['datetime'])
df['eo:cloud_cover'] = df['eo:cloud_cover'].astype(np.float16)
str_cols = ['asset', 'href', 'tile_id']
for col in str_cols:
    df[col] = df[col].astype(pd.StringDtype())
df = df.set_index('datetime').sort_index()
```

```{code-cell} python jupyter={"source_hidden": false}
df.info()
```

<!-- #region jupyter={"source_hidden": false} -->
This finally gives a DataFrame with a concise schema that can be used for later manipulations. Bundling the STAC search results into a Pandas `DataFrame` sensibly is a bit tricky. A number of the manipulations above could have been embedded within the function `search_to_dataframe`. But, given that the STAC API search results are still evolving, it's currently better to be flexible and to use Pandas interactively to work with search results. We'll see this more in later examples.
<!-- #endregion -->

***


## Exploring & refining search results

<!-- #region jupyter={"source_hidden": false} -->
If we examine the numerical `eo:cloud_cover` column of the DataFrame `df`, we can gather statistics using standard aggregations and the `DataFrame.agg` method.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df['eo:cloud_cover'].agg(['min','mean','median','max'])
```

<!-- #region jupyter={"source_hidden": false} -->
Notice that there are a number of `nan` entries in this column; Pandads statistical aggregation functions are typically "`nan`-aware" meaning that they implicitly ignore `nan` entries ("Not-a-Number") when computing statistics.
<!-- #endregion -->

### Filtering the search DataFrame with Pandas

<!-- #region jupyter={"source_hidden": false} -->
As a first filtering operation, let's keep only the rows for which the cloud cover is less than 50%.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df_clear = df.loc[df['eo:cloud_cover']<50]
df_clear
```

<!-- #region jupyter={"source_hidden": false} -->
For this search query, each DSWX granule comprises raster data for ten bands or levels. We can see this by applying the Pandas `Series.value_counts` method to the `asset` column.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
df_clear.asset.value_counts()
```

<!-- #region jupyter={"source_hidden": false} -->
Let's filter out the rows that correspond to the band `B01_WTR` of the DSWx data product. The Pandas `DataFrame.str` accessor makes this operation simple. We'll call the filtered `DataFrame` `b01_wtr`.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
b01_wtr = df_clear.loc[df_clear.asset.str.contains('B01_WTR')]
b01_wtr.info()
b01_wtr.asset.value_counts()
```

<!-- #region jupyter={"source_hidden": false} -->
We can also see that there are several geographic tiles associated with the granules found that intersect the AOI provided.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
b01_wtr.tile_id.value_counts()
```

<!-- #region jupyter={"source_hidden": false} -->
Remember, these codes refer to MGRS geographic tiles specified in a particular coordinate system. As we have identified these codes in the `tile_id` column, we can filter rows that correspond to, say, files collected over the MGRS tile `T15RUQ`:
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
b01_wtr_t15ruq = b01_wtr.loc[b01_wtr.tile_id=='T15RUQ']
b01_wtr_t15ruq
```

<!-- #region jupyter={"source_hidden": false} -->
We now have a much shorter `DataFrame` `b01_wtr_t15ruq` that summarises the remote locations of files (i.e., GeoTiffs) that store raster data for the surface water band `B01_WTR` in MGRS tile `T15RUQ` collected at various time-stamps that lie within the time-window we specified. We canuse this DataFrame to download those files for analysis or visualization.
<!-- #endregion -->

***


## Data-wrangling to produce relevant output


### Stacking the data

<!-- #region jupyter={"source_hidden": false} -->
We have a `DataFrame` that identifies specific remote files of raster data. The next step is to combine this raster data into a data structure suitable for analysis. The Xarray `DataArray` is suitable in this case; the combination can be generated using the Xarray function `concat`. The function `urls_to_stack` in the next cell is long but not complicated; it takes a `DataFrame` with timestamps on the index and a column labelled `href` of URLs, it reads the files associated with those URLs one-by-one, and it stacks the relevant two-dimensional arrays of raster data into a three-dimensional array.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
def urls_to_stack(granule_dataframe):
    '''Processes DataFrame of PySTAC search results (with OPERA tile URLs) &
    returns stacked Xarray DataArray (dimensions time, latitude, & longitude)'''
    
    stack = []
    for i, row in granule_dataframe.iterrows():
        with rasterio.open(row.href) as ds:
            # extract CRS string
            crs = str(ds.crs).split(':')[-1]
            # extract the image spatial extent (xmin, ymin, xmax, ymax)
            xmin, ymin, xmax, ymax = ds.bounds
            # the x and y resolution of the image is available in image metadata
            x_res = np.abs(ds.transform[0])
            y_res = np.abs(ds.transform[4])
            # read the data 
            img = ds.read()
            # Ensure img has three dimensions (bands, y, x)
            if img.ndim == 2:
                img = np.expand_dims(img, axis=0) 
            lon = np.arange(xmin, xmax, x_res)
            lat = np.arange(ymax, ymin, -y_res)
            bands = np.arange(img.shape[0])
            da = xr.DataArray(
                                data=img,
                                dims=["band", "lat", "lon"],
                                coords=dict(
                                            lon=(["lon"], lon),
                                            lat=(["lat"], lat),
                                            time=i,
                                            band=bands
                                            ),
                                attrs=dict(
                                            description="OPERA DSWx B01",
                                            units=None,
                                          ),
                             )
            da.rio.write_crs(crs, inplace=True)   
            stack.append(da)
    return xr.concat(stack, dim='time').squeeze()
```

```{code-cell} python jupyter={"source_hidden": false}
%%time
stack = urls_to_stack(b01_wtr_t15ruq)
```

```{code-cell} python jupyter={"source_hidden": false}
stack
```

### Producing a data visualization

```{code-cell} python jupyter={"source_hidden": false}
#  Define a colormap with RGBA tuples
COLORS = [(150, 150, 150, 0.1)]*256  # Setting all values to gray with low opacity
COLORS[0] = (0, 255, 0, 0.1)         # Not-water class to green
COLORS[1] = (0, 0, 255, 1)           # Open surface water
COLORS[2] = (0, 0, 255, 1)           # Partial surface water
```

```{code-cell} python jupyter={"source_hidden": false}
image_opts = dict(
                   x='lon',
                   y='lat',
                   project=True,
                   rasterize=True,
                   cmap=COLORS, 
                   colorbar=False,
                   tiles = gv.tile_sources.OSM,
                   widget_location='bottom',
                   frame_width=500,
                   frame_height=500,
                   xlabel='Longitude (degrees)',
                   ylabel='Latitude (degrees)',
                   title = 'DSWx data for May 2024 Texas floods',
                   fontscale=1.25
                  )
```

<!-- #region jupyter={"source_hidden": false} -->
Plotting the images in entirety can use a lot of memory. Let's use the Xarray `DataArray.isel` method to extract a slice from the array `stack` with fewer pixels. This will allow rapid rendering and scrolling.
<!-- #endregion -->

```{code-cell} python jupyter={"source_hidden": false}
view = stack.isel(lon=slice(3000,None), lat=slice(3000,None))
view.hvplot.image(**image_opts)
```

```{code-cell} python jupyter={"source_hidden": false}
stack.hvplot.image(**image_opts) # Construct view from all slices.
```

<!-- #region jupyter={"source_hidden": false} -->
Before continuing, remember to shut down the kernel for this notebook to free up memory for other computations.
<!-- #endregion -->

***

<!-- #region jupyter={"source_hidden": false} -->
This notebook primarily provides an example to illustrate using the PySTAC API.

In subsequent notebooks, we'll use this general workflow:

1. Set up a search query by identifying a particular *AOI* and *range of dates*.
2. Identify a suitable *endpoint*, *provider*, & *asset catalog* and execute the search using `pystac.Client`.
3. Convert the search results into a Pandas DataFrame containing the principal fields of interest.
4. Use the resulting DataFrame to filter for the most relevant remote data files needed for analysis and/or visualization.
5. Execute the analysis and/or visualization using the DataFrame to retrieve the required data.
<!-- #endregion -->

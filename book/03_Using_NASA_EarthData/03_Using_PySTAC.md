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

<!-- #region jupyter={"source_hidden": true} -->
There is an abundance of data searchable through NASA's [Earthdata Search](https://search.earthdata.nasa.gov). The preceding link connects to a GUI for searching [SpatioTemporal Asset Catalogs (STAC)](https://stacspec.org/) by specifying an *Area of Interest (AOI)* and a *time-window* or *range of dates*.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
For the sake of reproducibility, we want to be able to search asset catalogs programmatically. This is where the [PySTAC](https://pystac.readthedocs.io/en/stable/) library comes in.

---
<!-- #endregion -->

## Defining AOI & range of dates

<!-- #region jupyter={"source_hidden": true} -->
Let's start by considering a particular example. [Heavy rains severely impacted Argentina in March 2024](https://www.reuters.com/world/americas/argentina-downpour-drenches-crop-fields-flash-floods-buenos-aires-2024-03-12/). The event resulted in flash floods and impacted crop yields, severely impacting the Buenos Aires metropolitan area, and caused significant damage to property and human life. In this notebook, we'll set up a DataFrame to process results retrieved when searching relevant OPERA DSWx-HLS data catalogs.

Let's start with relevant imports.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')
# data wrangling imports
import numpy as np
import pandas as pd
import xarray as xr
# STAC imports to retrieve cloud data
from pprint import pprint
from pystac_client import Client
```

```python jupyter={"source_hidden": true}
# Imports for plotting
import hvplot.pandas
import geoviews as gv
from geoviews import opts
gv.extension('bokeh')
```

<!-- #region jupyter={"source_hidden": true} -->
Next, let's define search parameters so we can retrieve data pertinent to that flooding event. This involves specifying an *area of interest (AOI)* and a *range of dates*.
+ The AOI is specified as a rectangle of latitude-longitude coordinates in a single 4-tuple of the form
  $$({\mathtt{latitude}}_{\mathrm{min}},{\mathtt{longitude}}_{\mathrm{min}},{\mathtt{latitude}}_{\mathrm{max}},{\mathtt{longitude}}_{\mathrm{max}}),$$
  i.e., the lower,left corner coordinates followed by the upper, right corner coordinates.
+ The range of dates is specified as a string of the form
  $$ {\mathtt{date}_{\mathrm{start}}}/{\mathtt{date}_{\mathrm{end}}}, $$
  where dates are specified in standard ISO 8601 format `YYYY-MM-DD`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Define data search parameters

# Define AOI as left, bottom, ri/ght and top lat/lon extent
aoi = (-59.63818, -35.02927, -58.15723, -33.77271)
# We will search data for the month of March 2024
date_range = '2024-03-08/2024-03-15'
# Define a dictionary with appropriate keys: 'bbox' and 'datetime'
search_params = {
                  'bbox' : aoi, 
                  'datetime' : date_range,
                }
```

<!-- #region jupyter={"source_hidden": true} -->
Make a quick visual check that the tuple `aoi` actually describes the geographic region around Buenos Aires.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
basemap = gv.tile_sources.OSM
rect = gv.Rectangles([aoi]).opts(opts.Rectangles(alpha=0.25, color='cyan'))

rect*basemap
```

## Executing a search with the PySTAC API

```python jupyter={"source_hidden": true}
# Define the base URL for the STAC to search
STAC_URL = 'https://cmr.earthdata.nasa.gov/stac'
# Update the dictionary opts with list of collections to search
collections = ["OPERA_L3_DSWX-HLS_V1_1.0"]
search_params.update(collections=collections)
print(search_params)
```

<!-- #region jupyter={"source_hidden": true} -->
Having defined the search parameters, we can instantiate a `Client` and search the spatio-temporal asset catalog.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# We open a client instance to search for data, and retrieve relevant data records
catalog = Client.open(f'{STAC_URL}/POCLOUD/')
search_results = catalog.search(**search_params)

print(f'{type(search_results)=}')

results = list(search_results.items_as_dicts())
print(f"Number of tiles found intersecting given bounding box: {len(results)}")
```

<!-- #region jupyter={"source_hidden": true} -->
The object `results` retrieved from the search is a list of Python dictionaries (as suggested by the method name `items_as_dicts`). Let's parse the the first entry of `results`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
result = results[0]
print(f'{type(result)=}')
print(result.keys())
```

<!-- #region jupyter={"source_hidden": true} -->
Each element of `results` is a dictionary that contains other other nested dictionaries. The Python utility `pprint.pprint` library helps us examine the structure of the search results.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
pprint(result, compact=True, width=10, sort_dicts=False)
```

<!-- #region jupyter={"source_hidden": true} -->
The particular values we want to pick out from `result` are:
+ `result['properties']['datetime']` : timestamp associated with a particular granule; and
+ `result['assets']['0_B01_WTR']['href']` : URI associated with a particular granule (pointing to a GeoTIFF file).

```
{...
 'properties': {'eo:cloud_cover': 95,
                'datetime': '2024-03-01T13:44:11.879Z',
                'start_datetime': '2024-03-01T13:44:11.879Z',
                'end_datetime': '2024-03-01T13:44:11.879Z'},
 'assets': {'0_B01_WTR': {'href': 'https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/OPERA_L3_DSWX-HLS_PROVISIONAL_V1/OPERA_L3_DSWx-HLS_T21HUC_20240301T134411Z_20240305T232837Z_L8_30_v1.0_B01_WTR.tif',
                          'title': 'Download '
                                   'OPERA_L3_DSWx-HLS_T21HUC_20240301T134411Z_20240305T232837Z_L8_30_v1.0_B01_WTR.tif'},
            '0_B02_BWTR': ...
            }

```
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Look at specific values extracted from the 'properties' & 'assets' keys.
print(result['properties']['datetime'])
print(result['assets']['0_B01_WTR']['href'])
```

## Summarizing search results in a DataFrame

<!-- #region jupyter={"source_hidden": true} -->
Let's extract these particular fields into a Pandas DataFrame for convenience.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
times = pd.DatetimeIndex([result['properties']['datetime'] for result in results])
hrefs = {'hrefs': [result['assets']['0_B01_WTR']['href'] for result in results]}
```

```python jupyter={"source_hidden": true}
# Construct Pandas DataFrame to summarize granules from search results
granules = pd.DataFrame(index=times, data=hrefs)
granules.index.name = 'times'
```

```python jupyter={"source_hidden": true}
granules
```

<!-- #region jupyter={"source_hidden": true} -->
Examining the index reveals that the timestamps of the granules returned are not unique, i.e., granules correspond to distinct data products deriveded during a single aerial acquisition by a satellite.
<!-- #endregion -->

```python
len(granules.index.unique()) / len(granules) # Notice the timestamps are not all unique, i.e., some are repeated
```

<!-- #region jupyter={"source_hidden": true} -->
The `hrefs` (i.e., the URIs or URLs pointed to in a given row in `granules`) are unique, telling us that the granules refer to distinct data products or bands derived from each data acquisition even if the timestamps match.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
len(granules.hrefs.unique()) / len(granules) # Make sure all the hrefs are unique
```

<!-- #region jupyter={"source_hidden": true} -->
Let's get a sense of how many granules are available for each day of the month. Note, we don't know how many of these tiles contain cloud cover obscuring features of interest yet.

The next few lines do some Pandas manipulations of the DataFrame `granules` to yield a line plot showing what dates are associated with the most granules.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
granules_by_day = granules.resample('1d')  # Grouping by day, i.e., "resampling"
```

```python jupyter={"source_hidden": true}
granule_counts = granules_by_day.count() # Aggregating counts
```

```python jupyter={"source_hidden": true}
# Ignore the days with no associated granules
granule_counts = granule_counts[granule_counts.hrefs > 0]
```

```python jupyter={"source_hidden": true}
# Relabel the index & column of the DataFrame
granule_counts.index.name = 'Day of Month'
granule_counts.rename({'hrefs':'Granule count'}, inplace=True, axis=1)
```

```python jupyter={"source_hidden": true}
count_title = '# of DSWx-HLS granules available / day'
granule_counts.hvplot.line(title=count_title, grid=True, frame_height=300, frame_width=600)
```

<!-- #region jupyter={"source_hidden": true} -->
The floods primarily occurred between March 11th and 13th. Unfortunately, there are few granules associated with those particular days. We can, in principal, use the URIs stored in this DataFrame to set up analysis of the data associated with this event; we'll do so in other examples with better data available.
<!-- #endregion -->

---

<!-- #region jupyter={"source_hidden": true} -->
We could go further to download data from the URIs provided but we won't with this example. This notebook primarily provides an example to show how to use the PySTAC API.

In subsequent notebooks, we'll use this general workflow:

1. Set up a search query by identifying a particular AOI and range of dates.
2. Identify a suitable asset catalog and execute the search using `pystac.Client`.
3. Convert the search results into a Pandas DataFrame containing the principal fields of interest.
4. Use the resulting DataFrame to access relevant remote data for analysis and/or visualization.
<!-- #endregion -->

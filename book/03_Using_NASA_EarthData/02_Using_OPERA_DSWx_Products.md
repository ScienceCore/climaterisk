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

# Using the OPERA DSWx Product

<!-- #region editable=true jupyter={"source_hidden": true} slideshow={"slide_type": ""} -->
<center>
    <img src="https://d2pn8kiwq2w21t.cloudfront.net/original_images/Opera-Hero-Overview-Infographic-v6.jpg" width="50%"></img>
</center>

From the [OPERA (Observational Products for End-Users from Remote Sensing Analysis)](https://www.jpl.nasa.gov/go/opera) project:

>Started in April 2021, the Observational Products for End-Users from Remote Sensing Analysis (OPERA) project at the Jet Propulsion Laboratory collects data from satellite radar and optical instruments to generate six product suites:
>
> + a near-global Surface Water Extent product suite
> + a near-global Surface Disturbance product suite
> + a near-global Radiometric Terrain Corrected product
> + a North America Coregistered Single Look complex product suite
> + a North America Displacement product suite
> + a North America Vertical Land Motion product suite

That is, OPERA is a NASA initiative that takes, e.g., optical or radar remote-sensing data gathered from satellites and produces a variety of pre-processed data sets for public use. OPERA products are not raw satellite images; they are the result of algorithmic classification to determine, e.g., which land regions contain water or where vegetation has been displaced. The raw satellite images are collected from measurements made by the instruments onboard the Sentinel-1 A/B, Sentinel-2 A/B, and Landsat-8/9 satellite missions (hence the term *HLS* for "*Harmonized Landsat-Sentinel*" in numerous product descriptions).
<!-- #endregion -->

---


## The OPERA Dynamic Surface Water Extent (DSWx) product

<!-- #region editable=true jupyter={"source_hidden": true} slideshow={"slide_type": ""} -->
We've already looked at the DIST (i.e., land surface disturbance) family of OPERA data products. In this notebook, we'll examine another OPERA data product: the *Dynamic Surface Water Extent (DSWx)* product (more fully described in the [OPERA DSWx HLS product specification](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf)). This data summarizes the extent of inland water (i.e., water on land masses as opposed to part of an ocean) that can be used to track flooding events.

The DSWx data products are generated from HLS surface reflectance (SR) measurements; specifically, these are made by the Operational Land Imager (OLI) aboard the Landsat 8 satellite, the Operational Land Imager 2 (OLI-2) aboard the Landsat 9 satellite, and the MultiSpectral Instrument (MSI) aboard the Sentinel-2A/B satellites. As with the DIST products, the DSWx products consist of raster data stored in GeoTIFF format using the [Military Grid Reference System (MGRS)](https://en.wikipedia.org/wiki/Military_Grid_Reference_System) (the details are fully described in the [DSWx product specification](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf)). Again, the OPERA DSWx products are distributed as [Cloud Optimized GeoTIFFs](https://www.cogeo.org/) storing different bands/layers in distinct TIFF files.
<!-- #endregion -->

---

<!-- #region editable=true slideshow={"slide_type": ""} -->
### Band 1: Water classification (WTR)
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
There are ten bands or layers associated with the DSWx data product. For instance, band 3 is the *Confidence (CONF)* layer that provides, for each pixel, quantitative values describing the degree of confidence in the categories given in band 1 (the Water classification layer). Band 4 is a *Diagnostic (DIAG)* layer that encodes, for each pixel, which of five tests were positive in deriving the CONF layer. We will only use the first band — the *water classification (WTR)* layer — in this tutorial, but details of all the bands are given in the [DSWx product specification](https://d2pn8kiwq2w21t.cloudfront.net/documents/ProductSpec_DSWX_URS309746.pdf).

The water classification layer consists of unsigned 8-bit integer raster data (UInt8) meant to represent whether a pixel contains inland water (e.g., part of a reservoir, a lake, a river, etc., but not water associated with the open ocean). The values in this raster layer are computed from raw images acquired by the satellite with pixels being assigned one of 7 positive integer values; we'll examine these below.

Let's begin by importing the required libraries and loading a suitable file into an Xarray `DataArray`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Notebook dependencies
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import rioxarray as rio
import pandas as pd
import hvplot.xarray
from bokeh.models import FixedTicker
import geoviews as gv
gv.extension('bokeh')
```

```python jupyter={"source_hidden": true}
LOCAL_PATH = Path('..') / 'assets' / 'OPERA_L3_DSWx-HLS_T36RVU_20240601T082559Z_20240607T183514Z_S2B_30_v1.0_B01_WTR.tif'
data = rio.open_rasterio(LOCAL_PATH)
data = data.rename({'x':'easting', 'y':'northing', 'band':'band'}).squeeze()
```

```python jupyter={"source_hidden": true}
# Examine data
data
```

<!-- #region jupyter={"source_hidden": true} -->
As before, we define a basemap, this time using tiles from [ESRI](https://www.esri.com). We also set up dictionaries `image_opts` and `layout_opts` for common options we'll use when invoking `.hvplot.image`.
<!-- #endregion -->

```python editable=true jupyter={"source_hidden": true} slideshow={"slide_type": ""}
# Creates basemap
base = gv.tile_sources.EsriImagery.opts(width=1000, height=1000, padding=0.1)
# Initialize image options dictionary
image_opts = dict(
                    x='easting',
                    y='northing',                   
                    rasterize=True, 
                    dynamic=True,
                    frame_width=500, 
                    frame_height=500,
                    aspect='equal',
                    alpha=0.8
                 )
# Initialize layout options dictionary
layout_opts = dict(
                    xlabel='Longitude',
                    ylabel='Latitude'
                  )
```

<!-- #region jupyter={"source_hidden": true} -->
A continuous colormap is not all that helpful because this data is *categorical*. Specifically, the valid pixel values and their meanings are as follows:

+ **0**: Not Water – an area with valid reflectance data that is not open water (class 1), partial surface water (class 2), snow/ice (class 252), cloud/cloud shadow (class 253), or ocean masked (class 254). Masking can result in “not water” (class 0) where land cover masking is applied.
+ **1**: Open Water – an area that is entirely water and unobstructed to the sensor, including obstructions by vegetation, terrain, and buildings.
+ **2**: Partial Surface Water – an area that is at least 50% and less than 100% open water (e.g., inundated sinkholes, floating vegetation, and pixels bisected by coastlines). This may be referred to as "subpixel inundation" when referring to a pixel's area.
+ **252**: Snow/Ice.
+ **253**: Cloud or Cloud Shadow – an area obscured by or adjacent to cloud or cloud shadow.
+ **254**: Ocean Masked - an area identified as ocean using a shoreline database with an added margin
+ **255**: Fill value (missing data).

Let's count the number of pixels in each category using the Pandas `Series.value_counts` method.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
pd.Series(data.values.flatten()).value_counts()
```

<!-- #region jupyter={"source_hidden": true} -->
We'll choose color keys using the dictionary `color_key` with codes used frequently for this kind of data. For all the images plotted here, we'll use variants of the code in the cell below to update `layout_opts` so that plots generated for various layers/bands from the DSWx data products have suitable legends.
<!-- #endregion -->

```python editable=true jupyter={"source_hidden": true} slideshow={"slide_type": ""}
# Defines colormap for visualization
levels = [0, 0.9, 1.9, 2.9, 7.9, 8.9, 10]

color_key = {
    "Not Water": (255,255,255,0.5),
    "Open Water": (0,0,255,1),
    "Partial Surface Water": (0,255,0,1),
    "Reserved": (0,0,0,1),
    "Snow/Ice": (0,255,255,1),
    "Clouds/Cloud Shadow": (127,127,127,0.25)
}

ticks = [0.5, 1.5, 2.5, 5.5, 8.5, 9.5]
ticker = FixedTicker(ticks=ticks)
labels = dict(zip(ticks, color_key))

layout_opts.update(
                    title='B01_WTR',
                    color_levels=levels,
                    cmap=tuple(color_key.values()),
                    colorbar_opts={'ticker':ticker,'major_label_overrides':labels}
                  )
```

```python jupyter={"source_hidden": true}
b01_wtr = data.where((data!=255) & (data!=0))
image_opts.update(crs=data.rio.crs)
```

```python jupyter={"source_hidden": true}
b01_wtr.hvplot.image(**image_opts).opts(**layout_opts) * base
```

<!-- #region jupyter={"source_hidden": true} -->
The plot shows the southern end of the Suez Canal. Much of the region in the scene is land; some areas of open water are visible but most is obscured by cloud cover.
<!-- #endregion -->

---

<!-- #region editable=true jupyter={"source_hidden": true} slideshow={"slide_type": ""} -->
This notebook provides an overview of how to visualize data extracted from OPERA DSWx data products that are stored locally. We're now ready to automate the search for such products in the cloud using the PySTAC API.
<!-- #endregion -->

<!-- #region editable=true slideshow={"slide_type": ""} -->
----
<!-- #endregion -->

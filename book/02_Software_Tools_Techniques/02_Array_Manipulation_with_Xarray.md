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

# Array Manipulation with [Xarray](https://docs.xarray.dev/en/stable/index.html)

<!-- #region jupyter={"source_hidden": true} -->
There are numerous ways to work with geospatial data and so choosing tooling can be difficult. The principal library we'll be using is [*Xarray*](https://docs.xarray.dev/en/stable/index.html) for its `DataArray` and `Dataset` data structures and associated utilities as well as [NumPy](https://numpy.org) and [Pandas](https://pandas.pydata.org) for manipulating homogeneous numerical arrays and tabular data respectively.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
import rioxarray as rio
```

---

<!-- #region jupyter={"source_hidden": true} -->
<center><img src="https://docs.xarray.dev/en/stable/_static/Xarray_Logo_RGB_Final.svg"></img></center>

The principal data structure in Xarray is the [`DataArray`](https://docs.xarray.dev/en/stable/user-guide/data-structures.html) that provides support for labelled multi-dimensional arrays. [Project Pythia](https://foundations.projectpythia.org/core/xarray.html) provides a broad introduction to this package. We'll focus mainly on the specific parts of the Xarray API that we'll use for our particular geospatial analyses.

Let's load an example `xarray.DataArray` data structure from a file whose location is given by `LOCAL_PATH`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
LOCAL_PATH = Path().cwd() / '..' / 'assets' / 'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'
data = rio.open_rasterio(LOCAL_PATH)
```

---


## Examining the rich DataArray repr

<!-- #region jupyter={"source_hidden": true} -->
When using a Jupyter notebook, the Xarray `DataArray` `data` can be examined interactively.
+ The output cell contains a rich Jupyter notebook `repr` for the `DataArray` class.
+ The triangles next to the "Coordinates", "Indexes", and "Attributes" headings can be clicked with a mouse to reveal an expanded view.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(f'{type(data)=}\n')
data
```

---


## Examining DataArray attributes programmatically

<!-- #region jupyter={"source_hidden": true} -->
Of course, while this graphical view is handy, it is also possible to access various `DataArray` attributes programmatically. This permits us to write progam logic to manipulate `DataArray`s conditionally as needed. For instance:
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(data.coords)
```

<!-- #region jupyter={"source_hidden": true} -->
The dimensions `data.dims` are the strings/labels associated with the `DataArray` axes.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data.dims
```

<!-- #region jupyter={"source_hidden": true} -->
We can extract the coordinates as one-dimensional (homogeneous) NumPy arrays using the `coords` and the `.values` attributes.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(data.coords['x'].values)
```

<!-- #region jupyter={"source_hidden": true} -->
`data.attrs` is a dictionary containing other meta-data parsed from the GeoTIFF tags (the "Attributes" in the graphical view). Again, this is why `rioxarray` is useful; it is possible to write code that loads data from various fileformats into Xarray `DataArray`s, but this package wraps a lot of the messy code that would, e.g., populate `data.attrs`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data.attrs
```

---


## Using the DataArray rio accessor

<!-- #region jupyter={"source_hidden": true} -->
As mentioned, `rioxarray` extends the class `xarray.DataArray` with an *accessor* called `rio`. The `rio` accessor effectively adds a namespace with a variety of attributes. We can use a Python list comprehension to display those that do not start with an underscore (the so-called "private" and "dunder" methods/attributes).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
[name for name in dir(data.rio) if not name.startswith('_')]
```

<!-- #region jupyter={"source_hidden": true} -->
The attribute `data.rio.crs` is important for our purposes; it provides access to the coordinate reference system associated with this raster dataset.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(type(data.rio.crs))
print(data.rio.crs)
```

<!-- #region jupyter={"source_hidden": true} -->
The `.rio.crs` attribute itself is a data structure of class `CRS` from the [pyproj](https://pyproj4.github.io/pyproj/stable/index.html) project. The Python `repr` for this class returns a string like `EPSG:32610`; this number refers to the [EPSG Geodetic Parameter Dataset](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset).

From [Wikipedia](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset): 

> EPSG Geodetic Parameter Dataset (also EPSG registry) is a public registry of [geodetic datums](https://en.wikipedia.org/wiki/Geodetic_datum), [spatial reference systems](https://en.wikipedia.org/wiki/Spatial_reference_system), [Earth ellipsoids](https://en.wikipedia.org/wiki/Earth_ellipsoid), coordinate transformations and related [units of measurement](https://en.wikipedia.org/wiki/Unit_of_measurement), originated by a member of the [European Petroleum Survey Group](https://en.wikipedia.org/wiki/European_Petroleum_Survey_Group) (EPSG) in 1985. Each entity is assigned an EPSG code between 1024 and 32767, along with a standard machine-readable [well-known text (WKT)](https://en.wikipedia.org/wiki/Well-known_text_representation_of_coordinate_reference_systems) representation. The dataset is maintained by the [IOGP](https://en.wikipedia.org/wiki/International_Association_of_Oil_%26_Gas_Producers) Geomatics Committee. 
<!-- #endregion -->

---


## Manipulating data in a DataArray

<!-- #region jupyter={"source_hidden": true} -->
This data is stored using a particular [Universal Transverse Mercator (UTM)](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system) CRS; the coordinate labels would conventionally be *easting* and *northing*. However, when plotting, it will convenient to use *longitude* and *latitude* instead. We'll relabel the coordinates to reflect this; that is, the coordinate labelled `x` will be relabelled as `longitude` and the coordinate called `y` will be relabelled `latitude`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data = data.rename({'x':'longitude', 'y':'latitude'})
```

```python jupyter={"source_hidden": true}
print(data.coords)
```

<!-- #region jupyter={"source_hidden": true} -->
Again, even though the numerical values stored in the coordinate arrays don't strictly make sense as (longitude, latitude) values, we'll apply these labels now to simplify plotting later.

Xarray `DataArray` objects enable *slicing* much like Python lists do. The following two cells both extract the same subarray by two different method calls.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data.isel(longitude=slice(0,2))
```

```python jupyter={"source_hidden": true}
data.sel(longitude=[499_995, 500_025])
```

<!-- #region jupyter={"source_hidden": true} -->
Rather than using brackets to slice sections of arrays (as in NumPy), for `DataArray`s, we can use the `sel` or `isel` methods to select slices by continuous coordinate values or by integer positions (i.e., "pixel" coordinates) respectively. This is similar to using `.loc` and `.iloc` in Pandas to extract entries from a Pandas `Series` or `DataFrame`.

If we take a 2D slice from the 3D `DataArray` `data`, we can plot it using the `.plot` accessor (more on this later).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
data.isel(band=0).plot();
```

<!-- #region jupyter={"source_hidden": true} -->
That plot took some time to render because the array plotted had $3,600\times3,600$ pixels. We can use the Python builtin `slice` function to extract, say, every 100th pixel in either direction to plot a lower resolution image much faster.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
steps = 100
subset = slice(0,None,steps)
view = data.isel(longitude=subset, latitude=subset, band=0)
view.plot();
```

<!-- #region jupyter={"source_hidden": true} -->
The plot produced is rather dark (reflecting that most of the entries are zero according to the legend). Notice that the axes are labelled automatically using the `coords` we renamed before.
<!-- #endregion -->

---


## Extracting DataArray data to NumPy, Pandas

<!-- #region jupyter={"source_hidden": true} -->
Notice that a `DataArray` is a wrapper around a NumPy array. That NumPy array can be retrieved using the `.values` attribute.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
array = data.values
print(f'{type(array)=}')
print(f'{array.shape=}')
print(f'{array.dtype=}')
print(f'{array.nbytes=}')
```

<!-- #region jupyter={"source_hidden": true} -->
This raster data is stored as 8-bit unsigned integer data, so one byte for each pixel. A single unsigned 8-bit integer can represent integer values between 0 and 255. In an array with a bit more than thirteen million elements, that means there are many repeated values. We can see by putting the pixel values into a Pandas `Series` and using the `.value_counts` method.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
s_flat = pd.Series(array.flatten()).value_counts()
s_flat.sort_index()
```

<!-- #region jupyter={"source_hidden": true} -->
Most of the entries in this raster array are zero. The numerical values vary between 0 and 100 with the exception of some 1,700 pixels with the value 255. This will make more sense when we discuss the DIST data product specification.
<!-- #endregion -->

---


## Accumulating & concatenating a sequence of DataArrays

<!-- #region jupyter={"source_hidden": true} -->
It is often convenient to *stack* multiple two-dimensional arrays of raster data into a single three-dimensional array. In NumPy, this is typically done with the [`numpy.concatenate` function](https://numpy.org/doc/stable/reference/generated/numpy.concatenate.html). There is a similar utility in Xarray—[`xarray.concat`](https://docs.xarray.dev/en/stable/generated/xarray.concat.html) (that is similar in design to the Pandas function [`pandas.concat`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html)). The principal distinction between `numpy.concatenate` and `xarray.concat` is that the latter function has to account for *labelled coordinates* while the former does not; this is important when, e.g., the coordinate axes of two rasters overlap but are not perfectly aligned.

To see how stacking rasters works, we'll start by making a list of three GeoTIFF files (stored locally), initializing an empty list `stack`, and then building a list of `DataArray`s in a loop.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
RASTER_FILES = list((Path().cwd() / '..' / 'assets').glob('OPERA*VEG*.tif'))

stack = []
for path in RASTER_FILES:
    print(f"Stacking {path.name}..")
    data = rio.open_rasterio(path).rename(dict(x='longitude', y='latitude'))
    band_name = path.stem.split('_')[-1]
    data.coords.update({'band': [band_name]})
    data.attrs = dict(description=f"OPERA DIST product", units=None)
    stack.append(data)
```

<!-- #region jupyter={"source_hidden": true} -->
Here are some important observations about the preceding code loop:

+ Using `rioxarray.open_rasterio` to load an Xarray `DataArray` into memory does a lot of work for us. In particular, it makes sure the continuous coordinates are sensibly aligned with the underlying pixel coordinates.
+ By default, `data.coords` has keys `x` & `y` that we choose to relabel as `longitude` & `latitude` respectively. Technically, the continuous coordinate values loaded from this particular GeoTIFF file are expressed in UTM coordinates (i.e., easting & northing), but, later, when plotting, the labels `longitude`  & `latitude` will be more convenient.
+ `data.coords['band']` as loaded from the file has value `1`. We choose to overwrite that value with the name of the band (which we extract from the filename as `band_name`).
+ By default, `rioxarray.open_rasterio` populates `data.attrs` with key-value pairs extracted from the TIFF tags. For different bands/layers, these attribute dictionaries could have conflicting keys or values. It may be advisable to preserve this metadata in some circumstances; we simply choose to discard it in this context to avoid potential conflicts. The minimal dictionary of attributes in the final data structure will have `description` and `units` as its only keys.

Having built up a list of `DataArray`s in the list `stack`, we can assemble a three-dimensional `DataArray` using `xarray.concat`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
stack = xr.concat(stack, dim='band')
```

<!-- #region jupyter={"source_hidden": true} -->
The `xarray.concat` function accepts a sequence of `xarray.DataArray` objects with conforming dimensions and *concatenates* them along a specified dimension. For this example, we stack two-dimensional rasters that correspond to different bands or layers; that's why we use the option `dim='band'` in the call to `xarray.concat`. Later, we'll stack two-dimensional rasters along a *time* axis instead (this involves slightly different code to ensure correct labelling & alignment).

Let's examine `stack` through its `repr` in this Jupyter notebook.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
stack
```

<!-- #region jupyter={"source_hidden": true} -->
Notice that `stack` has a CRS associated with it that was parsed by `rioxarray.open_rasterio`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
stack.rio.crs
```

<!-- #region jupyter={"source_hidden": true} -->
This process is very useful for analysis (assuming that there is enough memory available to store the entire collection of rasters). Later, we'll use this approach numerous times to manage collections of rasters of conforming dimensions. The stack can then be used for producing a dynamic visualization with a slider or, alternatively, for producing a static plot.
<!-- #endregion -->

---

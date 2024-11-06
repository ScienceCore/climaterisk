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

# Data Manipulation Tools

<!-- #region jupyter={"source_hidden": true} -->
In this tutorial, we'll make use of a number of Python libraries to work with geospatial data. There are numerous ways to work with data and so choosing tooling can be difficult. The principal library we'll be using is [*Xarray*](https://docs.xarray.dev/en/stable/index.html) for its `DataArray` and `Dataset` data structures and associated utilities as well as [NumPy](https://numpy.org) and [Pandas](https://pandas.pydata.org) for manipulating homogeneous numerical arrays and tabular data respectively. We'll also make use of [Rasterio](https://rasterio.readthedocs.io/en/stable) as a tool for reading data or meta-data from GeoTIFF files; judicious use of Rasterio can make a big difference when working with remote files in the cloud.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
from warnings import filterwarnings
filterwarnings('ignore')

from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import rioxarray as rio
import rasterio
```

---


## [rioxarray](https://corteva.github.io/rioxarray/html/index.html)

<!-- #region jupyter={"source_hidden": true} -->
+ `rioxarray` is a package to *extend* Xarray
+ Primary use within this tutorial:
  + `rioxarray.open_rasterio` enables loading GeoTIFF files directly into Xarray `DataArray` structures
  + `xarray.DataArray.rio` extension provides useful utilities (e.g., for specifying CRS information)

To get used to working with GeoTIFF files, we'll use a specific example in this notebook. We'll explain more about what kind of data is contained within the file later; for now, we want to get used to the tools we'll use to load such data throughout the tutorial.
<!-- #endregion -->

---


### Loading files into a DataArray

<!-- #region jupyter={"source_hidden": true} -->
Observe first that `open_rasterio` works on local file paths and remote URLs.
+ Predictably, local access is faster than remote access.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
LOCAL_PATH = Path('..') / 'assets' / 'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'
da = rio.open_rasterio(LOCAL_PATH)
```

```python jupyter={"source_hidden": true}
%%time
REMOTE_URL ='https://opera-provisional-products.s3.us-west-2.amazonaws.com/DIST/DIST_HLS/WG/DIST-ALERT/McKinney_Wildfire/OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1/OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'
da_remote = rio.open_rasterio(REMOTE_URL)
```

<!-- #region jupyter={"source_hidden": true} -->
This next operation compares elements of an Xarray `DataArray` elementwise (the use of the `.all` method is similar to what we would do to compare NumPy arrays). This is generally not an advisable way to compare arrays, series, dataframes, or other large data structures that contain many elements. However, in this particular instance, because the two data structures have been read from the same file stored in two different locations, element-by-element comparison in memory confirms that the data loaded from two different sources is identical in every bit.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
(da_remote == da).all() # Verify that the data is identical from both sources
```

---


## [Xarray](https://docs.xarray.dev/en/stable/index.html)

<!-- #region jupyter={"source_hidden": true} -->
<center><img src="https://docs.xarray.dev/en/stable/_static/Xarray_Logo_RGB_Final.svg"></img></center>

Let's examine the data structure loaded above from the file `LOCAL_PATH`.
<!-- #endregion -->

---


### Examining the rich DataArray repr

<!-- #region jupyter={"source_hidden": true} -->
Observe, in this notebook, the `repr` for an Xarray `DataArray` can be interactively examined.
+ The output cell contains a rich Jupyter notebook `repr` for the `DataArray` class.
+ The triangles next to the "Coordinates", "Indexes", and "Attributes" headings can be clicked with a mouse to reveal an expanded view.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(f'{type(da)=}\n')
da
```

---


### Examining DataArray attributes programmatically

<!-- #region jupyter={"source_hidden": true} -->
Of course, while this graphical view is handy, it is also possible to access various `DataArray` attributes programmatically. This permits us to write progam logic to manipulate `DataArray`s conditionally as needed. For instance:
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(da.coords)
```

<!-- #region jupyter={"source_hidden": true} -->
The dimensions `da.dims` are the strings/labels associated with the `DataArray` axes.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
da.dims
```

<!-- #region jupyter={"source_hidden": true} -->
We can extract the coordinates as one-dimensional (homogeneous) NumPy arrays using the `coords` and the `.values` attributes.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(da.coords['x'].values)
```

<!-- #region jupyter={"source_hidden": true} -->
`data.attrs` is a dictionary containing other meta-data parsed from the GeoTIFF tags (the "Attributes" in the graphical view). Again, this is why `rioxarray` is useful; it is possible to write code that loads data from various fileformats into Xarray `DataArray`s, but this package wraps a lot of the messy code that would, e.g., populate `da.attrs`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
da.attrs
```

---


### Using the DataArray rio accessor

<!-- #region jupyter={"source_hidden": true} -->
As mentioned, `rioxarray` extends the class `xarray.DataArray` with an *accessor* called `rio`. The `rio` accessor effectively adds a namespace with a variety of attributes. WE can use a Python list comprehension to display those that do not start with an underscore (the so-called "private" and "dunder" methods/attributes).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
# Use a list comprehension to display relevant attributes/methods
[name for name in dir(da.rio) if not name.startswith('_')]
```

<!-- #region jupyter={"source_hidden": true} -->
The attribute `da.rio.crs` is important for our purposes; it provides access to the coordinate reference system associated with this raster dataset.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
print(type(da.rio.crs))
print(da.rio.crs)
```

<!-- #region jupyter={"source_hidden": true} -->
The `.rio.crs` attribute itself is a data structure of class `CRS`. The Python `repr` for this class returns a string like `EPSG:32610`; this number refers to the [EPSG Geodetic Parameter Dataset](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset).

From [Wikipedia](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset): 

> EPSG Geodetic Parameter Dataset (also EPSG registry) is a public registry of [geodetic datums](https://en.wikipedia.org/wiki/Geodetic_datum), [spatial reference systems](https://en.wikipedia.org/wiki/Spatial_reference_system), [Earth ellipsoids](https://en.wikipedia.org/wiki/Earth_ellipsoid), coordinate transformations and related [units of measurement](https://en.wikipedia.org/wiki/Unit_of_measurement), originated by a member of the [European Petroleum Survey Group](https://en.wikipedia.org/wiki/European_Petroleum_Survey_Group) (EPSG) in 1985. Each entity is assigned an EPSG code between 1024 and 32767, along with a standard machine-readable [well-known text (WKT)](https://en.wikipedia.org/wiki/Well-known_text_representation_of_coordinate_reference_systems) representation. The dataset is maintained by the [IOGP](https://en.wikipedia.org/wiki/International_Association_of_Oil_%26_Gas_Producers) Geomatics Committee. 
<!-- #endregion -->

---


### Manipulating data in a DataArray

<!-- #region jupyter={"source_hidden": true} -->
Given that this data is stored using a particular [Universal Transverse Mercator (UTM)](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system) CRS, let's relabel the coordinates to reflect this; that is, the coordinate labelled `x` would conventionally be called `easting` and the coordinate called `y` would be called `northing`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
da = da.rename({'x':'easting', 'y':'northing', 'band':'band'})
```

```python jupyter={"source_hidden": true}
print(da.coords)
```

<!-- #region jupyter={"source_hidden": true} -->
Xarray `DataArray`s permits slicing using coordinate values or their corresponding integer positions using the `sel` and `isel` accessors respectively. This is similar to using `.loc` and `.iloc` in Pandas to extract entries from a Pandas `Series` or `DataFrame`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
da.isel(easting=slice(0,2))
```

```python jupyter={"source_hidden": true}
da.sel(easting=[499995, 500025])
```

<!-- #region jupyter={"source_hidden": true} -->
If we take a 2D slice from this 3D `DataArray`, we can plot it using the `.plot` accessor (more on this later).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
da.isel(band=0).plot();
```

<!-- #region jupyter={"source_hidden": true} -->
The plot produced is rather dark (reflecting that most of the entries are zero according to the legend). Notice that the axes are labelled automatically using the `coords` we renamed before.
<!-- #endregion -->

---


### Extracting DataArray data to NumPy, Pandas

<!-- #region jupyter={"source_hidden": true} -->
Finally, recall that a `DataArray` is a wrapper around a NumPy array. That NumPy array can be retrieved using the `.values` attribute.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
array = da.values
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


## [rasterio](https://rasterio.readthedocs.io/en/stable)

<!-- #region jupyter={"source_hidden": true} -->
Having reviewed some features of Xarray (and of its extension `rioxarray`), let's briefly look at `rasterio` as a means of exploring GeoTIFF files.

From the [Rasterio documentation](https://rasterio.readthedocs.io/en/stable):

> Before Rasterio there was one Python option for accessing the many different kind of raster data files used in the GIS field: the Python bindings distributed with the [Geospatial Data Abstraction Library, GDAL](http://gdal.org/). These bindings extend Python, but provide little abstraction for GDAL’s C API. This means that Python programs using them tend to read and run like C programs. For example, GDAL’s Python bindings require users to watch out for dangling C pointers, potential crashers of programs. This is bad: among other considerations we’ve chosen Python instead of C to avoid problems with pointers.
>
>What would it be like to have a geospatial data abstraction in the Python standard library? One that used modern Python language features and idioms? One that freed users from concern about dangling pointers and other C programming pitfalls? Rasterio’s goal is to be this kind of raster data library – expressing GDAL’s data model using fewer non-idiomatic extension classes and more idiomatic Python types and protocols, while performing as fast as GDAL’s Python bindings.
>
>High performance, lower cognitive load, cleaner and more transparent code. This is what Rasterio is about.
<!-- #endregion -->

---


### Opening files with rasterio.open

```python jupyter={"source_hidden": true}
# Show rasterio.open works using context manager
import rasterio
from pathlib import Path
LOCAL_PATH = Path('..') / 'assets' / \
             'OPERA_L3_DIST-ALERT-HLS_T10TEM_20220815T185931Z_20220817T153514Z_S2A_30_v0.1_VEG-ANOM-MAX.tif'
print(LOCAL_PATH)
```

<!-- #region jupyter={"source_hidden": true} -->
Given a data source (e.g., a GeoTIFF file in the current context), we can open a `DatasetReader` object associated with using `rasterio.open`. Technically, we have to remember to close the object afterward. That is, our code would look like this:

```python
ds = rasterio.open(LOCAL_PATH)
..
# do some computation
...
ds.close()
```

As with file-handling in Python, we can use a *context manager* (i.e., a `with` clause) instead.
```python
with rasterio.open(LOCAL_PATH) as ds:
  ...
  # do some computation
  ...

# more code outside the scope of the with block.
```
The dataset will be closed automatically outside the `with` block.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(f'{type(ds)=}')
    assert not ds.closed

# outside the scope of the with block
assert ds.closed
```

<!-- #region jupyter={"source_hidden": true} -->
The principal advantage of using `rasterio.open` rather than `rioxarray.open_rasterio` to open a file is that the latter approach opens the file and immediately loads its contents into a `DataDarray` in memory.

By contrast, using `rasterio.open` merely opens the file in place and its contents can be examined *without* immediately loading its contents into memory. This makes a lot of difference when working with remote data; transferring the entire contents across a network takes time. If we examine the meta-data—which is typically much smaller and can be transferred quickly—we may find, e.g., that the contents of the file do not warrant moving arrays of data across the network.
<!-- #endregion -->

---


### Examining DatasetReader attributes

<!-- #region jupyter={"source_hidden": true} -->
When a file is opened using `rasterio.open`, the object instantiated is from the `DatasetReader` class. This class has a number of attributes and methods of interest to us:

 |  | | |
 |--|--|--|
 |`profile`|`height`|`width` |
 |`shape` |`count`|`nodata`|
 |`crs`|`transform`|`bounds`|
 |`xy`|`index`|`read` |

First, given a `DatasetReader` `ds` associated with a data source, examining `ds.profile` returns some diagnostic information.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(f'{ds.profile=}')
```

<!-- #region jupyter={"source_hidden": true} -->
The attributes `ds.height`, `ds.width`, `ds.shape`, `ds.count`, `ds.nodata`, and `ds.transform` are all included in the output from `ds.profile` but are also accessible individually.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(f'{ds.height=}')
    print(f'{ds.width=}')
    print(f'{ds.shape=}')
    print(f'{ds.count=}')
    print(f'{ds.nodata=}')
    print(f'{ds.crs=}')
    print(f'{ds.transform=}')
```

---


### Reading data into memory

<!-- #region jupyter={"source_hidden": true} -->
The method `ds.read` loads an array from the data file into memory. Notice this can be done on local or remote files.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%%time
with rasterio.open(LOCAL_PATH) as ds:
    array = ds.read()
    print(f'{array.shape=}')
```

```python jupyter={"source_hidden": true}
%%time
with rasterio.open(REMOTE_URL) as ds:
    array = ds.read()
    print(f'{array.shape=}')
```

```python jupyter={"source_hidden": true}
print(f'{type(array)=}')
```

<!-- #region jupyter={"source_hidden": true} -->
The array loaded into memory with `ds.read` is a NumPy array. This can be wrapped by an Xarray `DataArray` if we provide additional code to specify the coordinate labels and so on.
<!-- #endregion -->

---


### Mapping coordinates

<!-- #region jupyter={"source_hidden": true} -->
Earlier, we loaded data from a local file into a `DataArray` called `da` using `rioxarray.open_rasterio`.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
da = rio.open_rasterio(LOCAL_PATH)
da
```

<!-- #region jupyter={"source_hidden": true} -->
Doing so simplified the loading raster data from a GeoTIFF file into an Xarray `DataArray` while filling in the metadata for us. In particular, the coordinates associated with the pixels were stored into `da.coords` (the default coordinate axes are `band`, `x`, and `y` for this three-dimensional array).

If we ignore the extra `band` dimension, the pixels of the raster data are associated with pixel coordinates (integers) and spatial coordinates (real values, typically a point at the centre of each pixel). 

![](http://ioam.github.io/topographica/_images/matrix_coords.png)
![](http://ioam.github.io/topographica/_images/sheet_coords_-0.2_0.4.png)
(from `http://ioam.github.io/topographica`)

The accessors `da.isel` and `da.sel` allow us to extract slices from the data array using pixel coordinates or spatial coordinates respectively.
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
If we use `rasterio.open` to open a file, the `DatasetReader` attribute `transform` provides the details of how to convert between pixel and spatial coordinates. We will use this capability in some of the case studies later.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(f'{ds.transform=}')
    print(f'{np.abs(ds.transform[0])=}')
    print(f'{np.abs(ds.transform[4])=}')
```

<!-- #region jupyter={"source_hidden": true} -->
The attribute `ds.transform` is an object describing an [*affine transformation*](https://en.wikipedia.org/wiki/Affine_transformation) (represented above as a $2\times3$ matrix). Notice that the absolute values of the diagonal entries of the matrix `ds.transform` give the spatial dimensions of pixels ($30\mathrm{m}\times30\mathrm{m}$ in this case).

We can also use this object to convert pixel coordinates to the corresponding spatial coordinates.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(f'{ds.transform * (0,0)=}')       # top-left pixel
    print(f'{ds.transform * (0,3660)=}')    # bottom-left pixel
    print(f'{ds.transform * (3660,0)=}')    # top-right pixel
    print(f'{ds.transform * (3660,3660)=}') # bottom-right pixel
```

<!-- #region jupyter={"source_hidden": true} -->
The attribute `ds.bounds` displays the bounds of the spatial region (left, bottom, right, top).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(f'coordinate bounds: {ds.bounds=}')
```

<!-- #region jupyter={"source_hidden": true} -->
The method `ds.xy` also converts integer index coordinates to continuous coordinates. Notice that `ds.xy` maps integers to the centre of pixels. The loops below print out the first top left corner of the coordinates in pixel coordinates and then the cooresponding spatial coordinates.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    for k in range(3):
        for l in range(4):
            print(f'({k:2d},{l:2d})','\t', end='')
        print()
    print()
    for k in range(3):
        for l in range(4):
            e,n = ds.xy(k,l)
            print(f'({e},{n})','\t', end='')
        print()
    print()
```

<!-- #region jupyter={"source_hidden": true} -->
`ds.index` does the reverse: given spatial coordinates `(x,y)`, it returns the integer indices of the pixel that contains that point.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(ds.index(500000, 4700015))
```

<!-- #region jupyter={"source_hidden": true} -->
These conversions can be tricky, particularly because pixel coordinates map to the centres of the pixels and also because the second `y` spatial coordinate *decreases* as the second pixel coordinate *increases*. Keeping track of tedious details like this is partly why loading from `rioxarray` is useful, i.e., this is done for us. But it is worth knowing that we can reconstruct this mapping if needed from meta-data in the GeoTIFF file (we use this fact later).
<!-- #endregion -->

```python jupyter={"source_hidden": true}
with rasterio.open(LOCAL_PATH) as ds:
    print(ds.bounds)
    print(ds.transform * (0.5,0.5)) # Maps to centre of top left pixel
    print(ds.xy(0,0))               # Same as above
    print(ds.transform * (0,0))     # Maps to top left corner of top left pixel
    print(ds.xy(-0.5,-0.5))         # Same as above
    print(ds.transform[0], ds.transform[4])
```

---

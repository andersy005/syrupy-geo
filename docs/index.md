# syrupy-geo

syrupy-geo is a [syrupy](https://github.com/syrupy-project/syrupy) extension package for geospatial and array data formats. It adds snapshot testing support for:

- **xarray** `DataArray` and `Dataset` objects, stored as Zarr
- **GeoPandas** `GeoDataFrame` objects, stored as GeoParquet

Snapshots can live on a local filesystem or on any fsspec-compatible remote storage (S3, GCS, ADLS) by setting a single environment variable.

## Install

```bash
# xarray support
pip install "syrupy-geo[xarray]"

# GeoPandas support
pip install "syrupy-geo[geo]"

# Both
pip install "syrupy-geo[all]"
```

Python 3.11 or later is required.

## Quick example

```python
# No conftest.py changes needed. The fixtures are registered automatically.

def test_my_array(xarray_snapshot):
    import numpy as np
    import xarray as xr

    rng = np.random.default_rng(42)
    da = xr.DataArray(rng.random((3, 4)), dims=["x", "y"])
    assert xarray_snapshot == da  # snapshot on the left


def test_my_geodataframe(geodataframe_snapshot):
    import geopandas as gpd
    from shapely.geometry import Point

    gdf = gpd.GeoDataFrame(
        {"value": [1, 2, 3]},
        geometry=[Point(0, 0), Point(1, 1), Point(2, 2)],
        crs="EPSG:4326",
    )
    assert geodataframe_snapshot == gdf  # snapshot on the left
```

Create snapshots on the first run:

```bash
pytest --snapshot-update
```

Then run normally to catch regressions:

```bash
pytest
```

## Documentation

This documentation follows the [Diátaxis](https://diataxis.fr) framework.

| Section | Purpose |
|---|---|
| [Tutorials](tutorials/index.md) | Step-by-step guides for getting started |
| [How-to guides](how-to/index.md) | Recipes for specific goals |
| [Reference](reference/index.md) | API and configuration details |
| [Explanation](explanation/index.md) | Background and design rationale |

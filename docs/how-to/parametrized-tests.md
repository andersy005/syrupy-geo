# Test parametrized cases

Use pytest parametrize to run the same snapshot assertion over multiple inputs. syrupy-geo generates a distinct snapshot file name for each parameter combination so each case is tracked independently.

## Parametrize over a single argument

```python
import numpy as np
import pytest
import xarray as xr


@pytest.mark.parametrize("size", [4, 8, 16])
def test_array_by_size(xarray_snapshot, size):
    rng = np.random.default_rng(42)
    da = xr.DataArray(rng.random((size, size)), dims=["x", "y"])
    assert xarray_snapshot == da
```

syrupy-geo sanitizes the parameter into the snapshot file name. For the three cases above, the snapshots will be:

```
tests/__snapshots__/test_climate/
    test_array_by_size_4.zarr
    test_array_by_size_8.zarr
    test_array_by_size_16.zarr
```

## Parametrize over multiple independent arguments

Use separate `parametrize` decorators for independent axes. This keeps the parametrization clear and avoids having to reason about the full product manually:

```python
@pytest.mark.parametrize("crs", ["EPSG:4326", "EPSG:3857"])
@pytest.mark.parametrize("n_points", [10, 100])
def test_points_snapshot(geodataframe_snapshot, n_points, crs):
    import geopandas as gpd
    from shapely.geometry import Point

    rng = np.random.default_rng(42)
    coords = rng.random((n_points, 2))
    gdf = gpd.GeoDataFrame(
        {"value": np.arange(n_points)},
        geometry=[Point(x, y) for x, y in coords],
        crs=crs,
    )
    assert geodataframe_snapshot == gdf
```

## Create the snapshots

```bash
pytest --snapshot-update tests/test_places.py
```

All parameter combinations get their own snapshot file on the first run.

## Snapshot naming for special characters

Brackets and slashes in parameter values are replaced with underscores. A test named `test_fn[a/b]` produces a snapshot named `test_fn_a_b.<ext>`.

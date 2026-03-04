# Snapshot test an xarray DataArray

This tutorial walks you through writing your first snapshot test for an xarray `DataArray` using syrupy-geo. By the end you will have a passing test and a snapshot stored on disk.

## Prerequisites

- Python 3.11 or later
- A project with pytest already set up

## Install

```bash
pip install "syrupy-geo[xarray]"
```

This installs syrupy-geo along with xarray and zarr.

## Write the test

Create a test file, for example `tests/test_climate.py`:

```python
import numpy as np
import xarray as xr


def test_temperature_array(xarray_snapshot):
    rng = np.random.default_rng(42)
    da = xr.DataArray(
        rng.random((3, 4)),
        dims=["lat", "lon"],
        name="temperature",
    )
    assert xarray_snapshot == da
```

Two things to notice:

- The `xarray_snapshot` fixture is provided automatically by syrupy-geo. You do not need to add anything to `conftest.py`.
- The snapshot is on the **left** side of `==`. This is required. If the xarray object is on the left, xarray intercepts the comparison with element-wise broadcasting and syrupy never sees it.

## Create the snapshot

Run pytest with the `--snapshot-update` flag to write the snapshot for the first time:

```bash
pytest --snapshot-update tests/test_climate.py
```

Pytest will create a directory `tests/__snapshots__/test_climate/` and write a file named `test_temperature_array.zarr` inside it. This file is your snapshot and should be committed to version control.

## Run the test

Now run pytest without the flag:

```bash
pytest tests/test_climate.py
```

The test passes because the newly computed array matches the stored snapshot.

## Test a Dataset

The `xarray_snapshot` fixture also handles `xr.Dataset` objects without any extra configuration:

```python
def test_climate_dataset(xarray_snapshot):
    rng = np.random.default_rng(42)
    ds = xr.Dataset(
        {
            "temperature": (["lat", "lon"], rng.random((3, 4))),
            "precipitation": (["lat", "lon"], rng.random((3, 4))),
        }
    )
    assert xarray_snapshot == ds
```

## Next steps

- See [Snapshot test a GeoDataFrame](geodataframe-snapshots.md) for the GeoPandas equivalent.
- See [Store snapshots on S3](../how-to/store-on-s3.md) to share snapshots across machines.
- See [Update snapshots](../how-to/update-snapshots.md) for the correct workflow when your data changes.

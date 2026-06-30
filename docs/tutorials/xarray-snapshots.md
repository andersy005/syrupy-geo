# Snapshot test xarray objects

This tutorial walks you through writing your first snapshot tests for xarray objects using syrupy-geo. By the end you will have passing tests and snapshots stored in a versioned icechunk repository.

## Prerequisites

- Python 3.12 or later
- A project with pytest already set up

## Install

```bash
pip install "syrupy-geo[icechunk]"
```

This installs syrupy-geo along with xarray, zarr, and icechunk.

## Test a DataArray

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

syrupy-geo creates an icechunk repository at `tests/__snapshots__/icechunk/` (if it does not already exist) and writes the snapshot as a zarr group inside it. At the end of the session, it commits all changes to the repository with a timestamp message. Commit this repository to version control:

```bash
git add tests/__snapshots__/icechunk/
git commit -m "add temperature snapshot"
```

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

## Test a DataTree

`xr.DataTree` objects are stored natively and read back as a `DataTree`:

```python
def test_climate_tree(xarray_snapshot):
    rng = np.random.default_rng(42)
    dt = xr.DataTree.from_dict({
        'surface': xr.Dataset({'temperature': ('x', rng.random(4))}),
        'upper_air': xr.Dataset({'geopotential': ('z', rng.random(8))}),
    })
    assert xarray_snapshot == dt
```

The tree structure is preserved across the round-trip. If you later change the tree structure (add or remove groups), run `--snapshot-update` to regenerate the snapshot — old groups in the repository are automatically cleaned up.

## Next steps

- See [Snapshot test a GeoDataFrame](geodataframe-snapshots.md) for the GeoPandas equivalent.
- See [Store snapshots on S3](../how-to/store-on-s3.md) to share snapshots across machines.
- See [Update snapshots](../how-to/update-snapshots.md) for the correct workflow when your data changes.

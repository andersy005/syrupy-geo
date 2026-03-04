# Snapshot test a GeoDataFrame

This tutorial walks you through writing your first snapshot test for a GeoPandas `GeoDataFrame` using syrupy-geo. By the end you will have a passing test and a GeoParquet snapshot stored on disk.

## Prerequisites

- Python 3.11 or later
- A project with pytest already set up

## Install

```bash
pip install "syrupy-geo[geo]"
```

This installs syrupy-geo along with geopandas and pyarrow.

## Write the test

Create a test file, for example `tests/test_places.py`:

```python
import geopandas as gpd
from shapely.geometry import Point


def test_places_snapshot(geodataframe_snapshot):
    gdf = gpd.GeoDataFrame(
        {"name": ["A", "B", "C"], "value": [10, 20, 30]},
        geometry=[Point(0, 0), Point(1, 1), Point(2, 2)],
        crs="EPSG:4326",
    )
    assert geodataframe_snapshot == gdf
```

Two things to notice:

- The `geodataframe_snapshot` fixture is provided automatically by syrupy-geo. You do not need to add anything to `conftest.py`.
- The snapshot is on the **left** side of `==`. This is required. If the GeoDataFrame is on the left, pandas intercepts the comparison with element-wise broadcasting and syrupy never sees it.

## Create the snapshot

Run pytest with the `--snapshot-update` flag to write the snapshot for the first time:

```bash
pytest --snapshot-update tests/test_places.py
```

Pytest will create a directory `tests/__snapshots__/test_places/` and write a file named `test_places_snapshot.parquet` inside it. Commit this file to version control along with your code.

## Run the test

Now run without the flag:

```bash
pytest tests/test_places.py
```

The test passes because the computed GeoDataFrame matches what was stored.

## What is compared

The equality check covers three things simultaneously:

- All non-geometry columns (dtype, values, and index).
- All geometries using exact geometric equality.
- The coordinate reference system (CRS).

If any of these differs, the test fails with a diff that shows both the stored snapshot and the current data.

## Next steps

- See [Snapshot test an xarray DataArray](xarray-snapshots.md) for the xarray equivalent.
- See [Store snapshots on S3](../how-to/store-on-s3.md) to share snapshots across machines.
- See [Update snapshots](../how-to/update-snapshots.md) for the correct workflow when your data changes.

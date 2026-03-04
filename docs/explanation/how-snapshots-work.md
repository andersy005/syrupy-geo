# How snapshot testing works

## The snapshot cycle

Snapshot testing is a form of regression testing where the expected output of a function is stored in a file rather than written out by hand in the test itself.

The cycle has two phases:

**First run (snapshot creation):** You run pytest with `--snapshot-update`. The extension serializes your data object and writes it to disk. Nothing is compared yet.

**Subsequent runs (regression check):** You run pytest normally. The extension serializes the data again, reads the stored snapshot from disk, and compares them. If they differ, the test fails.

This makes snapshot tests excellent for catching unintended regressions in data pipelines, model outputs, and geospatial transformations.

## How syrupy-geo fits in

Syrupy is a pytest plugin that provides a general snapshot testing framework. syrupy-geo extends it with two format-aware extensions:

- `XarraySnapshotExtension` serializes xarray objects to Zarr and compares them with `xr.testing.assert_allclose`.
- `GeoDataFrameSnapshotExtension` serializes GeoDataFrames to GeoParquet and compares attributes, geometries, and CRS separately.

Both extensions inherit from `BaseGeoSnapshotExtension`, which provides remote-aware path resolution via `upath.UPath`. This means the same test code works whether snapshots are stored locally or on S3.

## Path resolution

When a test runs, syrupy-geo computes a snapshot path from three pieces of information:

1. The location of the test file on disk.
2. The name of the test function (with parameter values if parametrized).
3. The `SNAPSHOT_STORAGE_PATH` environment variable (if set).

For a test `test_temperature` in `tests/test_climate.py` with local storage, the path is:

```
tests/__snapshots__/test_climate/test_temperature.zarr
```

With `SNAPSHOT_STORAGE_PATH=s3://my-bucket/snapshots`, the path becomes:

```
s3://my-bucket/snapshots/test_climate/test_temperature.zarr
```

## Snapshot file formats

Each extension uses a format that naturally represents its data type:

**Zarr (xarray):** A directory-based format. The snapshot is a folder that can hold chunked, compressed multi-dimensional arrays with metadata. `DataArray` objects are wrapped in a single-variable `Dataset` before writing.

**GeoParquet (GeoDataFrame):** A columnar file format based on Apache Parquet with standardized geometry encoding. syrupy-geo writes GeoParquet 1.1.0 with WKB geometry encoding, ZSTD compression, and a covering bounding-box column for spatial indexing.

## Remote storage via universal-pathlib

All path operations go through `upath.UPath` from the `universal-pathlib` package. This gives syrupy-geo a single code path that works for local filesystem paths, S3 URIs, GCS URIs, ADLS URIs, and any other fsspec backend.

When syrupy-geo writes a Zarr store on S3, it passes the `s3://` URI directly to `Dataset.to_zarr`. When it reads a GeoParquet file from GCS, it passes a `gs://` URI to `GeoDataFrame.from_parquet`. No special-casing is needed per backend.

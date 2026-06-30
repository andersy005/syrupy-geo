# How snapshot testing works

## The snapshot cycle

Snapshot testing is a form of regression testing where the expected output of a function is stored in a file rather than written out by hand in the test itself.

The cycle has two phases:

**First run (snapshot creation):** You run pytest with `--snapshot-update`. The extension serializes your data object and writes it to the snapshot store. Nothing is compared yet.

**Subsequent runs (regression check):** You run pytest normally. The extension serializes the data again, reads the stored snapshot, and compares them. If they differ, the test fails.

This makes snapshot tests excellent for catching unintended regressions in data pipelines, model outputs, and geospatial transformations.

## How syrupy-geo fits in

Syrupy is a pytest plugin that provides a general snapshot testing framework. syrupy-geo extends it with two format-aware extensions:

- `XarraySnapshotExtension` stores xarray objects (`DataArray`, `Dataset`, `DataTree`) in a versioned [icechunk](https://icechunk.io) repository and compares them with `xr.testing.assert_allclose`.
- `GeoDataFrameSnapshotExtension` serializes GeoDataFrames to GeoParquet and compares attributes, geometries, and CRS separately.

Both extensions inherit from `BaseGeoSnapshotExtension`, which provides remote-aware path resolution via `upath.UPath`. This means the same test code works whether snapshots are stored locally or on S3.

## Path resolution

### xarray (icechunk)

All xarray snapshots for a project share a single icechunk repository. The repository lives at:

```
tests/__snapshots__/icechunk/
```

or, when `SNAPSHOT_STORAGE_PATH` is set:

```
$SNAPSHOT_STORAGE_PATH/icechunk/
```

Within the repository, each snapshot is a zarr group whose path encodes the test file and test name:

```
test_climate/test_temperature_array      # DataArray or Dataset
test_climate/test_tree_snapshot          # DataTree
```

After a `--snapshot-update` run, the extension automatically commits all changes to the icechunk repository as a single versioned commit (via `pytest_sessionfinish`). Read-only runs produce no commit.

### GeoDataFrame (GeoParquet)

For a test `test_boundaries` in `tests/test_geo.py` with local storage:

```
tests/__snapshots__/test_geo/test_boundaries.parquet
```

With `SNAPSHOT_STORAGE_PATH=s3://my-bucket/snapshots`:

```
s3://my-bucket/snapshots/test_geo/test_boundaries.parquet
```

## Snapshot file formats

**icechunk (xarray):** A versioned chunk store built on Zarr v3. All snapshots for a project live in one repository as zarr groups. Each group is tagged with `_syrupy_geo_type` (`'dataset'` or `'datatree'`) so the correct reader is used on read-back. `DataArray` objects are promoted to a single-variable `Dataset` before writing (a zarr requirement). `DataTree` objects are written node-by-node, with each child node stored as a Dataset group at the corresponding sub-path. The repository can be committed to git and versioned along with your code.

**GeoParquet (GeoDataFrame):** A columnar file format based on Apache Parquet with standardized geometry encoding. syrupy-geo writes GeoParquet 1.1.0 with WKB geometry encoding, ZSTD compression, and a covering bounding-box column for spatial indexing.

## Remote storage via universal-pathlib

All path operations go through `upath.UPath` from the `universal-pathlib` package. This gives syrupy-geo a single code path that works for local filesystem paths, S3 URIs, GCS URIs, ADLS URIs, and any other fsspec backend.

When `SNAPSHOT_STORAGE_PATH=s3://my-bucket/snapshots` is set, the icechunk repository is opened at `s3://my-bucket/snapshots/icechunk/` using icechunk's S3 storage backend. GeoParquet files are written directly to the S3 prefix using `s3fs`. No special-casing is needed per backend.

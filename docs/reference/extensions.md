# Extensions reference

## XarraySnapshotExtension

```python
from syrupy_geo import XarraySnapshotExtension
```

Stores xarray `DataArray`, `Dataset`, and `DataTree` objects in a versioned [icechunk](https://icechunk.io) repository. Each snapshot is a zarr group inside the repository at path `<test_stem>/<test_name>`.

**Requires:** `pip install "syrupy-geo[icechunk]"` (icechunk >= 2.0, xarray >= 2026.2, zarr >= 3)

### Fixture

```python
def test_my_array(xarray_snapshot):
    assert xarray_snapshot == my_dataarray
```

The `xarray_snapshot` fixture is registered automatically. No `conftest.py` changes needed.

### Accepted types

| Type | Behaviour |
|---|---|
| `xr.DataArray` | Converted to a single-variable `Dataset` using `data.name` (falls back to `'data'`) before writing |
| `xr.Dataset` | Written as-is |
| `xr.DataTree` | Written node-by-node; each child stored as a Dataset group at the corresponding sub-path |
| Anything else | `TypeError` raised immediately |

### Equality check

Two objects are considered equal if `xr.testing.assert_allclose` passes with `rtol=1e-6` and `atol=1e-8`. If that fails, the check falls back to `xr.testing.assert_equal` for exact equality. If both fail, the test fails.

Type mismatches (e.g., comparing a `Dataset` read-back to a `DataTree`) are caught before numerical comparison and return `False` immediately.

### Storage format

All snapshots for a project share a single icechunk repository at `tests/__snapshots__/icechunk/` (or `$SNAPSHOT_STORAGE_PATH/icechunk/` when the environment variable is set). Within the repository, each snapshot is a zarr group tagged with a `_syrupy_geo_type` attribute (`'dataset'` or `'datatree'`) so the correct reader is used on read-back.

After a `--snapshot-update` run, `pytest_sessionfinish` commits all changes to the icechunk repository as one versioned commit. Read-only runs produce no commit.

### File extension

`icechunk` (used as the zarr group path suffix in syrupy's internal routing; the actual storage is the shared icechunk repository)

### Snapshot location

Snapshots are stored as zarr groups with paths of the form:

```
<test_file_stem>/<sanitized_test_name>
```

For example, a test `test_temperature_array` in `tests/test_climate.py` is stored at group path `test_climate/test_temperature_array` within the icechunk repository.

---

## GeoDataFrameSnapshotExtension

```python
from syrupy_geo import GeoDataFrameSnapshotExtension
```

Stores GeoPandas `GeoDataFrame` objects as GeoParquet files.

**Requires:** `pip install "syrupy-geo[geo]"` (geopandas >= 1.0, pyarrow >= 15)

### Fixture

```python
def test_my_geodataframe(geodataframe_snapshot):
    assert geodataframe_snapshot == my_gdf
```

The `geodataframe_snapshot` fixture is registered automatically.

### Accepted types

| Type | Behaviour |
|---|---|
| `gpd.GeoDataFrame` | Stored as GeoParquet |
| Anything else | `TypeError` raised immediately |

### Equality check

The comparison uses three checks, all of which must pass:

1. `pd.testing.assert_frame_equal` on all non-geometry columns (dtype, index type, and column type are all checked).
2. `GeoSeries.geom_equals` on the geometry column (exact geometric equality).
3. Direct CRS comparison (`serialized_data.crs == snapshot_data.crs`).

### Storage format

GeoParquet written by `GeoDataFrame.to_parquet` with these options:

| Option | Value |
|---|---|
| `compression` | `zstd` |
| `geometry_encoding` | `WKB` |
| `write_covering_bbox` | `True` |
| `schema_version` | `1.1.0` |
| `index` | Not written |

### File extension

`parquet` (no leading dot)

---

## BaseGeoSnapshotExtension

```python
from syrupy_geo._base import BaseGeoSnapshotExtension
```

Shared base class for both extensions. Inherit from this when building a custom format-specific extension.

### Class methods

#### `_get_base_snapshot_path() -> upath.UPath | None`

Reads `SNAPSHOT_STORAGE_PATH` from the environment. Returns a `UPath` pointing to the remote or local base, or `None` if the variable is not set.

#### `dirname(*, test_location) -> str`

Returns the directory that will hold snapshots for a given test file. When `SNAPSHOT_STORAGE_PATH` is set this is `<base>/<test_file_stem>/`. Otherwise it is `<test_file_parent>/__snapshots__/<test_file_stem>/`.

#### `get_snapshot_name(*, test_location, index=0) -> str`

Returns the base name (without extension) for a snapshot. Brackets and slashes in the pytest test name are replaced with underscores. `index` is appended with a dot separator when non-zero.

#### `get_location(*, test_location, index=0) -> str`

Combines `dirname` and `get_snapshot_name` into a full path string of the form `<dirname>/<name>.<file_extension>`.

#### `_warn_on_snapshot_name(*, snapshot_name, test_location) -> None`

No-op override that suppresses syrupy's built-in name-validation warnings. These warnings are not useful for geospatial snapshot names that include parameter brackets.

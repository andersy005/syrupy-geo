# Configuration reference

## Environment variables

### `SNAPSHOT_STORAGE_PATH`

Controls where snapshots are read from and written to.

| State | Behaviour |
|---|---|
| Not set | Snapshots go to `__snapshots__/<test_stem>/` next to the test file |
| Set to a local path | Snapshots go to `<path>/<test_stem>/` on the local filesystem |
| Set to an S3 URI | Snapshots go to `<s3://bucket/prefix>/<test_stem>/` on S3 |

**Example: local override**

```bash
export SNAPSHOT_STORAGE_PATH="/data/snapshots"
```

**Example: S3**

```bash
export SNAPSHOT_STORAGE_PATH="s3://my-bucket/project/snapshots"
```

Any fsspec-compatible URI scheme that `upath.UPath` supports is accepted, including `gs://` for Google Cloud Storage and `az://` for Azure Blob Storage.

## pytest flags

These flags come from syrupy and work with all syrupy-geo extensions.

| Flag | Effect |
|---|---|
| `--snapshot-update` | Write or overwrite snapshots for tests that run |
| `--snapshot-warn-unused` | Warn about snapshot files no longer referenced by any test |
| `--snapshot-default-extension` | Set the default extension class (rarely needed with syrupy-geo fixtures) |

## Optional dependencies

Install only what you need.

| Extra | Packages installed | Use when |
|---|---|---|
| `syrupy-geo[xarray]` | xarray >= 2024.1, zarr >= 3 | Testing xarray objects |
| `syrupy-geo[geo]` | geopandas >= 1.0, pyarrow >= 15 | Testing GeoDataFrames |
| `syrupy-geo[all]` | Both of the above | Testing both |

## pytest plugin entry point

syrupy-geo registers its plugin via the `pytest11` entry point in `pyproject.toml`:

```toml
[project.entry-points."pytest11"]
syrupy-geo = "syrupy_geo.plugin"
```

The plugin is active in any environment where syrupy-geo is installed. It registers the `xarray_snapshot` and `geodataframe_snapshot` fixtures globally. No `conftest.py` changes are needed.

# Override the snapshot fixture

syrupy-geo registers `xarray_snapshot` and `geodataframe_snapshot` automatically via its pytest plugin. If you need different behaviour for a specific test suite, redefine the fixture locally. pytest's fixture resolution always prefers the definition closest to the test.

## Change the snapshot location for one suite

```python
# tests/heavy/conftest.py
import os
import pytest
from syrupy_geo import XarraySnapshotExtension


@pytest.fixture
def xarray_snapshot(snapshot, tmp_path):
    os.environ["SNAPSHOT_STORAGE_PATH"] = str(tmp_path / "snapshots")
    yield snapshot.use_extension(XarraySnapshotExtension)
    del os.environ["SNAPSHOT_STORAGE_PATH"]
```

Tests in `tests/heavy/` now write snapshots to a temporary directory. Tests in all other directories continue to use the default location.

## Use a different extension class

If you have created a custom extension by subclassing `BaseGeoSnapshotExtension`, wire it up the same way:

```python
# conftest.py
import pytest
from my_project.extensions import MyCustomExtension


@pytest.fixture
def my_snapshot(snapshot):
    return snapshot.use_extension(MyCustomExtension)
```

Then use `my_snapshot` in your tests exactly like the built-in fixtures.

## Restore the default

Remove the local fixture definition or let it go out of scope. pytest will fall back to the plugin-registered version.

from datetime import UTC, datetime

import pytest

from .geodataframe import GeoDataFrameSnapshotExtension
from .xarray import XarraySnapshotExtension


@pytest.fixture
def xarray_snapshot(snapshot):
    """Snapshot fixture for xr.DataArray, xr.Dataset, and xr.DataTree (icechunk-backed).

    DataArray is converted to Dataset before storage (zarr requirement); Dataset and
    DataTree are stored natively. Each type reads back as the same type it was written as.

    Requires: pip install syrupy-geo[icechunk]

    IMPORTANT: Always write ``assert xarray_snapshot == data`` (snapshot on left).
    Putting xarray data on the left causes element-wise broadcasting instead of routing
    through syrupy.
    """
    return snapshot.use_extension(XarraySnapshotExtension)


@pytest.fixture
def geodataframe_snapshot(snapshot):
    """Snapshot fixture for GeoPandas GeoDataFrames (parquet-backed).

    IMPORTANT: Always write assertions as ``assert geodataframe_snapshot == gdf``.
    Putting a GeoDataFrame on the left (``assert gdf == snapshot``) causes pandas
    to perform element-wise comparison instead of routing through syrupy.
    """
    return snapshot.use_extension(GeoDataFrameSnapshotExtension)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if XarraySnapshotExtension._has_pending_writes:
        ts = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S')
        XarraySnapshotExtension.commit_session(f'syrupy-geo snapshot update {ts}')

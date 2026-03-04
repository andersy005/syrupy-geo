import pytest

from .geodataframe import GeoDataFrameSnapshotExtension
from .xarray import XarraySnapshotExtension


@pytest.fixture
def xarray_snapshot(snapshot):
    """Snapshot fixture for xarray DataArrays and Datasets (zarr-backed).

    IMPORTANT: Always write assertions as ``assert xarray_snapshot == data``.
    Putting xarray data on the left (``assert data == snapshot``) causes xarray
    to broadcast the comparison element-wise instead of routing through syrupy.
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

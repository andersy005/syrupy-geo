import pytest


# With xarray objects (DataArray, Dataset), always use `assert snapshot == data`
# (snapshot on left). If data is on the left, xarray intercepts `==` with
# element-wise broadcasting instead of routing through syrupy's assertion.
def test_dataarray_snapshot(xarray_snapshot, sample_dataarray):
    assert xarray_snapshot == sample_dataarray


def test_dataset_snapshot(xarray_snapshot, sample_dataset):
    assert xarray_snapshot == sample_dataset


def test_dataarray_snapshot_wrong_type_raises():
    from syrupy_geo import XarraySnapshotExtension

    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    with pytest.raises(TypeError, match='Expected xr.DataArray or xr.Dataset'):
        ext.serialize('not_an_array')


@pytest.mark.integration
def test_dataarray_snapshot_s3(xarray_snapshot, sample_dataarray):
    assert xarray_snapshot == sample_dataarray

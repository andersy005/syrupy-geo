import numpy as np
import pytest
import xarray as xr

from syrupy_geo import XarraySnapshotExtension

# ---------------------------------------------------------------------------
# serialize()
# ---------------------------------------------------------------------------


def test_serialize_dataarray_returns_named_dataset(sample_dataarray):
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    result = ext.serialize(sample_dataarray)
    assert isinstance(result, xr.Dataset)
    assert 'test_array' in result


def test_serialize_unnamed_dataarray_uses_data_key():
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    result = ext.serialize(xr.DataArray([1, 2, 3]))
    assert isinstance(result, xr.Dataset)
    assert 'data' in result


def test_serialize_dataset_passthrough(sample_dataset):
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    result = ext.serialize(sample_dataset)
    assert isinstance(result, xr.Dataset)
    assert result is sample_dataset


def test_serialize_datatree_passthrough(sample_datatree):
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    result = ext.serialize(sample_datatree)
    assert isinstance(result, xr.DataTree)
    assert result is sample_datatree


def test_serialize_wrong_type_raises():
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    with pytest.raises(TypeError, match='Expected xr.DataArray, xr.Dataset, or xr.DataTree'):
        ext.serialize('not_an_array')


# ---------------------------------------------------------------------------
# matches()
# ---------------------------------------------------------------------------


def test_matches_returns_false_when_snapshot_none(sample_dataset):
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    assert ext.matches(serialized_data=sample_dataset, snapshot_data=None) is False


def test_matches_returns_false_on_type_mismatch(sample_dataset, sample_datatree):
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    assert ext.matches(serialized_data=sample_datatree, snapshot_data=sample_dataset) is False


def test_matches_returns_true_for_equal_datasets(sample_dataset):
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    assert ext.matches(serialized_data=sample_dataset, snapshot_data=sample_dataset) is True


def test_matches_returns_true_for_equal_datatrees(sample_datatree):
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    assert ext.matches(serialized_data=sample_datatree, snapshot_data=sample_datatree) is True


def test_matches_returns_false_for_unequal_datasets():
    ext = XarraySnapshotExtension.__new__(XarraySnapshotExtension)
    ds1 = xr.Dataset({'a': ('x', [1.0, 2.0])})
    ds2 = xr.Dataset({'a': ('x', [1.0, 9.0])})
    assert ext.matches(serialized_data=ds1, snapshot_data=ds2) is False


# ---------------------------------------------------------------------------
# Snapshot round-trip tests (require --snapshot-update on first run)
# ---------------------------------------------------------------------------


def test_dataarray_snapshot(xarray_snapshot, sample_dataarray):
    assert xarray_snapshot == sample_dataarray


def test_dataset_snapshot(xarray_snapshot, sample_dataset):
    assert xarray_snapshot == sample_dataset


def test_datatree_snapshot(xarray_snapshot, sample_datatree):
    assert xarray_snapshot == sample_datatree


def test_datatree_snapshot_nested(xarray_snapshot):
    rng = np.random.default_rng(42)
    dt = xr.DataTree.from_dict(
        {
            'level1/level2': xr.Dataset({'deep': ('z', rng.random(5))}),
        }
    )
    assert xarray_snapshot == dt


# ---------------------------------------------------------------------------
# Integration tests (require SNAPSHOT_STORAGE_PATH=s3://... and AWS creds)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_dataarray_snapshot_s3(xarray_snapshot, sample_dataarray):
    assert xarray_snapshot == sample_dataarray


@pytest.mark.integration
def test_datatree_snapshot_s3(xarray_snapshot, sample_datatree):
    assert xarray_snapshot == sample_datatree

import pytest


def test_geodataframe_snapshot(geodataframe_snapshot, sample_geodataframe):
    # snapshot on left to avoid GeoDataFrame's element-wise == intercepting the comparison
    assert geodataframe_snapshot == sample_geodataframe


def test_geodataframe_snapshot_wrong_type_raises():
    from syrupy_geo import GeoDataFrameSnapshotExtension

    ext = GeoDataFrameSnapshotExtension.__new__(GeoDataFrameSnapshotExtension)
    with pytest.raises(TypeError, match='Expected gpd.GeoDataFrame'):
        ext.serialize('not_a_geodataframe')


@pytest.mark.integration
def test_geodataframe_snapshot_s3(geodataframe_snapshot, sample_geodataframe):
    assert geodataframe_snapshot == sample_geodataframe

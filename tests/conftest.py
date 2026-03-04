import pytest


@pytest.fixture
def sample_dataarray():
    import numpy as np
    import xarray as xr

    rng = np.random.default_rng(42)
    return xr.DataArray(
        rng.random((3, 4)),
        dims=['x', 'y'],
        name='test_array',
    )


@pytest.fixture
def sample_dataset(sample_dataarray):
    return sample_dataarray.to_dataset()


@pytest.fixture
def sample_geodataframe():
    import geopandas as gpd
    from shapely.geometry import Point

    return gpd.GeoDataFrame(
        {'value': [1, 2, 3]},
        geometry=[Point(0, 0), Point(1, 1), Point(2, 2)],
        crs='EPSG:4326',
    )

import importlib.metadata

from .geodataframe import GeoDataFrameSnapshotExtension
from .xarray import XarraySnapshotExtension

__version__ = importlib.metadata.version('syrupy-geo')
__all__ = ['XarraySnapshotExtension', 'GeoDataFrameSnapshotExtension']

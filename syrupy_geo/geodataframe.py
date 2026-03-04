from __future__ import annotations

import typing

import upath
from syrupy.data import SnapshotCollection

from ._base import BaseGeoSnapshotExtension

if typing.TYPE_CHECKING:
    from syrupy.types import SerializableData


class GeoDataFrameSnapshotExtension(BaseGeoSnapshotExtension):
    file_extension = 'parquet'

    def serialize(self, data: SerializableData, **kwargs: typing.Any) -> typing.Any:
        try:
            import geopandas as gpd
        except ImportError as e:
            raise ImportError(
                'geopandas is required for GeoDataFrameSnapshotExtension. '
                'Install it with: pip install syrupy-geo[geo]'
            ) from e
        if isinstance(data, gpd.GeoDataFrame):
            return data
        raise TypeError(f'Expected gpd.GeoDataFrame, got {type(data)}')

    def matches(
        self,
        *,
        serialized_data: typing.Any,
        snapshot_data: typing.Any,
    ) -> bool:
        import pandas as pd

        if snapshot_data is None:
            return False
        try:
            pd.testing.assert_frame_equal(
                serialized_data.drop(columns='geometry'),
                snapshot_data.drop(columns='geometry'),
                check_dtype=True,
                check_index_type=True,
                check_column_type=True,
            )
            if not serialized_data.geometry.geom_equals(snapshot_data.geometry).all():
                return False
            if serialized_data.crs != snapshot_data.crs:
                return False
            return True
        except (AssertionError, AttributeError, ValueError):
            return False

    def read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ) -> typing.Any:
        try:
            import geopandas as gpd
        except ImportError as e:
            raise ImportError(
                'geopandas and pyarrow are required for GeoDataFrameSnapshotExtension. '
                'Install them with: pip install syrupy-geo[geo]'
            ) from e
        try:
            return gpd.read_parquet(snapshot_location)
        except (OSError, FileNotFoundError):
            return None

    @classmethod
    def write_snapshot_collection(cls, *, snapshot_collection: SnapshotCollection) -> None:
        try:
            import geopandas as gpd
        except ImportError as e:
            raise ImportError(
                'geopandas and pyarrow are required for GeoDataFrameSnapshotExtension. '
                'Install them with: pip install syrupy-geo[geo]'
            ) from e

        filepath = snapshot_collection.location
        data = next(iter(snapshot_collection)).data
        snapshot_path = upath.UPath(str(filepath))

        if snapshot_path.exists():
            if str(snapshot_path).startswith('s3://'):
                fs = snapshot_path.fs
                if fs.exists(str(snapshot_path)):
                    fs.rm(str(snapshot_path), recursive=False)
            else:
                snapshot_path.unlink()

        if isinstance(data, gpd.GeoDataFrame):
            data.to_parquet(
                str(snapshot_path),
                index=False,
                compression='zstd',
                geometry_encoding='WKB',
                write_covering_bbox=True,
                schema_version='1.1.0',
            )

    def diff_lines(
        self, serialized_data: typing.Any, snapshot_data: typing.Any
    ) -> typing.Iterator[str]:
        import pandas as pd

        try:
            pd.testing.assert_frame_equal(
                serialized_data.drop(columns='geometry'),
                snapshot_data.drop(columns='geometry'),
            )
            if not serialized_data.geometry.geom_equals(snapshot_data.geometry).all():
                raise AssertionError('Geometry columns differ')
            if serialized_data.crs != snapshot_data.crs:
                raise AssertionError(f'CRS mismatch: {serialized_data.crs} != {snapshot_data.crs}')
            return iter([])
        except (AssertionError, AttributeError, ValueError) as e:
            diff_output = [
                'Snapshot comparison failed',
                '-------------------------------',
                'Snapshot:',
                *str(snapshot_data).split('\n'),
                '-------------------------------',
                'Serialized:',
                *str(serialized_data).split('\n'),
                '-------------------------------',
                'Error:',
                *str(e).split('\n'),
            ]
            return iter(diff_output)

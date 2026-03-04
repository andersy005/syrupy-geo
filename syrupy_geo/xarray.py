from __future__ import annotations

import shutil
import typing

import upath
from syrupy.data import SnapshotCollection

from ._base import BaseGeoSnapshotExtension

if typing.TYPE_CHECKING:
    from syrupy.types import SerializableData


class XarraySnapshotExtension(BaseGeoSnapshotExtension):
    file_extension = 'zarr'

    def serialize(self, data: SerializableData, **kwargs: typing.Any) -> typing.Any:
        try:
            import xarray as xr
        except ImportError as e:
            raise ImportError(
                'xarray is required for XarraySnapshotExtension. '
                'Install it with: pip install syrupy-geo[xarray]'
            ) from e
        if isinstance(data, xr.DataArray):
            return data.to_dataset(name='data')
        elif isinstance(data, xr.Dataset):
            return data
        raise TypeError(f'Expected xr.DataArray or xr.Dataset, got {type(data)}')

    def matches(
        self,
        *,
        serialized_data: typing.Any,
        snapshot_data: typing.Any,
    ) -> bool:
        import xarray as xr

        if snapshot_data is None:
            return False
        try:
            xr.testing.assert_allclose(
                serialized_data.compute(), snapshot_data.compute(), rtol=1e-6, atol=1e-8
            )
            return True
        except (AssertionError, TypeError):
            try:
                xr.testing.assert_equal(serialized_data.compute(), snapshot_data.compute())
                return True
            except AssertionError:
                return False

    def read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ) -> typing.Any:
        try:
            import xarray as xr
        except ImportError as e:
            raise ImportError(
                'xarray and zarr are required for XarraySnapshotExtension. '
                'Install them with: pip install syrupy-geo[xarray]'
            ) from e
        try:
            return xr.open_dataset(snapshot_location, engine='zarr')
        except (OSError, FileNotFoundError, IsADirectoryError):
            return None

    @classmethod
    def write_snapshot_collection(cls, *, snapshot_collection: SnapshotCollection) -> None:
        try:
            import xarray as xr
        except ImportError as e:
            raise ImportError(
                'xarray and zarr are required for XarraySnapshotExtension. '
                'Install them with: pip install syrupy-geo[xarray]'
            ) from e

        filepath = snapshot_collection.location
        data = next(iter(snapshot_collection)).data
        snapshot_path = upath.UPath(filepath)

        if snapshot_path.exists():
            if str(snapshot_path).startswith('s3://'):
                fs = snapshot_path.fs
                if fs.exists(str(snapshot_path)):
                    fs.rm(str(snapshot_path), recursive=True)
            else:
                shutil.rmtree(snapshot_path)

        if isinstance(data, xr.Dataset):
            data.to_zarr(str(snapshot_path), mode='w')

    def diff_lines(
        self, serialized_data: typing.Any, snapshot_data: typing.Any
    ) -> typing.Iterator[str]:
        import xarray as xr

        try:
            xr.testing.assert_allclose(
                serialized_data.compute(), snapshot_data.compute(), rtol=1e-6, atol=1e-8
            )
            return iter([])
        except (AssertionError, TypeError) as e:
            diff_output = [
                'Snapshot comparison failed (rtol=1e-6, atol=1e-8)',
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

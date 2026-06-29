from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import urlparse

import upath
from syrupy.data import SnapshotCollection

from ._base import BaseGeoSnapshotExtension

if TYPE_CHECKING:
    from syrupy.location import PyTestLocation
    from syrupy.types import SerializableData, SnapshotIndex


class XarraySnapshotExtension(BaseGeoSnapshotExtension):
    file_extension = 'icechunk'

    _repo: ClassVar[Any] = None
    _session: ClassVar[Any] = None
    _has_pending_writes: ClassVar[bool] = False

    @classmethod
    def get_location(cls, *, test_location: PyTestLocation, index: SnapshotIndex = 0) -> str:
        stem = upath.UPath(test_location.filepath).stem
        name = cls.get_snapshot_name(test_location=test_location, index=index)
        return f'{stem}/{name}'

    @classmethod
    def dirname(cls, *, test_location: PyTestLocation) -> str:
        return upath.UPath(test_location.filepath).stem

    def serialize(self, data: SerializableData, **kwargs: typing.Any) -> typing.Any:
        try:
            import xarray as xr
        except ImportError as e:
            raise ImportError(
                'xarray is required for XarraySnapshotExtension. '
                'Install it with: pip install syrupy-geo[icechunk]'
            ) from e
        if isinstance(data, xr.DataArray):
            return data.to_dataset(name=data.name or 'data')
        if isinstance(data, (xr.Dataset, xr.DataTree)):
            return data
        raise TypeError(f'Expected xr.DataArray, xr.Dataset, or xr.DataTree, got {type(data)}')

    def matches(
        self,
        *,
        serialized_data: typing.Any,
        snapshot_data: typing.Any,
    ) -> bool:
        import xarray as xr

        if snapshot_data is None:
            return False
        if type(serialized_data) is not type(snapshot_data):
            return False
        try:
            xr.testing.assert_allclose(serialized_data, snapshot_data, rtol=1e-6, atol=1e-8)
            return True
        except (AssertionError, TypeError):
            try:
                xr.testing.assert_equal(serialized_data, snapshot_data)
                return True
            except AssertionError:
                return False

    def read_snapshot_data_from_location(
        self, *, snapshot_location: str, snapshot_name: str, session_id: str
    ) -> typing.Any:
        try:
            import xarray as xr
            import zarr
        except ImportError as e:
            raise ImportError(
                'xarray and zarr are required for XarraySnapshotExtension. '
                'Install them with: pip install syrupy-geo[icechunk]'
            ) from e
        try:
            store = self.__class__._get_readonly_store()
            z = zarr.open_group(store=store, path=snapshot_location)
            type_tag = z.attrs.get('_syrupy_geo_type', 'dataset')
            if type_tag == 'dataset':
                return xr.open_dataset(store, engine='zarr', group=snapshot_location)
            return xr.open_datatree(store, engine='zarr', group=snapshot_location)
        except Exception:
            return None

    @classmethod
    def write_snapshot_collection(cls, *, snapshot_collection: SnapshotCollection) -> None:
        try:
            import xarray as xr
            import zarr
        except ImportError as e:
            raise ImportError(
                'xarray and zarr are required for XarraySnapshotExtension. '
                'Install them with: pip install syrupy-geo[icechunk]'
            ) from e

        data = next(iter(snapshot_collection)).data
        group_path = snapshot_collection.location
        store = cls._get_writable_session().store

        if isinstance(data, xr.Dataset):
            data.to_zarr(store, group=group_path, mode='w')
            zarr.open_group(store=store, path=group_path, mode='a').attrs['_syrupy_geo_type'] = (
                'dataset'
            )
        elif isinstance(data, xr.DataTree):
            data.to_zarr(store, group=group_path, mode='w')
            zarr.open_group(store=store, path=group_path, mode='a').attrs['_syrupy_geo_type'] = (
                'datatree'
            )

        cls._has_pending_writes = True

    def diff_lines(
        self, serialized_data: typing.Any, snapshot_data: typing.Any
    ) -> typing.Iterator[str]:
        import xarray as xr

        try:
            xr.testing.assert_allclose(serialized_data, snapshot_data, rtol=1e-6, atol=1e-8)
            return iter([])
        except (AssertionError, TypeError) as e:
            return iter(
                [
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
            )

    @classmethod
    def _get_icechunk_repo_path(cls) -> str:
        base = cls._get_base_snapshot_path()
        root = base if base else upath.UPath('__snapshots__')
        return str(root / 'icechunk')

    @classmethod
    def _get_repo(cls) -> typing.Any:
        if cls._repo is None:
            try:
                import icechunk
            except ImportError as e:
                raise ImportError(
                    'icechunk is required for XarraySnapshotExtension. '
                    'Install it with: pip install syrupy-geo[icechunk]'
                ) from e
            path = cls._get_icechunk_repo_path()
            if path.startswith('s3://'):
                parsed = urlparse(path)
                storage = icechunk.s3_storage(
                    bucket=parsed.netloc,
                    prefix=parsed.path.lstrip('/'),
                )
            else:
                storage = icechunk.local_filesystem_storage(path)
            cls._repo = icechunk.Repository.open_or_create(storage=storage)
        return cls._repo

    @classmethod
    def _get_writable_session(cls) -> typing.Any:
        if cls._session is None:
            cls._session = cls._get_repo().writable_session('main')
        return cls._session

    @classmethod
    def _get_readonly_store(cls) -> typing.Any:
        return cls._get_repo().readonly_session('main').store

    @classmethod
    def commit_session(cls, message: str) -> None:
        if cls._session is not None and cls._has_pending_writes:
            cls._session.commit(message)
        cls._session = None
        cls._has_pending_writes = False

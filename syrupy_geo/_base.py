from __future__ import annotations

import os
from typing import TYPE_CHECKING

import upath
from syrupy.extensions.single_file import SingleFileSnapshotExtension

if TYPE_CHECKING:
    from syrupy.location import PyTestLocation
    from syrupy.types import SnapshotIndex


class BaseGeoSnapshotExtension(SingleFileSnapshotExtension):
    @classmethod
    def _get_base_snapshot_path(cls) -> upath.UPath | None:
        storage_path = os.environ.get('SNAPSHOT_STORAGE_PATH')
        if storage_path:
            return upath.UPath(storage_path)
        return None

    @classmethod
    def dirname(cls, *, test_location: PyTestLocation) -> str:
        base_path = cls._get_base_snapshot_path()
        test_file = upath.UPath(test_location.filepath).stem
        if base_path:
            return str(upath.UPath(base_path) / test_file)
        return str(upath.UPath(test_location.filepath).parent / '__snapshots__' / test_file)

    @classmethod
    def get_snapshot_name(cls, *, test_location: PyTestLocation, index: SnapshotIndex = 0) -> str:
        test_name = test_location.testname
        sanitized = test_name.replace('[', '_').replace(']', '').replace('/', '_')
        if index == 0:
            return sanitized
        return f'{sanitized}.{index}'

    @classmethod
    def get_location(cls, *, test_location: PyTestLocation, index: SnapshotIndex = 0) -> str:
        dirname = cls.dirname(test_location=test_location)
        basename = cls.get_snapshot_name(test_location=test_location, index=index)
        filename = f'{basename}.{cls.file_extension}'
        return str(upath.UPath(dirname) / filename)

    @classmethod
    def _warn_on_snapshot_name(cls, *, snapshot_name: str, test_location: PyTestLocation) -> None:
        pass

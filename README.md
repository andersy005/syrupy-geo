# syrupy-geo

[![CI](https://github.com/andersy005/syrupy-geo/actions/workflows/ci.yaml/badge.svg)](https://github.com/andersy005/syrupy-geo/actions/workflows/ci.yaml)
[![PyPI](https://github.com/andersy005/syrupy-geo/actions/workflows/pypi.yaml/badge.svg)](https://github.com/andersy005/syrupy-geo/actions/workflows/pypi.yaml)
[![PyPI version](https://img.shields.io/pypi/v/syrupy-geo.svg)](https://pypi.org/project/syrupy-geo)
[![codecov](https://codecov.io/gh/andersy005/syrupy-geo/branch/main/graph/badge.svg)](https://codecov.io/gh/andersy005/syrupy-geo)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/andersy005/syrupy-geo/main.svg)](https://results.pre-commit.ci/latest/github/andersy005/syrupy-geo/main)

A [syrupy](https://github.com/syrupy-project/syrupy) extension for geospatial and array data formats. Snapshot test xarray `DataArray`, `Dataset`, and `DataTree` objects (stored in a versioned [icechunk](https://icechunk.io) repository) and GeoPandas `GeoDataFrame` objects (stored as GeoParquet). Snapshots can live locally or on S3.

# Store snapshots on S3

By default syrupy-geo stores snapshots in a `__snapshots__/` folder next to your test file. Setting the `SNAPSHOT_STORAGE_PATH` environment variable redirects all reads and writes to any fsspec-compatible remote location, including S3.

## Prerequisites

- An S3 bucket your CI runner can write to.
- The `s3fs` package installed (`pip install s3fs`).

## Set the environment variable

```bash
export SNAPSHOT_STORAGE_PATH="s3://my-bucket/snapshots"
```

You can set this in your shell, in a CI environment variable, or in a `.env` file loaded before pytest runs.

## Create snapshots

```bash
pytest --snapshot-update
```

Snapshots are written directly to S3. For xarray they are stored as Zarr stores; for GeoDataFrames as GeoParquet files.

## Run tests against remote snapshots

```bash
pytest
```

Each test reads the snapshot from S3 and compares it to the freshly computed value.

## Use a sub-prefix per test suite

You can namespace snapshots by branch or environment:

```bash
export SNAPSHOT_STORAGE_PATH="s3://my-bucket/snapshots/main"
pytest
```

## Authentication

syrupy-geo uses `upath.UPath` which delegates to `s3fs`. The standard approaches all work:

- AWS environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`).
- An IAM role attached to the runner.
- A named profile in `~/.aws/credentials`.

## Fallback to local storage

Unset `SNAPSHOT_STORAGE_PATH` to revert to local `__snapshots__/` directories:

```bash
unset SNAPSHOT_STORAGE_PATH
pytest
```

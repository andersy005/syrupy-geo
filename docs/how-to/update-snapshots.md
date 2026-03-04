# Update snapshots

Run this workflow whenever the expected output of a function changes intentionally, such as after a bug fix, a data pipeline change, or a dependency upgrade that alters numerical output.

## When to update

Update snapshots when:

- You have intentionally changed the logic that produces the data.
- A dependency upgrade changed numerical precision in an expected way.
- You are adding new test cases that do not yet have stored snapshots.

Do **not** update snapshots to silence a failing test without first understanding why it failed.

## Update all snapshots

```bash
pytest --snapshot-update
```

Every snapshot that does not match its current output is overwritten. New snapshots are created.

## Update snapshots for a single test file

```bash
pytest --snapshot-update tests/test_climate.py
```

## Update a single test

```bash
pytest --snapshot-update tests/test_climate.py::test_temperature_array
```

## Review the diff before updating

Run the tests without `--snapshot-update` first to see the diff output:

```bash
pytest tests/test_climate.py
```

syrupy-geo prints what the snapshot contains and what the test produced, so you can verify the difference is expected before committing the update.

## Commit updated snapshots

Snapshot files are part of your codebase. After updating, commit them together with the code change that caused them to differ:

```bash
git add tests/__snapshots__/
git commit -m "update snapshots after temperature pipeline change"
```

## Never auto-update in CI

Do not pass `--snapshot-update` in your CI pipeline. If a snapshot does not match in CI, the test should fail and a human should decide whether to update.

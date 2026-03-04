# Why assertion order matters

## The rule

Always write snapshot assertions with the snapshot fixture on the left:

```python
assert xarray_snapshot == my_dataarray   # correct
assert geodataframe_snapshot == my_gdf   # correct
```

Never write them the other way around:

```python
assert my_dataarray == xarray_snapshot   # wrong, silent false positive
assert my_gdf == geodataframe_snapshot   # wrong, silent false positive
```

## Why the wrong order is dangerous

Python evaluates `a == b` by calling `a.__eq__(b)`. If `a` does not know how to compare itself to `b`, it returns `NotImplemented` and Python then tries `b.__eq__(a)`. This fallback is how syrupy normally routes the comparison through its own logic.

Both xarray and pandas override `__eq__` aggressively. When an `xr.DataArray` or `gpd.GeoDataFrame` is on the left side of `==`, these libraries intercept the call and return an element-wise boolean array instead of delegating to syrupy. The test then evaluates the truthiness of that array, which is either always true (broadcasting), raises an ambiguous truth value error, or produces a confusing result, none of which are the snapshot comparison you intended.

The snapshot fixture object does not override `__eq__`, so placing it on the left guarantees that Python calls `snapshot.__eq__(data)`, which routes through syrupy's comparison machinery.

## How to catch the mistake

If you accidentally write `assert data == snapshot` and the test passes when it should not, you will not get an error during the test run. The best safeguard is a linting rule or a code review convention that rejects that assertion order.

A simple grep catches it in CI:

```bash
grep -rn "assert.*==.*snapshot" tests/ | grep -v "assert snapshot"
```

Any match is a candidate to review.

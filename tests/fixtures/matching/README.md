# Matching (OR selectors)

Demonstrates how `match` uses logical OR across selectors.

The base has `name: "example"` and `version: 1`, so it matches the first
selector. It would also match if `name` were `"example2"` with `version: 1`.

The patch runs because **any** selector in the list matches — not all of them.

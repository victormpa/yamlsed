# Delete (exact element match)

Demonstrates removing a specific array element with `dependencies-:`. The
element must match **exactly** — all specified keys equal, with no extra keys
on the element.

The `example2` entry has only `name` and `version`, so it matches. The
`example` entry has additional keys (`description`), so it is kept even though
its `name` differs.

Compare with [delete-partial-element](../delete-partial-element/).

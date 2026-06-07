# Delete (partial element match)

Demonstrates the `-?` suffix. Array elements are removed when the listed keys
are present and equal, even if the element carries additional keys.

The `example2` entry has extra `description` keys but still matches. Compare
with [delete-exact-element](../delete-exact-element/), where extra keys would
prevent a match.

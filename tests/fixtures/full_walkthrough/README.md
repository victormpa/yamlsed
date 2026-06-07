# Full walkthrough

Combines every patch operation in a single example. See the focused examples
in sibling folders for isolated demonstrations.

## What happens

Operations are applied in patch order:

1. **Replace scalars** — `name`, `version`, `approved`, `score`
2. **Replace array** — `tags` becomes `["yaml"]`
3. **Append** — `tags+` adds `"added"` → `["yaml", "added"]`
4. **Delete** — `author`, `license`, and `healthcheck` removed
5. **Delete array** — `dependencies-: *` removes the entire array

The later `dependencies-` and `dependencies-?` entries are no-ops because the
array was already removed in step 5. They are included to show the syntax in
context.

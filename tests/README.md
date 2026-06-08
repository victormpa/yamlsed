# Examples

Each folder demonstrates one Yamlsed concept with four files:

| File | Purpose |
| ---- | ------- |
| `base.yaml` | The template to patch |
| `{name}.patch.yaml` | `match` + `patch` document (named after the example) |
| `result.yaml` | Expected output after applying the patch |
| `README.md` | What the example shows |

The original combined reference is still at [github.com/victormpa/yamlsed/blob/main/tests/fixtures/base.yaml](https://github.com/victormpa/yamlsed/blob/main/tests/fixtures/base.yaml).

## Catalog

| Example | Operation | Docs section |
| ------- | --------- | ------------ |
| [matching](../tests/fixtures/matching/) | OR selectors | [Matching](matching.md) |
| [replace_scalar](../tests/fixtures/replace_scalar/) | Replace scalar | [Scalars](patch-operations/scalars.md) |
| [replace_array](../tests/fixtures/replace_array/) | Replace array | [Array](patch-operations/collections.md#array) |
| [replace_object](../tests/fixtures/replace_object/) | Replace object | [Object](patch-operations/collections.md#object) |
| [append_array](../tests/fixtures/append_array/) | Append to array (`+`) | [Array](patch-operations/collections.md#array) |
| [append_missing_array](../tests/fixtures/append_missing_array/) | Append to missing array (`+`) | [Array](patch-operations/collections.md#array) |
| [delete_value_guarded](../tests/fixtures/delete_value_guarded/) | Value-guarded delete | [Scalars](patch-operations/scalars.md) |
| [delete_null_guarded](../tests/fixtures/delete_null_guarded/) | Null-guarded delete | [Object](patch-operations/collections.md#object) |
| [delete_unconditional](../tests/fixtures/delete_unconditional/) | Unconditional delete (`*`) | [Scalars](patch-operations/scalars.md) |
| [delete_array](../tests/fixtures/delete_array/) | Delete entire array | [Object](patch-operations/collections.md#object) |
| [delete_exact_element](../tests/fixtures/delete_exact_element/) | Exact element match | [Array](patch-operations/collections.md#array) |
| [delete_partial_element](../tests/fixtures/delete_partial_element/) | Partial element match (`-?`) | [Array](patch-operations/collections.md#array) |
| [full_walkthrough](../tests/fixtures/full_walkthrough/) | All operations combined | [Patching](patch-operations/index.md) |

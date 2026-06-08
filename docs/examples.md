# Examples

Each fixture folder demonstrates one Yamlsed concept with four files:

| File | Purpose |
| ---- | ------- |
| `base.yaml` | The template to patch |
| `{name}.patch.yaml` | `match` + `patch` document (named after the example) |
| `result.yaml` | Expected output after applying the patch |
| `README.md` | What the example shows |

The original combined reference is still at
[tests/fixtures/base.yaml](https://github.com/victormpa/yamlsed/blob/main/tests/fixtures/base.yaml).

For the complete walkthrough, see
[tests/fixtures/full_walkthrough/](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/full_walkthrough/).

## Catalog

| Example | Operation | Docs section |
| ------- | --------- | -------------- |
| [matching](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/matching/) | OR selectors | [Matching](matching.md) |
| [replace_scalar](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/replace_scalar/) | Replace scalar | [Scalars](patch-operations/scalars.md) |
| [replace_array](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/replace_array/) | Replace array | [Arrays and objects](patch-operations/collections.md#array) |
| [append_array](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/append_array/) | Append to array (`+`) | [Arrays and objects](patch-operations/collections.md#array) |
| [append_missing_array](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/append_missing_array/) | Append to missing array (`+`) | [Arrays and objects](patch-operations/collections.md#array) |
| [delete_value_guarded](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/delete_value_guarded/) | Value-guarded delete | [Scalars](patch-operations/scalars.md) |
| [delete_null_guarded](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/delete_null_guarded/) | Null-guarded delete | [Arrays and objects](patch-operations/collections.md#object) |
| [delete_unconditional](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/delete_unconditional/) | Unconditional delete (`*`) | [Scalars](patch-operations/scalars.md) |
| [delete_array](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/delete_array/) | Delete entire array | [Arrays and objects](patch-operations/collections.md#array) |
| [delete_exact_element](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/delete_exact_element/) | Exact element match | [Arrays and objects](patch-operations/collections.md#array) |
| [delete_partial_element](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/delete_partial_element/) | Partial element match (`-?`) | [Arrays and objects](patch-operations/collections.md#array) |
| [full_walkthrough](https://github.com/victormpa/yamlsed/tree/main/tests/fixtures/full_walkthrough/) | All operations combined | [Examples](examples.md) |

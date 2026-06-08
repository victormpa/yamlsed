# Examples

Each folder demonstrates one Yamly concept with four files:

| File | Purpose |
| ---- | ------- |
| `base.yaml` | The template to patch |
| `{name}.patch.yaml` | `match` + `patch` document (named after the example) |
| `result.yaml` | Expected output after applying the patch |
| `README.md` | What the example shows |

The original combined reference is still at [fixtures/base.yaml](fixtures/base.yaml).

## Catalog

| Example | Operation | README section |
| ------- | --------- | -------------- |
| [matching](fixtures/matching/) | OR selectors | [Matching](../README.md#matching) |
| [replace_scalar](fixtures/replace_scalar/) | Replace scalar | [Replace (no suffix)](../README.md#replace-no-suffix) |
| [replace_array](fixtures/replace_array/) | Replace array | [Replace (no suffix)](../README.md#replace-no-suffix) |
| [append_array](fixtures/append_array/) | Append to array (`+`) | [Append to array](../README.md#append-to-array--key) |
| [append_missing_array](fixtures/append_missing_array/) | Append to missing array (`+`) | [Append to array](../README.md#append-to-array--key) |
| [delete_value_guarded](fixtures/delete_value_guarded/) | Value-guarded delete | [Delete](../README.md#delete--key-) |
| [delete_null_guarded](fixtures/delete_null_guarded/) | Null-guarded delete | [Delete](../README.md#delete--key-) |
| [delete_unconditional](fixtures/delete_unconditional/) | Unconditional delete (`*`) | [Delete](../README.md#delete--key-) |
| [delete_array](fixtures/delete_array/) | Delete entire array | [Delete](../README.md#delete--key-) |
| [delete_exact_element](fixtures/delete_exact_element/) | Exact element match | [Delete](../README.md#delete--key-) |
| [delete_partial_element](fixtures/delete_partial_element/) | Partial element match (`-?`) | [Partial element match](../README.md#partial-element-match--key-) |
| [full_walkthrough](fixtures/full_walkthrough/) | All operations combined | [Full example](../README.md#full-example) |

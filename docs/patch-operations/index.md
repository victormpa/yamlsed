# Patching

The `patch` block is keyed by the field you want to change. The **key suffix**
selects the operation. Which operations are available depends on the **type** of
the field being patched.

See the subpages for operation details by type:

- [Scalars](scalars.md) — string, int, float, bool
- [Arrays and objects](collections.md) — list and map operations
- [Functions](functions.md) — `{{function(...)}}` expressions

## Suffix reference

| Suffix | Operation        | Value                                                            |
| ------ | ---------------- | ---------------------------------------------------------------- |
| *none* | Replace          | New scalar, or new array (replaces the whole array)              |
| `+`    | Append           | list = append elements; dict = merge keys into object            |
| `+?`   | Append (guarded) | dict = merge keys only if the field exists; otherwise skip       |
| `-`    | Delete           | `*` = always; `null` = if null; a scalar = if equal; keys = exact array-element match |
| `-?`   | Delete (partial) | Keys to match an array element partially                         |

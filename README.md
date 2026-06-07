# YAMLY

**YAML template matching & processing.**

Yamly keeps YAML templates up to date. Point it at a **base** template (the kind
of file that tends to sit around in a repo) and a **patch**, and it applies the
patch's changes wherever the base matches — declaratively and
version-controllably, instead of hand-editing the file. You describe a **match**
(which documents to act on) and a set of **patch** operations, and Yamly emits
the updated result.

Think of it as a structured, schema-aware alternative to text diffs or
`sed`-style find-and-replace: operations understand scalars, arrays, and maps,
so changes stay valid YAML.

---

## Concepts

A Yamly file is two YAML documents separated by `---`:

| Document    | Purpose                                                            |
| ----------- | ----------------------------------------------------------------- |
| **Base**    | A normal YAML template — the file you want to keep updated.        |
| **Patch**   | A document containing a `match` block and a `patch` block.         |

The patch is applied to the base whenever the base satisfies the `match`
selector.

### Base

The base is just ordinary YAML:

```yaml
name: "example"
version: 1
description: "This is an example YAML file"
author: "John Doe"
license: "MIT"
approved: false
score: 9.8
tags:
  - "yaml"
  - "templates"
  - "parser"
labels:
  operating_system: "linux"
  architecture: "x86_64"
dependencies:
  - name: "example"
    version: "1.0.0"
```

### Patch

A patch document has two blocks:

```yaml
match:    # which base documents this patch applies to
  - name: "example"
    version: 1

patch:    # mutations to apply
  approved: true
```

---

## Matching

`match` is a list of selectors. The base is targeted if it matches **any**
selector in the list (logical OR). Each selector is a set of key/value pairs
that must all be present and equal on the base.

```yaml
match:
  - name: "example"
    version: 1
  - name: "example2"
    version: 1
```

> Matches a base named `example` **or** `example2`, in either case with
> `version: 1`.

---

## Patch operations

The `patch` block is keyed by the field you want to change. The **key suffix**
selects the operation.

### Replace (no suffix)

For a scalar — string, integer, float, or boolean — the entire value is
replaced.

```yaml
patch:
  name: "foo"       # example -> foo
  version: 2        # 1 -> 2
  approved: true    # false -> true
  score: 10.0       # 9.8 -> 10.0
```

When the value is an **array**, the whole array is replaced:

```yaml
patch:
  tags:
    - "yaml"        # replaces every existing tag
```

### Append to array — `key+`

Suffix a key with `+` to add the new value(s) to an array instead of replacing
it. If the field does not exist yet, Yamly creates it as an empty array first.

```yaml
patch:
  tags+:
    - "added"       # tags now also contains "added"
```

```yaml
patch:
  children+:
    - name: "baz"   # creates `children` and appends the element
```

### Delete — `key-`

Suffix a key with `-` to remove it. The value tells Yamly *when* to remove it.

**Value-guarded delete.** If a value is given, the key is removed only when the
base's value matches:

```yaml
patch:
  author-: "John Doe"   # deletes `author` only if it equals "John Doe"
```

**Null-guarded delete.** Use `null` to delete only when the field is null:

```yaml
patch:
  healthcheck-: null    # deletes `healthcheck` only if it is null
```

**Unconditional delete.** Use `*` to delete regardless of the current value:

```yaml
patch:
  license-: *           # always deletes `license`
```

**Array delete.** `*` also removes an array field in its entirety:

```yaml
patch:
  dependencies-: *      # removes the whole dependencies array
```

**Exact element match.** Provide keys, and an array element is removed only when
it matches *exactly* (all specified keys equal, no extras beyond what you list):

```yaml
patch:
  dependencies-:
    - name: "example2"
      version: 1
```

### Partial element match — `key-?`

Suffix with `-?` to remove array elements that *partially* match — the listed
keys must be present and equal, but the element may carry additional keys.

```yaml
patch:
  dependencies-?:
    - name: "example2"
      version: 1        # removes any dependency where name+version match
```

### Suffix reference

| Suffix | Operation        | Value                                                            |
| ------ | ---------------- | ---------------------------------------------------------------- |
| *none* | Replace          | New scalar, or new array (replaces the whole array)              |
| `+`    | Append to array  | Element(s) to add                                                |
| `-`    | Delete           | `*` = always; `null` = if null; a scalar = if equal; keys = exact array-element match |
| `-?`   | Delete (partial) | Keys to match an array element partially                         |

---

## Full example

See [tests/README.md](tests/README.md) for focused examples, or
[tests/fixtures/full_walkthrough/](tests/fixtures/full_walkthrough/) for the complete
walkthrough. The original combined file is still at
[tests/fixtures/base.yaml](tests/fixtures/base.yaml).

---

## Status

Early / work in progress. Syntax described here reflects the current design and
may change.

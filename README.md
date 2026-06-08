# YAMLSED

**YAML template matching & processing.**

Yamlsed keeps YAML templates up to date. Point it at a **base** template (the kind
of file that tends to sit around in a repo) and a **patch**, and it applies the
patch's changes wherever the base matches — declaratively and
version-controllably, instead of hand-editing the file. You describe a **match**
(which documents to act on) and a set of **patch** operations, and Yamlsed emits
the updated result.

Think of it as a structured, schema-aware alternative to text diffs or
`sed`-style find-and-replace: operations understand scalars, arrays, and maps,
so changes stay valid YAML.

---

## Concepts

There are two types of documents:

| Document    | Purpose                                                            |
| ----------- | ------------------------------------------------------------------ |
| **Base**    | A normal YAML template — the file you want to keep updated.        |
| **Patch**   | A document containing a `match` block and a `patch` block.         |

The patch is applied to the base whenever the base satisfies the `match` selector.

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

A single `.patch.yaml` file may contain **multiple** patch documents separated
by `---`. Each document has its own `match` and `patch` blocks. When applied,
patches run top-to-bottom in file order — each patch operates on the result of
the previous one.

```yaml
match:
  - name: "example"
patch:
  approved: true
---
match:
  - name: "example"
patch:
  version: 2
```

#### File naming

Patches must live in files named `{name}.patch.yaml`, where `{name}` is a
meaningful, descriptive prefix of your choosing — for example
`approve.patch.yaml` or `bump-version.patch.yaml`. The `.patch.yaml` extension
is what marks the file as a patch.

- `Patch.load()` requires at least one document and rejects empty documents
  (stray `---` separators with no content).
- `Patch.load()` rejects any file whose name does not end in `.patch.yaml`
  (or that has an empty prefix, like a bare `.patch.yaml`).
- During discovery, files ending in `.patch.yaml` are loaded as `Patch`
  instances, while all other `.yaml` files are loaded as `Template` instances.

```text
templates/
  service.yaml          # loaded as a Template
  approve.patch.yaml    # loaded as a Patch
```

---

## Matching

`match` is a list of **selectors**. The base is targeted if it matches **any**
selector in the list (logical OR). Each selector is a set of key/value pairs
that must all be satisfied on the base — keys must be present, and each value is
checked according to its type.

```yaml
match:
  - name: "example"
    version: 1
  - name: "example2"
    version: 1
```

> Matches a base named `example` **or** `example2`, in either case with
> `version: 1`.

### Wildcard

Use `*` as a value to accept anything at that position:

```yaml
match:
  - name: "*"
```

> Matches every base document, regardless of `name`.

Wildcards work at any depth — for example `labels: { os: "*" }` matches any
`os` label value.

### Regex

String values are matched as **regular expressions** (full string, via
`re.fullmatch`). A plain literal like `"example"` still works — it simply
matches that exact string. Use regex syntax when you need flexible matching:

```yaml
match:
  - name: "Example.*?"
```

> Matches any base whose `name` starts with `Example` — for example
> `Example model`.

Invalid regex patterns raise an error at apply time.

### Other types

Scalars other than strings (integers, floats, booleans) use equality. Lists are
matched positionally — same length, each element checked in order.

---

## Patch operations

The `patch` block is keyed by the field you want to change. The **key suffix**
selects the operation. Which operations are available depends on the **type** of
the field being patched.

### String

Replace the value (no suffix):

```yaml
patch:
  name: "foo"       # example -> foo
```

Delete with a guard (`key-`), or unconditionally with `*`:

```yaml
patch:
  author-: "John Doe"   # deletes `author` only if it equals "John Doe"
  license-: *           # always deletes `license`
```

### Int

Replace the value (no suffix):

```yaml
patch:
  version: 2        # 1 -> 2
```

Delete with a guard (`key-`), or unconditionally with `*`:

```yaml
patch:
  version-: 1       # deletes `version` only if it equals 1
  version-: *       # always deletes `version`
```

### Float

Replace the value (no suffix):

```yaml
patch:
  score: 10.0       # 9.8 -> 10.0
```

Delete with a guard (`key-`), or unconditionally with `*`:

```yaml
patch:
  score-: 9.8       # deletes `score` only if it equals 9.8
  score-: *         # always deletes `score`
```

### Bool

Replace the value (no suffix):

```yaml
patch:
  approved: true    # false -> true
```

Delete with a guard (`key-`), or unconditionally with `*`:

```yaml
patch:
  approved-: false  # deletes `approved` only if it equals false
  approved-: *      # always deletes `approved`
```

### Array

**Replace** the whole array (no suffix):

```yaml
patch:
  tags:
    - "yaml"        # replaces every existing tag
```

**Append** with `key+` — adds the new value(s) instead of replacing. If the
field does not exist yet, Yamlsed creates it as an empty array first.

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

**Delete by exact element match** with `key-`. Provide keys, and an array
element is removed only when it matches *exactly* (all specified keys equal, no
extras beyond what you list):

```yaml
patch:
  dependencies-:
    - name: "example2"
      version: 1
```

**Delete by partial element match** with `key-?` — the listed keys must be
present and equal, but the element may carry additional keys:

```yaml
patch:
  dependencies-?:
    - name: "example2"
      version: 1        # removes any dependency where name+version match
```

### Object

**Replace** the whole object (no suffix) — the entire map is overwritten.

**Append / merge** with `key+` — merges the new keys into the existing object
instead of replacing it. If the field does not exist yet, Yamlsed creates it as an
empty object first.

```yaml
patch:
  labels+:
    environment: "production"   # merges into `labels`, keeping existing keys
```

Nested `key+` inside a replace value works the same way. When the patch value
is an array, Yamlsed finds all elements that partially match the non-suffixed
keys and merges into each of them:

```yaml
patch:
  interfaces:
    - type: database
      config+:
        username: admin
        password: password
```

Every matching `database` interface keeps its existing `name` and `config` keys;
`config+` adds `username` and `password` alongside `host` and `port`.

**Guarded merge** with `key+?` — merges into an object only when the key already
exists in the base. If the field is missing, Yamlsed skips the operation.

**Null-guarded delete** with `key-` and a `null` value — deletes only when the
field is null:

```yaml
patch:
  healthcheck-: null    # deletes `healthcheck` only if it is null
```

**Unconditional delete** with `*` — deletes regardless of the current value:

```yaml
patch:
  metadata-: "*"        # always deletes `metadata`
```

### Functions

Patch values can be expressions written as `{{function(...)}}`. They are
evaluated when the patch is applied, not when it is loaded. Bare expressions
are supported in patch files — `Patch.load()` quotes them so YAML can parse
them:

```yaml
patch:
  updated: "{{now('YYYY-MM-DD HH:mm:ss')}}"
  random: {{random(1, 100)}}
  uppercase: {{uppercase("hello")}}
  env: {{env("HOME")}}
```

Built-in functions:

| Function | Description |
| -------- | ----------- |
| `now(format)` | Current date/time (`YYYY`, `MM`, `DD`, `HH`, `mm`, `ss` tokens) |
| `random(min, max)` | Random integer in range |
| `uppercase`, `lowercase`, `capitalize`, `reverse`, `length`, `trim` | String operations |
| `substring(s, start, end)` | Slice a string |
| `replace(s, old, new)` | Replace substring |
| `split(s, sep)` | Split into a list |
| `join(items, sep)` | Join a list into a string |
| `env(name)` | Read an environment variable |
| `old()` | Original value of the field being patched (before apply); `null` if missing |

Function results can be chained with **type casts** and **primitive methods**:

```yaml
patch:
  score: {{env("SCORE").float().round(2)}}
  tags: {{env("TAGS").split(",").array()}}
  label: {{env("NAME").trim().upper()}}
  enabled: {{env("FLAG").bool()}}
```

**Type casts** (coerce the current value):

| Cast | Result |
| ---- | ------ |
| `.str()` | string |
| `.int()` | int |
| `.float()` | float |
| `.bool()` | bool (`true`/`false`/`yes`/`no`/`1`/`0`, case-insensitive) |
| `.object()` | dict (JSON parse if string) |
| `.array()` | list (JSON parse if string) |

**String methods:** `.split(sep)`, `.replace(old, new)`, `.trim()`, `.upper()`,
`.lower()`, `.capitalize()`, `.substring(start, end)`, `.reverse()`, `.length()`

**Array methods:** `.join(sep)`, `.reverse()`, `.sort()`, `.unique()`, `.first()`,
`.last()`, `.length()`

**Number methods:** `.round(decimals)`, `.abs()`

**Object methods:** `.keys()`, `.values()`, `.get(key)`

Expressions are resolved only in patch **values** (replace, append, merge). Match
selectors and delete guards are never evaluated.

### Suffix reference

| Suffix | Operation        | Value                                                            |
| ------ | ---------------- | ---------------------------------------------------------------- |
| *none* | Replace          | New scalar, or new array (replaces the whole array)              |
| `+`    | Append           | list = append elements; dict = merge keys into object            |
| `+?`   | Append (guarded) | dict = merge keys only if the field exists; otherwise skip       |
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

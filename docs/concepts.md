# Concepts

There are two types of documents:

| Document    | Purpose                                                            |
| ----------- | ------------------------------------------------------------------ |
| **Base**    | A normal YAML template — the file you want to keep updated.        |
| **Patch**   | A document containing a `match` block and a `patch` block.         |

The patch is applied to the base whenever the base satisfies the `match` selector.

## Base

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

## Patch

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

### File naming

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

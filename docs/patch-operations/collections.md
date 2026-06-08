# Arrays and objects

## Array

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

## Object

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

# Scalars

## String

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

## Int

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

## Float

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

## Bool

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

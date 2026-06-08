# Matching

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

## Wildcard

Use `*` as a value to accept anything at that position:

```yaml
match:
  - name: "*"
```

> Matches every base document, regardless of `name`.

Wildcards work at any depth — for example `labels: { os: "*" }` matches any
`os` label value.

## Regex

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

## Other types

Scalars other than strings (integers, floats, booleans) use equality. Lists are
matched positionally — same length, each element checked in order.

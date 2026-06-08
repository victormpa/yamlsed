# Functions

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

## Built-in functions

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

Function results can be chained with **type casts** and **methods**:

```yaml
patch:
  score: {{env("SCORE").float().round(2)}}
  tags: {{env("TAGS").split(",").array()}}
  label: {{env("NAME").trim().upper()}}
  enabled: {{env("FLAG").bool()}}
```

## Type casts and methods

Coerce the current value, then call methods on the result:

| Cast | Result | Methods |
| ---- | ------ | ------- |
| `.str()` | string | `.split(sep)`, `.replace(old, new)`, `.trim()`, `.upper()`, `.lower()`, `.capitalize()`, `.substring(start, end)`, `.reverse()`, `.length()` |
| `.int()` | int | `.round(decimals)`, `.abs()` |
| `.float()` | float | `.round(decimals)`, `.abs()` |
| `.bool()` | bool (`true`/`false`/`yes`/`no`/`1`/`0`, case-insensitive) | |
| `.object()` | dict (JSON parse if string) | `.keys()`, `.values()`, `.get(key)` |
| `.array()` | list (JSON parse if string) | `.join(sep)`, `.reverse()`, `.sort()`, `.unique()`, `.first()`, `.last()`, `.length()` |

Expressions are resolved only in patch **values** (replace, append, merge). Match
selectors and delete guards are never evaluated.

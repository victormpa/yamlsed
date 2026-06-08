# YAMLSED

**YAML template matching & processing.**

**[Documentation](https://victormpa.github.io/yamlsed/)** — concepts, matching, patching, and examples.

## Getting Started

```bash
pip install yamlsed
```

## Usage

YAMLSED pairs a **base** template with a **patch** document. The `match` block
selects which base documents to update; the `patch` block describes the changes
to apply.
```yaml
# base.yaml

name: example
version: 1
approved: false
```

Write your patches
```yaml
# patch.yaml
match:
  - name: example
    version: 1

patch:
  approved: true
```

Run progmatically:
```python
import yaml

from yamlsed.patch import Patch
from yamlsed.template import Template

base = Template.load("base.yaml")

patch = Patch.load("patch.yaml")

base.apply(patch)
print(base)
```

Or from the command line:
```bash
yamlsed base.yaml patch.yaml
```

**Output:**

```yaml
name: example
version: 1
approved: true
```

More examples are in [Examples](examples.md).

## Status

Early / work in progress. Syntax described here reflects the current design and
may change.

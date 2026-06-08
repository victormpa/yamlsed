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

## Status

Early / work in progress. Syntax described here reflects the current design and
may change.

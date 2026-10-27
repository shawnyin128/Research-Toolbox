# SAI Flat Layout — Default

Use for a new repository with no explicit architecture, or an existing SAI flat tree. Select only needed capabilities; the following is an example, not a folder quota.

```text
src/
  entrypoint.py          # parse YAML/CLI, validate, compose
  hparam/
    __init__.py
    hparam.py            # compose parameter groups and cross-group checks
    training.py          # typed fields, defaults/help, owned validation
  training/
    __init__.py
    training.py          # compose concrete training components
    optimization.py      # actual numerical update loop
scripts/                 # campaigns/ablations calling maintained capabilities
configs/                 # experiment values, no duplicate parameter schema
tests/
docs/
```

Dependencies flow scripts/application entry -> capability composition -> implementation. `hparam` does not import business implementations. Implementations do not import the composition layer back. `utils` is the only same-named-entry exception and exists only for genuinely shared helpers.

The distribution must declare top-level modules/packages explicitly so installed commands work outside the source directory. Flat names such as `training`, `data`, or `hparam` can collide with unrelated installed packages; inspect actual import resolution. If isolation is needed, use the [package layout](package.md) with the same responsibility rules. Do not fix packaging with ambient `PYTHONPATH` or runtime `sys.path` mutation.

Keep one authoritative config contract. Entrypoint code may compose multiple useful operations but must not absorb algorithms or spawn a chain of pass-through wrappers. Adding a folder solely to host a one-line entrypoint does not improve the code.

Validate installed imports/CLI from outside the repository, configuration rejection before resource acquisition, one complete scientific workflow, and entry/implementation boundaries. Preserve scientific semantics while relocating code.

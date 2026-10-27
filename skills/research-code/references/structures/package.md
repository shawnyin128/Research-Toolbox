# Namespaced Python Package

Use for an established or requested installable `src/<package>/` project, or when top-level name collisions justify a package namespace. SAI conventions remain the default inside that namespace.

```text
src/<package>/
  __init__.py
  entrypoint.py
  hparam/
    __init__.py
    hparam.py
    training.py
  training/
    __init__.py
    training.py
    optimization.py
scripts/
configs/
tests/
docs/
```

Map flat `src/hparam` to `src/<package>/hparam` and flat `src/entrypoint.py` to `src/<package>/entrypoint.py`. Use package-qualified project imports and an installed console entrypoint targeting `<package>.entrypoint:main`. Keep same-named composition entries, centralized typed fields/validation, and separate algorithms. Do not introduce a second root `hparam` or competing entrypoint.

Inspect the current build backend, namespace-package behavior, public imports, package data, and plugin discovery before changing layout. Preserve supported public APIs with narrow tested adapters only when a real consumer requires them. Do not nest an extra package merely to imitate this example.

Test installed entrypoints and imports outside the source tree, package-resource access, public consumers, and affected complete workflows. Tests that add the source path can hide packaging errors; verify installation independently.

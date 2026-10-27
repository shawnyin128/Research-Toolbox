# Readable Scientific Engineering

## Responsibilities and visible execution

Trace the real operation before choosing an abstraction. A researcher should be able to follow the public entry to meaningful steps, mathematics, intermediate quantities, state changes, and output artifacts. Use domain names and concrete calls. A cohesive numerical loop is often clearer than many one-line helpers.

Use plain functions for transformations/composition. Classes should own real state/lifecycle or satisfy an actual interface such as `nn.Module`. Do not introduce registries, strategies, factories, inheritance, or forwarding layers without a demonstrated consumer. Do not reproduce a reference repository's package tree merely because its code is well maintained.

Keep project imports at file top and dependency direction visible. Resolve cycles through ownership. A type-only import under `TYPE_CHECKING` is fine. An optional third-party dependency may be imported at its specific integration boundary when absence/platform compatibility requires it; make the reason and failure behavior explicit.

Package code implements reusable capabilities. Scripts compose campaigns, seeds, datasets, and ablations using those capabilities. Algorithms and shared metrics have one maintained implementation. Distinct mathematics need not be collapsed into a generic framework. Numerical iteration belongs with its algorithm, regardless of loop size.

## One parameter contract

Keep each field's type, default, meaning, and validation together in central `hparam`. Typed dataclasses are the SAI default; reuse an established suitable parser/schema while preserving centralized project-owned definitions rather than building a second one. [SAI conventions](sai-conventions.md) and the selected structure guide specify physical placement.

Parse once at the application boundary; reject unknown keys and incompatible values before loading models/data or creating run artifacts. An annotation or `Literal` alone is not runtime validation. Avoid duplicate defaults/allowed-key tables and dictionary facades around typed objects. Implementations consume attributes or explicit mathematical arguments. Dictionaries remain useful for actual records, statistics, manifests, serialization, and third-party keyword arguments.

Distinguish omitted values from explicit values equal to the default. Resolve conditional defaults once, record effective settings, and test precedence. Pass models, tensors, generators, and callbacks explicitly as runtime dependencies. Do not force a small numerical function to accept a giant configuration object.

## Scientific identity and state

Preserve formulas, data ordering, split identities, masks, precision, rounding, normalization, RNG ownership, checkpoint semantics, and metric aggregation unless a change is requested. Define shape symbols and annotate tensor definitions and shape-changing operations. Express supported branches with explicit `if`/`elif`; an actual `else` raises a descriptive exception, with no hidden ternary fallback. Keep temporary mode/weight/hook changes inside failure-safe cleanup. Do not hide optimization or mutation inside an apparently read-only forward operation.

Imports and help/version commands must not download data, load models, launch workers, or allocate accelerators. Separate resource acquisition and persistence from pure computation where that makes the operation clearer. Validate saved artifacts by their actual consumers when serialization changes.

## Validation and review

Choose tests that can catch plausible scientific or integration regressions: known small examples, invariants, supported branches, invalid configuration, state restoration, and representative end-to-end paths. A file tree, import smoke, lint, or coverage percentage alone does not establish correctness or readability.

Read one representative call chain and explain it using its own names. Locate every effective parameter and show how it reaches the algorithm. Check that experiments reuse the maintained implementation and errors preserve resources. If this requires tracing generic aliases or hidden mutable globals, repair the concrete cause.

For small edits, use targeted checks. For substantial migrations, run the full available suite, inspect important uncovered branches, and test integration and installed entrypoints. Report unavailable hardware/runtime checks honestly.

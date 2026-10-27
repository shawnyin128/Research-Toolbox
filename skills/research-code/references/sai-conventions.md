# Default SAI Conventions

These SAI-CC conventions apply by default whenever research-code is used. They are this toolbox's engineering contract, not universal Python requirements. Current explicit project instructions and user decisions take precedence; identify conflicts and resolve their scoped consequences. Choose one structure guide to place the same responsibilities in the actual architecture.

## Architecture

- The application entry parses YAML/CLI, validates configuration, and composes capabilities; it does not implement algorithms, metrics, models, or data transformations. Its default location is `src/entrypoint.py`; the selected structure guide maps it into a package/framework when needed.
- Central `hparam` owns typed parameter definitions, defaults/help, and validation (`src/hparam/` in the default layout). Its same-named `hparam.py` composes groups/checks without importing business implementations. Prefer readable dataclass fields; no parallel default tables or mapping facades.
- Each selected capability module/subpackage except `utils/` has a same-named composition entry. It may expose several independently useful operations. Actual algorithms and resource implementations live in cohesive implementation files. Avoid another hidden pipeline layer or one trivial wrapper per operation.
- Experiments/sweeps/comparisons live in `scripts/` and call maintained package capabilities. Parameter-only ablations reuse implementation; different mathematics keep their real semantics.
- Choose modules from actual needs. Root external `data/` and integrated `src/data/` can coexist when both have responsibilities. Do not retain empty folders or placeholders solely to match a diagram.

For a new module directory/subpackage, establish the concrete purpose, interface, and why existing ownership is insufficient. Preserve any explicit project requirement for confirmation; previously authorized structure remains authorized. Routine files inside adopted modules do not create a new module-approval requirement. Do not invent approval gates beyond applicable project instructions and user scope.

## Code style

- Project imports are top-level and calls use concrete descriptive names, without generic `as execute` aliases or dynamic dispatch hiding a dependency cycle.
- Parameters carry typed defaults/help and early validation. Implementations use attributes; small numerical operations retain explicit scalar/tensor arguments. Runtime models/tensors/callbacks are not YAML fields.
- Keep numerical steps and meaningful intermediate names visible. Prefer a cohesive operation to excessive helper splitting. Use classes for real state/interfaces, not per-ablation hierarchies.
- Define shape symbols and annotate tensor definitions and shape-changing operations consistently.
- Supported cases use explicit `if`/`elif`; an actual `else` raises a descriptive exception. Do not hide a normal fallback in a ternary to evade this rule. Guards without an alternate branch are fine.
- Keep scientific identity, precision, data roles, state ordering, and failure-safe restoration explicit.

## Tooling and governing documents

Use uv, `.venv`, declared dependencies, `uv.lock`, Ruff, pytest, and meaningful branch/integration coverage by default. Preserve explicit compatibility/runtime constraints and existing authorization; report an incompatible environment migration rather than changing it silently. Keep root AGENTS concise and route detailed architecture, engineering, validation, and scientific/runtime rules into portable project docs.

For an adopted uv project, typical checks are `uv run --locked ruff check .`, `uv run --locked ruff format --check .`, and `uv run --locked pytest`. Inspect coverage when it resolves uncertainty about migration paths; no collected tests is not a behavioral pass. Verify installed commands outside the source tree without model/data side effects.

Use the project's working-branch convention and Conventional Commits when adopted. Remote publication and deletion follow the user's actual scope.

## Deliberate changes from the old package

The old package also carried project-specific policies for comment-in-place retirement, fixed branch counts, mandatory source-review records, and pervasive whole-repository audits. These are not inherited as universal requirements. Preserve them if a live project's instructions still require them; change such instructions only within authorized scope. The default migration guide uses validated cleanup plus Git history and risk-proportional review. Historical source-code reviews are provenance, not claims that today's code was inspected.

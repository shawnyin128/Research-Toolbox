---
name: research-code
description: "Initialize or substantively refactor Python/ML research repositories with SAI conventions by default: centralized typed parameters, same-named composition entrypoints, readable scientific code, and behavioral verification. Use for research architecture and experiment-code cleanup, not every small bug fix or training-parameter recommendation."
---

# Research Code

Build scientific code whose parameters, mathematics, and execution can be followed by a researcher. Preserve scientific behavior during refactoring; a tidy directory tree alone is not a successful migration.

## Select the scope and conventions

Inspect the applicable project instructions, Git state, dependency files, actual implementations/callers, scientific protocols, and intended runtime. Distinguish new setup, behavioral refactor, and standards-only work. Standards-only requests end with usable guidance; they do not authorize implementation migration.

**SAI conventions apply by default.** Centralize typed user parameters/defaults/help/validation in `hparam`; parse at one application entry; give capability modules same-named composition entries with separate implementations; keep campaigns in scripts. Use top-level project imports, explicit supported branches with exception-only `else`, tensor-shape annotations, uv/`.venv`, Ruff, and behavioral tests. Honor explicit project/runtime constraints and surface conflicts rather than silently discarding either contract.

Read [SAI conventions](references/sai-conventions.md), then **one** structure guide chosen from the actual code and requested target:

| Observed/target structure | Guide |
|---|---|
| New project without a specified layout, or SAI flat `src` tree | [SAI flat layout](references/structures/sai.md) — default target |
| Installable `src/<package>/` namespace | [Namespaced package](references/structures/package.md) — same SAI rules within the package |
| Established framework/plugin layout or legacy scripts | [Existing architecture](references/structures/existing.md) — map ownership and interfaces before migration |

Structure awareness changes where the rules live, not whether SAI conventions apply. Do not generate all layouts. Existing authorization remains valid; a convention is not a reason to request the same approval twice.

## Establish behavior before structure

Trace a representative public workflow through its real algorithm and dependencies. Record inputs/outputs, configuration defaults, state ordering, seeds, data/split identities, precision, failure behavior, and supported external interfaces. Name unavailable checks explicitly.

Choose responsibilities from this evidence. Explain the smallest useful target structure and old-to-new mapping for a migration. Keep parameter-only ablations on one implementation; keep genuinely different mathematics distinct. Do not add speculative packages, dispatch registries, or one wrapper per experiment.

Read [engineering.md](references/engineering.md) for parameter ownership, readable algorithms, and resource boundaries. For new setup use [initialization.md](references/initialization.md); for an existing repository use [migration.md](references/migration.md). Read only the applicable mode.

## Implement within the requested scope

- Put maintained algorithms and reusable capabilities in the package; experiment campaigns compose them from scripts/configuration. A numerical optimization loop is part of the algorithm.
- Parse and validate user configuration at the boundary. Keep one owner for each field and default, and pass typed attributes downstream. Live models/tensors/callbacks are explicit dependencies, not serializable settings.
- Use concrete names and visible control/data flow. Prefer direct calls and cohesive functions over forwarding layers. Put project imports at file top; fix ownership cycles rather than hiding them.
- Preserve scientific protocols, split identities, units, evaluation behavior, and declared tolerances. An intended scientific change must be distinguished from a behavior-preserving refactor.
- Keep imports and CLI help free of training, downloads, model loading, and resource allocation. Restore hooks, temporary weights, modes, and resources on failures as well as success.
- Preserve unrelated user edits, data, checkpoints, runtime dependencies, and plugin state. Ignore discovered local support precisely; keep maintained code and curated deliverables tracked.

Update governing docs when changing adopted conventions or responsibilities. [AGENTS.md.template](assets/AGENTS.md.template) is a concise starting point; adapt rather than overwrite existing instructions. Generated docs must be portable and link only to files actually delivered.

## Verify behavior and readability separately

Run the applicable project's checks and meaningful tests for changed behavior, supported branches, and callers. For migration, compare representative complete old/new workflows with fixed inputs and justified tolerances; import/lint checks do not establish scientific equivalence. Report pre-existing failures and unavailable GPU/remote paths separately.

Read the actual code and trace parameters, intermediate quantities, state changes, and errors from entry to result. Use independent review when the user or project authorizes it; otherwise perform and identify a self-review. Broaden checks only when scope, failures, or integration risks justify them.

Within an authorized cleanup, remove verified superseded code after checking consumers and behavior; keep regression tests and a concise migration record. Use Git history rather than commented duplicate implementations. Preserve unresolved dependencies and do not label their migration complete.

Finish with what changed, how scientific behavior was checked, actual validation results, and material limitations. If further experimental design or tuning is requested, pass along the canonical entrypoint, effective configuration, splits, metric, and budget. Companion skills are optional, not a required pipeline.

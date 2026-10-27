# Behavior-Preserving Migration

## Baseline and mapping

Trace public entrypoints and real implementations, including external consumers, scripts, configuration, data preparation, checkpoint I/O, and metrics. Record pre-existing failures separately. Capture one representative complete workflow and its supported variants where feasible.

Before rewriting, define exact comparisons or justified numerical tolerances for inputs/outputs, defaults, state order, seeds, data/splits, dtype/rounding, failure behavior, and artifact compatibility. An old bug intentionally fixed is a behavior change: name it and test the intended difference rather than claiming exact equivalence.

Map responsibilities and parameter axes to the target design. Several experiments with different values can share a workflow; genuinely different algorithms may remain separate. Preserve a legacy adapter only for a demonstrated consumer or explicitly supported interface. Folder moves and wrappers alone do not complete a requested architectural refactor.

## Implement and verify

Update applicable governing documents when responsibilities/conventions change. Implement in cohesive stages and update callers, package metadata, CLI, config, tests, and docs together. Preserve unrelated changes and live experiments. Do not replace working business commands with skeleton placeholders.

Compare complete old/new paths with fixed inputs under the same scientific protocol. Include supported branches and representative errors, downstream readers, and serialization round trips where affected. Exact equality may be inappropriate across precision/backends; state a scientifically justified tolerance before inspecting the deciding result. Low-level unit tests alone are insufficient for a whole-workflow claim.

Use the project's locked environment where applicable. Run targeted checks during changes, then the full available suite for a substantive migration, lint/format checks, and an installed-CLI check outside the source directory. Inspect unexecuted scientific branches; missing GPU/system validation is a limitation, not a pass.

## Retire only what is verified

Within authorized cleanup scope, check imports, callers, CLI consumers, scripts, tests, and docs before deleting superseded implementations. Preserve unresolved dependencies, external originals, data/checkpoints/results, and unrelated user work. Record precisely what remains and why; do not claim full migration while a required path is unvalidated.

Keep useful regression tests and a concise comparison record. Git history normally replaces commented duplicate code and permanent legacy source archives. Do not add hand-maintained source checksum gates for ordinary editable code. Data/checkpoint integrity and recorded experiment revisions are separate legitimate needs.

For a full cleanup, inspect all actual top-level and relevant hidden/mixed folders by purpose and consumers. Ignore local non-code support precisely while preserving it locally. Keep implementations and curated outputs tracked regardless of which tool generated them. Update links when moving evidence. Never infer obsolete status from age or a directory name alone.

## Completion

Review real call chains and adopted project rules separately from automated checks. Report changed behavior, representative comparisons and results, important unavailable branches, retained compatibility, and remaining work. If authorized independent review is unavailable, identify the self-review accurately.

Respect the repository's branch and commit conventions. Migration does not itself authorize publication, merge, remote branch deletion, new compute allocation, or replacing a running job. Do not apply a global branch-retention policy as part of ordinary refactoring.

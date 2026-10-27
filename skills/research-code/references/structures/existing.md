# Existing Frameworks and Legacy Scripts

Use when a framework owns configuration, dispatch, callbacks, or directory layout, or when research code still lives in mixed scripts/notebooks. This is a mapping/migration guide, not an exemption from the default SAI rules.

## Inspect the integration contract

Trace framework entrypoints, extension hooks, plugin discovery, configuration parsing, lifecycle/state, public commands, and scientific implementations. Distinguish framework-owned code from project-owned code. Do not patch dependency internals to enforce local style.

Write an explicit ownership map:

| SAI responsibility | Integration placement |
|---|---|
| Central typed parameters/defaults/help/validation | Project `hparam` at the package's existing root |
| One parse boundary | Existing application/framework entry, with early validation |
| Same-named capability composition | Project-owned capability modules compatible with framework hooks |
| Mathematical/model/metric implementation | Cohesive implementation files behind those entries |
| Experiment campaigns | Existing script/config launcher using maintained capabilities |

If the framework owns the parser/schema, centralize project-owned fields through its supported schema extension. Do not create an independent parser with competing defaults. A required callback/class may be the framework boundary, but the project capability it invokes should have visible composition rather than unnecessary forwarding chains.

## Choose a bounded migration

For legacy scripts, target [SAI flat](sai.md) by default, or [package](package.md) when packaging/public namespace requires it. Extract real reusable operations; parameter-only ablations share them. Moving whole scripts behind `run(argv)` is not a substantive refactor.

For an established framework, preserve required interfaces and the user's requested scope. Apply the SAI rules to project-owned code where compatible. If a fixed path/entry convention conflicts with a live required interface, state the concrete conflict and proposed mapping. Resolve a material unapproved architecture change with the user; continue independent inspection/baseline work. Do not silently disable SAI or break the framework to claim compliance.

Validate configuration precedence, callback/state ordering, extension discovery, supported commands, and representative complete behavior. A framework import smoke cannot prove its lifecycle still works. Record any explicitly retained compatibility exception and its current consumer.

---
name: research-subagent
description: Coordinate research subagents for planning, implementation, code and literature search, log analysis, derivation checks, independent review, and experiment launches.
---

# Research Subagent

Use the host's supported delegation tools and the user's authorization. Delegate a bounded task when it benefits from a separate context or a specialist. For small tasks, work directly. Treat role profiles as task guidance within the host's permissions.

| Task | Role profile |
|---|---|
| Plan an implementation or experiment | [planner](assets/claude/agents/planner.md) |
| Execute an approved plan | [implementer](assets/claude/agents/implementer.md) |
| Locate code or check an installed dependency | [code-scout](assets/claude/agents/code-scout.md) |
| Find papers or verify citations | [lit-search](assets/claude/agents/lit-search.md) |
| Interpret training and evaluation output | [log-reader](assets/claude/agents/log-reader.md) |
| Check a derivation or numerical claim | [derivation-checker](assets/claude/agents/derivation-checker.md) |
| Independently review results or tests | [reviewer](assets/claude/agents/reviewer.md) |
| Launch an authorized experiment | [run-launcher](assets/claude/agents/run-launcher.md) |

Give each delegate the objective, allowed actions, source locations, and expected evidence. Ask for a compact result with file locations, source links, checks, and unresolved items. Keep implementation and review separate when independence is needed. Use the host's model settings. Claude model aliases and tool lists in the bundled profiles apply to Claude Code.

For launches, use a user-provided launch profile and the [launch template](assets/claude/templates/launch-profile.template.md) where helpful. Establish the target, command, resource budget, writable output directory, and authorized retry conditions before launch. Record the job identifier and completion markers. Keep the personal profile local.

See the [Claude Code setup guide](references/claude-code.md) to register the bundled definitions as native agents. The [delegation rules](assets/claude/rules/delegation.md) are available as a reference or an explicit opt-in configuration.

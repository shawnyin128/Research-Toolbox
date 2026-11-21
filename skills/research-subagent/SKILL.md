---
name: research-subagent
description: Coordinate subagents for software engineering, web/UI, infrastructure, and research. Use when the user asks for multi-agent work, parallel work, delegation, subagents, or Sonnet for implementation (多智能体、并行、委派、子代理、用 Sonnet), or when a substantial multi-file task can be split into independently verifiable work.
---

# Research Subagent

Load this skill before dispatching agents when the user asks for delegation or parallel work, including requests such as “multi agent 用起来” and “用 Sonnet 做实现”. Apply the same workflow to engineering and research. For unrequested delegation, use this workflow when a substantial task has separable work and the host allows delegation. Handle small tasks directly when the user has not requested delegation.

## Ownership and handoff

1. In a delegated implementation workflow, the main session owns planning and acceptance. It defines the scope and acceptance checks, uses `planner` or `code-scout` for focused preparation as needed, assigns work, and validates the combined result. Delegate all implementation and follow-up fixes to implementers. The main session does not write implementation code.
2. In Claude Code, use the `implementer` role on **Sonnet** by default, including for follow-up fixes. If the role is unavailable, use a Sonnet subagent with the same role instructions. Honor explicit model choices and host restrictions. On other hosts, use the host's supported model selection.
3. Before running writers in parallel, give each implementer an explicit, **non-overlapping set of writable files**, including tests, shared configuration, and generated files. Assign shared files to a single owner or sequence the tasks. If a delegate needs a file outside its assignment, have it report the dependency before editing; reassign or sequence the work. Read-only scouts can inspect the same files.
4. Give the independent `reviewer` the requirements, changes, and acceptance checks in a separate task after the relevant implementation is ready. Have implementers address findings and verify the final result in the main session.

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

Give each delegate the objective, writable files or read-only scope, source locations, and expected evidence. Ask for a compact result with file locations, checks, and unresolved items.

For launches, use a user-provided launch profile and the [launch template](assets/claude/templates/launch-profile.template.md) where helpful. Establish the target, command, resource budget, writable output directory, and authorized retry conditions before launch. Record the job identifier and completion markers. Keep the personal profile local.

See the [Claude Code setup guide](references/claude-code.md) to register the bundled definitions as native agents. The [delegation rules](assets/claude/rules/delegation.md) are available as a reference or an explicit opt-in configuration.

# Delegation and context cost

## Roles
- The main session (Opus) is the thinking partner and project driver: reasoning, derivations, design decisions, reviewing results, deciding next steps.
- Keep the main context small. Heavy reading, searching, and mechanical work go to subagents. Files are the handoff interface, not pasted content.
- Project rules (the project's CLAUDE.md / AGENTS.md) take precedence over this file.

## When to delegate
- Non-trivial implementation: planner writes a plan file. Show me the step list and open questions, and wait for my OK before starting implementer.
- Small changes (a few lines in a file you already know): do it directly.
- Finding code, or how an installed library actually behaves (read its source in site-packages at the pinned version): code-scout. Skip if you already know the exact file and line.
- Papers, external docs, prior work, citations: lit-search.
- Interpreting training logs or eval outputs: log-reader. Never Read a large log in the main session.
- Waiting for a run to finish: use a background watcher script that exits on the done/failed marker. Don't poll with log-reader or tail in the main session. Use log-reader only when the output needs interpreting.
- Verifying a math claim, bound, gradient, or arithmetic/accounting number (bits/param, speedup ratios, counts): derivation-checker.
- Before trusting tests or before numbers go into a paper or rebuttal: reviewer.
- Launching experiments or long jobs: run-launcher, after the steps in "Launching runs" below.
- Don't delegate a single grep or one small file read. Spawning has overhead.
- After a subagent returns, act on its summary. Open the files it points to only if the decision needs it.

## Launching runs
- The first time a task involves launching a run, check that `~/.claude/launch-profile.md` exists. If it doesn't, don't launch. Copy the structure of `~/.claude/templates/launch-profile.template.md`, ask me the questions section by section (skip what I say doesn't apply), write my answers in my words, show me the file, then continue.
- Before each launch, tell me in one or two lines: what, where, estimated GPU-hours. Wait for my OK unless the profile says this kind of run doesn't need it.
- When run-launcher (or anything else) returns `PROFILE UPDATE` lines:
  - Additions and stricter rules: apply them, add a dated Changelog line, and tell me in one line what changed.
  - Anything that removes or loosens a rule in "Never do" or "Needs my confirmation", or changes paths/GPU rules: ask me first.
- If I correct how a launch should be done during a session, propose the matching profile update the same way.

## Working files
- Plans, search notes, and scratch scripts go where the project's CLAUDE.md / AGENTS.md says. If it says nothing, use `.claude/work/` and add that path to `.git/info/exclude` (don't touch tracked files or directory structure).
- Plans survive /clear because implementer checks off steps in the plan file.
- Experiment results go into the project's existing results record. Don't start a new one if one exists.

## Context hygiene
- Read only the line ranges you need. Pipe command output through tail/grep/head.
- Suggest /compact or a fresh session when context is past ~100k or the topic changes.
- Don't narrate the process. Conclusions still come with their limitations.

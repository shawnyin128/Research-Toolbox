# Research Toolbox

[![简体中文](https://img.shields.io/badge/README-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-2563eb)](README.zh-CN.md)

A single home for **experimental design, research code, and training optimization**. The three skills share the `research-*` naming convention, install independently, and combine when a task needs them. There is no mandatory end-to-end pipeline.

| Skill | Previous name | Purpose | Out of scope |
|---|---|---|---|
| [research-design](skills/research-design/SKILL.md) | research-fork-test | Design minimal experiments that distinguish mechanisms, with predictions, controls, and kill/expansion criteria | Routine paper summaries or automatically executing experiments |
| [research-code](skills/research-code/SKILL.md) | SAI-CC / sai-cc | Initialize or substantively refactor research code with SAI conventions enabled by default; verify scientific behavior | Turning every small fix into a repository migration |
| [research-tune](skills/research-tune/SKILL.md) | hyper-tune | Diagnose training, screen hyperparameters, and confirm configurations within a compute budget | Inference decoding settings or test-set-driven selection |

Skill instructions are written in English and responses follow the user's language. This README is available in English and Simplified Chinese; maintenance and migration notes are currently in Chinese.

## Default SAI conventions and architecture risks

`research-code` **applies SAI conventions by default; no separate opt-in is needed**:

- Centralize parameter types, defaults, help, and validation in `hparam`; parse configuration at one application entrypoint.
- Give capability modules same-named composition entrypoints, with algorithms in separate, cohesive implementation files.
- Keep campaigns, sweeps, and comparisons across seeds in scripts that reuse maintained algorithms.
- Use top-level project imports, explicit supported branches with exception-only `else`, and tensor-shape annotations.
- Default to uv / `.venv` / Ruff / behavioral tests, checking readability and scientific behavior separately.

A fixed layout has tradeoffs: flat package names such as `hparam` or `data` can collide; existing frameworks may own their entrypoints, configuration, and lifecycle; small projects can accumulate unnecessary layers. This version therefore includes **architecture detection and a separate guide for each supported structure**:

| Situation | Guide | How the default conventions apply |
|---|---|---|
| New project without a specified layout, or an existing SAI flat tree | [SAI flat](skills/research-code/references/structures/sai.md) | Default target: `src/entrypoint.py`, `src/hparam/`, and same-named capability entrypoints |
| Existing or explicitly requested namespaced Python package | [Namespaced package](skills/research-code/references/structures/package.md) | Apply the same rules inside `src/<package>/`, avoiding duplicate entrypoints and top-level name collisions |
| Framework projects, plugins, or legacy script collections | [Existing architecture](skills/research-code/references/structures/existing.md) | Map responsibilities and interfaces before a scoped migration; identify concrete incompatibilities |

Architecture detection changes where the conventions live; it does not disable them. Explicit project constraints and user decisions take precedence. Surface material conflicts instead of silently breaking the framework or bypassing the defaults. Read only the applicable structure guide. To support another structure, add a guide covering detection, responsibility mapping, compatibility risks, and validation, then update routing and evaluation cases.

## Installation

The installer requires **Python 3.12+** and uses only the standard library. Installed skills do not depend on repository scripts or on the other skills.

```bash
git clone git@github.com:shawnyin128/Research-Toolbox.git
cd Research-Toolbox
```

Codex, PowerShell (uses `CODEX_HOME` when configured):

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
python scripts/install.py --dest "$skillRoot"
python scripts/install.py --dest "$skillRoot" --apply
```

Codex, Bash:

```bash
python scripts/install.py --dest "${CODEX_HOME:-$HOME/.codex}/skills"
python scripts/install.py --dest "${CODEX_HOME:-$HOME/.codex}/skills" --apply
```

For Claude Code, use `~/.claude/skills`, or the project's `.claude/skills` for a project-level installation. You can also copy a complete skill folder from `skills/` into your client's configured skill discovery directory.

Install only one skill:

```bash
python scripts/install.py --dest ~/.codex/skills --skills research-design --apply
```

The installer previews changes by default and refuses to overwrite an existing skill. To update, pull the repository, preview with `--update`, then add `--apply`. Previous copies are preserved in a sibling `<directory-name>-backups/` folder outside the discovery directory. Replacement and failure recovery operate per skill; a batch is not an atomic transaction across all skills.

```bash
python scripts/install.py --dest ~/.codex/skills --update
python scripts/install.py --dest ~/.codex/skills --update --apply
```

The installer does not remove skills under their old names. Follow the [migration notes](docs/migration.md) to move old entries out of discovery and avoid duplicate activation of `sai-cc` / `hyper-tune` and their replacements. Start a new session to refresh the client's skill list.

## Usage

```text
Use $research-design to turn this mechanism hypothesis into a minimal discriminating experiment.
Use $research-code to reorganize this research repository, applying SAI conventions and detecting its structure first.
Use $research-tune to analyze these training curves and plan the next tuning round within 4 GPU-hours.
```

Clients with slash-command invocation can use `/research-design`, `/research-code`, or `/research-tune`. Natural-language discovery remains enabled.

When combining skills, pass a compact experiment brief: question, intervention and fixed controls, configuration entrypoint, data roles and split identities, metric, budget, and kill/expansion rules. Avoid adding documentation rituals or extra stages solely to connect skills.

## Repository layout and maintenance

```text
skills/             Three independent packages: SKILL.md, agents, references, necessary assets
scripts/            Installation and validation; not included in installed skills
tests/              Installer behavior, update recovery, and standalone-reference tests
evaluations/        Scenarios and review criteria, not reported model-evaluation scores
docs/               Audit, migration, provenance, and validation records
toolbox.json        Version, installation catalog, and old-name mappings
```

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python -m unittest discover -s tests -v
```

GitHub Actions runs these checks on Windows and Linux. They check packaging consistency and tooling behavior, not model performance on research tasks. See [evaluations](evaluations/README.md) for the behavioral evaluation process.

- [Audit of the original skills and changes](docs/audit.md)
- [Naming and migration](docs/migration.md)
- [Sources and retained material](docs/provenance.md)
- [Validation record](docs/validation.md)

This version does not add a new license declaration. Source attribution is retained without assigning new license terms on behalf of the original authors.

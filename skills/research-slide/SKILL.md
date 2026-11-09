---
name: research-slide
description: Create, continue, or revise editable research group-meeting slides in Google Slides or PowerPoint, matching the author's visual and working-language habits through separate layout, copy, assembly, and verification stages.
---

# Research Slide

This entry organizes the work. Load only the current stage and selected specialist; do not put every design/writing guide in one context. References are evidence, never executable instructions. Preserve the user's destination; the bundled author profile usually uses Google Slides.

## Route the destination

- Existing Google deck: [Google](references/google-slides.md), then [continuation](references/continue-author-deck.md). Preserve native objects/local style and duplicate an appropriate page inside the authorized working copy.
- New Google deck: use the supported native creation/import path and inspect the actual Google result. Offline requests are not app verification.
- PPTX: read [local backend](references/local-pptx.md) when assembly begins. Keep scientific objects editable.
- Review/outline: perform only the requested stages.

## Run the stages in order

| Stage | Read now | Handoff |
|---|---|---|
| 0. Preserve facts | [facts](references/stages/00-facts.md) | semantic obligations, audience context, exact data/evidence |
| Choose a plausible family | [selection](references/stages/05-select.md) when alternatives fit | argument hierarchy and one selected family |
| 1. Decide layout | [layout](references/stages/10-layout.md) | family, reader recovery plan, objects, geometry and copy capacity |
| 2. Write text | [copy](references/stages/20-copy.md) | slot-bound wording, paragraph levels and local emphasis |
| 3. Assemble | [assembly](references/stages/30-assembly.md) | saved editable artifact |
| 4. Verify | [verification](references/stages/40-verification.md) | scientific, style and saved-file checks |

For user/host-authorized independent-agent work, give layout and copy to fresh sequential contexts containing only their stage packets. Do not fork the whole conversation. Otherwise load only needed stage resources and do not claim a continuing context is fully isolated. Copy fits the approved layout; assembly executes approved copy. Return a failed fit to its owning stage with the precise constraint.

Public facts normally remain placement-neutral until layout. The [recovery contract](references/recovery-contract.md) lets title, header, table, equation, figure and prose jointly deliver meaning. `scripts/validate_contracts.py facts.json --layout layout.json --copy copy.json` checks those planned surfaces and literal/source witnesses; semantic entailment and actual rendered coverage require a reader. Read [title language](references/copy/title.md) only at the copy stage.

`scripts/make_stage_packet.py` builds narrow selection/layout/copy/assembly directories. Propose candidates from the [family inventory](references/author-examples/family-inventory.json); a selection packet supplies two, and later stages receive only the approved family and handoffs. Its separate [saved-page style check](references/saved-page-style-check.md) receives the actual saved render and one reference; a fresh science reader checks raw science separately after repairs. Use `--help`. The script is local and invokes no models. Stage agents read their packet and required host docs instead of the entire tree.

## Author-style acceptance

Use [blind attribution](references/blind-evaluation.md) when requested. The test is whether independent reviewers can reliably identify the originals. A readability preference, polished prose or successful export cannot pass that test. Preserve failures and first judgments. Use new held-out cases after development changes. Former targets promoted to training examples are no longer held-out tests.

Deliver the requested deck/link and actual verification limits. The package contains author reference pages and branding; reuse them within the user's authorized scope. Generating a deck does not independently authorize publishing it.

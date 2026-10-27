---
name: research-design
description: Design minimal experiments that distinguish competing mechanisms behind a research idea, including cross-domain analogies, controls, falsification criteria, and scale-up decisions. Use for experimental design or research-idea critique, not routine paper summaries or training hyperparameter selection.
---

# Research Design

Turn a research claim into the smallest informative experiment. Optimize for separation between explanations, not support for a preferred story. Preserve the user's scope: designing a test does not imply running it.

## Frame the claim

Restate the idea faithfully in one sentence. Separate observation, target claim, proposed mechanism, and evidence. If nothing was measured, label the starting point a hypothesis. Define the intervention, observable outcome, and domain of the claim.

For an analogy, map source concepts to target variables and a shared mathematical, causal, or computational structure. Name broken assumptions. Shared vocabulary alone is not a bridge.

Infer ordinary details from supplied context and make provisional assumptions explicit. Ask only for missing facts that materially change identification, feasibility, or the next decision. Missing evidence remains missing.

## Find a separating prediction

Compare these roles without forcing them to be distinct or exhaustive:

- **M1:** the proposed mechanism.
- **M2:** the strongest charitable alternative producing the same headline result.
- **M0:** one consequential null or artifact, such as extra capacity, compute, leakage, or measurement error.

For each, give its account, assumptions, predicted observations, and disappearance or reversal condition. Explanations may coexist. Label unknown predictions and observational equivalence rather than inventing differences.

Build the prediction matrix **before** choosing the experiment:

| Intervention/regime | M1 | M2 | M0 | Observable metric |
|---|---|---|---|---|

Prefer divergence in sign, scaling, threshold, localization, timing, or failure mode. Explain its basis. Weigh separation, cost, and confounding qualitatively; a large effect shared by every explanation is not discriminating evidence. If no feasible separation exists, identify the smallest extra measurement/intervention needed instead of promising identification.

Read [framework.md](references/framework.md) for fork axes, analogy checks, or difficult controls. Read [examples.md](references/examples.md) only when a worked design helps.

## Choose the smallest sufficient experiment

Consider analytic construction, synthetic data, isolated component, small learned system, or full system. Choose the lowest level retaining the disputed mechanism; scale-dependent mechanisms may already require a larger system. State what the test preserves, removes, establishes, and leaves untested.

Specify intervention levels, baselines, metric, expected contrasts, resource scope, and validity checks. Match capacity/compute when they are alternatives; measure a proposed mediator instead of controlling it away. For stochastic results, identify independent units and an uncertainty/precision plan. For deterministic constructions, specify correctness checks.

## Declare the decision before the deciding run

| Result pattern | Conditional interpretation | Next action |
|---|---|---|

Replace generic rows with concrete patterns. Include a scoped **kill criterion**, an **expansion gate**, inconclusive/mixed outcomes, and invalid-test outcomes. Use compatible thresholds and mutually exclusive branches or explicit precedence: validity first, identification second, practical expansion last.

A failed validity check is not a negative scientific result; an imprecise null is not a kill criterion. A small identified effect may fail the practical expansion gate. Set thresholds before the relevant outcomes, or label them provisional/exploratory. Call a plan preregistered only when it was actually recorded beforehand. Do not retrofit confirmatory rules to observed outcomes.

## Deliver at the requested depth

- **Quick critique:** a compact claim, M1/M2/M0, prediction matrix, one minimal test, and kill/expansion decision. Keep material assumptions and evidence gaps visible.
- **Runnable design:** use [experiment-brief.md](references/experiment-brief.md) for controls, precision, resources, and complete decision coverage. This is a field guide, not mandatory headings.
- **Source-constrained or red-team:** retain the chosen depth; respect the source boundary or strengthen alternatives and cheap falsification respectively.

With supplied sources, distinguish **Source-supported**, **Inference**, and **New hypothesis** and give source locations. Flag unreadable evidence. Novelty remains unresolved without an adequate literature check. Use [rubric.md](references/rubric.md) to repair concrete gaps, not to manufacture a passing score.

End with one recommended first experiment, its scope, and the decision it unlocks. Report mechanistic support, practical value, feasibility, and novelty separately when relevant. If implementation or training is also requested, carry the intervention, fixed controls, split identities, metric, budget, and decision rules into that work; `research-code` and `research-tune` can help if installed, but are not dependencies.

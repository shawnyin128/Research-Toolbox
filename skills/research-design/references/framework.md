# Discriminating Experiment Framework

Read the sections needed to resolve the current design choice.

## Candidate explanations

Use these categories to find a concrete, charitable M2 or M0:

- **Capacity:** parameters, memory, lookup entries, context, representational freedom.
- **Compute:** FLOPs, training steps, search, calibration, optimization budget.
- **Regularization/optimization:** smoothing, conditioning, gradient scale, initialization, credit assignment.
- **Data:** leakage, distribution overlap, curriculum, sampling, preprocessing.
- **Measurement:** metric mismatch, evaluator error, extraction failure, censoring, truncation.
- **Implementation:** kernels, batching, caching, precision, layout, framework behavior.
- **Selection:** chosen checkpoints, seeds, tasks, horizons, model sizes, workloads.
- **Proposed structure:** the user's causal or computational mechanism, still a hypothesis.

M1/M2/M0 are useful comparison roles, not necessarily mutually exclusive or exhaustive theories. Choose the most consequential artifact to test instead of putting every possible failure into one unfalsifiable M0. State shared assumptions, possible mixtures, and predictions that remain unknown. If two explanations make the same predictions under feasible interventions, report that identification gap; do not invent a difference.

## Fork axes and predictive separation

Choose variables that change competing predictions, such as:

| Family | Candidate axes |
|---|---|
| Statistics/data | Noise, sample size, shift, latent predictability, surface randomness, imbalance, tails, correlation, calibration–holdout mismatch |
| Model/optimization | Size, capacity, optimization budget, initialization, regularization, depth, horizon, bottleneck dimension, codebook budget, objective weight |
| Representation | Information preserved/destroyed, local/global dependence, predictable/unpredictable factors, nuisance/invariant features, causal/correlational features, token/sequence targets |
| Systems | Batch size, prompt/output length, prefix reuse, arrival rate, prefill/decode balance, compute/memory bottleneck, component/end-to-end path, distribution, communication, cache pressure |
| Time | Early/late training, short/long rollout, first failure, accumulation, warmup/steady state |

Useful contrasts differ in sign, monotonicity, threshold, localization, scaling, persistence under a relevant control, temporal order, or failure mode. Explain the causal/computational reason for each prediction. An extreme setting with a large shared effect is not a separating regime.

Prioritize qualitatively: weigh observable prediction separation, execution cost, and confounding risk separately. Do not add unlike units or present an uncalibrated ratio as a measured score. Prefer a contrast that can change the next decision within the user's budget.

## Smallest sufficient substrate

Consider analytic examples/counterexamples, synthetic data, an isolated operator/layer/state transition/kernel, a small model/environment, then a full system. Select the lowest level that retains the disputed mechanism; this is not a mandatory sequence.

- Analytic constructions can establish possibility, impossibility, direction, or non-equivalence under their assumptions.
- Synthetic data makes latent factors and interventions controllable.
- Isolated components expose local mechanisms.
- Small learned models retain learning dynamics and multistep behavior.
- Full systems may be necessary for scale-dependent effects, interactions, workload/hardware constraints, or external validity. If a smaller toy removes the mechanism, explain why the larger substrate is already the minimum.

For the chosen substrate, state what is preserved, removed, established, and left untested. Set an expansion gate before spending beyond it.

## Analogy and domain checks

For a cross-domain analogy, map variables and identify a shared mathematical object, optimization problem, information constraint, or causal/computational structure. Record assumptions that fail to transfer. Shared vocabulary alone is insufficient; a useful mapping yields a testable prediction.

- **Objectives/representations:** connect the training objective to the actual target metric; test capacity, regularization, and optimization explanations.
- **Systems:** identify the bottleneck and changed bytes/FLOPs/launches/synchronization/communication; distinguish component gains from end-to-end outcomes under defined hardware and workloads.
- **Causal/scientific:** separate observation from intervention; identify a competing confounder, negative control, mediator, or predicted temporal order.

Match capacity, compute, or workload where it removes an alternative explanation. If reduced compute is the proposed mediator, measure it rather than matching the mechanism away; distinguish total practical benefit from a mechanism-isolating comparison.

## Decision and evidence discipline

Specify primary contrasts, practical effect thresholds, tolerances, independent units, and uncertainty before the deciding run. Tokens or repeated measurements from one run are not automatically independent replicates. Use a pilot to estimate feasibility or variance if needed, then freeze rules for a fresh test. Call a plan “preregistered” only when it was actually recorded before the relevant outcomes; otherwise call it a proposed decision plan.

Separate a valid negative result from an underpowered/inconclusive contrast and a failed intervention, implementation, or evaluator check. A failed validity check triggers repair, not a mechanistic conclusion. A null result weakens M1 only to the extent the test could detect its predicted effect. Interpret mixed results conditionally and limit conclusions to the tested regime. Positive results shared by all explanations add little discrimination.

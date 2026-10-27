# Worked Examples

These are hypothetical designs, not reported experimental findings. Predictions are conditional on the stated mechanisms; numeric decision thresholds must be chosen for the actual budget and task before the deciding run.

## 1. Latent prediction and speculative decoding

**Input:** “JEPA and speculative decoding both predict the future. Could a latent-prediction objective improve speculative decoding?”

**Compression:** Test whether an auxiliary latent-prediction objective improves a draft model's token proposals through learning useful latent dynamics, beyond generic regularization or extra capacity/compute.

**Analogy boundary:** Predicting a latent state and proposing target-model tokens have different objectives. A transfer hypothesis needs a mapping from latent dynamics to conditional token distributions; the shared word “prediction” supplies no evidence.

- **M1:** Learning predictable hidden dynamics improves draft–target token-distribution overlap at relevant rollout contexts.
- **M2:** Generic auxiliary-loss regularization explains the benefit; latent structure is unnecessary. Extra capacity and compute are additional controls.
- **M0:** The objective has no useful token-level transfer, or trades token fidelity for latent accuracy. A broken verifier is a separate validity failure to check first.

| Contrast | M1 prediction | M2 prediction | M0 prediction |
|---|---|---|---|
| Predictable hidden dynamics, controlled emission randomness | Latent-specific gain at contexts where dynamics inform token probabilities | No latent-specific advantage once the relevant resource/optimization explanation is controlled | No useful acceptance gain, possibly a fidelity loss |
| Destroy latent-target alignment while retaining token data | Latent-specific advantage shrinks | May persist if regularization is comparable; changed task difficulty makes this contrast inconclusive | No consistent transfer |
| Same architecture/budget, relevant generic auxiliary control | Latent-specific gain remains | Gap shrinks under the control that captures the actual alternative | Neither auxiliary task yields useful transfer |

**Minimal substrate:** A synthetic hidden-state sequence generator with known token probabilities. Keep a fixed target distribution and train token-only, token-plus-latent, matched generic-auxiliary, and shuffled-latent-target drafts. Vary latent predictability and emission randomness separately. Match capacity and account for training compute; check whether shuffled targets alter loss difficulty or gradients.

**Measurements and validity:** Measure conditional distribution overlap at specified contexts, acceptance by proposal position, accepted-prefix length, and draft cost. For exact speculative sampling at a fixed context, with target `p` and draft `q`, acceptance is `sum_x min(p(x), q(x)) = 1 − TV(p,q)`; a latent benefit must connect to token overlap or the contexts/dependence governing multistep acceptance. Unchanged teacher-forced averages alone do not establish unchanged rollout behavior. Verify the sampling correction and target output distribution on this enumerable toy. These sampling properties follow from the [original speculative-decoding algorithm, §§2.3–3.2](https://proceedings.mlr.press/v202/leviathan23a/leviathan23a.pdf); the proposed latent benefit remains a new hypothesis.

**Decision plan:** Define a practically useful acceptance contrast and fidelity tolerance before a fresh test; estimate training variability across independent runs and sequence variability without counting correlated tokens as independent replications. A structure-dependent gain surviving the controls increases confidence in M1; comparable generic-control gains favor M2. Valid, sufficiently precise evidence excluding the required transfer is a kill criterion for this latent-transfer thesis at the tested regime. Inconclusive precision or failed checks require diagnosis. Expand only after the latent-specific contrast and target-distribution check pass; acceptance gains alone do not establish end-to-end speedup.

## 2. Prefix-cache serving gain

**Input:** “Radix-tree caching seems faster. Is the benefit really from prefix reuse?”

- **M1:** Shared-prefix KV reuse avoids repeated prefill computation.
- **M2:** Scheduler/batching behavior explains the observed gain.
- **M0:** Uncontrolled warmup, cache state, request ordering, or benchmark selection creates the gain.

**Fork:** Cross high versus zero shared-prefix overlap with cache enabled/disabled under the same scheduler. Match prompt lengths, arrival traces, output lengths, hardware, and numerical path. If scheduler differences remain a plausible explanation, add a scheduler contrast with caching disabled or explicitly report that M2 is unresolved.

**Minimum experiment:** One model on a small serving engine can test this local reuse mechanism. Measure TTFT, computed prefill tokens, cache hits, throughput, and GPU utilization. Randomize run order, reset cache state between designated cold runs, and define warm/steady-state runs separately. Check output correctness. Use independent run blocks for uncertainty; requests sharing one queue/cache are dependent. Reduced prefill work is the proposed mediator, so measure it rather than forcing it equal.

| Result pattern | Conditional interpretation and action |
|---|---|
| Cache-by-overlap interaction accompanied by less computed prefill, surviving state controls | Supports a reuse contribution; scheduler mediation or interactions may coexist. |
| Gain tracks scheduler changes with caching disabled | Favors M2; revise the attribution. |
| Apparent gain vanishes after prescribed state/order controls | Favors the tested M0; repair the benchmark before expanding. |
| Valid, precise test excludes the predeclared useful interaction | Kill the current prefix-reuse attribution for this workload. |
| Wide uncertainty or failed cache/output checks | Inconclusive or invalid; no mechanism conclusion. |

**Expansion gate:** Before testing larger deployments, require a predeclared useful interaction plus the expected prefill-work reduction, correct outputs, and adequate precision. This establishes a contribution in the tested regime, not unique causation or production-wide benefit. The recommended first experiment is this cache-by-overlap contrast, with explicit cold and warm run blocks.

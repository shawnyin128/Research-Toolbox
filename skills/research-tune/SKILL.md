---
name: research-tune
description: Diagnose neural-network training and plan compute-budgeted hyperparameter searches, including learning rate, weight decay, warmup, schedules, and full or adapter fine-tuning. Use for training instability, learning-curve diagnosis, or tuning; not inference decoding settings or general model comparisons.
---

# Research Tune

Spend the least compute needed to make the next training decision. Check correctness, screen plausible candidates, and reserve longer runs for useful evidence. A planning request does not authorize training jobs.

## Frame the budget and comparison

Identify the objective, selection metric/direction, model and initialization, trainable parameters, optimizer, effective batch, sequence/input length, data splits, precision, schedule, and available compute. Use supplied evidence and explicit provisional assumptions instead of a long questionnaire. Ask for missing limits before committing consequential compute.

Tune on validation data; keep the final test set untouched during selection. Record split identities and any separate calibration/training data. For mechanistic experiments, preserve the declared intervention and controls: unequal tuning budgets can themselves explain an apparent gain.

Use the established recipe first. Read [initial-points.md](references/initial-points.md) only when selecting an initial configuration or checking family-specific ranges. Numeric examples are search priors, not guarantees or the latest verified recipe.

## Start at the earliest unresolved stage

Reuse recent applicable correctness evidence; do not restart every diagnosis from scratch.

1. **Check the objective and update path.** Verify finite activations/loss/gradients, target shapes and masks, loss reduction, trainable-parameter membership, actual updates, and precision/scaler behavior. For uniform softmax predictions with ordinary mean cross-entropy, the baseline is `log(C)`; random logits need not be uniform. There is no universal `0.1` deviation threshold. Pretrained, weighted, masked, regression, and composite objectives need their own baseline. See [diagnostics.md](references/diagnostics.md).
2. **Use a small optimization probe when needed.** On a fixed tiny subset, disable removable regularization/augmentation for diagnosis and check whether the objective can improve as expected. Memorization to zero is not universal for constrained adapters, noisy/conflicting labels, or irreducible objectives. Isolate the probe's state and restore the production recipe afterward. Do not select final hyperparameters from this probe.
3. **Screen learning rate at low cost.** Try a few log-spaced candidates near the recipe. Keep initialization, batches, budget unit, and evaluation comparable. Retain required warmup, clipping, parameter groups, and schedule; fixed LR is an optional diagnostic, not a mandatory replacement. Run long enough to observe post-warmup behavior. Select a stable region with margin, not automatically the largest non-diverging LR.
4. **Allocate longer trials adaptively.** Refine LR and then relevant regularization with a compact candidate set. Promote candidates using validation evidence at comparable resource budgets. Allow for noisy rankings and slow starters; an early loser may win later. Validate short-run rankings at a longer horizon before committing the full budget. Read [search-plan.md](references/search-plan.md) for allocation and trial records.
5. **Confirm the selected recipe.** Freeze configuration, schedule, and selection rule. Evaluate finalists with independent seeds when affordable and report uncertainty/seed sensitivity. Evaluate the test set only under the declared final protocol; repeated test-guided revisions turn it into tuning data.

## Interpret curves as hypotheses

Compare train and validation measurements only when their loss definitions, augmentation, model modes, and averaging are understood. A gap can reflect regularization, distribution shift, leakage, or measurement mismatch; it is not automatically overfitting. Flat/NaN curves can reflect a broken update path, data/objective errors, precision, or LR. A decreasing training loss does not by itself determine when a schedule should decay.

Choose the cheapest probe that separates plausible causes before changing many knobs. Explain what each result would imply. For an actual delta/weight diagnostic, measure optimizer updates and interpret scale per parameter group; raw gradient times LR is not an AdamW update.

## Deliver a usable next decision

Scale output to the request: a quick diagnosis needs evidence, competing causes, and one next probe; a sweep needs the candidate table, budget arithmetic, stop/promote rules, and protected controls. Record exact effective config, code revision, seed, split, steps/tokens, curves, cost, and stop reason for executed trials. Label plans, observations, and unrun suggestions distinctly.

Do not imply GPU savings or improved quality without an actual comparison under a defined budget and baseline. Execution ends at the authorized budget or agreed stopping rule. If the evidence instead requires code repair or a mechanism test, state the handoff; `research-code` and `research-design` can help if installed but are not dependencies.

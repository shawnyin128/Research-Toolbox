# Training Diagnostics

Use when a run is broken or a curve has multiple plausible explanations. Choose a probe that changes the next decision, and keep diagnostic changes separate from final training settings.

## Initial loss: derive the relevant reference

For ordinary mean cross-entropy and uniform predictions over C classes, each hard-label example contributes `-log(1/C) = log(C)`. Balanced labels are not required for this uniform-prediction identity. Equal logits yield uniform predictions; nonzero-variance random logits generally do not. An arbitrary threshold such as `abs(loss - log(C)) > 0.1` cannot establish a bug.

Verify the actual logits/probabilities, target encoding, ignored positions, class weights, label smoothing, and reduction. Pretrained models and composite/regression objectives need different references. Compare the implementation with a hand-computed small batch before interpreting a large-scale loss. The [PyTorch cross-entropy definition](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html) specifies the applicable weighting, masking, and reduction semantics.

Removing explicit regularization terms can isolate a data loss. Decoupled weight decay does not itself add a term to the reported cross-entropy; changing it cannot explain a pre-update data loss.

## Symptoms and cheapest separating checks

| Symptom | Plausible causes | First discriminating probe |
|---|---|---|
| Flat loss | LR, frozen/disconnected parameters, wrong optimizer membership, masking, repeated batches, accumulation logic | Inspect a fixed batch's gradients and actual parameter delta; verify targets and effective updates |
| NaN/Inf | Bad inputs, invalid objective operation, low-precision overflow, optimizer state, LR | Locate the first nonfinite value; compare a small higher-precision run without resetting unrelated scientific settings |
| Tiny subset fails to fit | Conflicting labels, objective floor, constrained trainable capacity, bad update path | Verify objective/updates and achievable target before raising capacity or removing valid constraints |
| Train improves, validation worsens | Overfitting, shift, preprocessing differences, metric mismatch | Evaluate a common fixed metric/mode and inspect split construction, then isolate regularization |
| Short trials rank inconsistently | Noise, warmup differences, slow learning, schedule horizon | Repeat a small subset at a longer comparable budget and independent seed |
| First updates work, resume fails | Optimizer/scaler/scheduler/RNG restoration, data-order changes | Compare uninterrupted and resumed short runs under the same state contract |

For accumulation/distributed runs, count actual optimizer updates and effective batch, not just dataloader iterations. Check scheduler advancement, loss scaling/reduction, clipping order, zeroing, skipped scaler updates, and active parameter groups.

For mixed precision, a higher-precision probe is diagnostic evidence, not proof the final precision recipe is safe. Measure actual deltas for adaptive optimizers. Ratios of update norm to weight norm are group-dependent and unstable near zero-norm weights; no universal target is a pass/fail rule.

Interpret train/validation gaps after checking augmentation, dropout, label smoothing, EMA, reduction, and sampling. Matching metric names do not imply matching measurements. Split leakage and distribution mismatch require data fixes, not larger sweeps.

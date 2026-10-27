# Initial Training Points

These are conservative search priors adapted from the original hyper-tune table, **not newly benchmarked optima or current official recipes**. Prefer the repository/model's validated recipe, then nearby alternatives. Check the exact model, initialization, trainable subset, data, effective batch, optimizer implementation, and total budget before using a row. Do not infer a complete schedule from an LR value.

| Family | Initial optimizer/LR search region | Weight decay prior | Preserve/check |
|---|---|---|---|
| Classic CNN classification from scratch | SGD with momentum 0.9; LR roughly `1e-2`–`1e-1` | `1e-4`–`5e-4` | Batch and augmentation assumptions; warmup/schedule from the actual recipe |
| Small MLP/CNN exploratory run | AdamW around `3e-4`–`1e-3` | Include `0`, then `1e-4`–`1e-2` if useful | Tiny-subset optimization and data scaling |
| ViT/modern vision training | AdamW around `1e-4`–`1e-3`, depending on initialization/batch | Often `0.01`–`0.1` | Pretraining vs fine-tuning, warmup, augmentation, decay parameter groups |
| Transformer encoder fine-tuning | AdamW around `1e-5`–`5e-5` | Often `0.01` | Pretrained starting point, task head, limited data, warmup |
| Small randomly initialized transformer | AdamW around `3e-4`–`1e-3` as first probe | `0`–`0.1` depending on recipe | Do not automatically reuse pretrained encoder LR; verify attention/precision stability |
| Decoder full fine-tuning | AdamW around `5e-6`–`2e-5` | Recipe-dependent, often `0`–`0.1` | Catastrophic forgetting, effective token batch, length, task mix |
| LoRA/QLoRA fine-tuning | AdamW family around `5e-5`–`2e-4` as a first bracket | Often `0`–`0.01` | Rank/alpha scaling, target modules, trainable heads, optimizer precision |

For detector/segmentation variants, diffusion, GANs, large pretraining, and RL, start from the exact architecture/algorithm's documented recipe. Their objective/lifecycle and coupled parameters make a single generic table unreliable. State what is unknown and propose a small validation probe rather than inventing a confident default.

## Cross-cutting interpretation

- Effective batch includes device count and accumulation; variable-length data also changes tokens per update. LR scaling is a heuristic that must be checked, not an automatic multiplier for every optimizer.
- AdamW decay, explicit L2 penalties, and optimizer implementations are not interchangeable. Preserve grouping and exclusions from the baseline recipe.
- Warmup is measured in actual optimizer steps or another explicitly defined unit. Required warmup/schedules remain in cheap probes; compare meaningful post-warmup windows.
- Mixed precision and clipping affect stability. A finite full-precision diagnostic does not validate the intended low-precision run.
- LoRA rank, alpha, target modules, and trainable embeddings/heads change the optimization problem. Tune them after establishing a usable LR region unless one is the research intervention.
- Choose candidate counts from available compute. No fixed epoch, seed, or 100-step rule fits every task.

Numerical ranges are starting hypotheses. Report a chosen value together with its assumptions and the evidence that would move it up or down.

# Budgeted Search and Trial Records

## Define the resource envelope

Choose a budget unit meaningful for the task: optimizer updates, processed tokens/examples, accelerator-hours, wall time, or environment steps. Record hardware count and startup/evaluation/checkpoint overhead. Equal epochs can represent unequal compute across models or input lengths.

Use an explicit calculation before scheduling:

`planned cost = diagnostic probes + sum(candidates at stage × measured cost per candidate) + confirmation + overhead`

For example, a 4-hour accelerator budget could reserve 0.25 h for diagnostics, 6 × 0.25 h for screening, 2 × 0.75 h for refinement, and 0.75 h for confirmation/overhead. This is budget arithmetic, not a universal allocation. Measure throughput before promising that a step count fits. Unknown costs remain estimates until observed.

## Screen without changing the experiment

Prefer a small LR candidate set such as `[base/3, base, base*3]`, adjusted for the family and evidence. Hold other settings fixed first; introduce weight decay or another axis when optimization works. Avoid a Cartesian product simply because a search tool supports one.

Use comparable initialization/data order for cheap paired comparisons, then independent seeds for finalist robustness. Record reset/resume policy; optimizer/scheduler/RNG state makes a resumed run different from an independent restart.

Retain recipe-critical warmup, clipping, schedule, parameter groups, and preprocessing. Shortening a full cosine schedule changes the optimization trajectory; truncating a long schedule can leave all trials in warmup. Choose and report one fidelity policy, measure post-warmup behavior, and check whether short-run rankings transfer. The [Transformers schedule API](https://huggingface.co/docs/transformers/main_classes/optimizer_schedules) explicitly parameterizes warmup and total training steps for relevant schedules.

Promotion rules should use validation quality, uncertainty, stability, and resource cost. Compare at commensurate budgets and allow plausible slow starters to reach an informative stage. Predetermine nonfinite/divergence stops and a minimum observation window; pruning on noisy training loss alone can select the wrong recipe.

## Record and confirm

| Run/config ID | LR/WD and changed axes | Seed | Split IDs | Steps/tokens | Cost | Train/validation metric | Decision/reason |
|---|---|---|---|---|---|---|---|

Save effective configuration, code revision, initialization/checkpoint identity, trainable parameter groups, batch/precision, schedule horizon, curves, actual costs, and stop reason. Do not invent unobserved outcomes. Reuse the project's tracking system rather than imposing a new service.

Choose validation metric/direction and tie-breaking before selection. Match search effort across competing methods when comparing scientific claims, or expose unequal tuning as a limitation. Keep final test data outside all adaptive decisions. Freeze the selected recipe for confirmation; report individual seed results and dispersion when replicates exist, without implying one seed proves stability.

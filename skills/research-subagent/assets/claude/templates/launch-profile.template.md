# Launch profile
<!-- Personal. Lives at ~/.claude/launch-profile.md. Don't commit to a shared repo. -->
<!-- Claude fills this in with you on first use and proposes updates as it learns. -->

## 1. Machines
<!-- name | GPUs (model x count) | scheduler (none / Slurm / ...) | notes -->

## 2. How to connect
<!-- ssh alias, jump host, tunnel script, or "use skill <name>, see <path to SKILL.md>" -->

## 3. How to submit and get an id
<!-- per machine: nohup/tmux/queue file/sbatch..., where the PID or job id comes from -->

## 4. How to check a run is alive
<!-- ps / nvidia-smi / squeue / marker files / log heartbeat -->

## 5. Paths
<!-- writable dirs per machine, data locations, where run dirs go -->

## 6. GPU rules
<!-- which cards may be used, fixed GPU models for comparable runs -->

## 7. Never do
<!-- e.g. kill processes you didn't start, salloc/sbatch yourself, write outside project dir -->

## 8. Needs my confirmation
<!-- e.g. anything over N GPU-hours, any run on machine X -->

## Changelog
<!-- YYYY-MM-DD: what changed and why -->

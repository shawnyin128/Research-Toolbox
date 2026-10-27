# Research Toolbox

把科研中的**实验设计、代码工程、训练调参**放在同一个仓库维护。三个 skill 使用统一的 `research-*` 命名，各自可单独安装、独立调用，按实际任务组合，不要求每次完整走一遍流程。

| Skill | 原名称 | 负责什么 | 不负责什么 |
|---|---|---|---|
| [research-design](skills/research-design/SKILL.md) | research-fork-test | 把想法变成能区分机制的最小实验，给出预测、对照、停止与扩展条件 | 一般论文摘要、默认执行实验 |
| [research-code](skills/research-code/SKILL.md) | SAI-CC / sai-cc | 默认采用 SAI 规范，初始化或实质性重构科研代码，验证科学行为 | 每个小修复都触发全仓迁移 |
| [research-tune](skills/research-tune/SKILL.md) | hyper-tune | 在明确预算内诊断训练、筛选超参数、确认最终配置 | 推理采样参数、用测试集选参 |

Skill 指令用英文保持技术术语一致，按用户语言回答；仓库说明与迁移记录用中文。

## 默认的 SAI 结构与适用风险

`research-code` **默认带有 SAI 约定，不需要另行启用**：

- 参数类型、默认值、帮助与验证集中在 `hparam`；在统一应用入口解析。
- 能力模块使用同名组合入口，实际算法放在独立且内聚的实现文件。
- 实验、扫参、跨 seed 比较放在 scripts，复用维护中的算法。
- 顶层项目导入、明确的支持分支与异常 `else`、张量形状注释。
- 默认 uv / `.venv` / Ruff / 行为测试，分别检查可读性与科学行为。

结构固定也有代价：平铺的 `hparam`、`data` 等包名可能冲突；已有框架可能拥有自己的入口、配置与生命周期；小项目可能因为机械拆层产生过多文件。因此本版本已经支持**结构识别 + 每种结构独立指导文件**：

| 场景 | 指导文件 | 如何应用默认约定 |
|---|---|---|
| 新项目未指定结构 / 已是 SAI 平铺结构 | [SAI flat](skills/research-code/references/structures/sai.md) | 默认目标：`src/entrypoint.py`、`src/hparam/`、能力模块同名入口 |
| 已有或明确要求标准 Python 包结构 | [Namespaced package](skills/research-code/references/structures/package.md) | 在 `src/<package>/` 内落实同样规则，避免重复入口与包名污染 |
| 框架工程、插件工程、旧脚本集合 | [Existing architecture](skills/research-code/references/structures/existing.md) | 先映射实际职责/接口，再按范围迁移；明确不兼容点 |

结构识别改变约定的落位方式，不关闭 SAI 约定。明确的项目约束和用户决定优先；遇到实质冲突必须指出，而不是静默破坏框架或绕过默认规范。只读当前适用的一份结构指南，不加载所有指南。新增结构时增加一份指导文件，说明识别条件、责任映射、兼容风险和验证方法，再补路由与评估场景。

## 安装

安装脚本要求 **Python 3.12+**，仅使用标准库。每个 skill 运行时不依赖仓库脚本或另外两个 skill。

```bash
git clone git@github.com:shawnyin128/Research-Toolbox.git
cd Research-Toolbox
```

Codex，PowerShell（设置过 `CODEX_HOME` 时使用其 skills 目录）：

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
python scripts/install.py --dest "$skillRoot"
python scripts/install.py --dest "$skillRoot" --apply
```

Codex，Bash：

```bash
python scripts/install.py --dest "${CODEX_HOME:-$HOME/.codex}/skills"
python scripts/install.py --dest "${CODEX_HOME:-$HOME/.codex}/skills" --apply
```

Claude Code 可将目标改为 `~/.claude/skills`，项目级安装则使用项目的 `.claude/skills`。也可以直接复制 `skills/` 下选中的完整文件夹到客户端的 skill 发现目录。安装位置由客户端配置决定。

只安装一个：

```bash
python scripts/install.py --dest ~/.codex/skills --skills research-design --apply
```

默认只预览；已有目标默认拒绝覆盖。更新时先拉取仓库，再运行 `--update` 预览，确认后加 `--apply`。旧版保存在目标目录旁的 `<目录名>-backups/`，不混进可被发现的 skills 目录。每个 skill 单独替换，失败时尝试恢复该 skill 的原副本；批次不是跨 skill 的原子事务。

```bash
python scripts/install.py --dest ~/.codex/skills --update
python scripts/install.py --dest ~/.codex/skills --update --apply
```

安装脚本不会删除旧名字的 skill。为避免 `sai-cc` / `hyper-tune` 与新版本重复触发，请按 [迁移说明](docs/migration.md) 移出旧入口。重新开启会话，让客户端刷新 skill 列表。

## 使用

```text
用 $research-design 把这个机制假设变成一个最小辨别实验。
用 $research-code 整理这个科研仓库，默认采用 SAI 规范，先识别当前结构。
用 $research-tune 分析这个训练曲线，在 4 GPU-hours 内设计下一轮调参。
```

在支持斜杠调用的客户端，使用对应 `/research-design`、`/research-code`、`/research-tune`。自然语言触发也保留。

组合使用时，传递一份简短实验说明：研究问题、干预/固定对照、配置入口、数据角色与 split、指标、预算、停止/扩展规则。不要为了串联 skill 而增加文档仪式或强制执行额外阶段。

## 仓库组织与维护

```text
skills/             三个独立运行包：SKILL.md、agents、references、必要 assets
scripts/            安装与校验，不随 skill 安装
tests/              安装安全性、更新恢复、独立引用等行为测试
evaluations/        场景与评审标准；不是伪造的模型评测成绩
docs/               梳理、命名迁移、来源、验证记录
toolbox.json        版本、安装清单、旧名映射
```

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python -m unittest discover -s tests -v
```

GitHub Actions 在 Windows 和 Linux 上执行以上检查。静态检查验证打包一致性，不证明模型在真实研究任务中的表现；行为评测流程见 [evaluations](evaluations/README.md)。

- [三个原 skill 的梳理与优化](docs/audit.md)
- [命名与迁移](docs/migration.md)
- [来源与保留范围](docs/provenance.md)
- [本次验证记录](docs/validation.md)

当前版本没有新增许可证声明；保留来源记录，未替原始作者指定新的授权条款。

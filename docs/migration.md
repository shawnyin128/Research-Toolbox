# 命名与迁移

| 原包 | 新包 / 调用名 | 迁移原因 |
|---|---|---|
| `research-fork-test` | `research-design` | 保留机制辨别方法，用更直观的科研阶段命名 |
| `sai-cc`（仓库 SAI-CC） | `research-code` | 名称直接表达用途；SAI 约定默认保留 |
| `hyper-tune` | `research-tune` | 与 toolbox 命名一致，限定为训练调参 |

仓库统一为 `Research-Toolbox`；skill 文件夹、frontmatter 的 name、默认调用提示保持一致，UI 名称分别为 Research Design / Research Code / Research Tune。

## 本机迁移

1. 检查旧目录内是否有本地修改，先与当前仓库版本比较。
2. 安装新名字并确认独立引用校验通过。
3. 把旧名字的目录移到客户端 skill 发现目录以外留存；不要在 skills 目录内保留完整旧包或用旧名复制新包。
4. 更新常用提示里的 `$hyper-tune`、`$sai-cc`、`$research-fork-test`；重新开启会话确认新入口。

本次仓库整合不会修改全局安装目录，也不会删除、归档或改写两个旧 GitHub 仓库。安装脚本更新的是相同新名称的包；旧名称迁移由上述步骤处理，避免不知情覆盖个人修改。

## 内容兼容变化

- 默认 SAI 约定生效，并按平铺、标准包、已有框架三类结构落位。固定目录不能不加分析地套进任何框架。
- 保留同名组合入口、集中参数、参数化实验、形状注释与异常分支规范。减少无条件全仓审计、固定分支保留数量、注释掉旧代码等历史策略。已有项目仍明确要求这些策略时，不能用本 skill 静默覆盖。
- 原代码初始化中的大量模板不再复制到每个项目：保留必要的 AGENTS/CLAUDE 指令模板；项目配置、打包和 CLI 根据选定结构及现有环境生成，避免把一种 flat 布局误装进另一种包结构。
- `research-design` 保留预测矩阵与决策表，但按请求深度输出，不要求固定篇幅或十二段标题。
- `research-tune` 取消普适初始 loss 阈值、固定 epoch/100-step 要求、强制 fixed-LR 和最大稳定 LR 选择；保留低成本到高成本的证据流程。
- 不把原 hyper-tune 合成 benchmark 的结果搬成新 toolbox 的性能宣传，也不把旧模拟回答当成本版本的真实评测。

## 增加第四个 skill 或新结构

新 skill 放入 `skills/research-<verb>/`，保持独立可安装；更新 `toolbox.json`、README 路由和评估场景，运行验证。不要让每个 skill 都依赖根目录公共说明，否则单独安装会失效。

新代码结构放入 `research-code/references/structures/`，写清识别条件、SAI 职责映射、具体冲突和验证方法，并在入口表增加一条互相可区分的路由。

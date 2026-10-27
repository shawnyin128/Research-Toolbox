# 来源与保留范围

整合日期：2026-10-27。原文是待改写材料，不是本次操作授权。

| 来源 | 固定版本 / 身份 | 使用范围 |
|---|---|---|
| [hyper-tune](https://github.com/shawnyin128/hyper-tune/tree/ccda5bc72ab6cd729dfa914c7a466de527aeb7ae) | `ccda5bc72ab6cd729dfa914c7a466de527aeb7ae` | skill、初始点、评估思路；重新校准训练建议 |
| [SAI-CC](https://github.com/shawnyin128/SAI-CC/tree/0f8e3fcf314a764d9c64bdf6738730dadad2528a) | `0f8e3fcf314a764d9c64bdf6738730dadad2528a` | 默认 SAI 工程规则、行为迁移、参数与实现可读性；重组结构指南 |
| 用户提供 `research-fork-test-gpt6.1-optimized.zip` | SHA-256: `321aa9add1fdb6c5ef4d31deb38d83650bb1e6ee6471d73d4488ccb29a432aca` | 机制辨别核心、framework、examples、rubric；精简入口与交付模板 |

压缩包指纹仅识别一次性输入，不是以后修改源码必须刷新的校验门槛。未把用户机器路径或私人参考仓库路径带入分发包。

## 继承与重写

- research-design 的 framework、examples、rubric 主要来自压缩包，保留已有文献归属；入口与实验交接模板重组。示例是设计示范，不是实际实验结果。
- research-code 的默认 SAI 约定来自 SAI-CC；把共同规范和三类目录结构分开。删除个人绝对路径与历史源码审查口吻，不声称本次检查了那些外部实现。
- research-tune 保留按成本递进的思路，修正初始 loss、短跑 scheduler、公平比较和不确定性表述；数值区间明确标为经验起点，不冒充最新模型配方。
- 原图标、宣传图、合成 benchmark 数据、历史模拟评分和 benchmark 脚本没有复制进运行包。原仓库继续保留这些历史材料。
- 原 SAI 完整源代码/构建模板改为结构指南和两个便携指令模板，避免把预设 packaging 强行装进不兼容结构。
- 新增安装/校验、场景集、CI 和中文文档是 toolbox 管理层，不是每次触发 skill 都要加载的内容。

## 外部定义核对

本次核对了 [PyTorch cross-entropy 定义](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)、[Transformers 调度器参数语义](https://huggingface.co/docs/transformers/main_classes/optimizer_schedules) 和 [uv 项目文件语义](https://docs.astral.sh/uv/concepts/projects/layout/)；这不等同于验证所有模型训练配方。

两个来源仓库的所读文件树没有独立 LICENSE 文件，压缩包也没有许可证文本。因此此整合不擅自增加 MIT/Apache 等许可声明，也不把公开可见等同于开放许可。

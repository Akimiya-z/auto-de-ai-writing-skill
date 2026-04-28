# Author Notes

- 来源文件：`examples/source_brief.md`，用于定义示例项目需求。
- AI 初稿：`examples/original.md`，根据 source brief 生成，保留典型 AI 口吻用于测试。
- 修改稿：`examples/revised.md`，由 `adversarial_loop.py` 自动生成，用来展示 A/B/C 闭环效果。
- 项目定位：做一个 `auto-de-ai-writing-skill`，流程包含 AI 味检测、真实材料补充、自动改写、复测和报告输出。
- 技术实现：Python 脚本包括 `ai_rate.py`、`analyze_text.py`、`rewrite_prompt.py`、`auto_rewrite.py`、`review_text.py`、`adversarial_loop.py`、`voice_profile.py` 和 `make_report.py`。
- 独立审查：`review_text.py` 检查来源材料覆盖、文本质量、局限说明和指标投机，专门拦截堆文件名或堆数字的改写稿。
- 复现约束：不默认运行本地大模型，因为安装 `torch`、下载模型和处理硬件差异会提高门槛。
- 自动化要求：不依赖手动网页截图；优先支持 Sapling API；没有 API key 时使用本地规则评分。
- 关键判断：检测器分数不能证明文本作者，但可以作为项目内的实验指标。

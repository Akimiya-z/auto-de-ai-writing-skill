# 示例文件说明

这组示例用于展示项目的完整输入、改写提示和评测报告。

| 文件 | 作用 |
|---|---|
| `source_brief.md` | 示例需求说明，作为文本来源 |
| `original.md` | 根据 source brief 生成的 AI 初稿，用来测试 AI-like 率 |
| `author_notes.md` | 作者补充材料，包括项目方案、技术选择和限制 |
| `voice_sample.md` | 作者语气样本，用于 voice calibration |
| `rewrite_prompt.md` | 根据原文、来源、作者材料和语气样本自动生成的改写提示 |
| `revised.md` | A/B 闭环自动生成的修改稿 |
| `report.md` | 自动生成的 AI 率前后对比报告和迭代记录 |

复现实验：

```bash
python scripts/run_pipeline.py
```

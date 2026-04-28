# 借鉴的类似项目和设计取舍

本项目借鉴的是结构和工程做法，不复制具体文本。

## 参考项目

1. `blader/humanizer`
   - 链接：https://github.com/blader/humanizer
   - 借鉴点：把 AI 味识别、改写和复查拆成流程，减少一次性同义词替换带来的随意性。
   - 本项目对应实现：`analyze_text.py` 的模式命中、`rewrite_prompt.py` 的结构化改写提示、`make_report.py` 的复查报告。

2. `Aboudjem/humanizer-skill`
   - 链接：https://github.com/Aboudjem/humanizer-skill
   - 借鉴点：skill 本身应该提供 detect/rewrite/edit 这类明确模式，并包含可操作的 pattern catalog。
   - 本项目对应实现：`PATTERN_CATALOG`、高风险句子列表、模式 ID、修改建议。

3. `glebis/claude-skills` 中的 de-ai 思路
   - 链接：https://github.com/glebis/claude-skills
   - 借鉴点：先收集上下文和作者材料，再改写；质量优先于单纯规避检测。
   - 本项目对应实现：`source_brief.md`、`author_notes.md`、`voice_sample.md` 和报告中的“文章来源”。

4. Wikipedia `Signs of AI writing`
   - 链接：https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
   - 借鉴点：AI 写作痕迹不只是词语问题，还包括结构、语气、证据缺失和模板化风格。
   - 本项目对应实现：内容、结构、语言、证据、voice、style 六类指标。

## 本项目和普通 humanizer 的区别

- 面向中文项目说明、技术报告和长文本修改，优先覆盖课程作业里的中文写作场景。
- 默认不用本地大模型，降低复现成本。
- 输出报告必须说明文章来源和作者补充材料。
- 分数只作为实验指标，不宣称能证明作者身份。
- 保留可选 Sapling API，但没有 API key 时仍能完整运行。

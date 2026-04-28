# 改写任务

请把下面的 AI 初稿改成一篇更像真实作者写出的中文项目说明。目标不是编造经历，也不是故意制造病句，而是加入真实来源、作者补充材料、项目实现细节和个人取舍，让文本更具体、更可解释。

## 当前检测结果

- AI-like Rate：59.45%

## 主要命中模式

- P01 意义拔高：5 次；建议：把宏大评价改成具体结果、数据、文件或来源要求。
- P02 模板化开头结尾：3 次；建议：直接从任务、材料、项目选择或问题开始写。
- P03 机械连接词：6 次；建议：保留真实逻辑关系，删除没有推理作用的排序词。
- P04 空泛抽象词：8 次；建议：替换为脚本名、指标、文件、案例或具体动作。
- P05 二元平衡套话：2 次；建议：改成一个明确取舍：为什么这样做，放弃了什么。

## 高风险句子

- `100.0` 随着人工智能技术的快速发展，AI 生成文本正在深刻改变用户的写作方式和内容生产方式。（意义拔高、模板化开头结尾、模板化开头或总结、长句缺少具体细节、缺少作者痕迹；模式：P01、P02、P07）
- `100.0` 在当今内容生产背景下，如何降低 AI 生成文字的 AI 率，已经成为一个具有重要意义的问题。（意义拔高、模板化开头结尾、模板化开头或总结、抽象词密集、长句缺少具体细节、缺少作者痕迹；模式：P01、P02、P07）
- `100.0` 一方面，它能够保存完整的处理流程，另一方面，它也能够展示项目的技术特点和应用价值。（意义拔高、机械连接词、空泛抽象词、二元平衡套话、抽象词密集、连接词堆叠；模式：P01、P03、P04、P05）
- `99.0` 该方法能够有效降低 AI 生成文本的 AI 率，并充分体现文本优化效果，对于中文写作辅助项目具有重要意义。（意义拔高、空泛抽象词、模板化开头或总结、抽象词密集；模式：P01、P04）
- `58.0` 首先，可以利用 AI 工具对生成文本进行全面分析，从而发现文本中存在的问题。（机械连接词、空泛抽象词、长句缺少具体细节、缺少作者痕迹；模式：P03、P04、P07）
- `58.0` 此外，还可以结合不同的检测方式，对修改前后的结果进行对比，从而进一步提升文本质量。（机械连接词、空泛抽象词、长句缺少具体细节、缺少作者痕迹；模式：P03、P04、P07）

## 文章来源

# Source Brief: Auto De-AI Writing Skill

This source brief defines the sample scenario used by the repository. It is intentionally generic so the project can be published as a normal GitHub project.

## Goal

Build a reusable skill-style workflow that can take an AI-generated Chinese draft, identify AI-flavored writing patterns, guide a more concrete revision, and generate a reproducible before/after report.

## Requirements

- Provide a GitHub-ready project structure.
- Analyze AI-generated Chinese text automatically.
- Calculate a reproducible AI-like rate without requiring a local large model.
- Generate a structured rewrite prompt based on source material, author notes, and voice sample.
- Produce a Markdown report with before/after score, reduction formula, pattern hits, high-risk sentences, and limitations.
- Keep optional third-party API support, but make the default path runnable with only Python standard library.

## Evaluation Target

The demo should show a measurable reduction from the original draft to the revised text:

$$
reduction=\frac{before-after}{before}\times100\%
$$

## 作者补充材料

# Author Notes

- 来源文件：`examples/source_brief.md`，用于定义示例项目需求。
- AI 初稿：`examples/original.md`，根据 source brief 生成，保留典型 AI 口吻用于测试。
- 修改稿：`examples/revised.md`，加入项目文件、实现选择和个人判断后形成。
- 项目定位：做一个 `auto-de-ai-writing-skill`，不是只替换同义词，而是检测 AI 味、补充真实材料、生成改写提示并输出报告。
- 技术实现：Python 脚本包括 `ai_rate.py`、`analyze_text.py`、`rewrite_prompt.py`、`voice_profile.py` 和 `make_report.py`。
- 复现约束：不默认运行本地大模型，因为安装 `torch`、下载模型和处理硬件差异会提高门槛。
- 自动化要求：不依赖手动网页截图；优先支持 Sapling API；没有 API key 时使用本地规则评分。
- 关键判断：检测器分数不能证明文本作者，但可以作为项目内的实验指标。

## Voice Profile

- 平均句长：35.67
- 句长变异系数：0.4297
- 作者痕迹数量：4
- 高频词：API、可复现、检测、AI-like、Rate、catalog、pattern、skill
- 风格要求：保留第一人称、文件名、脚本名、命令和真实取舍。

## 改写要求

1. 保留原文主题和任务要求；如果 source brief 中有主题，以 source brief 为准。
2. 明确说明文本来源来自 source brief 或用户提供的材料。
3. 加入可核验的材料，例如项目文件、脚本名、命令、指标、案例、数据或实现取舍。
4. 删除空泛套话，例如“随着技术发展”“具有重要意义”“综上所述”。
5. 不要编造 API 结果；没有 API key 时只写本地 AI-like Rate。
6. 结尾必须说明检测分数只是实验指标，不是作者身份证明。

## AI 初稿

# 如何通过 GitHub 项目降低 AI 生成文本的 AI 率

随着人工智能技术的快速发展，AI 生成文本正在深刻改变用户的写作方式和内容生产方式。在当今内容生产背景下，如何降低 AI 生成文字的 AI 率，已经成为一个具有重要意义的问题。通过 GitHub 项目、skills 以及相关自动化方法，可以有效提升文本的人类化程度，并充分体现降重效果。

首先，可以利用 AI 工具对生成文本进行全面分析，从而发现文本中存在的问题。其次，可以通过自动化程序对文本进行优化，使语言表达更加自然，内容结构更加合理。此外，还可以结合不同的检测方式，对修改前后的结果进行对比，从而进一步提升文本质量。

在具体实现过程中，GitHub 项目可以发挥重要作用。一方面，它能够保存完整的处理流程，另一方面，它也能够展示项目的技术特点和应用价值。通过构建一个 skill，可以实现从文本检测、内容分析到自动改写的完整流程。这种方式不仅能够提高效率，也能够增强项目的规范性和完整性。

然而，AI 生成文本的降重并不是简单的文字替换，而是需要综合考虑表达方式、逻辑结构和内容质量。只有在合理使用 AI 工具的基础上，才能更好地降低 AI 率，并避免文本过于机械化和模板化的问题。因此，自动化降 AI 率方法具有一定的现实意义。

综上所述，通过构建 GitHub 项目和 skill，可以形成从检测、分析、改写到报告生成的完整闭环。该方法能够有效降低 AI 生成文本的 AI 率，并充分体现文本优化效果，对于中文写作辅助项目具有重要意义。

# Auto De-AI Writing Skill

Auto De-AI Writing Skill 是一个面向中文文本的 AI-like 率检测、改写提示生成和前后对比报告工具。它把常见 humanizer/de-ai skill 的做法整理成一个可复现的 GitHub 项目：先识别 AI 味模式，再结合来源材料、作者补充材料和 voice sample 生成改写提示，最后输出 Markdown 评测报告。

项目默认不依赖本地大模型，也不需要手动网页截图。没有 API key 时，只用 Python 标准库即可运行本地 `AI-like Rate`；如果配置 `SAPLING_API_KEY`，则优先调用 Sapling AI Detector API。

## 项目报告摘要

很多 AI 初稿的问题不是单个词不自然，而是整篇文章呈现出固定模式：模板化开头、空泛拔高、机械连接词、二元平衡套话、缺少真实来源和作者判断。单纯同义词替换通常无法解释“为什么文本更像人写”，也很难复现实验结果。

本项目把“降 AI 味”拆成可验证的工程流程：

1. 计算原文 AI-like 率。
2. 标记命中的 AI 写作模式和高风险句子。
3. 读取 source brief、author notes 和 voice sample。
4. 生成结构化 rewrite prompt。
5. 对修改稿再次检测。
6. 自动生成包含公式、模式表和限制说明的 Markdown 报告。

示例运行结果：

| 指标 | 修改前 | 修改后 | 降幅 |
|---|---:|---:|---:|
| AI-like Rate | 59.45% | 21.66% | 63.57% |

降幅计算：

\[
reduction=\frac{before-after}{before}\times100\%
\]

本示例对应：

\[
\frac{59.45-21.66}{59.45}\times100\%=63.57\%
\]

## 功能

- 自动计算文本 AI-like 率。
- 支持可选 Sapling AI Detector API。
- 无 API key 时自动回退到本地规则评分。
- 识别中文 AI 味模式，包括模板化开头、空泛词、机械连接词、二元平衡套话和作者痕迹不足。
- 生成结构化 rewrite prompt，可直接交给任意 AI 写作工具执行修改。
- 支持 voice sample，用于保留作者语气、文件名、命令和项目取舍。
- 自动生成 Markdown 报告，包括前后分数、降幅公式、命中模式、风险句子、来源材料和限制说明。

## 快速开始

```bash
git clone <your-repo-url>
cd auto-de-ai-writing-skill
python scripts/run_pipeline.py
```

一键流程会生成或更新：

- `examples/rewrite_prompt.md`
- `examples/report.md`

也可以分步运行：

```bash
python scripts/ai_rate.py examples/original.md
python scripts/analyze_text.py examples/original.md
python scripts/rewrite_prompt.py examples/original.md \
  --notes examples/author_notes.md \
  --source examples/source_brief.md \
  --voice examples/voice_sample.md \
  --out examples/rewrite_prompt.md
python scripts/make_report.py examples/original.md examples/revised.md \
  --notes examples/author_notes.md \
  --source examples/source_brief.md \
  --out examples/report.md
```

如果要启用 Sapling API：

```bash
export SAPLING_API_KEY="your-api-key"
python scripts/ai_rate.py examples/original.md --provider auto
```

## 方法设计

### 1. Pattern Catalog

`scripts/analyze_text.py` 内置 `PATTERN_CATALOG`，把 AI 味拆成可解释模式：

| ID | 类别 | 模式 | 处理建议 |
|---|---|---|---|
| P01 | content | 意义拔高 | 把宏大评价改成具体结果、数据、文件或来源要求 |
| P02 | structure | 模板化开头结尾 | 直接从任务、材料、项目选择或问题开始 |
| P03 | structure | 机械连接词 | 删除没有推理作用的排序词 |
| P04 | language | 空泛抽象词 | 替换为脚本名、指标、文件、案例或具体动作 |
| P05 | rhetoric | 二元平衡套话 | 改成明确取舍：为什么这样做，放弃了什么 |
| P06 | evidence | 模糊归因 | 补充来源，或删掉无法证明的归因 |
| P07 | voice | 作者痕迹不足 | 加入来源背景、个人判断、项目取舍或调试记录 |
| P08 | style | 句长过于均匀 | 混合短句和长句，避免模板节奏 |

### 2. AI-like Rate

本地评分不是通用 AI 检测器，而是一个项目内实验指标。它综合以下维度：

\[
AI\text{-}like\ Rate = f(T,V,C,U,D,A)
\]

其中：

- \(T\)：模板表达得分
- \(V\)：空泛词得分
- \(C\)：连接词和重复连接词得分
- \(U\)：句长均匀度得分
- \(D\)：具体细节缺失得分
- \(A\)：作者痕迹缺失得分

第三方 API 可用时：

\[
AI\ Rate = score \times 100\%
\]

### 3. Voice Calibration

`scripts/voice_profile.py` 会从 `examples/voice_sample.md` 中提取：

- 平均句长
- 句长变异系数
- 作者痕迹数量
- 高频技术词
- 风格约束

这些信息会进入 `rewrite_prompt.md`，用于限制改写方向：保留第一人称、文件名、脚本名、命令和真实取舍。

### 4. Rewrite Prompt

`scripts/rewrite_prompt.py` 会把原文检测结果、source brief、author notes 和 voice profile 合成一个结构化提示。提示中包含：

- 当前 AI-like Rate
- 主要命中模式
- 高风险句子
- 来源材料
- 作者补充材料
- voice profile
- 不编造 API 结果和来源的约束

### 5. Report Generation

`scripts/make_report.py` 会输出 `examples/report.md`，包含：

- 原始 AI-like 率
- 修改后 AI-like 率
- 降幅公式
- 指标变化表
- 类别分数变化
- 原文命中模式
- 高风险句子
- 来源材料和作者补充材料
- 原始 JSON 结果
- 限制说明

## 项目结构

```text
auto-de-ai-writing-skill/
├── README.md
├── SKILL.md
├── LICENSE
├── .gitignore
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── ai_rate.py
│   ├── analyze_text.py
│   ├── make_report.py
│   ├── rewrite_prompt.py
│   ├── run_pipeline.py
│   └── voice_profile.py
├── references/
│   ├── ai_tells_zh.md
│   ├── inspiration.md
│   └── workflow.md
└── examples/
    ├── README.md
    ├── source_brief.md
    ├── original.md
    ├── author_notes.md
    ├── voice_sample.md
    ├── rewrite_prompt.md
    ├── revised.md
    └── report.md
```

## 示例说明

示例文件采用通用项目场景，不包含私人背景信息：

| 文件 | 作用 |
|---|---|
| `examples/source_brief.md` | 示例需求来源 |
| `examples/original.md` | 根据 brief 生成的 AI 初稿 |
| `examples/author_notes.md` | 作者补充材料和实现取舍 |
| `examples/voice_sample.md` | 作者语气样本 |
| `examples/rewrite_prompt.md` | 自动生成的改写提示 |
| `examples/revised.md` | 修改稿 |
| `examples/report.md` | 自动生成的评测报告 |

## 参考与借鉴

本项目借鉴成熟 humanizer/de-ai skill 的工程结构，而不是复制具体文本：

- `blader/humanizer`：检测、改写、复查分阶段。
- `Aboudjem/humanizer-skill`：pattern catalog 和明确任务模式。
- `glebis/claude-skills` 中的 de-ai 思路：先收集上下文和作者材料，再执行改写。
- Wikipedia `Signs of AI writing`：AI 写作痕迹包括结构、证据、语气和模板化表达。

详细取舍见 `references/inspiration.md`。

## 限制说明

- 本地 `AI-like Rate` 是启发式项目指标，不等于平台或商业检测器的结论。
- 第三方检测器结果也只能作为概率化参考，不能证明文本一定由 AI 或人类撰写。
- 项目不会编造来源、经历、数据或 API 返回值。
- 更好的降 AI 味方式不是制造病句，而是补充真实来源、具体实现和作者判断。

## License

MIT License. See `LICENSE`.

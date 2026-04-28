# Auto De-AI Writing Skill

一个可复现的中文 AI 文本改写评测项目：输入 AI 初稿、来源材料和作者补充材料，自动分析 AI 味特征，生成改写提示，并输出修改前后的 AI-like 率对比报告。

## 一句话说明

这个项目不是简单的同义词替换器。它把“降低 AI 味”拆成四步：

1. 检测：给 AI 初稿计算 `AI-like Rate`。
2. 定位：指出哪些句子像 AI 写的，以及命中了哪些模式。
3. 改写提示：结合来源材料、作者笔记和语气样本生成 rewrite prompt。
4. 复查：对修改稿再次评分，并生成 Markdown 报告。

默认模式不需要本地大模型，也不需要网页截图。只要有 Python 标准库就能跑完整示例；如果配置 `SAPLING_API_KEY`，脚本会优先调用 Sapling AI Detector API。

## 输入和输出

| 类型 | 文件 | 说明 |
|---|---|---|
| 输入 | `examples/original.md` | AI 初稿 |
| 输入 | `examples/source_brief.md` | 文本来源和任务背景 |
| 输入 | `examples/author_notes.md` | 作者补充材料、实现选择和限制 |
| 输入 | `examples/voice_sample.md` | 作者语气样本 |
| 中间产物 | `examples/rewrite_prompt.md` | 自动生成的结构化改写提示 |
| 输出 | `examples/revised.md` | 修改稿 |
| 输出 | `examples/report.md` | 自动生成的前后对比报告 |

## 快速运行

```bash
git clone https://github.com/Akimiya-z/auto-de-ai-writing-skill.git
cd auto-de-ai-writing-skill
python scripts/run_pipeline.py
```

运行后会更新：

- `examples/rewrite_prompt.md`
- `examples/report.md`

分步运行：

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
  --generated-at "2026-04-28 00:00:00" \
  --out examples/report.md
```

`--generated-at` 只是为了让仓库示例可复现。处理自己的文本时可以省略它，报告会使用当前时间。

## 示例结果

当前示例把一篇模板化 AI 初稿改成包含项目文件、脚本分工、技术取舍和限制说明的版本。自动报告给出的结果是：

| 指标 | 修改前 | 修改后 | 降幅 |
|---|---:|---:|---:|
| AI-like Rate | 59.45% | 21.55% | 63.75% |

降幅公式：

$$
reduction=\frac{before-after}{before}\times100\%
$$

本示例：

$$
\frac{59.45-21.55}{59.45}\times100\%=63.75\%
$$

报告还会列出：

- 命中的 AI 写作模式。
- 高风险句子。
- 修改前后各类指标变化。
- 来源材料和作者补充材料。
- 原始 JSON 结果。
- 检测分数的限制说明。

## 这个项目具体做了什么

### 1. 计算 AI-like Rate

`scripts/ai_rate.py` 提供统一检测入口：

- 有 `SAPLING_API_KEY`：优先使用 Sapling API。
- 没有 API key：使用本地规则评分。

本地评分是项目内实验指标，不等于商业检测器结论。它综合以下维度：

| 维度 | 含义 |
|---|---|
| `template_score` | 模板化开头、总结、套话 |
| `vague_score` | 空泛抽象词密度 |
| `connector_score` | 机械连接词和重复连接词 |
| `uniformity_score` | 句长过于均匀 |
| `detail_gap_score` | 缺少具体细节 |
| `author_gap_score` | 缺少作者痕迹 |

### 2. 标记 AI 写作模式

`scripts/analyze_text.py` 内置 `PATTERN_CATALOG`。它不是只数关键词，而是把问题分成可解释模式：

| ID | 类别 | 模式 | 建议 |
|---|---|---|---|
| P01 | content | 意义拔高 | 把宏大评价改成具体结果、数据、文件或来源要求 |
| P02 | structure | 模板化开头结尾 | 直接从任务、材料、项目选择或问题开始 |
| P03 | structure | 机械连接词 | 删除没有推理作用的排序词 |
| P04 | language | 空泛抽象词 | 替换为脚本名、指标、文件、案例或具体动作 |
| P05 | rhetoric | 二元平衡套话 | 改成明确取舍：为什么这样做，放弃了什么 |
| P06 | evidence | 模糊归因 | 补充来源，或删掉无法证明的归因 |
| P07 | voice | 作者痕迹不足 | 加入来源背景、个人判断、项目取舍或调试记录 |
| P08 | style | 句长过于均匀 | 混合短句和长句，避免模板节奏 |

### 3. 生成改写提示

`scripts/rewrite_prompt.py` 会把四类信息合成一个 rewrite prompt：

- 原文 AI-like Rate。
- 命中模式和高风险句子。
- `source_brief.md` 中的来源背景。
- `author_notes.md` 中的作者材料。
- `voice_sample.md` 中提取的语气特征。

生成的提示可以直接交给任意 AI 写作工具使用。

### 4. 生成前后对比报告

`scripts/make_report.py` 会生成 `examples/report.md`。报告不是只给一个分数，而是解释分数从哪里来、哪些模式减少了、哪些具体细节增加了。

## 如何用自己的文本

把自己的材料按下面方式替换即可：

1. 把 AI 初稿放到 `examples/original.md`。
2. 把来源材料或任务背景放到 `examples/source_brief.md`。
3. 把个人观点、真实材料、项目细节放到 `examples/author_notes.md`。
4. 可选：把自己的写作样本放到 `examples/voice_sample.md`。
5. 用 `python scripts/rewrite_prompt.py ...` 生成改写提示。
6. 根据提示写出 `examples/revised.md`。
7. 用 `python scripts/make_report.py ...` 生成报告。

## 可选：接入 Sapling API

```bash
export SAPLING_API_KEY="your-api-key"
python scripts/ai_rate.py examples/original.md --provider auto
```

没有 API key 时，项目会自动回退到本地 `AI-like Rate`，所以示例不会因为缺少外部服务而跑不起来。

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

## 设计参考

本项目借鉴成熟 humanizer/de-ai skill 的工程结构，而不是复制具体文本：

- `blader/humanizer`：检测、改写、复查分阶段。
- `Aboudjem/humanizer-skill`：pattern catalog 和明确任务模式。
- `glebis/claude-skills` 中的 de-ai 思路：先收集上下文和作者材料，再执行改写。
- Wikipedia `Signs of AI writing`：AI 写作痕迹包括结构、证据、语气和模板化表达。

详细说明见 `references/inspiration.md`。

## 限制

- `AI-like Rate` 是启发式项目指标，不是权威 AI 检测结论。
- 第三方检测器结果也只能作为概率参考，不能证明文本一定由 AI 或人类撰写。
- 项目不会编造来源、经历、数据或 API 返回值。
- 真正有效的“降 AI 味”不是制造病句，而是补充真实来源、具体实现和作者判断。

## License

MIT License. See `LICENSE`.

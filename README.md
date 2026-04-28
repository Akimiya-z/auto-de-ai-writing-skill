# Auto De-AI Writing Skill

[![test](https://github.com/Akimiya-z/auto-de-ai-writing-skill/actions/workflows/test.yml/badge.svg)](https://github.com/Akimiya-z/auto-de-ai-writing-skill/actions/workflows/test.yml)

这是一个课程作业项目。它要解决的问题是：给定一段中文 AI 初稿，自动检测其中的 AI 写作痕迹，自动改写高风险部分，再复测并生成修改前后的对比报告。

项目不把“降 AI 率”做成简单的同义词替换，而是拆成两个独立模块：

- A：检测器，给文本计算一个可复现的 `AI-like Rate`。
- B：改写器，根据检测结果、来源材料和作者补充信息生成修改稿。

完整流程是：

```text
original.md
-> A: detect
-> B: rewrite
-> A: detect again
-> compare
-> report.md
```

当修改稿低于目标阈值，或者继续改写收益很小时，循环停止。

## 作业目标

| 作业要求 | 本项目实现 |
|---|---|
| 自动测 AI 率 | `scripts/ai_rate.py` 计算统一的 `AI-like Rate` |
| 找出 AI 味来自哪里 | `scripts/analyze_text.py` 输出命中模式和高风险句子 |
| 自动降低 AI-like Rate | `scripts/adversarial_loop.py` 执行检测-改写-复测闭环 |
| 展示前后效果 | `examples/report.md` 生成分数、降幅、特征变化和迭代记录 |
| 能复现 | 默认只依赖 Python 标准库，运行 `python scripts/run_pipeline.py` 即可 |

## Quick Start

```bash
git clone https://github.com/Akimiya-z/auto-de-ai-writing-skill.git
cd auto-de-ai-writing-skill
python scripts/run_pipeline.py
```

运行后会更新三个示例文件：

- `examples/rewrite_prompt.md`
- `examples/revised.md`
- `examples/report.md`

当前示例输出：

```text
original: 59.45%
revised: 9.33%
stop: target reached
```

也就是示例文本从 `59.45%` 降到 `9.33%`，达到默认阈值 `25%`。

## 方法设计

本项目把所谓“AI 率”定义成项目内的可复现实验指标，而不是权威鉴定结论。

本地检测器主要看六类信号：

| 组件 | 含义 |
|---|---|
| `template_score` | 模板化开头、结尾、套话 |
| `vague_score` | 空泛抽象词密度 |
| `connector_score` | 机械连接词和重复连接词 |
| `uniformity_score` | 句长是否过于平均 |
| `detail_gap_score` | 是否缺少具体材料 |
| `author_gap_score` | 是否缺少作者判断和写作痕迹 |

简化公式是：

$$
AI\text{-}like\ Rate=f(T,V,C,U,D,A)
$$

其中 \(T,V,C,U,D,A\) 分别对应模板表达、空泛词、连接词、句长均匀度、细节缺失和作者痕迹缺失。

前后降幅按下面公式计算：

$$
\text{reduction}=\frac{\text{before}-\text{after}}{\text{before}}\times100\%
$$

示例结果：

$$
\frac{59.45-9.33}{59.45}\times100\%=84.31\%
$$

循环停止条件包括：

$$
S_t \leq \tau
$$

或：

$$
\Delta_t=S_{t-1}-S_t<\epsilon
$$

或：

$$
t \geq T_{\max}
$$

其中 \(S_t\) 是第 \(t\) 轮修改后的 AI-like Rate，\(\tau\) 是目标阈值，\(\epsilon\) 是最小有效降幅，\(T_{\max}\) 是最大轮数。

## 分步运行

如果不想直接运行完整 pipeline，可以按步骤执行：

```bash
python scripts/ai_rate.py examples/original.md
python scripts/analyze_text.py examples/original.md
```

生成改写提示：

```bash
python scripts/rewrite_prompt.py examples/original.md \
  --notes examples/author_notes.md \
  --source examples/source_brief.md \
  --voice examples/voice_sample.md \
  --out examples/rewrite_prompt.md
```

运行 A/B 闭环：

```bash
python scripts/adversarial_loop.py \
  --original examples/original.md \
  --notes examples/author_notes.md \
  --source examples/source_brief.md \
  --voice examples/voice_sample.md \
  --target-rate 25 \
  --max-rounds 5 \
  --provider local \
  --out examples/revised.md \
  --report examples/report.md
```

如果设置了 `SAPLING_API_KEY`，`scripts/ai_rate.py` 可以优先调用 Sapling AI Detector API；没有 key 时会自动使用本地规则评分。

## 示例文件

| 文件 | 作用 |
|---|---|
| `examples/source_brief.md` | 作业需求和示例来源 |
| `examples/original.md` | 待处理的中文 AI 初稿 |
| `examples/author_notes.md` | 作者补充材料和实现说明 |
| `examples/voice_sample.md` | 作者语气样本 |
| `examples/rewrite_prompt.md` | 根据检测结果生成的改写提示 |
| `examples/revised.md` | A/B 闭环自动生成的修改稿 |
| `examples/report.md` | 修改前后对比报告 |

报告中包含：

- 原始 AI-like Rate。
- 修改后 AI-like Rate。
- 降幅公式和计算过程。
- 命中的 AI 写作模式。
- 原文高风险句子。
- 本地特征变化。
- A/B 迭代记录。
- 局限说明。

## 核心脚本

| 脚本 | 作用 |
|---|---|
| `scripts/ai_rate.py` | 统一检测入口，输出 `AI-like Rate` |
| `scripts/analyze_text.py` | 分析模板表达、空泛词、连接词、高风险句子 |
| `scripts/rewrite_prompt.py` | 生成结构化改写提示 |
| `scripts/auto_rewrite.py` | 本地规则改写器 B |
| `scripts/adversarial_loop.py` | 串联 A/B/A 循环 |
| `scripts/make_report.py` | 生成 Markdown 对比报告 |
| `scripts/voice_profile.py` | 从作者样本提取轻量风格信息 |
| `scripts/run_pipeline.py` | 一键运行示例流程 |

## 测试

```bash
python -m py_compile scripts/*.py
python -m unittest discover -s tests -v
```

仓库包含 GitHub Actions，push 和 pull request 时会自动运行同样的检查。

## 作为 Skill 使用

这个仓库也是一个 Codex/Claude 风格的 skill：

- 核心说明：`SKILL.md`
- UI 元数据：`agents/openai.yaml`
- 工作流细节：`references/workflow.md`
- AI 写作模式表：`references/ai_tells_zh.md`

触发场景是：用户给出 AI 初稿，希望分析 AI 味、生成改写提示、保留作者材料，并输出修改前后的可解释报告。

## 项目结构

```text
auto-de-ai-writing-skill/
├── README.md
├── SKILL.md
├── LICENSE
├── .github/workflows/test.yml
├── agents/openai.yaml
├── examples/
│   ├── source_brief.md
│   ├── original.md
│   ├── author_notes.md
│   ├── voice_sample.md
│   ├── rewrite_prompt.md
│   ├── revised.md
│   └── report.md
├── references/
│   ├── ai_tells_zh.md
│   ├── inspiration.md
│   └── workflow.md
├── scripts/
│   ├── ai_rate.py
│   ├── analyze_text.py
│   ├── adversarial_loop.py
│   ├── auto_rewrite.py
│   ├── make_report.py
│   ├── rewrite_prompt.py
│   ├── run_pipeline.py
│   └── voice_profile.py
└── tests/test_pipeline.py
```

## 限制

本项目的 `AI-like Rate` 是项目内实验指标，不是学校或商业平台的权威检测结论。第三方检测器本身也只能给概率参考，不能证明文本一定由 AI 或人类撰写。

本地 `auto_rewrite.py` 是为了让作业能离线复现的 baseline，不等于最终高质量人工稿。正式提交文本时，仍建议结合 `examples/rewrite_prompt.md` 做人工检查和二次精修。

本项目不承诺通过任何第三方 AI 检测器，也不会编造来源、经历、引用或 API 结果。

## License

MIT License. See `LICENSE`.

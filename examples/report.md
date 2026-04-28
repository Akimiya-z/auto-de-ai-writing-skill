# AI 率前后对比报告

生成时间：2026-04-28 00:00:00

## 结论

- 原始 AI 率：59.45%
- 修改后 AI 率：9.33%
- 降幅：84.31%
- 原文文件：`examples/original.md`
- 修改稿文件：`examples/revised.md`
- 原文 provider: `local-ai-like`；修改后 provider: `local-ai-like`。

降幅公式：

$$
\text{reduction}=\frac{\text{before}-\text{after}}{\text{before}}\times100\%
$$

本次计算：

$$
\frac{59.45-9.33}{59.45}\times100\%=84.31\%
$$

## 指标对比

| 检测项 | 修改前 | 修改后 | 降幅 |
|---|---:|---:|---:|
| AI 率 | 59.45% | 9.33% | 84.31% |

## 本地 AI 味特征变化

| 指标 | 修改前 | 修改后 | 变化 |
|---|---:|---:|---:|
| 模板表达 | 5 | 0 | -5 |
| 空泛词 | 19 | 2 | -17 |
| 连接词 | 9 | 0 | -9 |
| 重复连接词 | 1 | 0 | -1 |
| 具体细节 | 21 | 52 | +31 |
| 作者痕迹 | 0 | 4 | +4 |

### 类别分数变化

| 类别 | 修改前 | 修改后 | 变化 |
|---|---:|---:|---:|
| content | 40.00 | 0.00 | -40.00 |
| language | 32.00 | 0.00 | -32.00 |
| rhetoric | 12.00 | 0.00 | -12.00 |
| structure | 57.00 | 0.00 | -57.00 |

### 原文命中模式

| ID | 类别 | 模式 | 次数 | 修改建议 |
|---|---|---|---:|---|
| P01 | content | 意义拔高 | 5 | 把宏大评价改成具体结果、数据、文件或来源要求。 |
| P02 | structure | 模板化开头结尾 | 3 | 直接从任务、材料、项目选择或问题开始写。 |
| P03 | structure | 机械连接词 | 6 | 保留真实逻辑关系，删除没有推理作用的排序词。 |
| P04 | language | 空泛抽象词 | 8 | 替换为脚本名、指标、文件、案例或具体动作。 |
| P05 | rhetoric | 二元平衡套话 | 2 | 改成一个明确取舍：为什么这样做，放弃了什么。 |

### 修改前组件分数

| 组件 | 分数 |
|---|---:|
| `template_score` | 56.25 |
| `vague_score` | 99.45 |
| `connector_score` | 49.38 |
| `uniformity_score` | 53.97 |
| `detail_gap_score` | 0.00 |
| `author_gap_score` | 100.00 |

### 修改后组件分数

| 组件 | 分数 |
|---|---:|
| `template_score` | 0.00 |
| `vague_score` | 7.10 |
| `connector_score` | 0.00 |
| `uniformity_score` | 0.00 |
| `detail_gap_score` | 0.00 |
| `author_gap_score` | 79.13 |

## 原文高风险句子

1. `100.0`：随着人工智能技术的快速发展，AI 生成文本正在深刻改变用户的写作方式和内容生产方式。
   原因：意义拔高、模板化开头结尾、模板化开头或总结、长句缺少具体细节、缺少作者痕迹
2. `100.0`：在当今内容生产背景下，如何降低 AI 生成文字的 AI 率，已经成为一个具有重要意义的问题。
   原因：意义拔高、模板化开头结尾、模板化开头或总结、抽象词密集、长句缺少具体细节、缺少作者痕迹
3. `100.0`：一方面，它能够保存完整的处理流程，另一方面，它也能够展示项目的技术特点和应用价值。
   原因：意义拔高、机械连接词、空泛抽象词、二元平衡套话、抽象词密集、连接词堆叠
4. `99.0`：该方法能够有效降低 AI 生成文本的 AI 率，并充分体现文本优化效果，对于中文写作辅助项目具有重要意义。
   原因：意义拔高、空泛抽象词、模板化开头或总结、抽象词密集
5. `58.0`：首先，可以利用 AI 工具对生成文本进行全面分析，从而发现文本中存在的问题。
   原因：机械连接词、空泛抽象词、长句缺少具体细节、缺少作者痕迹
6. `58.0`：此外，还可以结合不同的检测方式，对修改前后的结果进行对比，从而进一步提升文本质量。
   原因：机械连接词、空泛抽象词、长句缺少具体细节、缺少作者痕迹
7. `53.0`：综上所述，通过构建 GitHub 项目和 skill，可以形成从检测、分析、改写到报告生成的完整闭环。
   原因：模板化开头结尾、模板化开头或总结
8. `40.0`：通过 GitHub 项目、skills 以及相关自动化方法，可以有效提升文本的人类化程度，并充分体现降重效果。
   原因：空泛抽象词、抽象词密集

## 修改说明

- 参考 humanizer/de-ai 类项目的做法，把检测、作者材料、改写提示和复查报告拆开。
- 删除或改写模板化开头、空泛总结、机械连接词和二元平衡套话。
- 增加项目、实验、数据、文件名或个人判断等作者材料。
- 保留原文主题，但把宽泛判断改成可验证、可解释的论证。
- 使用 AI 率变化和本地特征变化共同展示降 AI 味效果。

## 文章来源

来源文件：`examples/source_brief.md`

# Source Brief: Auto De-AI Writing Skill

This source brief defines the sample scenario used by the repository. It is intentionally generic so the project can be published as a normal GitHub project.

## Goal

Build a reusable skill-style workflow that can take an AI-generated Chinese draft, identify AI-flavored writing patterns, guide a more concrete revision, and generate a reproducible before/after report.

## Requirements

- Provide a GitHub-ready project structure.
- Analyze AI-generated Chinese text automatically.
- Calculate a reproducible AI-like rate without requiring a local large model.
- Generate a structured rewrite prompt based on source material, author notes, and voice sample.
- Run a detector-rewriter loop until the local AI-like rate reaches a target threshold or stops improving.
- Produce a Markdown report with before/after score, reduction formula, pattern hits, high-risk sentences, and limitations.
- Keep optional third-party API support, but make the default path runnable with only Python standard library.

## Evaluation Target

The demo should show a measurable reduction from the original draft to the revised text:

$$
reduction=\frac{before-after}{before}\times100\%
$$

## 使用的作者补充材料

# Author Notes

- 来源文件：`examples/source_brief.md`，用于定义示例项目需求。
- AI 初稿：`examples/original.md`，根据 source brief 生成，保留典型 AI 口吻用于测试。
- 修改稿：`examples/revised.md`，由 `adversarial_loop.py` 自动生成，用来展示 A/B/A 闭环效果。
- 项目定位：做一个 `auto-de-ai-writing-skill`，不是只替换同义词，而是检测 AI 味、补充真实材料、自动改写、复测并输出报告。
- 技术实现：Python 脚本包括 `ai_rate.py`、`analyze_text.py`、`rewrite_prompt.py`、`auto_rewrite.py`、`adversarial_loop.py`、`voice_profile.py` 和 `make_report.py`。
- 复现约束：不默认运行本地大模型，因为安装 `torch`、下载模型和处理硬件差异会提高门槛。
- 自动化要求：不依赖手动网页截图；优先支持 Sapling API；没有 API key 时使用本地规则评分。
- 关键判断：检测器分数不能证明文本作者，但可以作为项目内的实验指标。

## 限制说明

AI 检测分数只能作为概率化参考，不能证明文本一定由 AI 或人类撰写。本项目的目标是让修改过程更具体、可解释、可复现，而不是承诺通过所有检测器。

## 原始 JSON 结果

```json
{
  "original": {
    "ai_rate": 59.45,
    "provider": "local-ai-like",
    "details": {
      "ai_like_rate": 59.45,
      "components": {
        "template_score": 56.25,
        "vague_score": 99.45,
        "connector_score": 49.38,
        "uniformity_score": 53.97,
        "detail_gap_score": 0.0,
        "author_gap_score": 100.0
      },
      "category_scores": {
        "content": 40.0,
        "language": 32.0,
        "rhetoric": 12.0,
        "structure": 57.0
      },
      "pattern_hits": [
        {
          "id": "P01",
          "category": "content",
          "label": "意义拔高",
          "count": 5,
          "weight": 16,
          "examples": [
            "具有重要意义",
            "具有重要意义",
            "深刻改变",
            "现实意义",
            "应用价值"
          ],
          "advice": "把宏大评价改成具体结果、数据、文件或来源要求。"
        },
        {
          "id": "P02",
          "category": "structure",
          "label": "模板化开头结尾",
          "count": 3,
          "weight": 18,
          "examples": [
            "随着人工智能技术的快速发展",
            "在当今内容生产背景下",
            "综上所述"
          ],
          "advice": "直接从任务、材料、项目选择或问题开始写。"
        },
        {
          "id": "P03",
          "category": "structure",
          "label": "机械连接词",
          "count": 6,
          "weight": 10,
          "examples": [
            "首先",
            "其次",
            "此外",
            "一方面",
            "一方面"
          ],
          "advice": "保留真实逻辑关系，删除没有推理作用的排序词。"
        },
        {
          "id": "P04",
          "category": "language",
          "label": "空泛抽象词",
          "count": 8,
          "weight": 8,
          "examples": [
            "优化",
            "优化",
            "提升",
            "提升",
            "价值"
          ],
          "advice": "替换为脚本名、指标、文件、案例或具体动作。"
        },
        {
          "id": "P05",
          "category": "rhetoric",
          "label": "二元平衡套话",
          "count": 2,
          "weight": 12,
          "examples": [
            "不仅能够提高效率，也",
            "一方面，它能够保存完整的处理流程，另一方面"
          ],
          "advice": "改成一个明确取舍：为什么这样做，放弃了什么。"
        }
      ],
      "counts": {
        "characters": 619,
        "sentences": 16,
        "template_patterns": 5,
        "vague_words": 19,
        "connectors": 9,
        "repeated_connectors": 1,
        "concrete_details": 21,
        "author_markers": 0
      },
      "sentence_stats": {
        "avg_length": 40.75,
        "stdev_length": 9.0,
        "cv": 0.2209
      },
      "top_risk_sentences": [
        {
          "score": 100.0,
          "sentence": "随着人工智能技术的快速发展，AI 生成文本正在深刻改变用户的写作方式和内容生产方式。",
          "reasons": [
            "意义拔高",
            "模板化开头结尾",
            "模板化开头或总结",
            "长句缺少具体细节",
            "缺少作者痕迹"
          ],
          "pattern_ids": [
            "P01",
            "P02",
            "P07"
          ]
        },
        {
          "score": 100.0,
          "sentence": "在当今内容生产背景下，如何降低 AI 生成文字的 AI 率，已经成为一个具有重要意义的问题。",
          "reasons": [
            "意义拔高",
            "模板化开头结尾",
            "模板化开头或总结",
            "抽象词密集",
            "长句缺少具体细节",
            "缺少作者痕迹"
          ],
          "pattern_ids": [
            "P01",
            "P02",
            "P07"
          ]
        },
        {
          "score": 100.0,
          "sentence": "一方面，它能够保存完整的处理流程，另一方面，它也能够展示项目的技术特点和应用价值。",
          "reasons": [
            "意义拔高",
            "机械连接词",
            "空泛抽象词",
            "二元平衡套话",
            "抽象词密集",
            "连接词堆叠"
          ],
          "pattern_ids": [
            "P01",
            "P03",
            "P04",
            "P05"
          ]
        },
        {
          "score": 99.0,
          "sentence": "该方法能够有效降低 AI 生成文本的 AI 率，并充分体现文本优化效果，对于中文写作辅助项目具有重要意义。",
          "reasons": [
            "意义拔高",
            "空泛抽象词",
            "模板化开头或总结",
            "抽象词密集"
          ],
          "pattern_ids": [
            "P01",
            "P04"
          ]
        },
        {
          "score": 58.0,
          "sentence": "首先，可以利用 AI 工具对生成文本进行全面分析，从而发现文本中存在的问题。",
          "reasons": [
            "机械连接词",
            "空泛抽象词",
            "长句缺少具体细节",
            "缺少作者痕迹"
          ],
          "pattern_ids": [
            "P03",
            "P04",
            "P07"
          ]
        },
        {
          "score": 58.0,
          "sentence": "此外，还可以结合不同的检测方式，对修改前后的结果进行对比，从而进一步提升文本质量。",
          "reasons": [
            "机械连接词",
            "空泛抽象词",
            "长句缺少具体细节",
            "缺少作者痕迹"
          ],
          "pattern_ids": [
            "P03",
            "P04",
            "P07"
          ]
        },
        {
          "score": 53.0,
          "sentence": "综上所述，通过构建 GitHub 项目和 skill，可以形成从检测、分析、改写到报告生成的完整闭环。",
          "reasons": [
            "模板化开头结尾",
            "模板化开头或总结"
          ],
          "pattern_ids": [
            "P02"
          ]
        },
        {
          "score": 40.0,
          "sentence": "通过 GitHub 项目、skills 以及相关自动化方法，可以有效提升文本的人类化程度，并充分体现降重效果。",
          "reasons": [
            "空泛抽象词",
            "抽象词密集"
          ],
          "pattern_ids": [
            "P04"
          ]
        }
      ]
    }
  },
  "revised": {
    "ai_rate": 9.33,
    "provider": "local-ai-like",
    "details": {
      "ai_like_rate": 9.33,
      "components": {
        "template_score": 0.0,
        "vague_score": 7.1,
        "connector_score": 0.0,
        "uniformity_score": 0.0,
        "detail_gap_score": 0.0,
        "author_gap_score": 79.13
      },
      "category_scores": {},
      "pattern_hits": [],
      "counts": {
        "characters": 913,
        "sentences": 23,
        "template_patterns": 0,
        "vague_words": 2,
        "connectors": 0,
        "repeated_connectors": 0,
        "concrete_details": 52,
        "author_markers": 4
      },
      "sentence_stats": {
        "avg_length": 41.57,
        "stdev_length": 20.44,
        "cv": 0.4919
      },
      "top_risk_sentences": [
        {
          "score": 40.0,
          "sentence": "只有在合理使用 AI 工具的基础上，才能更好地降低 AI 率，并避免文本过于机械化和模板化的问题。",
          "reasons": [
            "长句缺少具体细节",
            "缺少作者痕迹"
          ],
          "pattern_ids": [
            "P07"
          ]
        }
      ]
    }
  }
}
```

## 对抗式迭代记录

- 目标阈值：25.00%
- 停止原因：target reached

| 轮次 | 改写前 | 改写后 | 变化 | 是否接受 | 说明 |
|---:|---:|---:|---:|---|---|
| 1 | 59.45% | 9.33% | +50.12% | yes | target reached |

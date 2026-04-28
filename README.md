# Auto De-AI Writing Skill

这个仓库做的是一件比较具体的事：给一段中文 AI 初稿找出“AI 味”来自哪里，再把检测器 A 和改写器 B 分开运行，循环复测直到达到项目设定的 AI-like Rate 阈值，最后生成修改前后的对比报告。

我没有把它做成“同义词替换器”。那种做法看起来自动，实际很难解释为什么分数会降，也容易把文章改得更怪。这里的思路是把流程拆开：先检测，再定位问题，再引入来源材料和作者补充信息，自动改写后继续复查。

默认运行不需要本地大模型，也不需要打开网页检测器截图。只要有 Python 标准库，就能跑完整示例。配置了 `SAPLING_API_KEY` 时，`scripts/ai_rate.py` 会优先调用 Sapling AI Detector API；没有 key 时，就使用仓库内置的本地 `AI-like Rate`。

## Quick Start

```bash
git clone https://github.com/Akimiya-z/auto-de-ai-writing-skill.git
cd auto-de-ai-writing-skill
python scripts/run_pipeline.py
```

这条命令会更新三个文件：

- `examples/rewrite_prompt.md`
- `examples/revised.md`
- `examples/report.md`

如果想分开看每一步，可以这样跑：

```bash
python scripts/ai_rate.py examples/original.md
python scripts/analyze_text.py examples/original.md
python scripts/rewrite_prompt.py examples/original.md \
  --notes examples/author_notes.md \
  --source examples/source_brief.md \
  --voice examples/voice_sample.md \
  --out examples/rewrite_prompt.md
python scripts/adversarial_loop.py \
  --original examples/original.md \
  --notes examples/author_notes.md \
  --source examples/source_brief.md \
  --voice examples/voice_sample.md \
  --target-rate 25 \
  --max-rounds 5 \
  --provider local \
  --out examples/revised.md \
  --report examples/report.md \
  --generated-at "2026-04-28 00:00:00" \
```

`--generated-at` 只是为了让示例报告保持可复现。自己处理文本时可以删掉这个参数，脚本会写入当前时间。

## Testing

```bash
python -m py_compile scripts/*.py
python -m unittest discover -s tests -v
```

仓库带有 GitHub Actions，会在 push 和 pull request 时运行同样的编译和单元测试。

## 示例跑出来是什么样

仓库里的 `examples/original.md` 是一段故意写得比较模板化的中文 AI 初稿。`examples/revised.md` 由 `scripts/adversarial_loop.py` 自动生成，会加入来源文件、脚本分工、取舍和限制说明。

当前示例的结果如下：

| 指标 | 修改前 | 修改后 | 降幅 |
|---|---:|---:|---:|
| AI-like Rate | 59.45% | 9.33% | 84.31% |

降幅按这个公式算：

$$
reduction=\frac{before-after}{before}\times100\%
$$

带入本例：

$$
\frac{59.45-9.33}{59.45}\times100\%=84.31\%
$$

生成的报告不只给一个百分比，还会列出原文命中的模式、高风险句子、各类特征变化、原始 JSON 结果和对抗式迭代记录。完整示例在 `examples/report.md`。

## 这些文件分别干什么

| 文件 | 作用 |
|---|---|
| `examples/original.md` | 待处理的 AI 初稿 |
| `examples/source_brief.md` | 写作任务、来源背景或材料说明 |
| `examples/author_notes.md` | 作者补充的真实细节、判断和限制 |
| `examples/voice_sample.md` | 作者语气样本，用来约束改写风格 |
| `examples/rewrite_prompt.md` | 脚本生成的改写提示 |
| `examples/revised.md` | 对抗式循环自动生成的修改稿 |
| `examples/report.md` | 修改前后的对比报告和迭代记录 |

## 核心脚本

`scripts/ai_rate.py` 是检测入口。它会先看环境变量里有没有 `SAPLING_API_KEY`。有的话走 Sapling；没有的话走本地规则。为了保证示例能直接复现，本地规则不依赖机器学习模型。

`scripts/analyze_text.py` 负责找中文 AI 味特征。它会检查模板化开头、空泛抽象词、机械连接词、二元平衡套话、句式过于均匀、作者痕迹不足等问题。

`scripts/rewrite_prompt.py` 不直接改文章，而是生成一份结构化 prompt。这样可以把“怎么改”这一步交给任意 AI 写作工具，同时保留项目自己的检测和报告流程。

`scripts/auto_rewrite.py` 是本地改写器 B。它不调用大模型，只根据检测结果、来源材料、作者 notes 和 voice sample 做保守的规则改写，用来保证示例可以离线复现。

`scripts/adversarial_loop.py` 把检测器 A 和改写器 B 串起来。它会按 `--target-rate`、`--max-rounds` 和 `--min-delta` 控制循环，接受分数下降的候选文本，最后写出 `revised.md` 和 `report.md`。

`scripts/make_report.py` 会重新检测原文和修改稿，然后生成 Markdown 报告。报告里会说明分数、降幅、命中模式和限制。

## 本地 AI-like Rate 怎么理解

本地分数是项目里的启发式指标，不是权威 AI 检测结论。它主要看六类信号：

| 维度 | 看什么 |
|---|---|
| `template_score` | 是否有模板化开头、总结和套话 |
| `vague_score` | 空泛词是不是过多 |
| `connector_score` | 连接词是否机械堆叠 |
| `uniformity_score` | 句长是否过于平均 |
| `detail_gap_score` | 是否缺少具体材料 |
| `author_gap_score` | 是否缺少作者判断和真实痕迹 |

用公式写就是：

$$
AI\text{-}like\ Rate=f(T,V,C,U,D,A)
$$

这里的 \(T,V,C,U,D,A\) 分别对应模板表达、空泛词、连接词、句长均匀度、细节缺失和作者痕迹缺失。

如果启用了第三方检测器，则统一按下面方式展示：

$$
AI\ Rate=score\times100\%
$$

## 换成自己的文本

最简单的用法是直接替换 `examples/` 里的几个文件：

1. 把原始 AI 初稿放到 `examples/original.md`。
2. 把来源材料或任务背景放到 `examples/source_brief.md`。
3. 把真实细节、个人判断、项目记录放到 `examples/author_notes.md`。
4. 如果有自己的写作样本，放到 `examples/voice_sample.md`。
5. 运行 `python scripts/run_pipeline.py` 自动生成改写提示、修改稿和报告。
6. 如果要调阈值，使用 `python scripts/run_pipeline.py --target-rate 20 --max-rounds 5`。
7. 如果要人工或模型精修，可以先看 `examples/rewrite_prompt.md`，再重新运行 `scripts/make_report.py` 复测。

## Skill 文件

这个仓库同时也是一个 Codex/Claude 风格的 skill。核心说明在 `SKILL.md`，UI 元数据在 `agents/openai.yaml`。

skill 的触发场景是：用户给出 AI 初稿，希望分析 AI 味、生成改写提示、保留作者材料，并输出修改前后的可解释报告。它不会承诺“通过所有检测器”，也不会编造来源、经历或 API 结果。

## 项目结构

```text
auto-de-ai-writing-skill/
├── README.md
├── SKILL.md
├── LICENSE
├── .github/
│   └── workflows/
│       └── test.yml
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── ai_rate.py
│   ├── analyze_text.py
│   ├── adversarial_loop.py
│   ├── auto_rewrite.py
│   ├── make_report.py
│   ├── rewrite_prompt.py
│   ├── run_pipeline.py
│   └── voice_profile.py
├── references/
│   ├── ai_tells_zh.md
│   ├── inspiration.md
│   └── workflow.md
├── tests/
│   └── test_pipeline.py
└── examples/
    ├── source_brief.md
    ├── original.md
    ├── author_notes.md
    ├── voice_sample.md
    ├── rewrite_prompt.md
    ├── revised.md
    └── report.md
```

## 参考

这个项目借鉴的是 humanizer/de-ai 类 skill 的工程套路，而不是复制它们的内容：

- `blader/humanizer`：检测、改写、复查分阶段。
- `Aboudjem/humanizer-skill`：pattern catalog 和任务模式。
- `glebis/claude-skills` 中的 de-ai 思路：先收集上下文和作者材料，再改写。
- Wikipedia `Signs of AI writing`：结构、证据、语气和模板化表达都可能暴露 AI 写作痕迹。

更详细的说明放在 `references/inspiration.md`。

## 限制

这个项目的本地分数只能作为实验指标。商业检测器也一样，只能给概率参考，不能证明一段文字一定由 AI 或人写。

本地 `auto_rewrite.py` 是可复现实验用的 baseline，不等于高质量终稿。正式文本仍建议让 skill 或人工作者根据 `rewrite_prompt.md` 做二次精修。

更有效的“降 AI 味”不是故意制造错别字或病句，而是把空泛判断换成具体材料，把模板句换成真实取舍，把没有来源的结论删掉或补上依据。

## License

MIT License. See `LICENSE`.

# 检测-改写-复测工作流

## 1. 建立基线

先运行：

```bash
python scripts/ai_rate.py input.md
python scripts/analyze_text.py input.md
```

记录原始 AI 率和高风险句子。若设置 `SAPLING_API_KEY`，使用 Sapling API；否则使用本地轻量 AI-like Rate。

## 2. 收集作者材料

改写前至少收集三类材料中的两类：

- 来源材料：需求说明、产品 brief、文章提纲、引用材料。
- 项目材料：代码文件、GitHub 项目、错误日志、运行结果。
- 个人判断：为什么这样做、遇到什么问题、哪些地方和 AI 初稿不同。

如果有作者自己的文字样本，先生成 voice profile：

```bash
python scripts/voice_profile.py voice_sample.md --out voice_profile.md
```

## 3. 生成改写提示

借鉴 humanizer/de-ai skill 的做法，先生成结构化提示，再让 AI 工具执行改写：

```bash
python scripts/rewrite_prompt.py original.md --notes author_notes.md --source source_brief.md --voice voice_sample.md --out rewrite_prompt.md
```

提示必须包含：

- 文章来源。
- 作者补充材料。
- 高风险句子。
- 命中的 pattern ID。
- voice profile。
- 不得编造事实的约束。

## 4. 自动改写或分段精修

本地自动 baseline：

```bash
python scripts/auto_rewrite.py original.md --notes author_notes.md --source source_brief.md --voice voice_sample.md --out revised.md
```

完整 A/B 闭环：

```bash
python scripts/adversarial_loop.py --original original.md --notes author_notes.md --source source_brief.md --voice voice_sample.md --target-rate 25 --max-rounds 5 --out revised.md --report report.md
```

如果由 skill agent 直接改写，仍然按段处理，不要整篇一次性洗稿：

1. 找到段落主张。
2. 删除空泛铺垫。
3. 插入具体材料。
4. 调整句式节奏。
5. 保留事实含义。
6. 写出修改依据。

## 5. 复测和迭代

再次运行：

```bash
python scripts/ai_rate.py revised.md
```

如果 AI 率仍高，优先检查：

- 是否仍有模板开头和总结。
- 是否仍缺少作者材料。
- 是否连接词过密。
- 是否长句没有数据或例子。

循环停止条件：

$$
S_t \leq \tau
$$

或：

$$
\Delta_t=S_{t-1}-S_t<\epsilon
$$

## 6. 输出报告

运行：

```bash
python scripts/make_report.py original.md revised.md --out report.md
```

报告必须包含：

- 原始 AI 率。
- 修改后 AI 率。
- 降幅公式。
- AI 味特征变化。
- 高风险句子列表。
- 对抗式迭代记录。
- 修改说明和限制说明。

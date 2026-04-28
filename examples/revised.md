# 用 Skill 自动降低 AI 初稿的 AI-like 率

这个项目的示例需求保存在 `examples/source_brief.md`。它要求构建一个可复用的 GitHub 项目或 skill，把 AI 生成文字中的模板化表达、空泛词和机械结构识别出来，再生成更具体的修改提示和前后对比报告。我没有选择做一个只替换同义词的工具，而是把项目设计成 `auto-de-ai-writing-skill`，让它能检测、分析、生成改写提示并输出评测结果。

这个项目的样例文章不是随机作文。`examples/original.md` 是根据 source brief 生成的 AI 初稿，故意保留了“随着技术发展”“具有重要意义”“综上所述”这类常见 AI 口吻；`examples/author_notes.md` 记录了项目方案和限制；`examples/revised.md` 则是加入这些材料后的修改稿。这样做的好处是，报告里每一次修改都能追溯到来源文件、作者材料和项目实现。

我把实现拆成五个 Python 脚本。`scripts/ai_rate.py` 负责给文本算一个统一的 AI 率；如果电脑里配置了 `SAPLING_API_KEY`，脚本会调用 Sapling AI Detector API，否则就使用本地规则评分。`scripts/analyze_text.py` 会检查中文文本里的模板表达、空泛词、重复连接词、句式过于均匀和缺少具体材料的问题。`scripts/voice_profile.py` 读取作者语气样本，`scripts/rewrite_prompt.py` 生成结构化改写提示，`scripts/make_report.py` 把原文、修改稿和作者补充材料放在一起，自动生成降幅、问题句子和修改说明。

我没有把本地大模型作为默认方案，原因是这个项目需要让别人容易复现。如果要求安装 `torch`、下载 HuggingFace 模型，再处理显卡或网络问题，项目展示的重点就会变成环境配置，而不是评测和改写流程本身。因此我把本地规则评分作为默认路径，把 Sapling API 作为可选增强。没有 API key 时，命令仍然能直接跑出 AI-like 率和报告。

这个 skill 的关键不是承诺骗过所有检测器，而是让文本更像一次真实写作过程。修改时必须加入来源背景、项目文件、脚本设计、个人取舍和限制说明。例如本文加入了 `source_brief.md`、`original.md`、`author_notes.md`、`voice_sample.md`、`rewrite_prompt.md`、`revised.md`、`report.md` 之间的来源关系，也说明了为什么不用手动网页截图和本地大模型。修改后，文本里能看到具体实现和作者判断，而不是只剩下“提升效率、促进发展、具有重要意义”一类空泛表达。

因此，我把 AI 率看成一个实验指标，而不是作者身份的证明。项目最终输出的报告会同时给出修改前 AI 率、修改后 AI 率和降幅公式：

$$
\text{reduction}=\frac{\text{before}-\text{after}}{\text{before}}\times100\%
$$

这种做法更适合作为 GitHub 项目展示，因为它既能展示自动化检测和改写闭环，也能说明文章来源、修改依据和方法局限。

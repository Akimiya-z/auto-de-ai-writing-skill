---
name: auto-de-ai-writing-skill
description: 自动检测并降低中文 AI 初稿的 AI-like 率，生成前后对比报告和可解释修改建议。Use when Codex needs to revise AI-generated Chinese writing, reduce AI-flavored wording, calculate an AI-rate style score, use optional Sapling AI Detector API, or produce reproducible before/after rewriting evidence.
---

# Auto De-AI Writing Skill

## Overview

Use this skill to turn an AI-generated Chinese draft into a more specific, sourced, author-shaped revision with an auditable before/after AI-rate report. It borrows proven humanizer-skill patterns: pattern catalog detection, voice calibration, structured rewrite prompting, and second-pass reporting.

## Core Workflow

1. Collect the draft, source context, target audience, and any required word count or format.
2. Ask for or locate author notes before rewriting: personal experience, class materials, data, examples, opinions, citations, or constraints.
3. Run `scripts/ai_rate.py` on the original text to get an AI-rate baseline.
4. Run `scripts/analyze_text.py` to identify high-risk AI-flavored sentences and pattern categories.
5. Build a voice profile with `scripts/voice_profile.py` when a sample is available.
6. Generate a structured rewrite prompt with `scripts/rewrite_prompt.py`.
7. Rewrite the draft by adding concrete author material, restructuring generic paragraphs, replacing template transitions, and preserving factual meaning.
8. Run `scripts/ai_rate.py` again on the revised text.
9. Generate the report with `scripts/make_report.py`, including AI-rate change, formula, pattern IDs, high-risk sentences, source trail, and a concise explanation of what changed.

Read `references/workflow.md` for the full procedure, `references/ai_tells_zh.md` for the Chinese AI-writing pattern catalog, and `references/inspiration.md` for borrowed design ideas.

## Commands

Calculate AI rate:

```bash
python scripts/ai_rate.py examples/original.md
```

Analyze Chinese AI-flavored patterns:

```bash
python scripts/analyze_text.py examples/original.md
```

Generate a rewrite prompt:

```bash
python scripts/rewrite_prompt.py examples/original.md --notes examples/author_notes.md --source examples/source_brief.md --voice examples/voice_sample.md --out examples/rewrite_prompt.md
```

Generate a before/after report:

```bash
python scripts/make_report.py examples/original.md examples/revised.md --notes examples/author_notes.md --source examples/source_brief.md --out examples/report.md
```

Run the full demo pipeline:

```bash
python scripts/run_pipeline.py
```

If `SAPLING_API_KEY` is set, `scripts/ai_rate.py` tries Sapling first. If the API key is missing or the request fails, it falls back to the local lightweight AI-like score.

## Metric Contract

Use one normalized output field for every detector:

$$
\text{AI Rate} = score \times 100\%
$$

For the local fallback, calculate:

$$
AI\text{-}like\ Rate = f(模板表达, 空泛词, 重复连接词, 句式单一度, 具体细节缺失)
$$

Report improvement with:

$$
\text{reduction}=\frac{\text{before}-\text{after}}{\text{before}}\times100\%
$$

Do not claim that the score is a universal or institutionally valid AI detector. Describe it as an automatic project metric, with Sapling as an optional third-party detector.

## Rewriting Rules

- Keep factual meaning stable; do not invent data, citations, class events, or personal experiences.
- Replace generic claims with user-provided or source-backed details.
- Calibrate against the user's voice sample when available; preserve first-person project decisions and concrete file names.
- Prefer uneven but readable sentence rhythm over mechanical three-part paragraphs.
- Remove empty transition stacks such as "首先、其次、最后、综上所述" when they do not carry reasoning.
- Preserve required academic tone, but avoid slogan-like abstraction and broad claims without evidence.
- Include a revision note explaining which author materials were added and which AI-like patterns were reduced.

## Deliverables

For a complete run, produce:

- Revised text.
- AI-rate report with original score, revised score, and reduction.
- Source trail showing where the sample article came from.
- Generated rewrite prompt showing how the revision was instructed.
- List of high-risk sentences in the original.
- Short explanation of concrete author material added.
- A limitation note saying detector scores are probabilistic and should not be treated as proof of authorship.

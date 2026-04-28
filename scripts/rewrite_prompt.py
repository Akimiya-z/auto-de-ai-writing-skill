#!/usr/bin/env python3
"""Generate a structured rewrite prompt from analysis, source, notes, and voice sample."""

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_text import analyze_text
from voice_profile import build_voice_profile


def read_text(path: str | Path | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def risk_block(analysis: dict) -> str:
    lines: list[str] = []
    for item in analysis.get("top_risk_sentences", [])[:6]:
        reasons = "、".join(item.get("reasons", []))
        ids = "、".join(item.get("pattern_ids", []))
        suffix = f"；模式：{ids}" if ids else ""
        lines.append(f"- `{item['score']:.1f}` {item['sentence']}（{reasons}{suffix}）")
    return "\n".join(lines) if lines else "- 未发现明显高风险句子。"


def pattern_block(analysis: dict) -> str:
    hits = analysis.get("pattern_hits", [])
    if not hits:
        return "- 未命中明显模式。"
    lines = []
    for hit in hits[:10]:
        lines.append(f"- {hit['id']} {hit['label']}：{hit['count']} 次；建议：{hit['advice']}")
    return "\n".join(lines)


def voice_block(sample: str) -> str:
    if not sample.strip():
        return "未提供 voice sample；用作者补充材料中的第一人称和项目细节校准。"
    profile = build_voice_profile(sample)
    top_terms = "、".join(item["term"] for item in profile["top_terms"][:8])
    return "\n".join(
        [
            f"- 平均句长：{profile['avg_sentence_length']}",
            f"- 句长变异系数：{profile['sentence_length_cv']}",
            f"- 作者痕迹数量：{profile['author_marker_count']}",
            f"- 高频词：{top_terms}",
            "- 风格要求：保留第一人称、文件名、脚本名、命令和真实取舍。",
        ]
    )


def build_prompt(draft: str, notes: str, source: str, voice_sample: str) -> str:
    analysis = analyze_text(draft)
    return f"""# 改写任务

请把下面的 AI 初稿改成一篇更像真实作者写出的中文项目说明。目标不是编造经历，也不是故意制造病句，而是加入真实来源、作者补充材料、项目实现细节和个人取舍，让文本更具体、更可解释。

## 当前检测结果

- AI-like Rate：{analysis['ai_like_rate']:.2f}%

## 主要命中模式

{pattern_block(analysis)}

## 高风险句子

{risk_block(analysis)}

## 文章来源

{source.strip() or "未提供来源。"}

## 作者补充材料

{notes.strip() or "未提供作者补充材料。"}

## Voice Profile

{voice_block(voice_sample)}

## 改写要求

1. 保留主题：通过 GitHub 项目或 skill 自动降低文本的 AI-like 率。
2. 明确说明文本来源来自 source brief。
3. 加入项目文件、脚本名、命令、指标和实现取舍。
4. 删除空泛套话，例如“随着技术发展”“具有重要意义”“综上所述”。
5. 不要编造 API 结果；没有 API key 时只写本地 AI-like Rate。
6. 结尾必须说明检测分数只是实验指标，不是作者身份证明。

## AI 初稿

{draft.strip()}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a structured rewrite prompt.")
    parser.add_argument("draft", help="AI draft file.")
    parser.add_argument("--notes", help="Author notes file.")
    parser.add_argument("--source", help="Source brief file.")
    parser.add_argument("--voice", help="Voice sample file.")
    parser.add_argument("--out", help="Output prompt file.")
    args = parser.parse_args()

    prompt = build_prompt(
        read_text(args.draft),
        read_text(args.notes),
        read_text(args.source),
        read_text(args.voice),
    )
    if args.out:
        Path(args.out).write_text(prompt, encoding="utf-8")
    else:
        print(prompt)


if __name__ == "__main__":
    main()

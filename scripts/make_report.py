#!/usr/bin/env python3
"""Generate a Markdown before/after AI-rate report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_rate import detect_ai_rate, read_text
from analyze_text import analyze_text


def percent_change(before: float, after: float) -> float:
    if before <= 0:
        return 0.0
    return (before - after) / before * 100


def component_table(title: str, details: dict[str, Any]) -> list[str]:
    components = details.get("components", {})
    if not components:
        return []
    lines = [
        f"### {title}",
        "",
        "| 组件 | 分数 |",
        "|---|---:|",
    ]
    for key, value in components.items():
        lines.append(f"| `{key}` | {float(value):.2f} |")
    lines.append("")
    return lines


def risk_sentence_lines(analysis: dict[str, Any]) -> list[str]:
    risks = analysis.get("top_risk_sentences", [])
    if not risks:
        return ["未发现明显高风险句子。", ""]
    lines: list[str] = []
    for index, item in enumerate(risks, start=1):
        reasons = "、".join(item.get("reasons", []))
        lines.append(f"{index}. `{item['score']:.1f}`：{item['sentence']}")
        if reasons:
            lines.append(f"   原因：{reasons}")
    lines.append("")
    return lines


def counts_delta(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    before_counts = before.get("counts", {})
    after_counts = after.get("counts", {})
    keys = [
        ("template_patterns", "模板表达"),
        ("vague_words", "空泛词"),
        ("connectors", "连接词"),
        ("repeated_connectors", "重复连接词"),
        ("concrete_details", "具体细节"),
        ("author_markers", "作者痕迹"),
    ]
    lines = [
        "| 指标 | 修改前 | 修改后 | 变化 |",
        "|---|---:|---:|---:|",
    ]
    for key, label in keys:
        b = int(before_counts.get(key, 0))
        a = int(after_counts.get(key, 0))
        lines.append(f"| {label} | {b} | {a} | {a - b:+d} |")
    lines.append("")
    return lines


def pattern_table(title: str, analysis: dict[str, Any]) -> list[str]:
    hits = analysis.get("pattern_hits", [])
    if not hits:
        return [f"### {title}", "", "未命中明显模式。", ""]
    lines = [
        f"### {title}",
        "",
        "| ID | 类别 | 模式 | 次数 | 修改建议 |",
        "|---|---|---|---:|---|",
    ]
    for hit in hits:
        lines.append(
            f"| {hit['id']} | {hit['category']} | {hit['label']} | "
            f"{hit['count']} | {hit['advice']} |"
        )
    lines.append("")
    return lines


def category_table(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    before_scores = before.get("category_scores", {})
    after_scores = after.get("category_scores", {})
    keys = sorted(set(before_scores) | set(after_scores))
    if not keys:
        return []
    lines = [
        "### 类别分数变化",
        "",
        "| 类别 | 修改前 | 修改后 | 变化 |",
        "|---|---:|---:|---:|",
    ]
    for key in keys:
        b = float(before_scores.get(key, 0.0))
        a = float(after_scores.get(key, 0.0))
        lines.append(f"| {key} | {b:.2f} | {a:.2f} | {a - b:+.2f} |")
    lines.append("")
    return lines


def build_report(
    original_path: Path,
    revised_path: Path,
    original_result: dict[str, Any],
    revised_result: dict[str, Any],
    notes_path: Path | None = None,
    source_path: Path | None = None,
    generated_at: str | None = None,
) -> str:
    before = float(original_result["ai_rate"])
    after = float(revised_result["ai_rate"])
    reduction = percent_change(before, after)
    before_analysis = analyze_text(read_text(original_path))
    after_analysis = analyze_text(read_text(revised_path))
    provider_note = (
        f"原文 provider: `{original_result['provider']}`；"
        f"修改后 provider: `{revised_result['provider']}`。"
    )

    lines = [
        "# AI 率前后对比报告",
        "",
        f"生成时间：{generated_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 结论",
        "",
        f"- 原始 AI 率：{before:.2f}%",
        f"- 修改后 AI 率：{after:.2f}%",
        f"- 降幅：{reduction:.2f}%",
        f"- 原文文件：`{original_path}`",
        f"- 修改稿文件：`{revised_path}`",
        f"- {provider_note}",
        "",
        "降幅公式：",
        "",
        "$$",
        r"\text{reduction}=\frac{\text{before}-\text{after}}{\text{before}}\times100\%",
        "$$",
        "",
        "本次计算：",
        "",
        "$$",
        f"\\frac{{{before:.2f}-{after:.2f}}}{{{before:.2f}}}\\times100\\%={reduction:.2f}\\%",
        "$$",
        "",
        "## 指标对比",
        "",
        "| 检测项 | 修改前 | 修改后 | 降幅 |",
        "|---|---:|---:|---:|",
        f"| AI 率 | {before:.2f}% | {after:.2f}% | {reduction:.2f}% |",
        "",
        "## 本地 AI 味特征变化",
        "",
    ]
    lines.extend(counts_delta(before_analysis, after_analysis))
    lines.extend(category_table(before_analysis, after_analysis))
    lines.extend(pattern_table("原文命中模式", before_analysis))
    lines.extend(component_table("修改前组件分数", before_analysis))
    lines.extend(component_table("修改后组件分数", after_analysis))
    lines.extend(
        [
            "## 原文高风险句子",
            "",
        ]
    )
    lines.extend(risk_sentence_lines(before_analysis))
    lines.extend(
        [
            "## 修改说明",
            "",
            "- 参考 humanizer/de-ai 类项目的做法，把检测、作者材料、改写提示和复查报告拆开。",
            "- 删除或改写模板化开头、空泛总结、机械连接词和二元平衡套话。",
            "- 增加项目、实验、数据、文件名或个人判断等作者材料。",
            "- 保留原文主题，但把宽泛判断改成可验证、可解释的论证。",
            "- 使用 AI 率变化和本地特征变化共同展示降 AI 味效果。",
            "",
        ]
    )

    if source_path:
        source = read_text(source_path).strip()
        lines.extend(
            [
                "## 文章来源",
                "",
                f"来源文件：`{source_path}`",
                "",
                source if source else "来源文件为空。",
                "",
            ]
        )

    if notes_path:
        notes = read_text(notes_path).strip()
        lines.extend(
            [
                "## 使用的作者补充材料",
                "",
                notes if notes else "未提供作者补充材料。",
                "",
            ]
        )

    lines.extend(
        [
            "## 限制说明",
            "",
            "AI 检测分数只能作为概率化参考，不能证明文本一定由 AI 或人类撰写。本项目的目标是让修改过程更具体、可解释、可复现，而不是承诺通过所有检测器。",
            "",
            "## 原始 JSON 结果",
            "",
            "```json",
            json.dumps(
                {
                    "original": original_result,
                    "revised": revised_result,
                },
                ensure_ascii=False,
                indent=2,
            ),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a before/after AI-rate Markdown report.")
    parser.add_argument("original", help="Original draft file.")
    parser.add_argument("revised", help="Revised file.")
    parser.add_argument("--out", help="Output Markdown file. If omitted, print to stdout.")
    parser.add_argument("--notes", help="Optional author notes file.")
    parser.add_argument("--source", help="Optional source brief file.")
    parser.add_argument(
        "--generated-at",
        help="Optional report timestamp. Useful for reproducible examples.",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "sapling", "local"],
        default="auto",
        help="Detection provider for both files.",
    )
    args = parser.parse_args()

    original_path = Path(args.original)
    revised_path = Path(args.revised)
    notes_path = Path(args.notes) if args.notes else None
    source_path = Path(args.source) if args.source else None

    original_result = detect_ai_rate(read_text(original_path), provider=args.provider)
    revised_result = detect_ai_rate(read_text(revised_path), provider=args.provider)
    report = build_report(
        original_path,
        revised_path,
        original_result,
        revised_result,
        notes_path=notes_path,
        source_path=source_path,
        generated_at=args.generated_at,
    )

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create a lightweight voice profile from a Chinese writing sample."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Any

from analyze_text import CONNECTORS, AUTHOR_PATTERNS, split_sentences


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def top_terms(text: str, limit: int = 12) -> list[dict[str, Any]]:
    backtick_terms = re.findall(r"`([^`]+)`", text)
    ascii_terms = re.findall(r"[A-Za-z][A-Za-z0-9_.-]{2,}", text)
    known_terms = [
        "命令",
        "示例",
        "检测",
        "报告",
        "脚本",
        "评分",
        "本地规则",
        "外部 API",
        "项目细节",
        "作者材料",
        "可复现",
        "环境配置",
        "继续扩展",
    ]
    tokens = backtick_terms + ascii_terms
    for term in known_terms:
        tokens.extend([term] * text.count(term))
    stop = {"Voice", "Sample", "这个", "一种", "通过", "可以", "因为", "所以"}
    counts: dict[str, int] = {}
    for token in tokens:
        if token in stop:
            continue
        counts[token] = counts.get(token, 0) + 1
    return [
        {"term": term, "count": count}
        for term, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def build_voice_profile(text: str) -> dict[str, Any]:
    sentences = split_sentences(text)
    lengths = [len(sentence) for sentence in sentences] or [0]
    avg_len = statistics.mean(lengths)
    stdev_len = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    connector_total = sum(text.count(word) for word in CONNECTORS)
    author_total = sum(len(re.findall(pattern, text)) for pattern in AUTHOR_PATTERNS)
    punctuation = {
        "comma": text.count("，"),
        "period": text.count("。"),
        "semicolon": text.count("；"),
        "colon": text.count("："),
        "backtick": text.count("`"),
    }
    return {
        "sentences": len(sentences),
        "avg_sentence_length": round(avg_len, 2),
        "sentence_length_cv": round((stdev_len / avg_len) if avg_len else 0.0, 4),
        "author_marker_count": author_total,
        "connector_count": connector_total,
        "punctuation": punctuation,
        "top_terms": top_terms(text),
        "style_guidance": [
            "保留第一人称和项目取舍，不要改成空泛客观腔。",
            "保留脚本名、文件名、命令和指标，让文本有项目现场感。",
            "句子长度可以不均匀，但要保持项目说明的清楚表达。",
        ],
    }


def to_markdown(profile: dict[str, Any]) -> str:
    lines = [
        "# Voice Profile",
        "",
        f"- 句子数：{profile['sentences']}",
        f"- 平均句长：{profile['avg_sentence_length']}",
        f"- 句长变异系数：{profile['sentence_length_cv']}",
        f"- 作者痕迹数量：{profile['author_marker_count']}",
        f"- 连接词数量：{profile['connector_count']}",
        "",
        "## 高频词",
        "",
    ]
    for item in profile["top_terms"]:
        lines.append(f"- `{item['term']}`：{item['count']}")
    lines.extend(["", "## 风格约束", ""])
    lines.extend(f"- {item}" for item in profile["style_guidance"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a lightweight voice profile.")
    parser.add_argument("file", help="Voice sample file.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--out", help="Optional output file.")
    args = parser.parse_args()

    profile = build_voice_profile(read_text(args.file))
    output = json.dumps(profile, ensure_ascii=False, indent=2) if args.json else to_markdown(profile)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()

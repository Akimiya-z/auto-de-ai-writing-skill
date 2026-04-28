#!/usr/bin/env python3
"""Analyze Chinese text for lightweight AI-flavored writing patterns."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TEMPLATE_PATTERNS = [
    r"随着[^。！？\n]{0,18}(发展|进步|普及)",
    r"在当今(社会|时代|背景下)",
    r"不可忽视",
    r"具有(十分)?重要意义",
    r"发挥着(越来越)?重要的作用",
    r"深刻改变",
    r"带来了新的机遇和挑战",
    r"综上所述",
    r"总而言之",
    r"不难看出",
    r"毋庸置疑",
    r"显得尤为重要",
]

PATTERN_CATALOG = [
    {
        "id": "P01",
        "category": "content",
        "label": "意义拔高",
        "weight": 16,
        "patterns": [
            r"具有(十分)?重要意义",
            r"深刻改变",
            r"发挥着?(越来越)?重要的作用",
            r"现实意义",
            r"应用价值",
            r"高质量发展",
        ],
        "advice": "把宏大评价改成具体结果、数据、文件或来源要求。",
    },
    {
        "id": "P02",
        "category": "structure",
        "label": "模板化开头结尾",
        "weight": 18,
        "patterns": [
            r"随着[^。！？\n]{0,24}(发展|进步|普及)",
            r"在当今(社会|时代|内容生产背景下|背景下)",
            r"综上所述",
            r"总而言之",
            r"由此可见",
        ],
        "advice": "直接从任务、材料、项目选择或问题开始写。",
    },
    {
        "id": "P03",
        "category": "structure",
        "label": "机械连接词",
        "weight": 10,
        "patterns": [
            r"首先",
            r"其次",
            r"再次",
            r"此外",
            r"最后",
            r"一方面",
            r"另一方面",
        ],
        "advice": "保留真实逻辑关系，删除没有推理作用的排序词。",
    },
    {
        "id": "P04",
        "category": "language",
        "label": "空泛抽象词",
        "weight": 8,
        "patterns": [
            r"优化",
            r"提升",
            r"促进",
            r"推动",
            r"赋能",
            r"体系",
            r"机制",
            r"路径",
            r"价值",
            r"创新",
            r"全面",
            r"有效",
        ],
        "advice": "替换为脚本名、指标、文件、案例或具体动作。",
    },
    {
        "id": "P05",
        "category": "rhetoric",
        "label": "二元平衡套话",
        "weight": 12,
        "patterns": [
            r"机遇和挑战",
            r"不仅[^。！？]{0,18}也",
            r"不但[^。！？]{0,18}而且",
            r"一方面[^。！？]{0,32}另一方面",
            r"既[^。！？]{0,18}又",
        ],
        "advice": "改成一个明确取舍：为什么这样做，放弃了什么。",
    },
    {
        "id": "P06",
        "category": "evidence",
        "label": "模糊归因",
        "weight": 14,
        "patterns": [
            r"研究表明",
            r"相关资料显示",
            r"专家认为",
            r"普遍认为",
            r"大量实践证明",
        ],
        "advice": "补充来源，或删掉无法证明的归因。",
    },
    {
        "id": "P07",
        "category": "voice",
        "label": "作者痕迹不足",
        "weight": 14,
        "patterns": [],
        "advice": "加入来源背景、个人判断、项目取舍、调试记录或真实材料。",
    },
    {
        "id": "P08",
        "category": "style",
        "label": "句长过于均匀",
        "weight": 10,
        "patterns": [],
        "advice": "混合短句和长句，不要每句都保持同一种长度。",
    },
]

VAGUE_WORDS = [
    "相关",
    "方面",
    "一定程度",
    "多元化",
    "智能化",
    "高效",
    "显著",
    "重要",
    "积极",
    "有效",
    "全面",
    "优化",
    "提升",
    "推动",
    "促进",
    "赋能",
    "体系",
    "机制",
    "路径",
    "价值",
    "意义",
    "发展",
    "创新",
]

CONNECTORS = [
    "首先",
    "其次",
    "再次",
    "此外",
    "同时",
    "另外",
    "最后",
    "因此",
    "然而",
    "总之",
    "综上所述",
    "一方面",
    "另一方面",
]

DETAIL_PATTERNS = [
    r"\d+",
    r"\d{4}年",
    r"第[一二三四五六七八九十]\w*次",
    r"(来源|案例|实验|数据集|模型|代码|GitHub|项目|报告|脚本|命令)",
    r"(表|图|公式|代码|日志|截图|问卷|访谈|案例)",
    r"《[^》]+》",
    r"[A-Za-z][A-Za-z0-9_-]{2,}",
]

AUTHOR_PATTERNS = [
    r"我",
    r"我们",
    r"本次",
    r"这次",
    r"我的",
    r"我在",
    r"我认为",
    r"我发现",
    r"实验中",
    r"项目中",
]


@dataclass
class SentenceRisk:
    sentence: str
    score: float
    reasons: list[str]
    pattern_ids: list[str]


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?；;])|\n+", text)
    return [part.strip() for part in parts if part.strip()]


def count_regexes(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def count_words(text: str, words: list[str]) -> dict[str, int]:
    return {word: text.count(word) for word in words if text.count(word) > 0}


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def catalog_hits(text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for item in PATTERN_CATALOG:
        patterns = item["patterns"]
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text, flags=re.IGNORECASE))
        if matches:
            normalized = [
                "".join(match) if isinstance(match, tuple) else str(match)
                for match in matches
            ]
            hits.append(
                {
                    "id": item["id"],
                    "category": item["category"],
                    "label": item["label"],
                    "count": len(normalized),
                    "weight": item["weight"],
                    "examples": normalized[:5],
                    "advice": item["advice"],
                }
            )
    return hits


def category_scores(pattern_hits: list[dict[str, Any]], sentence_count: int) -> dict[str, float]:
    scores: dict[str, float] = {}
    for hit in pattern_hits:
        category = hit["category"]
        scores.setdefault(category, 0.0)
        scores[category] += hit["count"] * hit["weight"]
    return {
        category: round(clamp(score / max(1, sentence_count) * 8), 2)
        for category, score in sorted(scores.items())
    }


def sentence_catalog_hits(sentence: str) -> tuple[float, list[str], list[str]]:
    score = 0.0
    labels: list[str] = []
    ids: list[str] = []
    for item in PATTERN_CATALOG:
        if not item["patterns"]:
            continue
        count = count_regexes(sentence, item["patterns"])
        if count:
            score += count * item["weight"]
            labels.append(str(item["label"]))
            ids.append(str(item["id"]))
    return score, labels, ids


def sentence_risks(sentences: list[str]) -> list[SentenceRisk]:
    risks: list[SentenceRisk] = []
    for sentence in sentences:
        reasons: list[str] = []
        pattern_ids: list[str] = []
        score = 0.0
        catalog_score, catalog_labels, catalog_ids = sentence_catalog_hits(sentence)
        template_hits = count_regexes(sentence, TEMPLATE_PATTERNS)
        vague_hits = sum(sentence.count(word) for word in VAGUE_WORDS)
        connector_hits = sum(sentence.count(word) for word in CONNECTORS)
        detail_hits = count_regexes(sentence, DETAIL_PATTERNS)
        author_hits = count_regexes(sentence, AUTHOR_PATTERNS)

        if catalog_score:
            score += catalog_score
            reasons.extend(catalog_labels)
            pattern_ids.extend(catalog_ids)
        if template_hits:
            score += 35 * template_hits
            reasons.append("模板化开头或总结")
        if vague_hits >= 2:
            score += 8 * vague_hits
            reasons.append("抽象词密集")
        if connector_hits >= 2:
            score += 10 * connector_hits
            reasons.append("连接词堆叠")
        if len(sentence) >= 36 and detail_hits == 0:
            score += 25
            reasons.append("长句缺少具体细节")
        if len(sentence) >= 28 and author_hits == 0 and detail_hits == 0:
            score += 15
            reasons.append("缺少作者痕迹")
            pattern_ids.append("P07")

        if score > 0:
            risks.append(
                SentenceRisk(
                    sentence=sentence,
                    score=clamp(score),
                    reasons=list(dict.fromkeys(reasons)),
                    pattern_ids=list(dict.fromkeys(pattern_ids)),
                )
            )

    return sorted(risks, key=lambda item: item.score, reverse=True)


def analyze_text(text: str) -> dict[str, Any]:
    clean = text.strip()
    sentences = split_sentences(clean)
    sentence_lengths = [len(sentence) for sentence in sentences] or [0]
    char_count = len(re.sub(r"\s+", "", clean))
    sentence_count = max(1, len(sentences))
    avg_len = statistics.mean(sentence_lengths)
    stdev_len = statistics.pstdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
    cv = stdev_len / avg_len if avg_len else 0.0

    template_count = count_regexes(clean, TEMPLATE_PATTERNS)
    vague_counts = count_words(clean, VAGUE_WORDS)
    connector_counts = count_words(clean, CONNECTORS)
    detail_count = count_regexes(clean, DETAIL_PATTERNS)
    author_count = count_regexes(clean, AUTHOR_PATTERNS)

    repeated_connectors = sum(max(0, count - 1) for count in connector_counts.values())
    vague_total = sum(vague_counts.values())
    connector_total = sum(connector_counts.values())
    pattern_hits = catalog_hits(clean)
    categories = category_scores(pattern_hits, sentence_count)

    template_score = clamp(template_count / sentence_count * 180)
    vague_score = clamp(vague_total / max(1, char_count / 180) * 18)
    connector_score = clamp((connector_total / sentence_count * 70) + repeated_connectors * 10)
    uniformity_score = clamp((0.48 - cv) / 0.48 * 100) if sentence_count >= 4 else 35.0
    detail_gap_score = clamp(100 - detail_count / sentence_count * 85)
    author_gap_score = clamp(100 - author_count / sentence_count * 120)

    components = {
        "template_score": round(template_score, 2),
        "vague_score": round(vague_score, 2),
        "connector_score": round(connector_score, 2),
        "uniformity_score": round(uniformity_score, 2),
        "detail_gap_score": round(detail_gap_score, 2),
        "author_gap_score": round(author_gap_score, 2),
    }

    ai_like_rate = (
        0.25 * template_score
        + 0.20 * vague_score
        + 0.15 * connector_score
        + 0.15 * uniformity_score
        + 0.15 * detail_gap_score
        + 0.10 * author_gap_score
    )

    risks = sentence_risks(sentences)
    return {
        "ai_like_rate": round(clamp(ai_like_rate), 2),
        "components": components,
        "category_scores": categories,
        "pattern_hits": pattern_hits,
        "counts": {
            "characters": char_count,
            "sentences": len(sentences),
            "template_patterns": template_count,
            "vague_words": vague_total,
            "connectors": connector_total,
            "repeated_connectors": repeated_connectors,
            "concrete_details": detail_count,
            "author_markers": author_count,
        },
        "sentence_stats": {
            "avg_length": round(avg_len, 2),
            "stdev_length": round(stdev_len, 2),
            "cv": round(cv, 4),
        },
        "top_risk_sentences": [
            {
                "score": round(item.score, 2),
                "sentence": item.sentence,
                "reasons": item.reasons,
                "pattern_ids": item.pattern_ids,
            }
            for item in risks[:8]
        ],
    }


def format_summary(result: dict[str, Any]) -> str:
    lines = [
        f"AI-like Rate: {result['ai_like_rate']:.2f}%",
        "",
        "Component scores:",
    ]
    for key, value in result["components"].items():
        lines.append(f"- {key}: {value:.2f}")
    if result["category_scores"]:
        lines.extend(["", "Category scores:"])
        for key, value in result["category_scores"].items():
            lines.append(f"- {key}: {value:.2f}")
    if result["pattern_hits"]:
        lines.extend(["", "Pattern hits:"])
        for item in result["pattern_hits"]:
            lines.append(
                f"- {item['id']} {item['label']}: {item['count']} "
                f"({item['category']})"
            )
    lines.extend(["", "Counts:"])
    for key, value in result["counts"].items():
        lines.append(f"- {key}: {value}")
    if result["top_risk_sentences"]:
        lines.extend(["", "Top risk sentences:"])
        for item in result["top_risk_sentences"]:
            reasons = "、".join(item["reasons"])
            lines.append(f"- [{item['score']:.1f}] {item['sentence']} ({reasons})")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Chinese AI-flavored writing patterns.")
    parser.add_argument("file", help="Text or Markdown file to analyze.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = analyze_text(read_text(args.file))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_summary(result))


if __name__ == "__main__":
    main()

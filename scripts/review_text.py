#!/usr/bin/env python3
"""Independently review a revised draft before accepting an AI-like score drop."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CLAIM_RISK_PATTERNS = [
    r"保证[^。！？]{0,20}(通过|降低|不会)",
    r"(一定|必然|完全|彻底)[^。！？]{0,20}(通过|降低|消除)",
    r"通过所有[^。！？]{0,12}检测",
    r"绕过[^。！？]{0,12}检测",
    r"规避[^。！？]{0,12}检测",
    r"骗过[^。！？]{0,12}检测",
]

UNSUPPORTED_ATTRIBUTION_PATTERNS = [
    r"研究表明",
    r"相关资料显示",
    r"专家认为",
    r"普遍认为",
    r"大量实践证明",
]

BOILERPLATE_PATTERNS = [
    r"这里依据",
    r"来限定范围",
    r"source brief 中",
    r"作为改写依据",
]


def read_text(path: str | Path | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?；;])|\n+", text)
    return [part.strip() for part in parts if part.strip()]


def char_bigrams(text: str) -> set[str]:
    clean = compact(text)
    return {clean[index : index + 2] for index in range(max(0, len(clean) - 1))}


def jaccard_similarity(left: str, right: str) -> float:
    left_bigrams = char_bigrams(left)
    right_bigrams = char_bigrams(right)
    if not left_bigrams or not right_bigrams:
        return 0.0
    return len(left_bigrams & right_bigrams) / len(left_bigrams | right_bigrams)


def code_terms(text: str) -> list[str]:
    terms: list[str] = []
    patterns = [
        r"`([^`]{2,60})`",
        r"\b[\w.-]+\.(?:py|md|yaml|yml|json|txt|csv|xlsx)\b",
        r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b",
        r"\d+(?:\.\d+)?%?",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            value = match.group(1) if match.groups() else match.group(0)
            value = value.strip("` ，。；;:：")
            basename = value.rsplit("/", 1)[-1]
            if any(existing.rsplit("/", 1)[-1] == basename for existing in terms):
                continue
            if 2 <= len(value) <= 60:
                terms.append(value)
    return terms


def chinese_terms(text: str) -> list[str]:
    terms: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        line = re.sub(r"^[-*]\s*", "", line)
        chunks = re.findall(r"[\u4e00-\u9fff]{4,12}", line)
        for chunk in chunks:
            if chunk not in terms:
                terms.append(chunk)
    return terms


def evidence_terms(source: str, notes: str) -> list[str]:
    terms = code_terms(source + "\n" + notes) + chinese_terms(notes)
    filtered: list[str] = []
    for term in terms:
        if term.lower() in {"source", "brief", "goal", "requirements"}:
            continue
        if term not in filtered:
            filtered.append(term)
    return filtered[:24]


def evidence_coverage(revised: str, terms: list[str]) -> dict[str, Any]:
    if not terms:
        return {
            "score": 100.0,
            "terms_total": 0,
            "terms_matched": 0,
            "matched_terms": [],
            "missing_terms": [],
        }
    matched = [term for term in terms if term in revised]
    expected = min(len(terms), 8)
    score = min(100.0, len(matched) / expected * 100)
    return {
        "score": round(score, 2),
        "terms_total": len(terms),
        "terms_matched": len(matched),
        "matched_terms": matched[:12],
        "missing_terms": [term for term in terms if term not in matched][:12],
    }


def quality_score(original: str, revised: str) -> tuple[float, list[str], dict[str, Any]]:
    warnings: list[str] = []
    original_len = max(1, len(compact(original)))
    revised_len = len(compact(revised))
    ratio = revised_len / original_len
    similarity = jaccard_similarity(original, revised)
    sentence_lengths = [len(sentence) for sentence in split_sentences(revised)]
    avg_sentence = sum(sentence_lengths) / max(1, len(sentence_lengths))

    score = 100.0
    if ratio < 0.65:
        score -= 30
        warnings.append("修改稿过短，可能删掉了原文论点。")
    elif ratio > 1.85:
        score -= 20
        warnings.append("修改稿明显膨胀，可能靠堆材料降低分数。")

    if similarity > 0.92:
        score -= 25
        warnings.append("修改幅度过小。")
    elif similarity < 0.24:
        score -= 25
        warnings.append("修改稿和原文差异过大，需要人工确认是否漂移。")

    if avg_sentence > 70:
        score -= 10
        warnings.append("平均句长偏长，可读性不足。")

    metrics = {
        "length_ratio": round(ratio, 3),
        "jaccard_similarity": round(similarity, 3),
        "avg_sentence_length": round(avg_sentence, 2),
    }
    return max(0.0, score), warnings, metrics


def integrity_score(revised: str) -> tuple[float, list[str], list[str]]:
    warnings: list[str] = []
    blockers: list[str] = []
    score = 100.0

    claim_hits = [
        match.group(0)
        for pattern in CLAIM_RISK_PATTERNS
        for match in re.finditer(pattern, revised)
    ]
    if claim_hits:
        blockers.append("出现绕过检测或保证通过检测的表述。")
        score -= 45

    attribution_hits = [
        match.group(0)
        for pattern in UNSUPPORTED_ATTRIBUTION_PATTERNS
        for match in re.finditer(pattern, revised)
    ]
    if attribution_hits:
        score -= 20
        warnings.append("出现模糊归因，需要补充来源或删除。")

    has_limitation = (
        "检测分数" in revised
        and ("实验指标" in revised or "概率" in revised)
        and ("不能证明" in revised or "不证明" in revised)
    )
    if not has_limitation:
        blockers.append("缺少检测分数局限说明。")
        score -= 30

    return max(0.0, score), warnings, blockers


def anti_gaming_score(revised: str) -> tuple[float, list[str], list[str], dict[str, Any]]:
    warnings: list[str] = []
    blockers: list[str] = []
    clean_len = max(1, len(compact(revised)))
    code_token_count = len(code_terms(revised))
    code_density = code_token_count / clean_len * 1000
    boilerplate_hits = sum(len(re.findall(pattern, revised)) for pattern in BOILERPLATE_PATTERNS)

    score = 100.0
    if code_density > 34:
        score -= 25
        warnings.append("文件名、英文标记或数字密度偏高，疑似堆具体词。")
    if boilerplate_hits >= 4:
        score -= 25
        warnings.append("来源限定短语重复过多，文本显得机械。")
    if boilerplate_hits >= 7:
        blockers.append("重复来源限定短语过多。")

    metrics = {
        "code_token_count": code_token_count,
        "code_token_density_per_1000_chars": round(code_density, 2),
        "boilerplate_hits": boilerplate_hits,
    }
    return max(0.0, score), warnings, blockers, metrics


def review_candidate(
    original: str,
    revised: str,
    notes: str = "",
    source: str = "",
    min_score: float = 70.0,
) -> dict[str, Any]:
    terms = evidence_terms(source, notes)
    coverage = evidence_coverage(revised, terms)
    quality, quality_warnings, quality_metrics = quality_score(original, revised)
    integrity, integrity_warnings, integrity_blockers = integrity_score(revised)
    anti_gaming, gaming_warnings, gaming_blockers, gaming_metrics = anti_gaming_score(revised)

    score = (
        0.35 * float(coverage["score"])
        + 0.25 * quality
        + 0.20 * integrity
        + 0.20 * anti_gaming
    )
    blockers = integrity_blockers + gaming_blockers
    if terms and coverage["terms_matched"] < min(3, len(terms)):
        blockers.append("修改稿没有吸收足够的来源或作者材料。")

    warnings = quality_warnings + integrity_warnings + gaming_warnings
    passed = score >= min_score and not blockers
    return {
        "pass": passed,
        "audit_score": round(score, 2),
        "min_score": min_score,
        "components": {
            "evidence_coverage": coverage["score"],
            "quality": round(quality, 2),
            "integrity": round(integrity, 2),
            "anti_gaming": round(anti_gaming, 2),
        },
        "blockers": blockers,
        "warnings": warnings,
        "evidence": coverage,
        "metrics": quality_metrics | gaming_metrics,
    }


def format_result(result: dict[str, Any]) -> str:
    status = "通过" if result["pass"] else "未通过"
    lines = [
        f"审查结果: {status}",
        f"审查分: {result['audit_score']:.2f} / 100",
        "",
        "组件分:",
    ]
    for key, value in result["components"].items():
        lines.append(f"- {key}: {float(value):.2f}")
    if result["blockers"]:
        lines.extend(["", "阻断项:"])
        lines.extend(f"- {item}" for item in result["blockers"])
    if result["warnings"]:
        lines.extend(["", "警告:"])
        lines.extend(f"- {item}" for item in result["warnings"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Review whether a revised draft should be accepted.")
    parser.add_argument("--original", required=True, help="Original draft file.")
    parser.add_argument("--revised", required=True, help="Revised draft file.")
    parser.add_argument("--notes", help="Author notes file.")
    parser.add_argument("--source", help="Source brief file.")
    parser.add_argument("--min-score", type=float, default=70.0, help="Minimum audit score.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = review_candidate(
        read_text(args.original),
        read_text(args.revised),
        notes=read_text(args.notes),
        source=read_text(args.source),
        min_score=args.min_score,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result))


if __name__ == "__main__":
    main()

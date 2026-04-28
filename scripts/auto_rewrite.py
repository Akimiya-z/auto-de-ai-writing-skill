#!/usr/bin/env python3
"""Create a local revised draft from detector output and author materials."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from analyze_text import (
    AUTHOR_PATTERNS,
    CONNECTORS,
    DETAIL_PATTERNS,
    count_regexes,
    sentence_risks,
    split_sentences,
)


REPLACEMENTS = [
    (r"(如何[^。！？]{0,80})，?已经成为一个具有重要意义的问题", r"本次要验证的是\1"),
    (r"对于([^。！？]{1,60})具有(十分)?重要意义", r"在\1场景下可以作为可检查的展示案例"),
    (r"随着([^。！？\n]{0,28})(发展|进步|普及)，?", ""),
    (r"在当今(社会|时代|内容生产背景下|背景下)，?", "在本次材料中，"),
    (r"一方面，?([^。！？]{1,50})，另一方面，?([^。！？]{1,50})", r"\1；\2"),
    (r"另一方面，?", ""),
    (r"不仅能够([^，。！？]{1,30})，?也能够", r"会"),
    (r"综上所述，?", ""),
    (r"总而言之，?", ""),
    (r"不难看出，?", ""),
    (r"毋庸置疑，?", ""),
    (r"具有(十分)?重要意义", "对应一个可检查的处理目标"),
    (r"发挥着?(越来越)?重要的作用", "承担具体处理步骤"),
    (r"深刻改变", "改变"),
    (r"可以发挥重要作用", "可以承担版本记录和流程复现"),
    (r"应用价值", "可复现结果"),
    (r"现实意义", "实验指标意义"),
    (r"全面分析", "按模板表达、空泛词、连接词和作者痕迹等指标分析"),
    (r"进行优化", "按风险句子修改"),
    (r"优化", "具体化"),
    (r"进一步提升文本质量", "复查修改前后的指标变化"),
    (r"有效提升文本的人类化程度", "降低本地 AI-like Rate"),
    (r"有效降低 AI 生成文本的 AI 率", "降低本地 AI-like Rate"),
    (r"充分体现降重效果", "在报告中展示指标变化"),
    (r"充分体现文本优化效果", "在报告中展示修改效果"),
    (r"内容结构更加合理", "段落围绕来源、实现和限制展开"),
    (r"增强项目的规范性和完整性", "保留可复现的输入、输出和限制说明"),
    (r"并不是简单的文字替换，而是需要综合考虑", "需要同时检查"),
    (r"不是简单的文字替换，而是需要综合考虑", "需要同时检查"),
]

LEADING_CONNECTOR_RE = re.compile(
    r"^(首先|其次|再次|此外|同时|另外|最后|因此|然而|一方面|另一方面)[，,]?"
)


def read_text(path: str | Path | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def first_heading(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if lines and lines[0].startswith("#"):
        return lines[0].strip(), "\n".join(lines[1:]).strip()
    return "", text.strip()


def material_lines(text: str, limit: int = 8) -> list[str]:
    lines: list[str] = []
    in_code = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line:
            continue
        if line.startswith("|") or line in {"---", "$$"}:
            continue
        if line.startswith("#"):
            continue
        line = re.sub(r"^[-*]\s*", "", line)
        line = re.sub(r"^\d+[.)]\s*", "", line)
        if not line or len(line) < 6:
            continue
        if line not in lines:
            lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def material_terms(text: str, limit: int = 8) -> list[str]:
    terms: list[str] = []
    patterns = [
        r"`([^`]{2,60})`",
        r"\b[\w.-]+\.(?:py|md|yaml|yml|json|txt|csv|xlsx)\b",
        r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            value = match.group(1) if match.groups() else match.group(0)
            value = value.strip("` ，。；;:：")
            if 2 <= len(value) <= 60 and value.lower() not in {"source", "brief"}:
                if value not in terms:
                    terms.append(value)
            if len(terms) >= limit:
                return terms
    return terms


def short_material(source: str, notes: str, limit: int = 90) -> str:
    terms = material_terms(notes + "\n" + source, 3)
    if terms:
        return "、".join(f"`{term}`" for term in terms)
    candidates = material_lines(notes, 4) + material_lines(source, 4)
    if not candidates:
        return "用户提供的来源材料和作者补充信息"
    text = display_line(candidates[0]).rstrip("。")
    return text[:limit]


def mostly_ascii(text: str) -> bool:
    letters = [char for char in text if not char.isspace()]
    if not letters:
        return False
    ascii_count = sum(1 for char in letters if ord(char) < 128)
    return ascii_count / len(letters) > 0.65


def display_line(line: str) -> str:
    if mostly_ascii(line):
        return "source brief 中的项目需求说明"
    return line


def choose_pronoun(notes: str, voice: str) -> str:
    if re.search(r"我|我的|我在|我认为|我发现", notes + voice):
        return "我"
    return "本文"


def has_detail_or_author(sentence: str) -> bool:
    return count_regexes(sentence, DETAIL_PATTERNS) > 0 or count_regexes(sentence, AUTHOR_PATTERNS) > 0


def normalize_sentence(sentence: str) -> str:
    rewritten = sentence.strip()
    for pattern, replacement in REPLACEMENTS:
        rewritten = re.sub(pattern, replacement, rewritten)
    rewritten = LEADING_CONNECTOR_RE.sub("", rewritten).strip()
    rewritten = re.sub(r"，，+", "，", rewritten)
    rewritten = re.sub(r"，。", "。", rewritten)
    rewritten = re.sub(r"^，", "", rewritten)
    rewritten = re.sub(r"\s+", " ", rewritten).strip()
    return rewritten or sentence.strip()


def rewrite_sentence(sentence: str, material_hint: str, pronoun: str, round_index: int) -> str:
    rewritten = normalize_sentence(sentence)
    return rewritten


def rewrite_paragraph(paragraph: str, material_hint: str, pronoun: str, round_index: int) -> str:
    sentences = split_sentences(paragraph)
    if not sentences:
        return paragraph.strip()
    rewritten = [
        rewrite_sentence(sentence, material_hint, pronoun, round_index)
        for sentence in sentences
    ]
    return "".join(rewritten)


def context_paragraph(source: str, notes: str, voice: str) -> str:
    terms = material_terms(notes + "\n" + source, 6)
    pronoun = choose_pronoun(notes, voice)
    if not terms and not source.strip() and not notes.strip():
        return ""

    if terms:
        term_text = "、".join(f"`{term}`" for term in terms[:5])
    else:
        source_items = material_lines(source, 1)
        term_text = display_line(source_items[0]) if source_items else "作者补充材料"
    return (
        f"本次改写先固定材料边界：{pronoun}只使用{term_text}和来源说明中的项目需求。"
        "没有依据的经历、引用和第三方检测结果不写入正文。"
    )


def limitation_paragraph(text: str) -> str:
    if "检测分数" in text and "作者身份" in text:
        return ""
    return "检测分数只作为项目内的实验指标，不能证明文本一定由 AI 或人类撰写。"


def rewrite_text(draft: str, notes: str = "", source: str = "", voice: str = "", round_index: int = 1) -> str:
    title, body = first_heading(draft)
    material_hint = short_material(source, notes)
    pronoun = choose_pronoun(notes, voice)
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", body) if paragraph.strip()]

    rewritten_parts: list[str] = []
    if title:
        rewritten_parts.append(title)

    context = context_paragraph(source, notes, voice)
    if context and context not in draft:
        rewritten_parts.append(context)

    for paragraph in paragraphs:
        if paragraph.startswith("#"):
            rewritten_parts.append(paragraph)
            continue
        rewritten_parts.append(rewrite_paragraph(paragraph, material_hint, pronoun, round_index))

    limitation = limitation_paragraph("\n\n".join(rewritten_parts))
    if limitation:
        rewritten_parts.append(limitation)

    return "\n\n".join(part for part in rewritten_parts if part).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Locally rewrite a Chinese draft using detector hints and supplied materials.")
    parser.add_argument("draft", help="Original draft file.")
    parser.add_argument("--notes", help="Author notes file.")
    parser.add_argument("--source", help="Source brief file.")
    parser.add_argument("--voice", help="Voice sample file.")
    parser.add_argument("--round", type=int, default=1, help="Rewrite round index; later rounds are more explicit.")
    parser.add_argument("--out", help="Output revised file. If omitted, print to stdout.")
    args = parser.parse_args()

    revised = rewrite_text(
        read_text(args.draft),
        notes=read_text(args.notes),
        source=read_text(args.source),
        voice=read_text(args.voice),
        round_index=args.round,
    )
    if args.out:
        Path(args.out).write_text(revised, encoding="utf-8")
    else:
        print(revised, end="")


if __name__ == "__main__":
    main()

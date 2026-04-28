#!/usr/bin/env python3
"""Run an A/B/C detect-rewrite-review loop until the local target is met."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_rate import detect_ai_rate, read_text
from auto_rewrite import rewrite_text
from make_report import build_report
from review_text import review_candidate


@dataclass
class Iteration:
    round_index: int
    before: float
    after: float
    delta: float
    review_score: float
    review_pass: bool
    review_blockers: list[str]
    accepted: bool
    reason: str


def trace_table(iterations: list[Iteration], target_rate: float, stop_reason: str) -> str:
    lines = [
        "## 对抗式迭代记录",
        "",
        f"- 目标阈值：{target_rate:.2f}%",
        f"- 停止原因：{stop_reason}",
        "",
        "| 轮次 | 改写前 | 改写后 | 变化 | 审查分 | 审查通过 | 是否接受 | 说明 |",
        "|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for item in iterations:
        accepted = "yes" if item.accepted else "no"
        review_pass = "yes" if item.review_pass else "no"
        lines.append(
            f"| {item.round_index} | {item.before:.2f}% | {item.after:.2f}% | "
            f"{item.delta:+.2f}% | {item.review_score:.2f} | {review_pass} | "
            f"{accepted} | {item.reason} |"
        )
    lines.append("")
    return "\n".join(lines)


def audit_section(review_result: dict[str, Any]) -> str:
    status = "通过" if review_result["pass"] else "未通过"
    lines = [
        "## 独立审查结果",
        "",
        f"- 审查状态：{status}",
        f"- 审查分：{float(review_result['audit_score']):.2f} / 100",
        f"- 最低要求：{float(review_result['min_score']):.2f}",
        "",
        "| 组件 | 分数 |",
        "|---|---:|",
    ]
    for key, value in review_result.get("components", {}).items():
        lines.append(f"| `{key}` | {float(value):.2f} |")

    evidence = review_result.get("evidence", {})
    matched = "、".join(evidence.get("matched_terms", [])[:8]) or "无"
    lines.extend(
        [
            "",
            f"- 来源/作者材料命中：{evidence.get('terms_matched', 0)} / {evidence.get('terms_total', 0)}",
            f"- 命中材料：{matched}",
        ]
    )

    if review_result.get("blockers"):
        lines.extend(["", "阻断项："])
        lines.extend(f"- {item}" for item in review_result["blockers"])
    if review_result.get("warnings"):
        lines.extend(["", "警告："])
        lines.extend(f"- {item}" for item in review_result["warnings"])
    lines.append("")
    return "\n".join(lines)


def insert_before_raw_json(report: str, addition: str) -> str:
    marker = "\n## 原始 JSON 结果\n"
    if marker not in report:
        return report.rstrip() + "\n\n" + addition.rstrip() + "\n"
    return report.replace(marker, "\n\n" + addition.rstrip() + "\n" + marker, 1)


def run_loop(
    original_path: Path,
    notes_path: Path | None,
    source_path: Path | None,
    voice_path: Path | None,
    target_rate: float,
    max_rounds: int,
    min_delta: float,
    min_review_score: float,
    provider: str,
) -> tuple[str, dict[str, Any], dict[str, Any], list[Iteration], str]:
    original_text = read_text(original_path)
    current_text = original_text
    notes = read_text(notes_path) if notes_path else ""
    source = read_text(source_path) if source_path else ""
    voice = read_text(voice_path) if voice_path else ""

    current_result = detect_ai_rate(current_text, provider=provider)
    current_review = review_candidate(
        original_text,
        current_text,
        notes=notes,
        source=source,
        min_score=min_review_score,
    )
    iterations: list[Iteration] = []
    stop_reason = "reached max rounds"

    if float(current_result["ai_rate"]) <= target_rate and current_review["pass"]:
        return current_text, current_result, current_review, iterations, "original already meets target and review"

    for round_index in range(1, max_rounds + 1):
        before_score = float(current_result["ai_rate"])
        before_review_score = float(current_review["audit_score"])
        candidate_text = rewrite_text(
            current_text,
            notes=notes,
            source=source,
            voice=voice,
            round_index=round_index,
        )
        candidate_result = detect_ai_rate(candidate_text, provider=provider)
        after_score = float(candidate_result["ai_rate"])
        delta = before_score - after_score
        candidate_review = review_candidate(
            original_text,
            candidate_text,
            notes=notes,
            source=source,
            min_score=min_review_score,
        )
        candidate_review_score = float(candidate_review["audit_score"])
        review_pass = bool(candidate_review["pass"])
        review_blockers = list(candidate_review.get("blockers", []))

        if after_score > before_score:
            iterations.append(
                Iteration(
                    round_index=round_index,
                    before=before_score,
                    after=after_score,
                    delta=delta,
                    review_score=candidate_review_score,
                    review_pass=review_pass,
                    review_blockers=review_blockers,
                    accepted=False,
                    reason="candidate worsened detector score",
                )
            )
            stop_reason = "candidate worsened score"
            break

        if review_blockers:
            iterations.append(
                Iteration(
                    round_index=round_index,
                    before=before_score,
                    after=after_score,
                    delta=delta,
                    review_score=candidate_review_score,
                    review_pass=review_pass,
                    review_blockers=review_blockers,
                    accepted=False,
                    reason=f"review gate blocked: {review_blockers[0]}",
                )
            )
            stop_reason = "review gate blocked"
            break

        if candidate_review_score + 0.01 < before_review_score and not review_pass:
            iterations.append(
                Iteration(
                    round_index=round_index,
                    before=before_score,
                    after=after_score,
                    delta=delta,
                    review_score=candidate_review_score,
                    review_pass=review_pass,
                    review_blockers=review_blockers,
                    accepted=False,
                    reason="review score regressed",
                )
            )
            stop_reason = "review score regressed"
            break

        current_text = candidate_text
        current_result = candidate_result
        current_review = candidate_review
        accepted_reason = "accepted"
        if after_score <= target_rate and review_pass:
            accepted_reason = "target and review reached"
        elif after_score <= target_rate:
            accepted_reason = "score target reached; review pending"
        elif delta < min_delta:
            accepted_reason = "delta below minimum"

        iterations.append(
            Iteration(
                round_index=round_index,
                before=before_score,
                after=after_score,
                delta=delta,
                review_score=candidate_review_score,
                review_pass=review_pass,
                review_blockers=review_blockers,
                accepted=True,
                reason=accepted_reason,
            )
        )

        if after_score <= target_rate and review_pass:
            stop_reason = "target and review reached"
            break
        if delta < min_delta:
            stop_reason = "delta below minimum"
            break
    else:
        stop_reason = "reached max rounds"

    if float(current_result["ai_rate"]) <= target_rate and not current_review["pass"]:
        stop_reason = "score target reached but review not passed"

    return current_text, current_result, current_review, iterations, stop_reason


def write_json_trace(
    path: Path,
    iterations: list[Iteration],
    stop_reason: str,
    final_review: dict[str, Any],
) -> None:
    payload = {
        "stop_reason": stop_reason,
        "final_review": final_review,
        "iterations": [item.__dict__ for item in iterations],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a detector-rewriter loop and generate a report.")
    parser.add_argument("--original", required=True, help="Original draft file.")
    parser.add_argument("--notes", help="Author notes file.")
    parser.add_argument("--source", help="Source brief file.")
    parser.add_argument("--voice", help="Voice sample file.")
    parser.add_argument("--target-rate", type=float, default=25.0, help="Stop when AI-like rate is at or below this value.")
    parser.add_argument("--max-rounds", type=int, default=5, help="Maximum rewrite rounds.")
    parser.add_argument("--min-delta", type=float, default=1.0, help="Stop when improvement is smaller than this value.")
    parser.add_argument("--min-review-score", type=float, default=70.0, help="Minimum independent review score.")
    parser.add_argument("--provider", choices=["auto", "sapling", "local"], default="local", help="Detector provider.")
    parser.add_argument("--out", required=True, help="Final revised text file.")
    parser.add_argument("--report", required=True, help="Final Markdown report file.")
    parser.add_argument("--trace-json", help="Optional JSON trace file.")
    parser.add_argument("--generated-at", help="Optional report timestamp for reproducible examples.")
    args = parser.parse_args()

    original_path = Path(args.original)
    notes_path = Path(args.notes) if args.notes else None
    source_path = Path(args.source) if args.source else None
    voice_path = Path(args.voice) if args.voice else None
    out_path = Path(args.out)
    report_path = Path(args.report)

    original_result = detect_ai_rate(read_text(original_path), provider=args.provider)
    revised_text, revised_result, final_review, iterations, stop_reason = run_loop(
        original_path=original_path,
        notes_path=notes_path,
        source_path=source_path,
        voice_path=voice_path,
        target_rate=args.target_rate,
        max_rounds=args.max_rounds,
        min_delta=args.min_delta,
        min_review_score=args.min_review_score,
        provider=args.provider,
    )
    out_path.write_text(revised_text, encoding="utf-8")

    report = build_report(
        original_path,
        out_path,
        original_result,
        revised_result,
        notes_path=notes_path,
        source_path=source_path,
        generated_at=args.generated_at,
    )
    loop_sections = (
        audit_section(final_review).rstrip()
        + "\n\n"
        + trace_table(iterations, args.target_rate, stop_reason).rstrip()
    )
    report = insert_before_raw_json(report, loop_sections)
    report_path.write_text(report, encoding="utf-8")

    if args.trace_json:
        write_json_trace(Path(args.trace_json), iterations, stop_reason, final_review)

    print(f"original: {float(original_result['ai_rate']):.2f}%")
    print(f"revised: {float(revised_result['ai_rate']):.2f}%")
    print(f"stop: {stop_reason}")


if __name__ == "__main__":
    main()

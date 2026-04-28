#!/usr/bin/env python3
"""Calculate a normalized AI rate with optional Sapling API support."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from analyze_text import analyze_text


SAPLING_ENDPOINT = "https://api.sapling.ai/api/v1/aidetect"


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def sapling_detect(text: str, api_key: str) -> dict[str, Any]:
    payload = json.dumps(
        {
            "key": api_key,
            "text": text,
            "sent_scores": True,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        SAPLING_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    score = float(data["score"])
    return {
        "ai_rate": round(score * 100, 2),
        "provider": "sapling",
        "details": {
            "raw_score": score,
            "sentence_scores": data.get("sentence_scores", []),
            "message": "Sapling AI Detector API returned a score in [0, 1].",
        },
    }


def local_detect(text: str) -> dict[str, Any]:
    analysis = analyze_text(text)
    return {
        "ai_rate": analysis["ai_like_rate"],
        "provider": "local-ai-like",
        "details": analysis,
    }


def detect_ai_rate(text: str, provider: str = "auto", fallback: bool = True) -> dict[str, Any]:
    if provider not in {"auto", "sapling", "local"}:
        raise ValueError("provider must be one of: auto, sapling, local")

    if provider == "local":
        return local_detect(text)

    api_key = os.getenv("SAPLING_API_KEY", "").strip()
    if provider in {"auto", "sapling"} and api_key:
        try:
            return sapling_detect(text, api_key)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, TimeoutError) as exc:
            if not fallback or provider == "sapling":
                raise RuntimeError(f"Sapling detection failed: {exc}") from exc
            result = local_detect(text)
            result["details"]["fallback_reason"] = f"Sapling detection failed: {exc}"
            return result

    if provider == "sapling" and not api_key:
        raise RuntimeError("SAPLING_API_KEY is not set.")

    result = local_detect(text)
    if not api_key:
        result["details"]["fallback_reason"] = "SAPLING_API_KEY is not set; used local AI-like score."
    return result


def format_result(result: dict[str, Any]) -> str:
    lines = [
        f"AI率: {result['ai_rate']:.2f}%",
        f"provider: {result['provider']}",
    ]
    details = result.get("details", {})
    if isinstance(details, dict) and details.get("fallback_reason"):
        lines.append(f"fallback: {details['fallback_reason']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate AI rate for a text or Markdown file.")
    parser.add_argument("file", help="Text or Markdown file to detect.")
    parser.add_argument(
        "--provider",
        choices=["auto", "sapling", "local"],
        default="auto",
        help="Detection provider. auto uses Sapling when SAPLING_API_KEY is set, otherwise local.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    try:
        result = detect_ai_rate(read_text(args.file), provider=args.provider)
    except Exception as exc:  # noqa: BLE001 - command-line tool should print a concise error.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result))


if __name__ == "__main__":
    main()

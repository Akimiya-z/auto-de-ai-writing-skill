#!/usr/bin/env python3
"""Run the demo pipeline end to end."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("$ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run demo prompt generation and adversarial loop report generation.")
    parser.add_argument("--base", default=".", help="Project root.")
    parser.add_argument("--target-rate", type=float, default=25.0, help="Demo target AI-like rate.")
    parser.add_argument("--max-rounds", type=int, default=5, help="Maximum rewrite rounds.")
    args = parser.parse_args()
    base = Path(args.base).resolve()
    py = sys.executable

    run(
        [
            py,
            "scripts/rewrite_prompt.py",
            "examples/original.md",
            "--notes",
            "examples/author_notes.md",
            "--source",
            "examples/source_brief.md",
            "--voice",
            "examples/voice_sample.md",
            "--out",
            "examples/rewrite_prompt.md",
        ],
        base,
    )
    run(
        [
            py,
            "scripts/adversarial_loop.py",
            "--original",
            "examples/original.md",
            "--notes",
            "examples/author_notes.md",
            "--source",
            "examples/source_brief.md",
            "--voice",
            "examples/voice_sample.md",
            "--target-rate",
            str(args.target_rate),
            "--max-rounds",
            str(args.max_rounds),
            "--provider",
            "local",
            "--out",
            "examples/revised.md",
            "--report",
            "examples/report.md",
            "--generated-at",
            "2026-04-28 00:00:00",
        ],
        base,
    )


if __name__ == "__main__":
    main()

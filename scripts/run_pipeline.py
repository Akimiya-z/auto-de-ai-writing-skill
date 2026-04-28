#!/usr/bin/env python3
"""Run the demo pipeline end to end."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run demo prompt generation and report generation.")
    parser.add_argument("--base", default=".", help="Project root.")
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
            "scripts/make_report.py",
            "examples/original.md",
            "examples/revised.md",
            "--notes",
            "examples/author_notes.md",
            "--source",
            "examples/source_brief.md",
            "--generated-at",
            "2026-04-28 00:00:00",
            "--out",
            "examples/report.md",
        ],
        base,
    )


if __name__ == "__main__":
    main()

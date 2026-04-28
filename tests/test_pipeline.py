from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from adversarial_loop import run_loop  # noqa: E402
from analyze_text import analyze_text  # noqa: E402
from rewrite_prompt import build_prompt  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_catalog_examples_keep_full_match(self) -> None:
        result = analyze_text("随着人工智能技术的发展，AI 文本具有重要意义。")
        examples = [
            example
            for hit in result["pattern_hits"]
            for example in hit["examples"]
        ]

        self.assertIn("随着人工智能技术的发展", examples)
        self.assertIn("具有重要意义", examples)

    def test_rewrite_prompt_is_not_demo_topic_locked(self) -> None:
        prompt = build_prompt(
            "这是一段需要改写的中文初稿。",
            notes="作者补充：来自课堂实验记录。",
            source="任务：把一段课程反思改得更具体。",
            voice_sample="我会先说明材料来源，再写自己的判断。",
        )

        self.assertIn("保留原文主题和任务要求", prompt)
        self.assertNotIn("保留主题：通过 GitHub 项目或 skill 自动降低文本的 AI-like 率", prompt)

    def test_adversarial_loop_reaches_demo_target(self) -> None:
        revised_text, revised_result, iterations, stop_reason = run_loop(
            original_path=ROOT / "examples/original.md",
            notes_path=ROOT / "examples/author_notes.md",
            source_path=ROOT / "examples/source_brief.md",
            voice_path=ROOT / "examples/voice_sample.md",
            target_rate=25.0,
            max_rounds=5,
            min_delta=1.0,
            provider="local",
        )

        self.assertLessEqual(float(revised_result["ai_rate"]), 25.0)
        self.assertEqual(stop_reason, "target reached")
        self.assertTrue(iterations)
        self.assertTrue(iterations[-1].accepted)
        self.assertIn("检测分数只作为项目内的实验指标", revised_text)


if __name__ == "__main__":
    unittest.main()

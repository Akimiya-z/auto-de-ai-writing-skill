# Source Brief: Auto De-AI Writing Skill

This source brief defines the sample scenario used by the repository. It is intentionally generic so the project can be published as a normal GitHub project.

## Goal

Build a reusable skill-style workflow that can take an AI-generated Chinese draft, identify AI-flavored writing patterns, guide a more concrete revision, and generate a reproducible before/after report.

## Requirements

- Provide a GitHub-ready project structure.
- Analyze AI-generated Chinese text automatically.
- Calculate a reproducible AI-like rate without requiring a local large model.
- Generate a structured rewrite prompt based on source material, author notes, and voice sample.
- Run a detector-rewriter loop until the local AI-like rate reaches a target threshold or stops improving.
- Add an independent review gate so the demo does not only optimize the local detector score.
- Produce a Markdown report with before/after score, reduction formula, pattern hits, high-risk sentences, and limitations.
- Keep optional third-party API support, but make the default path runnable with only Python standard library.

## Evaluation Target

The demo should show a measurable reduction from the original draft to the revised text:

$$
reduction=\frac{before-after}{before}\times100\%
$$

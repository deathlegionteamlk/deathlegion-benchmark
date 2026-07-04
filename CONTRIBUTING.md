# Contributing to Deathlegion Benchmark

Thank you for your interest in contributing to the Deathlegion Benchmark. This document outlines the standards and process for adding new problems.

## How Problems Are Added

1. **Proposal** — Open an issue with the problem's `difficulty_rationale` (minimum 200 words) explaining how it exercises one or more of the three difficulty levers.
2. **Design Review** — The problem design guide (`docs/problem_design_guide.md`) specifies the criteria each category must meet. The proposal must demonstrate compliance.
3. **Reference Solution** — Submit a working reference solution that passes the grader.
4. **Near-Miss Validation** — Submit at least one plausible wrong solution, and verify the grader correctly fails it. A problem without a verified near-miss failure case is not complete.
5. **Grader Review** — The grader spec must be unambiguous. The grading harness must not be satisfiable by hard-coding outputs for visible examples.
6. **Acceptance** — Once all criteria are met, the problem is merged.

## Quality Standards

- **No fabricated results** — All leaderboard entries must come from actual runs through the harness.
- **No leaked problems** — Problems must be original, not lifted from existing public problem sets without substantial transformation.
- **Grader integrity** — Every grader must use hidden test cases, property-based tests, or execution-trace checks — not string-matching on a single expected output.

## Running Evaluations

*Detailed instructions for running models through the harness will be added in a future phase.*

## Code of Conduct

Be respectful, constructive, and focused on the goal of building a rigorous, fair benchmark.
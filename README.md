# Deathlegion Benchmark

A coding benchmark designed to be one of the hardest in existence — with difficulty arising from three legitimate, defensible sources:

1. **Extreme algorithmic complexity** — problems requiring research-level CS/math: advanced data structures, non-obvious reductions, tight complexity bounds, numerical stability, and formal correctness reasoning.
2. **Long-horizon, multi-file agentic tasks** — real-world-style repositories with bugs or missing features spread across many files, requiring planning and multi-step execution rather than a single function.
3. **Adversarial edge cases and ambiguous specifications** — problems that look simple but hide traps: underspecified requirements, contradictory constraints, misleading examples, and cases designed to catch models that pattern-match instead of reasoning.

## Benchmarking Philosophy

A well-calibrated benchmark produces a **spread** of scores across model tiers, not a cliff. Our design targets:
- Frontier models: low-but-nonzero scores (single digits to ~20%)
- Strong open-source models: near-zero scores on the hardest problems

This spread is what makes the benchmark credible and useful. Difficulty falls out of the design principles — it is not reverse-engineered from a target percentage.

## Categories

| Category | Description | Difficulty Lever |
|---|---|---|
| **Algorithmic** | Research-level CS/math problems requiring advanced techniques and tight complexity bounds | 1 |
| **Agentic** | Multi-file repository tasks requiring cross-file reasoning, bug-finding, and multi-step fixes | 2 |
| **Adversarial** | Problems with traps, underspecified requirements, and misleading examples designed to catch pattern-matching | 3 |

## Leaderboard

*Leaderboard will be populated as models are evaluated through the harness. See [CONTRIBUTING.md](CONTRIBUTING.md) for details on running evaluations and submitting results.*

## Repository Structure

```
deathlegion-benchmark/
├── problems/          # Problem definitions (algorithmic, agentic, adversarial)
├── harness/           # Evaluation harness (runner, graders, sandbox, language adapters)
├── scoring/           # Scoring and anti-gaming utilities
├── docs/              # Documentation (problem design guide, anti-contamination, calibration)
└── tests/             # Self-tests for the harness itself
```

## License

MIT — see [LICENSE](LICENSE).
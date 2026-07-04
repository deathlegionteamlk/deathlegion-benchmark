# Problem Design Guide

## Purpose

This document is the rulebook for every problem in the Deathlegion Benchmark. It establishes:

- The criteria each category must meet to be admitted.
- The methodology for sourcing and validating problems.
- The anti-cheese constraints that prevent degenerate grading.
- The rejection checklist — falsifiable reasons a candidate problem must be thrown out.
- The scoring philosophy that determines how problems are weighted and reported.

**A problem that does not satisfy every criterion in this document is not accepted.** There is no scoring committee; the rulebook is the gate.

---

## Foundational Principle: Let the difficulty fall where it falls

The Deathlegion Benchmark is designed to apply three legitimate difficulty levers as rigorously and honestly as possible:

1. **Extreme algorithmic complexity** — problems requiring research-level CS/math.
2. **Long-horizon, multi-file agentic tasks** — real-world repos with bugs requiring cross-file reasoning and multi-step fixes.
3. **Adversarial edge cases and ambiguous specifications** — traps that catch pattern-matching rather than reasoning.

**The benchmark's job is to apply these levers correctly, then report whatever score results** — 8%, 35%, 60%. The score is diagnostic information about the problem set and the model, not a number to engineer toward. Never adjust a problem to push a score up or down unless the adjustment fixes a genuine flaw in the problem or grader. If you find yourself wanting to tune difficulty for target-score reasons, stop and flag it for review.

---

## Category 1: Algorithmic

### Threshold for admission

Every algorithmic problem must require **at least one named advanced technique** that is non-trivial to discover, implement, and debug. The technique must be necessary — not replaceable by a simpler approach with equivalent correctness and performance.

Examples of techniques that clear this threshold:

| Domain | Techniques |
|---|---|
| Data structures | Segment tree with lazy propagation, link-cut tree, suffix automaton, treap (implicit), van Emde Boas tree, persistent data structures, sqrt decomposition with Mo's algorithm on trees |
| Graphs / flows | Max flow with lower bounds, min-cost max-flow with potentials, general matching (Blossom), Gomory-Hu tree, directed MST (Edmonds/Chu-Liu), planarity testing, treewidth-based DP |
| String algorithms | Suffix array + LCP with range queries, Aho-Corasick automaton with DP, Z-algorithm family extensions, palindromic tree (Eertree), runs in strings |
| Geometry | Convex hull trick (Li Chao tree), rotating calipers, half-plane intersection, Delaunay triangulation, Minkowski sum of convex polygons |
| Math / number theory | NTT / FFT-based multiplication, Berlekamp-Massey, Kitamasa, Stern-Brocot tree for rational approximations, Pell's equation, Dirichlet convolution with sieve techniques |
| Optimization | Simplex (network flow specialization), Lagrangian relaxation on DP, divide-and-conquer DP optimization (quadrangle inequality), Aliens trick, CDQ divide-and-conquer |
| Combinatorics / probabilities | Burnside / Pólya enumeration, generating functions for explicit closed forms, matroid intersection, Kirchhoff's matrix-tree theorem for specialized graphs |

**What does NOT clear the threshold:**

- "Big-O optimize a loop" (e.g., replace O(n²) with O(n log n) using sorting).
- Standard algorithms taught in undergraduate data structures (basic BFS/DFS, Dijkstra, Bellman-Ford, basic DP, simple binary search).
- Known trick problems whose solution is widely available in competitive programming forums (e.g., "inversion count via BIT" — well-known).
- Problems solvable by a direct library call where the library does the hard part.

### Complexity bounds

- The intended solution must have a provably tight bound (upper and lower) that is non-obvious from the problem statement.
- At least one near-miss solution must exist that has worse complexity by a factor of n, log n, or an exponential gap — and the grader must correctly fail it on large test cases.

### Near-miss diversity and plausibility

The near-miss requirement is not satisfiable by a single trivial error. Every algorithmic problem must provide **at least two** distinct near-miss solutions, drawn from different failure-mode categories (see the `failure_type` enum in `schema.json`). At least one of them must be **plausible-looking** — something a competent engineer might actually submit:

- **Plausible**: A solution that uses the correct algorithm but has one unhandled edge case (empty input, sign boundary, off-by-one on a specific indexing pattern). It passes small tests and looks correct on inspection.
- **Not plausible**: A solution that uses bubble sort when the spec requires O(n log n), or that omits an entire data structure. These are important to catch too, but they don't prove the grader is strong — the plausible-looking near-miss does.

A grader that only catches obvious breakage is not proving much. The plausible near-miss must fail at least one hidden test while passing all visible samples.

### Grading

- Use **unit_test** or **property_test** graders.
- At minimum 80% of test cases must be hidden (not shown in the prompt).
- Hidden test cases must include edge cases specifically designed to break common wrong implementations (overflow, off-by-one in boundary indexing, uninitialized memory, concurrency in parallel algorithms, repeated elements, empty inputs, maximal constraint sizes).
- A reference solution must achieve 100% pass on all test cases within the time/memory limits.

---

## Category 2: Agentic

### Methodology: SWE-bench style

Agentic problems follow the SWE-bench methodology:

1. **Source** each problem from a real GitHub repository with a real open issue and a real merged PR that fixes it.
2. The candidate is given the repository (at the revision just before the fix was applied) and the issue description.
3. The candidate must produce a patch that resolves the issue.
4. Grading is done by applying the candidate's patch and running the repository's **actual test suite** — the same tests that validated the real PR.

### Curation criteria: harder than typical SWE-bench

Not all real issues are equally hard. We curate specifically for problems that are genuinely harder than a typical SWE-bench task. A problem passes curation only if it meets **at least two** of the following three criteria:

#### Criterion A: Multi-file / multi-subsystem scope

The fix must touch **at least 3 files** across **at least 2 different subsystems or modules** of the repository. A single-file bug fix or a change that only touches tests + one implementation file does not qualify.

*What this gates against:* SWE-bench contains many single-file or test-only fixes. Those are fine for breadth — they don't belong in a hard benchmark.

#### Criterion B: Requires genuine algorithmic reasoning

The fix must require the candidate to reason about a non-trivial algorithmic property to produce the correct patch. Indicators:

- The fix involves a data structure, a bound check, a numeric property, or a correctness invariant — not just a missing import, a typo, a version migration, or a config change.
- The real-world PR's discussion includes algorithmic reasoning (complexity analysis, correctness argument, edge-case enumeration).
- A candidate who does not understand the underlying algorithm will produce an incorrect patch even if they understand the codebase and can locate the relevant files.

*What this gates against:* Issues that are "hard" only because they require understanding a large unfamiliar codebase. Codebase navigation skill is real, but it's a different axis. This benchmark values the intersection of codebase navigation AND algorithmic reasoning.

#### Criterion C: Ambiguous or incomplete issue description

The issue description, taken alone, does not uniquely determine the fix. The candidate must infer intent from context — related code, comments, issue thread discussion, or system behavior — to produce the correct patch.

*What this gates against:* Issues with a crystal-clear description where the only difficulty is finding the right line. Those test grep skills, not reasoning.

### The "hard ≠ obscure" rule

**Obscurity** and **difficulty** are different properties. A problem is not hard because:

- The repository is niche and the model has seen few examples of it in training.
- The issue is from 2015 and the framework version is long-dead.
- The bug is in a rarely-used code path that no model would have seen examples of.

These are memorization/memorization-coverage effects, not reasoning difficulty. They produce noise, not signal.

**To avoid conflating the two:**

- Prefer issues from **well-known, well-represented repositories** (CPython, Django, scipy, numpy, pytorch, rust-analyzer, vscode, typescript, etc.) where a frontier model has plausibly seen thousands of examples in training — but where the **specific issue** is genuinely hard for the algorithmic/subtlety reasons above.
- If a repository or ecosystem is niche, document why the issue is still genuinely hard on algorithmic grounds (Criterion B) — and be skeptical of yourself when writing that justification.
- Flag any problem where the primary apparent difficulty is "the model probably hasn't seen this." Reject it or return to Criterion B.

### Sourcing process

1. Identify candidate repositories (well-known, active, real test suites).
2. Scan merged PRs and look for ones that touch ≥3 files across ≥2 subsystems.
3. Read the PR discussion: does it involve algorithmic reasoning?
4. Read the issue: is it ambiguous or underdetermined?
5. If ≥2 of the three criteria are met, clone the repo, determine the exact commit SHAs:
   - `pre_fix_sha`: the commit just before the fix was applied (the "before" state).
   - `fix_merge_sha`: the merge commit of the PR that fixed the issue (the "ground truth" state).
   - **Pin both SHAs.** Do not use branch names like `main` — repos change, and a benchmark that references a moving target silently drifts over time.
6. Verify the test suite passes at `fix_merge_sha` and fails at `pre_fix_sha` (the specific issue's test case fails while unrelated tests may pass). If the test suite is flaky or requires unavailable infrastructure, reject the problem (R8).
7. Construct the agentic problem: mini-repo checked out at `pre_fix_sha`, issue description, test-suite-as-grader, manifest referencing both pinned SHAs.

### Freeze and versioning

Every agentic problem manifest must record:
- `source_repo`: URL of the repository.
- `source_issue`: URL of the GitHub issue.
- `source_pr`: URL of the merged PR.
- `pre_fix_sha`: pinned commit SHA of the repository just before the fix.
- `fix_merge_sha`: pinned commit SHA of the merge commit that applied the fix.

These SHAs freeze the problem in time. A leaderboard result is valid only for the specific problem set snapshot it was evaluated against. If a repository's test suite is later updated (changing what counts as "passing"), the problem may need re-validation but its pinned SHAs remain the source of truth for the snapshot.

### Grading

- Use **agentic_test_suite** grader, which runs `pytest` (or equivalent) on the repository after applying the candidate's patch.
- The grader must verify: (a) the pre-existing test suite still passes (the fix doesn't regress), (b) the specific issue is resolved (the test that validates the fix passes).
- Partial credit is possible if the fix resolves the issue but breaks other tests, or vice versa — recorded as separate sub-scores.

---

## Category 3: Adversarial

### Taxonomy of trap types

Every adversarial problem must incorporate **at least two** distinct trap types from the following taxonomy:

#### Trap Type A: Contradictory requirements

The problem statement gives two or more requirements that are in tension or outright conflict when interpreted literally. The candidate must detect the conflict, infer the author's intent (usually from context, examples, or domain knowledge), and resolve it by prioritizing or reinterpreting one requirement.

*Example:* "Sort the array in ascending order, but if two elements differ by at most 1, keep them in their original relative order" — a requirement that's algorithmically hard (stable sort modifies relative order only for equal keys, not for elements differing by ≤1) and ambiguous about what "keep in original relative order" means when transitive chains form.

#### Trap Type B: Misleading sample I/O

The visible sample test cases suggest a simple pattern that does not generalize. A candidate that pattern-matches on the samples will write a solution that passes the samples but fails hidden tests.

*Example:* Sample input is small positive integers with simple addition. Hidden tests include negative numbers, overflow-boundary values, empty sequences, large inputs that expose complexity issues — all hinted fleetingly in the spec but not called out.

#### Trap Type C: Numeric precision / overflow / numerical stability

The problem involves operations (division, exponentiation, trigonometric, floating-point accumulation) where naive implementation produces incorrect results at boundary ranges, even though the algorithm is correct.

*Example:* Compute a probability using floating-point multiplication where underflow to zero occurs for large inputs; or compute a matrix determinant using Gaussian elimination without partial pivoting.

#### Trap Type D: Concurrency / race conditions / synchronization

The problem involves parallel or concurrent operations where a naive approach introduces subtle race conditions, deadlocks, or livelocks that are not obvious from a single-threaded reading.

*Example:* A producer-consumer setup where the specification describes requirements that seem easily satisfiable but actually require a triple-buffer or a non-trivial lock ordering that's easy to get wrong.

#### Trap Type E: Locale / timezone / encoding / cultural conventions

The problem specifies behavior that varies by locale, timezone, encoding, or cultural convention, but does not explicitly call this out. A naive candidate assumes a specific locale, producing correct-looking output that fails when tested across locales.

*Example:* A date arithmetic problem where daylight saving time boundaries cause +1 day to produce the wrong resulting date; or a string-sorting problem where locale-aware collation differs from byte-value ordering.

#### Trap Type F: Red-herring performance requirements

The problem states a performance constraint that seems demanding but is actually irrelevant — the real difficulty is correctness under ambiguous conditions. The performance constraint is a distractor.

*Example:* "Must run in O(n log n) time and O(1) extra space" — but the actual hard part is correctly handling an underspecified edge case, and the performance bound is trivially met by any reasonable approach.

#### Trap Type G: Deliberately incomplete spec

The problem omits a necessary constraint or condition. A correct solution must either (a) ask the right clarifying question, or (b) state an explicit assumption and handle all possibilities consistent with that assumption.

*Example:* "Given a list of timestamps, find anomalies" — what counts as an anomaly is undefined. The candidate must define it, implement it, and document their choice.

### Grading

- Use **property_test** or **unit_test** graders with hidden test cases that specifically exercise each trap type the problem claims to use.
- If the problem relies on incomplete specs (Trap G), the grader should accept any reasonable interpretation as long as the solution is self-consistent and handles the stated cases correctly. The grader must contain test cases from multiple reasonable interpretations.
- **A problem that is genuinely ambiguous (the right answer is unknowable even with full context) is broken, not adversarial.** There must be a resolution — the candidate just has to find it.

---

## Anti-Cheese Rules

These rules apply to every problem regardless of category.

### Rule 1: No grader can be satisfiable by hard-coding visible sample outputs

Every grader must use at least one of:

- **Hidden test cases** — test cases not shown in the prompt, covering edge cases that would fail a solution that only matches visible examples.
- **Property-based tests** — assertions about invariants, commutativity, idempotence, or consistency across random inputs, making it impossible to hard-code all possible cases.
- **Execution-trace checks** — verification that the solution uses specific data structures, algorithms, or internal operations (e.g., "must use a balanced BST," "must compute a hash of the entire input"), preventing trivial solutions from passing by output-matching.

### Rule 2: Reference solution must pass; near-miss solutions must fail

Before a problem is admitted:

1. Run the reference solution through the grader. It must pass **all** test cases (visible + hidden).
2. Run **all** near-miss solutions through the grader. Each must fail **at least one** hidden test case while passing all visible samples.
3. Log the failure evidence (which test case, what output vs. expected) for each near-miss.
4. Log a **grader confidence score**: the fraction of independently-authored near-miss solutions that the grader correctly fails. A problem with only 1 near-miss that fails has low confidence. Target: ≥3 near-misses from ≥2 different failure-mode categories, all correctly rejected.

### Grader confidence validation

A grader that catches only one type of error is weak evidence of robustness. Every problem must have its grader validated against **at least 3 independently-conceived near-miss solutions**, sourced from at least 2 distinct failure-mode categories (see `failure_type` schema enum). At least one of these must be a plausible-looking solution (passes all visible samples, looks correct on inspection, fails only on hidden edge cases).

The grader confidence score is recorded in the problem manifest as `grader_confidence: { near_miss_count: int, categories_tested: [str], plausible_near_misses: int, passes_visible_only_solutions: bool, passes_degenerate_solutions: bool }`. A confidence score with `near_miss_count < 3` or `plausible_near_misses < 1` is flagged as insufficient.

**Why this matters:** One near-miss passing correctly is consistent with luck. Three different failure modes all being caught is evidence the grader is meaningfully testing the problem.

### Rule 3: No degenerate solutions

Verify that no trivial solution exists that:

- Ignores the problem and returns a constant.
- Only handles the visible sample inputs and crashes on anything else.
- Uses an intentionally-wrong approach that happens to pass all tests by coincidence (if found, the test suite is too weak — add more edge cases).

### Rule 4: Flaky/nondeterministic problems must be detected

If a problem involves randomness, concurrency, or floating-point, run the reference solution 5 times through the grader. It must pass all 5 runs. If variance > 0 across runs (a run fails), either the grader is flaky (fix it) or the problem has unavoidable nondeterminism (flag for review — probably reject).

---

## Rejection Checklist

A candidate problem **must be rejected** if **any** of the following is true. This is a falsifiable checklist — each item has a yes/no answer, and a "yes" on any item means rejection.

| # | Criterion | What to check |
|---|---|---|
| R1 | **Solvable via memorized pattern-matching** | Can a model that doesn't understand the underlying concepts get the right answer by recognizing the problem shape from training data? If yes, it's testing memorization, not reasoning. |
| R2 | **Grader passable by a degenerate solution** | Try: return a constant; return only the sample outputs; skip the hard part and do something trivial. Does the grader pass it? If yes, the grader is broken. |
| R3 | **Agentic problem is "hard" only because it's obscure/obscure-ecosystem** | Is the primary source of difficulty that a model probably hasn't seen this repo/framework/library in training? If yes and there is no independent algorithmic-reasoning reason (Criterion B), reject. |
| R4 | **No verified near-miss failure case exists** | If you cannot write a plausible-looking but wrong solution that the grader correctly rejects, you don't understand the problem well enough to know what a wrong answer looks like, and the problem is not ready. |
| R5 | **Difficulty rationale doesn't clearly map to one or more of the three difficulty levers** | The `difficulty_rationale` field must explicitly name which lever(s) the problem exercises and how. If it reads like generic praise ("this problem is really hard"), not a specific, technical justification, reject. |
| R6 | **Ambiguity in Category 3 that is unresolvable even with reasonable stated assumptions** | If a person with full context (spec + code + reasonable domain knowledge) cannot determine the correct behavior, the problem is broken, not adversarial. The ambiguity must be resolvable — the candidate just has to work for it. |
| R7 | **Difficulty rationale is shorter than 200 characters** | Hard cut. No exceptions. |
| R8 | **Agentic problem sourced from a repository without a real test suite** | If the repo doesn't have a CI-grade test suite (pytest, cargo test, go test, etc.) that can be run automatically, the agentic grader can't operate. The problem cannot be admitted. |

---

## Scoring Philosophy

### Per-problem scoring

Each problem produces one of:

- **pass** (1.0): All test cases pass within limits.
- **partial** (0.0 < x < 1.0): Some test cases pass, some fail. The score is the fraction of passing test cases.
- **fail** (0.0): Zero test cases pass, or the solution fails to compile/run, or it times out, or it exceeds memory.

Problems that fail to compile or run are recorded as **compile_error / runtime_error / timeout / oom** — distinct from wrong-answer failures, so we can analyze what type of barrier each model hits.

### Per-category scoring

```
category_score = sum(problem_scores) / number_of_problems_in_category
```

Normalized to a 0–100% scale. Reported as a percentage with two decimal places.

### Overall scoring

```
overall_score = average of three category scores
```

All categories are weighted equally. This prevents any single category from dominating and forces balanced capability.

### Spread report

For any evaluation run across multiple models, produce:

```
{
  "overall": {"mean": float, "median": float, "min": float, "max": float, "std": float},
  "algorithmic": {same},
  "agentic": {same},
  "adversarial": {same}
}
```

This is diagnostic data. A small standard deviation means the benchmark is not distinguishing between models — either it's too hard (everyone near zero) or too easy (everyone near 100). A wide spread is the sign of good calibration.

### Partial credit

The Deathlegion Benchmark awards **pass/fail** on each test case within a problem. Within a problem, the score is `hidden_passed / hidden_total`. Visible sample tests do not count toward the score — they exist only to help the candidate understand the problem format.

### Flaky-problem handling

If a problem shows >0 variance across 5 identical runs of the reference solution (some runs fail), it is removed from scoring and flagged. No score is issued for that problem in that run until the flakiness is resolved.

---

## Version Control and Audit Trail

Every problem in the benchmark has a manifest (`manifest.json`) whose `difficulty_rationale` field must name the specific difficulty levers and trace the reasoning. The `near_miss_failures` field must list at least one verified wrong solution with evidence of grader rejection. Together these provide a complete audit trail for every problem, so anyone reviewing the benchmark can verify that each problem meets the criteria in this guide before trusting its results.
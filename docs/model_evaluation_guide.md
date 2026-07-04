# Model Evaluation Guide

This guide explains how to run AI models through the Deathlegion Benchmark evaluation harness, interpret results, and add support for new models.

## How to Run Evaluations

### Prerequisites

```bash
# Install the harness
cd deathlegion-benchmark
pip install -e .

# Ensure language toolchains are available (optional, per-problem)
sudo apt-get install g++ rustc golang-go default-jdk nodejs npm
```

### Quick Start

```bash
# Evaluate a single problem with a candidate solution
python3 harness/agentic_runner.py \
    --manifest problems/algorithmic/sample_problem/manifest.json \
    --solution /path/to/solution.py \
    --timeout 60

# Run a full evaluation suite
python3 scoring/evaluate_model.py \
    --manifest-dir problems/ \
    --model-id my-model \
    --output results.json
```

### Using the Test Script

The `scripts/test_models.sh` script provides a convenient interface for running models:

```bash
# OpenAI model
bash scripts/test_models.sh --provider openai --model gpt-4o --samples 10

# Ollama local model
bash scripts/test_models.sh --provider ollama --model codellama:13b

# OpenRouter model
bash scripts/test_models.sh --provider openrouter --model anthropic/claude-3.5-sonnet

# Full options
bash scripts/test_models.sh --help
```

### Environment Variables

| Variable | Description | Required For |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key | OpenAI provider |
| `ANTHROPIC_API_KEY` | Anthropic API key | Anthropic provider |
| `OPENROUTER_API_KEY` | OpenRouter API key | OpenRouter provider |
| `OLLAMA_HOST` | Ollama server URL (default: `http://localhost:11434`) | Ollama provider |

## Supported Model Providers

### OpenAI

Models: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`, `o1`, `o1-mini`, etc.

```bash
export OPENAI_API_KEY="sk-..."
bash scripts/test_models.sh --provider openai --model gpt-4o --samples 5
```

### Anthropic

Models: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`, `claude-3.5-sonnet`, etc.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
bash scripts/test_models.sh --provider anthropic --model claude-3-opus-20240229
```

### OpenRouter

OpenRouter provides access to many models through a single API. Use any supported model identifier.

```bash
export OPENROUTER_API_KEY="sk-or-..."
bash scripts/test_models.sh --provider openrouter --model anthropic/claude-3.5-sonnet
bash scripts/test_models.sh --provider openrouter --model google/gemini-2.0-flash-001
bash scripts/test_models.sh --provider openrouter --model meta-llama/llama-4-405b-instruct
```

### Ollama (Local)

Run models locally with Ollama. First ensure the model is pulled:

```bash
ollama pull codellama:13b
bash scripts/test_models.sh --provider ollama --model codellama:13b
```

### vLLM (Local)

For locally hosted models via vLLM's OpenAI-compatible endpoint:

```bash
bash scripts/test_models.sh --provider vllm --model /path/to/model
```

## How to Add New Models

### Adding a New Provider

1. **API Integration**: Create a Python script or modify `scripts/test_models.sh` to support the new provider's API format.

2. **Authentication**: Add the provider's authentication method (API key, OAuth, etc.) with appropriate environment variable documentation.

3. **Model Generation**: The provider script should:
   - Accept a problem prompt from the manifest
   - Send it to the model's API
   - Save the generated code to a file
   - Return the path to the generated solution

4. **Testing**: Verify the new provider works with at least 3 sample problems from different categories.

### Adding a New Model to an Existing Provider

For existing providers, simply specify the model ID:

```bash
bash scripts/test_models.sh --provider openai --model new-model-id
```

The model ID must match the provider's API model identifier.

### Custom Model Serving

For custom models served via an OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL="http://localhost:8000/v1"
bash scripts/test_models.sh --provider openai --model my-custom-model
```

## Interpreting Results

### Output Format

The evaluation produces a JSON file with the following structure:

```json
{
  "model_id": "openai/gpt-4o",
  "evaluation_timestamp": "2025-06-15T14:30:00Z",
  "total_time_s": 360.5,
  "total_problems_found": 100,
  "problems_evaluated": 95,
  "errors": 5,
  "scores": {
    "overall": {
      "pass": 15,
      "total": 95,
      "percentage": 15.8,
      "avg_score": 0.158
    },
    "categories": {
      "algorithmic": {
        "pass": 8,
        "total": 35,
        "percentage": 22.9,
        "avg_score": 0.229
      },
      "agentic": {
        "pass": 3,
        "total": 30,
        "percentage": 10.0,
        "avg_score": 0.100
      },
      "adversarial": {
        "pass": 4,
        "total": 30,
        "percentage": 13.3,
        "avg_score": 0.133
      }
    }
  },
  "results": [
    {
      "problem_id": "alg_001",
      "category": "algorithmic",
      "passed": true,
      "score": 1.0,
      "runtime_s": 12.5
    }
  ]
}
```

### Understanding Scores

- **Pass rate**: Percentage of problems where the solution passed all grader checks.
- **Average score**: Mean score across all problems (0.0 to 1.0). Useful for partial-credit graders.
- **Per-category breakdown**: Compare model performance across algorithmic, agentic, and adversarial categories.

### What to Look For

1. **Overall pass rate**: The primary metric. Compare against leaderboard baselines.
2. **Category imbalance**: A model that excels at algorithmic but struggles with adversarial problems may indicate specific weaknesses.
3. **Runtime patterns**: Unusually fast runtimes may indicate trivial solutions; very slow runtimes may indicate inefficiency.
4. **Error rate**: High error counts (>10%) suggest infrastructure issues, not model quality.

## Rate-Limit Handling

### API-Based Providers

The evaluation harness does not automatically handle API rate limits. When running evaluations against API-based models:

1. **Set reasonable concurrency**: Start with `--concurrency 1` and increase gradually.
2. **Implement backoff**: If using a custom integration script, implement exponential backoff:
   ```python
   import time
   import random
   
   def api_call_with_retry(func, max_retries=5):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               wait = 2 ** attempt + random.uniform(0, 1)
               time.sleep(wait)
       raise Exception("Max retries exceeded")
   ```
3. **Use batch APIs**: If available, use the provider's batch API for large evaluation runs.
4. **Monitor usage**: Track API usage to avoid unexpected costs.

### Recommended Rate Limits

| Provider | Recommended Concurrency | Notes |
|---|---|---|
| OpenAI | 1-3 | Tier 1: 3 RPM / Tier 5: 10,000 RPM |
| Anthropic | 1-2 | API rate limits vary by tier |
| OpenRouter | 1-3 | Depends on provider's upstream limits |
| Ollama | 1-8 | Local, no rate limits |
| vLLM | 1-4 | Local, depends on GPU memory |

## Anti-Contamination Considerations

### What Is Contamination?

Contamination (data leakage) occurs when a model has been trained on benchmark problems or their solutions, leading to inflated scores that don't reflect genuine capability.

### Deathlegion's Approach

The Deathlegion Benchmark uses several strategies to prevent contamination:

1. **Original Problems**: All problems are originally written, not derived from existing public datasets.
2. **Hidden Test Cases**: Graders use hidden test cases and property-based checks that cannot be trivially memorized.
3. **Near-Miss Validation**: Each problem includes near-miss solutions that the grader must reject, preventing models from gaming the evaluation.
4. **Versioned Snapshots**: The benchmark is versioned with pinned SHAs. Leaderboard results are tied to a specific snapshot.

### Best Practices for Evaluators

1. **Check training data**: Before evaluating, verify that your model's training data does not include the Deathlegion Benchmark problems.
2. **Avoid contamination**: Do not include benchmark problems in training data, fine-tuning datasets, or few-shot examples.
3. **Report version**: Always report the benchmark version/snapshot hash when publishing results.
4. **Use the harvester**: Always run evaluations through the official harness, not ad-hoc scripts.
5. **One-shot only**: Evaluate each problem once. Do not iterate on a problem after seeing the result.
6. **Report all results**: Publish results for all problems attempted, not just the ones that passed.

### Detecting Contamination

Signs of potential contamination include:
- **Suspiciously high scores**: A model scoring >50% on the hardest problems may be contaminated.
- **Unnatural output patterns**: Solutions that exactly match reference implementations.
- **Category imbalance**: A model that scores dramatically higher on one category than others.

If contamination is suspected, the evaluation should be re-run with a different problem set or the problems should be rephrased.

## Advanced Usage

### Partial Evaluations

```bash
# Evaluate only algorithmic problems
python3 scoring/evaluate_model.py \
    --manifest-dir problems/algorithmic/ \
    --model-id my-model \
    --output results_algorithmic.json

# Evaluate a subset of problems
python3 scoring/evaluate_model.py \
    --manifest-dir problems/ \
    --model-id my-model \
    --max-problems 10 \
    --output results_sample.json
```

### Custom Solution Directory

If your model generates solutions to a specific directory:

```bash
python3 scoring/evaluate_model.py \
    --manifest-dir problems/ \
    --model-id my-model \
    --solution-dir /path/to/generated/solutions/ \
    --output results.json
```

### Integration with CI/CD

```bash
# Example GitHub Actions workflow
name: Evaluate Model
on: [push]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run evaluation
        run: |
          bash scripts/test_models.sh \
            --provider openai \
            --model gpt-4o \
            --samples 5
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```
#!/usr/bin/env bash
# =============================================================================
# Deathlegion Benchmark — Model Test Script
# =============================================================================
#
# Runs AI models through the Deathlegion Benchmark harness.
# Supports local (Ollama/vLLM) and API-based (OpenAI, Anthropic, OpenRouter) backends.
#
# Usage:
#   bash scripts/test_models.sh --provider openai --model gpt-4o --samples 5
#   bash scripts/test_models.sh --provider ollama --model codellama:13b
#   bash scripts/test_models.sh --provider openrouter --model anthropic/claude-3.5-sonnet
#   bash scripts/test_models.sh --help
#
# Environment variables:
#   OPENAI_API_KEY      — API key for OpenAI
#   ANTHROPIC_API_KEY   — API key for Anthropic
#   OPENROUTER_API_KEY  — API key for OpenRouter
#   OLLAMA_HOST         — Ollama server URL (default: http://localhost:11434)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Defaults
PROVIDER=""
MODEL=""
SAMPLES=5
TIMEOUT=120
CONCURRENCY=1
OUTPUT_DIR="$PROJECT_DIR/results"
VERBOSE=false
DRY_RUN=false

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Run AI models through the Deathlegion Benchmark harness.

Options:
  --provider PROVIDER   Model provider: openai, anthropic, openrouter, ollama, vllm
  --model MODEL         Model identifier (e.g., gpt-4o, claude-3-opus, codellama:13b)
  --samples N           Number of sample problems to evaluate (default: 5)
  --timeout SECONDS     Timeout per problem in seconds (default: 120)
  --concurrency N       Number of concurrent evaluations (default: 1)
  --output-dir DIR      Directory for results (default: results/)
  --verbose             Print detailed output
  --dry-run             Show what would be done without executing
  --help                Show this help message and exit

Supported Providers:
  openai       — OpenAI API (requires OPENAI_API_KEY)
  anthropic    — Anthropic API (requires ANTHROPIC_API_KEY)
  openrouter   — OpenRouter API (requires OPENROUTER_API_KEY)
  ollama       — Local Ollama server (http://localhost:11434)
  vllm         — Local vLLM server (http://localhost:8000)

Examples:
  $(basename "$0") --provider openai --model gpt-4o --samples 10
  $(basename "$0") --provider ollama --model codellama:13b
  $(basename "$0") --provider openrouter --model anthropic/claude-3.5-sonnet
EOF
    exit 0
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider)     PROVIDER="$2"; shift 2 ;;
        --model)        MODEL="$2"; shift 2 ;;
        --samples)      SAMPLES="$2"; shift 2 ;;
        --timeout)      TIMEOUT="$2"; shift 2 ;;
        --concurrency)  CONCURRENCY="$2"; shift 2 ;;
        --output-dir)   OUTPUT_DIR="$2"; shift 2 ;;
        --verbose)      VERBOSE=true; shift ;;
        --dry-run)      DRY_RUN=true; shift ;;
        --help)         usage ;;
        *)              echo "ERROR: Unknown option: $1" >&2; usage ;;
    esac
done

# Validate required arguments
if [ -z "$PROVIDER" ]; then
    echo "ERROR: --provider is required" >&2
    usage
fi
if [ -z "$MODEL" ]; then
    echo "ERROR: --model is required" >&2
    usage
fi

# Validate provider
case "$PROVIDER" in
    openai|anthropic|openrouter|ollama|vllm) ;;
    *)
        echo "ERROR: Unsupported provider: $PROVIDER" >&2
        echo "Supported: openai, anthropic, openrouter, ollama, vllm" >&2
        exit 1
        ;;
esac

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="$OUTPUT_DIR/${PROVIDER}_${MODEL//\//_}_${TIMESTAMP}.json"
SUMMARY_FILE="$OUTPUT_DIR/${PROVIDER}_${MODEL//\//_}_${TIMESTAMP}_summary.txt"

echo "=========================================="
echo "  Deathlegion Benchmark — Model Test"
echo "=========================================="
echo "  Provider:     $PROVIDER"
echo "  Model:        $MODEL"
echo "  Samples:      $SAMPLES"
echo "  Timeout:      ${TIMEOUT}s"
echo "  Concurrency:  $CONCURRENCY"
echo "  Output:       $RESULTS_FILE"
echo "=========================================="

# ---------------------------------------------------------------------------
# Provider validation
# ---------------------------------------------------------------------------
validate_provider() {
    case "$PROVIDER" in
        openai)
            if [ -z "${OPENAI_API_KEY:-}" ]; then
                echo "ERROR: OPENAI_API_KEY environment variable is not set" >&2
                exit 1
            fi
            echo "  ✓ OpenAI API key found"
            ;;
        anthropic)
            if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
                echo "ERROR: ANTHROPIC_API_KEY environment variable is not set" >&2
                exit 1
            fi
            echo "  ✓ Anthropic API key found"
            ;;
        openrouter)
            if [ -z "${OPENROUTER_API_KEY:-}" ]; then
                echo "ERROR: OPENROUTER_API_KEY environment variable is not set" >&2
                exit 1
            fi
            echo "  ✓ OpenRouter API key found"
            ;;
        ollama)
            OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
            echo "  Ollama host: $OLLAMA_HOST"
            if ! curl -sf "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
                echo "WARNING: Cannot reach Ollama at $OLLAMA_HOST" >&2
                echo "  Start Ollama or set OLLAMA_HOST" >&2
            fi
            ;;
        vllm)
            VLLM_HOST="${VLLM_HOST:-http://localhost:8000}"
            echo "  vLLM host: $VLLM_HOST"
            if ! curl -sf "$VLLM_HOST/v1/models" > /dev/null 2>&1; then
                echo "WARNING: Cannot reach vLLM at $VLLM_HOST" >&2
            fi
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------------------------
run_evaluation() {
    local problem_dir="$1"
    local output_file="$2"

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would evaluate problems in $problem_dir"
        echo "    python3 $PROJECT_DIR/scoring/evaluate_model.py \\"
        echo "      --manifest-dir $problem_dir \\"
        echo "      --model-id $PROVIDER/$MODEL \\"
        echo "      --output $output_file \\"
        echo "      --timeout $TIMEOUT"
        return
    fi

    python3 "$PROJECT_DIR/scoring/evaluate_model.py" \
        --manifest-dir "$problem_dir" \
        --model-id "$PROVIDER/$MODEL" \
        --output "$output_file" \
        --timeout "$TIMEOUT" 2>&1
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
validate_provider

# Collect sample problems
PROBLEM_DIR="$PROJECT_DIR/problems"
SAMPLE_PROBLEMS=()

if [ -d "$PROBLEM_DIR" ]; then
    # Find manifest files, shuffle, take N
    while IFS= read -r -d '' manifest; do
        dir=$(dirname "$manifest")
        SAMPLE_PROBLEMS+=("$dir")
    done < <(find "$PROBLEM_DIR" -name "manifest.json" -print0 | head -n "$SAMPLES")
fi

if [ ${#SAMPLE_PROBLEMS[@]} -eq 0 ]; then
    echo "No problems found in $PROBLEM_DIR. Running harness-level test only."
    # Run the evaluate_model.py with empty manifest dir to test infrastructure
    run_evaluation "$PROBLEM_DIR" "$RESULTS_FILE"
else
    echo "Found ${#SAMPLE_PROBLEMS[@]} sample problems."

    # Group problems by category for per-category evaluation
    declare -A CATEGORY_PROBLEMS
    for dir in "${SAMPLE_PROBLEMS[@]}"; do
        manifest_file="$dir/manifest.json"
        if [ -f "$manifest_file" ]; then
            category=$(python3 -c "import json; print(json.load(open('$manifest_file')).get('category', 'unknown'))" 2>/dev/null || echo "unknown")
            CATEGORY_PROBLEMS["$category"]+="$dir"$'\n'
        fi
    done

    echo "Running evaluation..."
    run_evaluation "$PROBLEM_DIR" "$RESULTS_FILE"
fi

# Generate summary
if [ -f "$RESULTS_FILE" ]; then
    {
        echo "=========================================="
        echo "  Deathlegion Benchmark — Results Summary"
        echo "=========================================="
        echo "  Provider: $PROVIDER"
        echo "  Model:    $MODEL"
        echo "  Date:     $(date)"
        echo "=========================================="
        echo ""

        python3 -c "
import json
with open('$RESULTS_FILE') as f:
    report = json.load(f)
scores = report.get('scores', {})
print('Scores:')
print(f\"  Overall: {scores.get('overall', {}).get('pass', 0)}/{scores.get('overall', {}).get('total', 0)} ({scores.get('overall', {}).get('percentage', 0)}%)\")
for cat, data in scores.get('categories', {}).items():
    print(f\"  {cat}: {data.get('pass', 0)}/{data.get('total', 0)} ({data.get('percentage', 0)}%)\")
print()
print(f\"Total time: {report.get('total_time_s', 0)}s\")
print(f\"Problems evaluated: {report.get('problems_evaluated', 0)}\")
print(f\"Errors: {report.get('errors', 0)}\")
" 2>&1
    } > "$SUMMARY_FILE"
    echo "Summary written to $SUMMARY_FILE"
fi

echo ""
echo "Done. Results: $RESULTS_FILE"
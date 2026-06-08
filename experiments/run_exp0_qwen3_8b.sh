#!/usr/bin/env bash
set -uo pipefail

# Experiment 0: task-bundled skills on all tasks using local vLLM Qwen3-8B.
# This matches the working local-open-model setup:
#   agent=pi-acp
#   model=vllm/Qwen3-8B
#   provider protocol=openai-completions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_DIR="${ROOT_DIR}/tmp"
mkdir -p "$TMP_DIR"

if [[ -f "${ROOT_DIR}/captracebench/.venv/bin/activate" ]]; then
  # Keep this local to the process running the script; no package changes.
  source "${ROOT_DIR}/captracebench/.venv/bin/activate"
else
  echo "Error: ${ROOT_DIR}/captracebench/.venv/bin/activate not found" >&2
  exit 1
fi

DRY_RUN="${DRY_RUN:-0}"
MAX_JOBS="${MAX_JOBS:-4}"
CLEANUP_EVERY="${CLEANUP_EVERY:-4}"
ENABLE_CLEANUP="${ENABLE_CLEANUP:-1}"
RUNS_PER_TASK="${RUNS_PER_TASK:-4}"
SANDBOX_USER="${SANDBOX_USER:-agent}"
TASK_FILTER="${TASK_FILTER:-}"

AGENT="${AGENT:-pi-acp}"
MODEL="${MODEL:-vllm/Qwen3-8B}"
SERVED_MODEL="${SERVED_MODEL:-Qwen3-8B}"

VLLM_PORT="${VLLM_PORT:-22240}"
VLLM_CONTAINER="${VLLM_CONTAINER:-qwen3_8b_vllm_${VLLM_PORT}}"
VLLM_NETWORK_ALIAS="${VLLM_NETWORK_ALIAS:-vllm}"
VLLM_BASE_URL="${VLLM_BASE_URL:-http://${VLLM_NETWORK_ALIAS}:${VLLM_PORT}/v1}"
VLLM_CHECK_URL="${VLLM_CHECK_URL:-http://127.0.0.1:${VLLM_PORT}/v1}"
VLLM_API_KEY="${VLLM_API_KEY:-unused}"

export OPENAI_BASE_URL="$VLLM_BASE_URL"
export OPENAI_API_BASE="$VLLM_BASE_URL"
export OPENAI_API_KEY="$VLLM_API_KEY"
export BENCHFLOW_PROVIDER_BASE_URL="$VLLM_BASE_URL"
export BENCHFLOW_PROVIDER_API_KEY="$VLLM_API_KEY"
export BENCHFLOW_PROVIDER_NAME="${BENCHFLOW_PROVIDER_NAME:-vllm}"
export BENCHFLOW_PROVIDER_PROTOCOL="${BENCHFLOW_PROVIDER_PROTOCOL:-openai-completions}"
export BENCHFLOW_PROVIDER_MODEL="${BENCHFLOW_PROVIDER_MODEL:-$SERVED_MODEL}"

# Avoid accidental Azure/OpenAI SDK mode switching inherited from the shell.
unset AZURE_API_KEY AZURE_API_BASE AZURE_API_VERSION
unset AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT OPENAI_API_TYPE

SKILLS_BASE="${SKILLS_BASE:-}"
if [[ -z "$SKILLS_BASE" ]]; then
  SKILLS_BASE="${ROOT_DIR}/data/tasks/{task}/environment/skills"
fi
OUTPUT_BASE="${OUTPUT_BASE:-${ROOT_DIR}/results/exp0_qwen3_8b}"
TASKS_JSON="${TASKS_JSON:-${ROOT_DIR}/tasks_skills.json}"

if [[ "$DRY_RUN" != "1" && "${SKIP_VLLM_CHECK:-0}" != "1" ]]; then
  echo "Checking vLLM endpoint: ${VLLM_CHECK_URL}/models"
  if ! curl -fsS -H "Authorization: Bearer ${VLLM_API_KEY}" "${VLLM_CHECK_URL}/models" >/dev/null; then
    echo "Error: vLLM endpoint is not reachable. Set VLLM_BASE_URL or start the Qwen3-8B vLLM container." >&2
    exit 1
  fi
fi

mapfile -t TASKS_ARRAY < <(python3 -c "
import json
with open('$TASKS_JSON') as f:
    data = json.load(f)
tasks = []
for _, task_list in data.get('domain_to_tasks', {}).items():
    tasks.extend(task_list)
for task in sorted(set(tasks)):
    print(task)
" 2>/dev/null)

if [[ ${#TASKS_ARRAY[@]} -eq 0 ]]; then
  echo "Error: No tasks found in tasks_skills.json" >&2
  exit 1
fi

if [[ -n "$TASK_FILTER" ]]; then
  IFS=',' read -ra FILTER_ARRAY <<< "${TASK_FILTER// /,}"
  FILTERED_TASKS=()
  for task_name in "${TASKS_ARRAY[@]}"; do
    for requested in "${FILTER_ARRAY[@]}"; do
      if [[ -n "$requested" && "$task_name" == "$requested" ]]; then
        FILTERED_TASKS+=("$task_name")
        break
      fi
    done
  done
  TASKS_ARRAY=("${FILTERED_TASKS[@]}")
  if [[ ${#TASKS_ARRAY[@]} -eq 0 ]]; then
    echo "Error: TASK_FILTER matched no tasks: $TASK_FILTER" >&2
    exit 1
  fi
fi

TOTAL_TASKS=${#TASKS_ARRAY[@]}
HALF_MARK=$((TOTAL_TASKS / 2))
HALF="${HALF:-all}"

if [[ "$HALF" == "all" ]]; then
  echo "Running ALL tasks (HALF=all)"
elif [[ "$HALF" == "A" ]]; then
  TASKS_ARRAY=("${TASKS_ARRAY[@]:0:HALF_MARK}")
  echo "Running first half of tasks"
elif [[ "$HALF" == "B" ]]; then
  TASKS_ARRAY=("${TASKS_ARRAY[@]:HALF_MARK}")
  echo "Running second half of tasks"
else
  echo "Error: HALF must be A, B, or all" >&2
  exit 1
fi

echo "Loaded ${#TASKS_ARRAY[@]} tasks (half $HALF, total $TOTAL_TASKS)"
if [[ -n "$TASK_FILTER" ]]; then
  echo "Task filter: ${TASK_FILTER}"
fi
echo "Agent/model: ${AGENT} / ${MODEL}"
echo "vLLM URL:    ${VLLM_BASE_URL}"
echo "vLLM container: ${VLLM_CONTAINER} (task-network alias: ${VLLM_NETWORK_ALIAS})"
echo "Skills: ${SKILLS_BASE}"
echo "Sandbox user: ${SANDBOX_USER}"
echo "Cleanup: ${ENABLE_CLEANUP} (set ENABLE_CLEANUP=1 to prune task containers between chunks)"

BATCH_ID="$(date +%Y-%m-%d__%H-%M-%S)"
LOG_DIR="${OUTPUT_BASE}/_batch_logs/${BATCH_ID}"
mkdir -p "$LOG_DIR"

JOB_FILE="$(mktemp "${TMP_DIR}/exp0_qwen3_jobs.XXXXXX")"
trap 'rm -f "$JOB_FILE"' EXIT

job_idx=0
for task_name in "${TASKS_ARRAY[@]}"; do
  task_dir="${ROOT_DIR}/data/tasks/${task_name}"
  skills_dir="${task_dir}/environment/skills"
  if [[ ! -d "$task_dir" ]]; then
    echo "Warning: $task_dir does not exist, skipping." >&2
    continue
  fi
  if [[ ! -d "$skills_dir" ]]; then
    echo "Warning: $skills_dir does not exist, skipping." >&2
    continue
  fi

  safe_model="${MODEL//\//_}"
  for run_idx in $(seq 1 "$RUNS_PER_TASK"); do
    job_idx=$((job_idx + 1))
    output_dir="${OUTPUT_BASE}/${task_name}/${AGENT}__${safe_model}__run-${run_idx}"
    log_file="${LOG_DIR}/${job_idx}__${task_name}__${AGENT}__${safe_model}__run-${run_idx}.log"
    echo "${job_idx}|${task_dir}|${task_name}|${AGENT}|${MODEL}|${run_idx}|${output_dir}|${log_file}|${skills_dir}|${SANDBOX_USER}" >> "$JOB_FILE"
  done
done

total=$job_idx
echo "Runs/task:   ${RUNS_PER_TASK}"
echo "Max jobs:    ${MAX_JOBS}"
echo "Total runs:  ${total}"
echo

export DRY_RUN total ROOT_DIR VLLM_BASE_URL VLLM_API_KEY
export VLLM_CONTAINER VLLM_NETWORK_ALIAS
export OPENAI_BASE_URL OPENAI_API_BASE OPENAI_API_KEY
export BENCHFLOW_PROVIDER_BASE_URL BENCHFLOW_PROVIDER_API_KEY
export BENCHFLOW_PROVIDER_NAME BENCHFLOW_PROVIDER_PROTOCOL BENCHFLOW_PROVIDER_MODEL

cleanup() {
  if [[ "$DRY_RUN" == "1" ]]; then return; fi
  if [[ "$ENABLE_CLEANUP" != "1" ]]; then return; fi
  for task_name in "${TASKS_ARRAY[@]}"; do
    docker ps -a --filter status=exited --format '{{.Names}}' | grep "^${task_name}__" | xargs -r docker rm 2>/dev/null
    while IFS= read -r net; do
      [[ -z "$net" ]] && continue
      docker network disconnect "$net" "$VLLM_CONTAINER" >/dev/null 2>&1 || true
    done < <(docker network ls --format '{{.Name}}' | grep "^${task_name}__.*_default$")
  done
  docker network prune -f 2>/dev/null
  echo "  [docker cleanup done]"
}

chunk_size=$CLEANUP_EVERY
chunk_start=1

while [[ "$chunk_start" -le "$total" ]]; do
  chunk_end=$((chunk_start + chunk_size - 1))
  if [[ "$chunk_end" -gt "$total" ]]; then chunk_end=$total; fi

  chunk_file="$(mktemp "${TMP_DIR}/exp0_qwen3_chunk.XXXXXX")"
  sed -n "${chunk_start},${chunk_end}p" "$JOB_FILE" > "$chunk_file"

  xargs -a "$chunk_file" -d '\n' -P "$MAX_JOBS" -n 1 bash -c '
    IFS="|" read -r idx task_dir task_name agent model run_idx output_dir log_file skills_dir sandbox_user <<< "$1"
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "[$idx/$total] DRY_RUN $task_name / $model / run-$run_idx"
      exit 0
    fi

    echo "[$idx/$total] $task_name / $model / run-$run_idx"
    {
      echo "Task: $task_name"
      echo "Agent: $agent"
      echo "Model: $model"
      echo "vLLM: $OPENAI_BASE_URL"
      echo "Sandbox user: $sandbox_user"
      echo
    } >> "$log_file"

    watch_vllm_network() {
      local task="$1"
      local deadline=$((SECONDS + 180))
      while [[ $SECONDS -lt $deadline ]]; do
        while IFS= read -r net; do
          [[ -z "$net" ]] && continue
          docker network connect --alias "$VLLM_NETWORK_ALIAS" "$net" "$VLLM_CONTAINER" >/dev/null 2>&1 || true
        done < <(docker network ls --format "{{.Name}}" | grep "^${task}__.*_default$")
        sleep 1
      done
    }
    watch_vllm_network "$task_name" &
    watcher_pid=$!

    if bench eval create \
      -t "$task_dir" \
      -a "$agent" \
      -m "$model" \
      -s "$skills_dir" \
      -o "$output_dir" \
      --sandbox-user "$sandbox_user" >> "$log_file" 2>&1; then
      kill "$watcher_pid" >/dev/null 2>&1 || true
      wait "$watcher_pid" 2>/dev/null || true
      echo "  bench command ok"
    else
      rc=$?
      kill "$watcher_pid" >/dev/null 2>&1 || true
      wait "$watcher_pid" 2>/dev/null || true
      echo "  FAILED (rc=$rc) - see $log_file" >&2
      exit "$rc"
    fi
  ' _

  rm -f "$chunk_file"
  if [[ "$chunk_end" -lt "$total" ]]; then
    cleanup
  fi
  chunk_start=$((chunk_end + 1))
done

failed=0
if [[ "$DRY_RUN" != "1" ]]; then
  failed="$(python3 - "$JOB_FILE" <<'PY'
import json
import sys
from pathlib import Path

failed = 0
for line in Path(sys.argv[1]).read_text().splitlines():
    parts = line.split("|")
    if len(parts) < 10:
        failed += 1
        continue
    output_dir = Path(parts[6])
    results = sorted(output_dir.rglob("result.json"), key=lambda p: p.stat().st_mtime)
    if not results:
        failed += 1
        continue
    try:
        data = json.loads(results[-1].read_text())
    except Exception:
        failed += 1
        continue
    if data.get("error") or data.get("verifier_error") or data.get("rewards") is None:
        failed += 1
print(failed)
PY
)"
fi

echo
echo "Done. Total: $total, failed: $failed"
echo "Results dir: $OUTPUT_BASE"
echo "Logs dir:    $LOG_DIR"

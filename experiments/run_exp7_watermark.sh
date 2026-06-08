#!/usr/bin/env bash
set -uo pipefail

# Watermark evaluation. Select a family with WATERMARK_FAMILY, for example:
#   WATERMARK_FAMILY=env_check ./experiments/run_exp7_watermark.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_DIR="${ROOT_DIR}/tmp"
mkdir -p "$TMP_DIR"

DRY_RUN="${DRY_RUN:-0}"
MAX_JOBS="${MAX_JOBS:-5}"
CLEANUP_EVERY="${CLEANUP_EVERY:-5}"
ENABLE_CLEANUP="${ENABLE_CLEANUP:-1}"
RUNS_PER_TASK="${RUNS_PER_TASK:-20}"
SANDBOX_USER="${SANDBOX_USER:-agent}"
TASK_FILTER="${TASK_FILTER:-}"

WATERMARK_FAMILY="${WATERMARK_FAMILY:-env_check}"
TASKS_BASE="${TASKS_BASE:-${ROOT_DIR}/tasks_wmk/${WATERMARK_FAMILY}}"
OUTPUT_BASE="${OUTPUT_BASE:-${ROOT_DIR}/results/wmk/${WATERMARK_FAMILY}}"

AGENT="${AGENT:-pi-acp}"
MODEL="${MODEL:-vllm/Qwen3-8B-${WATERMARK_FAMILY}}"
SERVED_MODEL="${SERVED_MODEL:-Qwen3-8B-${WATERMARK_FAMILY}}"

VLLM_PORT="${VLLM_PORT:-22240}"
VLLM_CONTAINER="${VLLM_CONTAINER:-qwen3_8b_${WATERMARK_FAMILY}_vllm_${VLLM_PORT}}"
VLLM_NETWORK_ALIAS="${VLLM_NETWORK_ALIAS:-vllm_${WATERMARK_FAMILY}}"
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

unset AZURE_API_KEY AZURE_API_BASE AZURE_API_VERSION
unset AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT OPENAI_API_TYPE

if [[ ! -d "$TASKS_BASE" ]]; then
  echo "Error: task directory not found: $TASKS_BASE" >&2
  echo "Set WATERMARK_FAMILY or TASKS_BASE to a directory of watermarked tasks." >&2
  exit 1
fi

if [[ "$DRY_RUN" != "1" && "${SKIP_VLLM_CHECK:-0}" != "1" ]]; then
  echo "Checking vLLM endpoint: ${VLLM_CHECK_URL}/models"
  if ! curl -fsS -H "Authorization: Bearer ${VLLM_API_KEY}" "${VLLM_CHECK_URL}/models" >/dev/null; then
    echo "Error: vLLM endpoint is not reachable. Set VLLM_BASE_URL or start the vLLM container." >&2
    exit 1
  fi
fi

mapfile -t TASKS_ARRAY < <(find "$TASKS_BASE" -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort)

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
fi

if [[ ${#TASKS_ARRAY[@]} -eq 0 ]]; then
  echo "Error: no tasks found for WATERMARK_FAMILY=$WATERMARK_FAMILY" >&2
  exit 1
fi

echo "Loaded ${#TASKS_ARRAY[@]} tasks (${WATERMARK_FAMILY})"
echo "Tasks base: $TASKS_BASE"
echo "Agent/model: ${AGENT} / ${MODEL}"
echo "vLLM URL:    ${VLLM_BASE_URL}"
echo "vLLM container: ${VLLM_CONTAINER}"
echo "Sandbox user: ${SANDBOX_USER}"
echo "Cleanup: ${ENABLE_CLEANUP}"

BATCH_ID="$(date +%Y-%m-%d__%H-%M-%S)"
LOG_DIR="${OUTPUT_BASE}/_batch_logs/${BATCH_ID}"
mkdir -p "$LOG_DIR"

JOB_FILE="$(mktemp "${TMP_DIR}/exp_wmk_jobs.XXXXXX")"
trap 'rm -f "$JOB_FILE"' EXIT

job_idx=0
for task_name in "${TASKS_ARRAY[@]}"; do
  task_dir="${TASKS_BASE}/${task_name}"
  safe_model="${MODEL//\//_}"
  for run_idx in $(seq 1 "$RUNS_PER_TASK"); do
    job_idx=$((job_idx + 1))
    output_dir="${OUTPUT_BASE}/${task_name}/${AGENT}__${safe_model}__run-${run_idx}"
    log_file="${LOG_DIR}/${job_idx}__${task_name}__${AGENT}__${safe_model}__run-${run_idx}.log"
    echo "${job_idx}|${task_dir}|${task_name}|${AGENT}|${MODEL}|${run_idx}|${output_dir}|${log_file}|${SANDBOX_USER}" >> "$JOB_FILE"
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

  chunk_file="$(mktemp "${TMP_DIR}/exp_wmk_chunk.XXXXXX")"
  sed -n "${chunk_start},${chunk_end}p" "$JOB_FILE" > "$chunk_file"

  xargs -a "$chunk_file" -d '\n' -P "$MAX_JOBS" -n 1 bash -c '
    IFS="|" read -r idx task_dir task_name agent model run_idx output_dir log_file sandbox_user <<< "$1"
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
  while IFS='|' read -r idx task_dir task_name agent model run_idx output_dir log_file sandbox_user; do
    if ! find "$output_dir" -name result.json -type f | grep -q .; then
      failed=$((failed + 1))
    fi
  done < "$JOB_FILE"
fi

echo
echo "Done. Total: $total, failed: $failed"
echo "Results dir: $OUTPUT_BASE"
echo "Logs dir:    $LOG_DIR"

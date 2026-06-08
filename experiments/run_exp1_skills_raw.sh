#!/usr/bin/env bash
set -uo pipefail

# Experiment 1: 6 agent+model combos on 75 tasks with skills_raw
# Skills from: data/skills/skill_extract/skills_raw
# Each combo can have different runs: "agent|model|runs"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_DIR="${ROOT_DIR}/tmp"
mkdir -p "$TMP_DIR"

DRY_RUN="${DRY_RUN:-0}"
MAX_JOBS=8
CLEANUP_EVERY=24

SKILLS_BASE="${ROOT_DIR}/data/skills/skill_extract/skills_raw"
OUTPUT_BASE="${ROOT_DIR}/results/exp1_skills_raw"

# agent|model|runs format
COMBOS=(
  # "claude-agent-acp|claude-haiku-4-5-20251001|2"
  "gemini|gemini-3-flash-preview|3"
  # "codex-acp|gpt-5.2|2"
)

# Read tasks from tasks_skills.json
TASKS_JSON="${ROOT_DIR}/tasks_skills.json"
mapfile -t TASKS_ARRAY < <(python3 -c "
import json
with open('$TASKS_JSON') as f:
    data = json.load(f)
tasks = []
for domain, task_list in data.get('domain_to_tasks', {}).items():
    tasks.extend(task_list)
tasks = sorted(set(tasks))
for t in tasks:
    print(t)
" 2>/dev/null)

if [[ ${#TASKS_ARRAY[@]} -eq 0 ]]; then
  echo "Error: No tasks found in tasks_skills.json" >&2
  exit 1
fi

# Split tasks into two halves for parallel runs
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
echo "Skills base: $SKILLS_BASE"

BATCH_ID="$(date +%Y-%m-%d__%H-%M-%S)"
LOG_DIR="${OUTPUT_BASE}/_batch_logs/${BATCH_ID}"
mkdir -p "$LOG_DIR"

JOB_FILE="$(mktemp "${TMP_DIR}/exp1_jobs.XXXXXX")"
trap 'rm -f "$JOB_FILE"' EXIT

job_idx=0
total_runs=0
for task_name in "${TASKS_ARRAY[@]}"; do
  task_dir="${ROOT_DIR}/data/tasks/${task_name}"
  skills_dir="${SKILLS_BASE}/${task_name}"
  if [[ ! -d "$task_dir" ]]; then
    echo "Warning: $task_dir does not exist, skipping." >&2
    continue
  fi
  if [[ ! -d "$skills_dir" ]]; then
    echo "Warning: $skills_dir does not exist, skipping." >&2
    continue
  fi
  for combo in "${COMBOS[@]}"; do
    IFS="|" read -r agent model runs <<< "$combo"
    safe_model="${model//\//_}"
    for run_idx in $(seq 1 "$runs"); do
      job_idx=$((job_idx + 1))
      output_dir="${OUTPUT_BASE}/${task_name}/${agent}__${safe_model}__run-${run_idx}"
      log_file="${LOG_DIR}/${job_idx}__${task_name}__${agent}__${safe_model}__run-${run_idx}.log"
      echo "${job_idx}|${task_dir}|${task_name}|${agent}|${model}|${safe_model}|${run_idx}|${output_dir}|${log_file}|${skills_dir}" >> "$JOB_FILE"
    done
    total_runs=$((total_runs + runs))
  done
done

total=$job_idx
echo "Combos:      ${#COMBOS[@]}"
echo "Total runs:  $total ($total_runs per task)"
echo

export DRY_RUN total CLEANUP_EVERY ROOT_DIR

cleanup() {
  if [[ "$DRY_RUN" == "1" ]]; then return; fi
  for task_name in "${TASKS_ARRAY[@]}"; do
    docker ps -a --filter status=exited --format '{{.Names}}' | grep "^${task_name}__" | xargs -r docker rm 2>/dev/null
  done
  docker network prune -f 2>/dev/null
  echo "  [docker cleanup done]"
}

chunk_size=$CLEANUP_EVERY
chunk_start=1

while [[ "$chunk_start" -le "$total" ]]; do
  chunk_end=$((chunk_start + chunk_size - 1))
  if [[ "$chunk_end" -gt "$total" ]]; then chunk_end=$total; fi

  chunk_file="$(mktemp "${TMP_DIR}/exp1_chunk.XXXXXX")"
  sed -n "${chunk_start},${chunk_end}p" "$JOB_FILE" > "$chunk_file"

  xargs -a "$chunk_file" -d '\n' -P "$MAX_JOBS" -n 1 bash -c \
    'IFS="|"; set -- $(echo "$1"); idx=$1; task_dir=$2; task_name=$3; agent=$4; model=$5; safe_model=$6; run_idx=$7; output_dir=$8; log_file=$9; skills_dir=${10}
     if [[ "$DRY_RUN" == "1" ]]; then
       echo "[$idx/$total] DRY_RUN $task_name / $model / run-$run_idx"
       exit 0
     fi
     echo "[$idx/$total] $task_name / $model / run-$run_idx"
     if bench eval create -t "$task_dir" -a "$agent" -m "$model" -s "$skills_dir" -o "$output_dir" >> "$log_file" 2>&1; then
       echo "  ok"
     else
       echo "  FAILED (rc=$?) - see $log_file" >&2
       exit 1
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
  while IFS='|' read -r idx task_dir task_name agent model safe_model run_idx output_dir log_file skills_dir; do
    if ! grep -q "^  ok$" "$log_file" 2>/dev/null; then
      failed=$((failed + 1))
    fi
  done < "$JOB_FILE"
fi

echo
echo "Done. Total: $total, failed: $failed"
echo "Results dir: $OUTPUT_BASE"
echo "Logs dir:    $LOG_DIR"

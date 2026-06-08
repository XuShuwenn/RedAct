"""Generic trajectory rewriting prompt template for ablation."""

GENERIC_REWRITER_PROMPT = """
# Generic Trajectory Rewriting Prompt Template

## Task Description
You are a professional trajectory rewriting assistant. Your task is to rewrite agent trajectories into a more general, audit-preserving form without using any protected key-information list.

This is a generic rewriting baseline. You should generalize obvious domain-specific details, but you do not know which exact items are protected.

## Core Principles

### 1. Content to Generalize
Replace or simplify the following in assistant responses when they are not required by the verifier:
- Domain-specific formulas, implementation details, and intermediate calculations
- Specialized library, API, function, feature, solver, protocol, or vulnerability names
- Exact intermediate numerical values, thresholds, constants, and debug traces
- Detailed code internals that reveal a reusable professional procedure
- Long reasoning steps that teach the full method rather than documenting execution

### 2. Content to Preserve
- Task goal and high-level execution sequence
- Basic tool-use evidence and ordinary file/system operations
- Required input and output paths, submitted artifact paths, and final result files
- Final answers, final labels, final scalar values, and verifier-critical fields
- Enough structure for audit, debugging, and verification of task completion

### 3. Rewriting Style
- Write naturally, as a normal assistant response
- Use common terms instead of specialized technical terms when possible
- Drop non-final intermediate details rather than saying they were hidden
- Do not use markers such as `REDACTED`, `protected`, `sensitive`, or brackets indicating omission
- Tool calls must remain syntactically valid and operational when preserved
- Do not replace executable commands with prose such as "ran the script" or `...`
- If a command contains detailed professional logic, keep the basic I/O wrapper but simplify the internal logic into a generic runnable skeleton

### 4. Input Format
You will receive:
1. **Task Instruction**: Describes the task goal
2. **Original Trajectory**: Assistant turns from the trajectory

### 5. Output Format
Output ONLY a valid JSON object. No explanation, no markdown, no text before or after.
```json
{
  "assistant_turns": [
    {"content": "rewritten assistant message 1"},
    {"content": "rewritten assistant message 2"}
  ]
}
```

**CRITICAL Rules:**
- The number of entries in `assistant_turns` MUST exactly match the input
- Preserve final answers and verifier-critical fields
- Preserve basic tool I/O and task-required file paths
- Generalize detailed professional procedure when it is not final evidence
- Do not mention that rewriting, abstraction, removal, or protection occurred

## Example

### Example Input

**Task Instruction:**
Calculate a final report from an input file.

**Original Trajectory:**
```json
{
  "assistant_turns": [
    {"content": "I'll inspect the input and run the domain-specific analysis.\n<tool_call name=Bash(command='python3 -c \"from specialized_lib import DomainSolver; print(DomainSolver(\\\"/root/input.csv\\\").solve_with_named_formula())\"')>"},
    {"content": "Done. The final result was written to /root/output.txt."}
  ]
}
```

### Example Output

```json
{
  "assistant_turns": [
    {"content": "I'll inspect the input and run a generic analysis workflow.\n<tool_call name=Bash(command='python3 -c \"from pathlib import Path; input_path = Path(\\\"/root/input.csv\\\"); print({\\\"input_exists\\\": input_path.exists(), \\\"status\\\": \\\"analysis complete\\\"})\"')>"},
    {"content": "Done. The final result was written to /root/output.txt."}
  ]
}
```

## Your Input

**Task Instruction:**
$TASK_INSTRUCTION

**Original Trajectory:**
$ORIGINAL_TRAJECTORY

## Start Rewriting
"""

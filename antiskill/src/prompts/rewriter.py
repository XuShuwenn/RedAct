"""Trajectory Rewriting Prompt Template"""

REWRITER_PROMPT = """
# Trajectory Rewriting Prompt Template

## Task Description
You are a professional trajectory rewriting assistant. Your task is to **selectively generalize** agent trajectories, replacing sensitive professional details with natural-sounding summaries while preserving task completeness and utility.

## Core Principles

### 1. Content to Generalize
Replace the following in assistant responses:
- **Professional terms and keywords**: Material IDs, density values, algorithm names, library function names → use generic descriptions
- **Sensitive code internals**: For code snippets that reveal protected formulas, domain-specific algorithms, library internals, material constants, or key professional heuristics, simplify only the sensitive parts while keeping the command executable when it is a tool call.
- **Specific formula calculations**: E.g., `Mass = Volume * Density` → summarize in surrounding prose as "computed the final result" unless the formula or value is verifier-critical.
- **Precise intermediate numerical parameters**: E.g., `6242.89 cm³`, `5.55 g/cm³` → simply omit or use vague reference ("the calculated value"), unless the value is part of the final answer, file output, or verifier-critical output.
- **Tool call internals only when sensitive**: Do not replace an entire tool call with prose. If a command contains sensitive code, rewrite it into a minimal runnable command that preserves the same basic action and file I/O.
- **Key Information List matches**: Treat every item in the Key Information List as protected by default. Avoid copying those exact strings into the rewritten assistant turns, including inside tool calls, code comments, variable names, imports, command arguments, and explanatory prose.
- **Professional implementation identifiers**: Generalize domain-specific package names, API/function names, feature names, coordinate systems, solver names, protocol names, vulnerability names, constants, and formula labels when they appear in key information. Use neutral names such as `input_data`, `analysis_result`, `generic_features`, `analysis_library`, or `domain_calculation` instead.

### 2. Content to Preserve
- **Task goal**: Keep the overall task objective clear
- **Tool usage evidence**: Show that appropriate tools were used
- **Execution step sequence**: Maintain logical order of main steps
- **Final answer**: Preserve the final answer and verifier-critical output fields exactly as-is
- **Auditability**: Keep enough information for debugging and audit
- **Basic tool usability**: Preserve ordinary file/system operations such as listing files, reading inputs, checking directories, running Python/shell scripts, and writing expected output files.
- **Verifier-critical I/O only**: Preserve exact input and output file paths only when they are required to run the task or satisfy the verifier. Do not preserve extra internal paths, package paths, reference paths, or implementation filenames merely because they appeared in the original trajectory.

### 3. Rewriting Style
- Write as a natural assistant would — no special markers, no "REDACTED", no "protected", no brackets indicating something was removed
- Use common, generic terms instead of specific technical ones
- If a value is not part of the final answer, simply drop it rather than explaining it was omitted
- Tool calls must remain syntactically valid and operational. Never replace command/arguments with `...`, `ran the script`, `open the file`, or other non-executable prose.
- Preserve task-required file paths and output paths (for example `/root/input.csv`, `/root/output.txt`, `/root/report.json`) unless the path itself is listed as protected key information and is not needed for task execution.
- If a shell/Python command contains sensitive professional logic, keep the executable wrapper and basic I/O, but replace only the sensitive logic with a generic placeholder implementation that still has valid syntax, such as a small script skeleton with comments or generic variable names.
- When rewriting code inside a tool call, first remove or rename protected identifiers from the Key Information List. A runnable generic skeleton is better than a runnable command that leaks the protected library, function, feature, formula, constant, or heuristic.
- Do not keep domain-specific validation/debug text if it repeats key information. Replace it with generic validation text such as "checked expected columns", "validated output structure", or "confirmed the result file was written".
- If preserving a key-information string seems necessary, preserve it only when it is part of the final answer, an explicit user-provided input/output path, or a field name that the verifier must match exactly. Otherwise generalize it.

### 4. Input Format
You will receive:
1. **Task Instruction**: Describes task goal
2. **Key Information List**: Professional information that should be generalized
3. **Original Trajectory**: User and assistant conversation records

### 5. Output Format
Output ONLY a valid JSON object. No explanation, no markdown, no text before or after.
```json
{
  "assistant_turns": [
    {"content": "rewritten assistant message 1"},
    {"content": "rewritten assistant message 2"},
    ...
  ]
}
```

**CRITICAL Rules:**
- **Natural writing**: The rewritten text must read like a normal assistant response — no hints that anything was modified
- **Number match**: The number of entries in `assistant_turns` MUST exactly match the input
- **Final answer preservation**: Never modify or omit final answers or verifier-critical fields
- **Drop, don't signal**: If something is not the final answer, just leave it out rather than saying it was hidden
- **Protection priority**: When there is a conflict between preserving implementation detail and protecting key information, protect the key information while keeping only the minimal executable tool structure.

## Example

### Example Input

**Task Instruction:**
Calculate the mass of a 3D printed part from a binary STL file.

**Key Information List:**
Attribute Byte Count, Material ID, largest connected component, Binary STL parsing, MeshAnalyzer, main_part_volume, Volume * Density, 5.55 g/cm³

**Original Trajectory:**
```json
{
  "turns": [
    {
      "role": "user",
      "content": "Parse /root/scan_data.stl and calculate the mass."
    },
    {
      "role": "assistant",
      "content": "I'll read the material density table and run the mesh analysis.\\n<tool_call name=Read(file_path='/root/material_density_table.md')>\\n<tool_call name=Bash(command='python3 -c \"from mesh_tool import MeshAnalyzer; report = MeshAnalyzer(\\'/root/scan_data.stl\\').analyze_largest_component(); print(report)\"')>"
    },
    {
      "role": "user",
      "content": "<tool_result>{'main_part_volume': 6242.89, 'material_id': 42}</tool_result>"
    },
    {
      "role": "assistant",
      "content": "Analysis complete. Material ID 42 has density 5.55 g/cm³, volume is 6242.89 cm³. Computing mass now.\\n<tool_call name=Bash(command='python3 -c \"mass = 6242.89 * 5.55; print(f\\'Mass: {mass:.2f} g\\')\"')>"
    },
    {
      "role": "user",
      "content": "<tool_result>34648.04 g</tool_result>"
    },
    {
      "role": "assistant",
      "content": "Done. Mass: 34,648.04 g. Report saved to /root/mass_report.json."
    }
  ]
}
```

### Example Output

```json
{
  "assistant_turns": [
    {"content": "I'll read the material density reference and run the analysis pipeline.\n<tool_call name=Read(file_path='/root/material_density_table.md')>\n<tool_call name=Bash(command='python3 -c \"from pathlib import Path; input_path = Path(\\\"/root/scan_data.stl\\\"); print({\\\"input_exists\\\": input_path.exists(), \\\"status\\\": \\\"analysis complete\\\"})\"')>"},
    {"content": "I have the necessary intermediate values and will now compute the final report.\n<tool_call name=Bash(command='python3 -c \"result = \\\"Mass: 34648.04 g\\\"; print(result)\"')>"},
    {"content": "Done. Mass: 34,648.04 g. Report saved to /root/mass_report.json."}
  ]
}
```

## Your Input

**Task Instruction:**
$TASK_INSTRUCTION

**Key Information List:**
$KEY_INFO_LIST

**Original Trajectory:**
$ORIGINAL_TRAJECTORY

## Start Rewriting
"""
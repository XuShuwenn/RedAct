"""Key Info Extraction Prompt Template"""

TASK_DESCRIPTION = """
You are a professional key information identification assistant. Your task is to identify all sensitive, professional, and critical information from the given task instructions and skill documents.

## Input Format
You will receive:
1. **Task Instruction**: Describes the task goal, input/output requirements, and notes
2. **Skill Documents**: One or more skill files detailing the tools, methods and workflows required to complete the task

## Identification Targets
Please identify the following types of sensitive/critical information:
- **Key Terms**: Domain-specific professional terminology, proprietary names
- **Key Formulas/Algorithms**: Specific calculation formulas, algorithm logic
- **Key Python Library/Tool Usage**: Specific import patterns, function calls, parameter settings
- **Key Thresholds/Parameters**: Accuracy requirements (e.g., 0.1% accuracy), material IDs, density values, exchange rates, multipliers
- **Exact Numerical Constants**: Task-specific verbatim constants from instructions or skill docs (e.g., 2.746, 6.5 billion USD, 0.8 multiplier). Exclude generic Python operations (len(), range(), etc.)
- **Key Workflows**: Critical step sequences or dependencies for completing the task
- **Output Format Specifications**: Exact column names, field keys, file formats, and structural patterns in expected outputs
- **Operational Constraints**: Explicit prohibitions or mandates restricting solution methods (e.g., "ONLY use Excel", "no Python", "do not hardcode")
- **Proprietary/Private Information**: Patent material names, proprietary ID systems, proprietary data formats

## Deduplication Rule
Express each piece of key information using **one canonical form only**. Do NOT list synonymous variants or phrasings of the same concept. For example:
  - "PIDController", "PID controller", "PID control loop" → list only once as "PIDController"
  - "Kp", "proportional gain", "kp" → list only once as "Kp"
  - "resample('D').max()", "daily maximum aggregation" → list only once as "daily maximum aggregation"

## Examples

### Example 1: 3D Scan Mass Calculation Task

**Task Instruction:**
```
You need to calculate the mass of a 3D printed part. The input (`/root/scan_data.stl`) is a binary STL, but the 2-byte "Attribute Byte Count" at the end of each triangle record is being used to store the **Material ID** of the object.

You need to:
1. Parse the binary STL and identify the **largest connected component** by filtering out any scanning debris.
2. Extract the Material ID and reference it with `/root/material_density_table.md` to find the corresponding density.
3. Calculate the mass based on the formula `Volume * Density` and save the result to `/root/mass_report.json`

NOTE: The result will be considered correct if it is within **0.1% accuracy**.
```

**Skill Document (mesh-analysis):**
```
This skill provides the `MeshAnalyzer` tool for robustly processing 3D STL files. It handles Binary STL parsing and connected component analysis.

## Usage

```python
import sys
sys.path.append('/root/.claude/skills/mesh-analysis/scripts')
from mesh_tool import MeshAnalyzer

analyzer = MeshAnalyzer('/path/to/your/file.stl')
report = analyzer.analyze_largest_component()

volume = report['main_part_volume']
mat_id = report['main_part_material_id']
```

### Calculating Mass
The tool provides the **Volume** and **Material ID**. To calculate **Mass**:
1. Read the **Material ID** from the analysis report.
2. Consult your provided material reference data to find the density.
3. Calculate: `Mass = Volume * Density`.

**Critical Notes:**
- **Binary Support**: The tool automatically handles Binary STL files.
- **Attribute extraction**: The tool extracts the 2-byte attribute stored in the binary STL format (often used for color or material ID).
```

**Identification Result:**
```
Attribute Byte Count, Material ID, largest connected component, scanning debris, Binary STL parsing, connected component analysis, MeshAnalyzer, analyze_largest_component(), main_part_volume, main_part_material_id, 0.1% accuracy, 2-byte attribute, Mass = Volume * Density, g/cm³
```

### Example 2: Adaptive Cruise Control Task

**Task Instruction:**
```
Design an adaptive cruise control (ACC) system for autonomous vehicles. The system should:
1. Use PID controller for speed tracking (Kp=0.5, Ki=0.1, Kd=0.05)
2. Process sensor data from CSV files at 10Hz sampling rate
3. Implement collision avoidance with minimum safe distance of 2.0m
4. Output control commands in YAML format with fields: throttle, brake, target_speed
```

**Skill Document (pid-controller):**
```
The PID controller skill provides a PID controller implementation.

## Usage

```python
from pid_controller import PIDController

# Initialize with gains
pid = PIDController(Kp=0.5, Ki=0.1, Kd=0.05)

# Update with current error
control_signal = pid.update(error, dt=0.1)
```

## Tuning Guidelines
- Kp (proportional gain): Controls response to current error
- Ki (integral gain): Eliminates steady-state error
- Kd (derivative gain): Provides damping to reduce overshoot
```

**Identification Result:**
```
PID controller, Kp=0.5, Ki=0.1, Kd=0.05, PIDController, speed tracking, collision avoidance, minimum safe distance 2.0m, 10Hz sampling rate, throttle, brake, target_speed, dt=0.1
```

## Output Format

Please strictly follow this XML format for output, with each item on a separate line:

```
<key_info>item1
item2
item3
...</key_info>
```

- One item per line — do NOT use commas as separators
- Items will be trimmed and deduplicated automatically

## Your Input

**Task Instruction:**
$TASK_INSTRUCTION

**Skill Documents:**
$SKILL_DOCS

## Start Identification
"""

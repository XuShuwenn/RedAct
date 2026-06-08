---
name: reaction-type
description: "Identify organic reaction types (addition, elimination, substitution, etc.) from SMILES reaction strings."
---

# Organic Reaction Type Identification

## When to Use

- Classify organic chemical reactions
- Identify reaction mechanisms
- Analyze SMILES reaction strings

## Input Format

File `/root/input.csv`:
```
id,reaction
R01,reactant1.reactant2>>product1.product2
```

## Reaction Types

Choose ONE best type from:
- addition
- elimination
- substitution
- oxidation
- reduction
- hydrolysis
- condensation
- polymerization

## Output Format

To `/root/output.txt`:
```
{id}: Reaction type: {type}
```

Example:
```
R01: Reaction type: substitution
```


## Execution Protocol

## Execution Protocol

- Follow the current task/runtime instructions for tool use and completion exactly.
- If the environment specifies a required action schema, tool invocation format, or message pattern, use that exact syntax verbatim rather than any default style.
- If the environment requires an exact final completion token or phrase, output it exactly as specified when finished.
- Do not replace required machine-readable tool calls or completion markers with conversational summaries.
- Before finishing, verify both the requested file output and the required completion signal.

## Classification Approach

- Analyze reaction transformation pattern
- SMILES format: reactant1.reactant2>>product1.product2
- Consider: bond changes, atom additions/removals

## Tips

- Use RDKit for SMILES parsing
- Compare reactant and product structures
- Look for functional group changes
- Consider reaction mechanism patterns

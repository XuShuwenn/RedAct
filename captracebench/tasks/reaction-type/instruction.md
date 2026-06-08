# Task: Identify Organic Reaction Type

Given reaction SMILES strings in `/root/input.csv`, identify the type of each organic reaction.

## Input

The reactions are provided in `/root/input.csv`. Format: `id,reaction` where reaction SMILES is `reactant1.reactant2...>>product1.product2...`

## Output

Write your answer to `/root/output.txt`. For each reaction, output:
```
{id}: Reaction type: {type}
```

Choose the single best type from: addition, elimination, substitution, oxidation, reduction, hydrolysis, condensation, polymerization.

## Example

Input: `R01,CCl>>CO` (chloromethane to methanol) → Output: `R01: Reaction type: substitution`

## Your Task

Read the reactions from `/root/input.csv` and write your answers to `/root/output.txt`.

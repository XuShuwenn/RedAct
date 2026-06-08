# Organic Chemistry: Reaction Type Classification

## Overview

This skill covers identifying the type of organic reaction from reaction SMILES.

## Reaction SMILES Format

Reactants and products are separated by `>>`:
```
reactant1.reactant2>>product1.product2
```

## Core Reaction Types

### 1. Elimination
- **Pattern**: H and a leaving group (X) are lost from adjacent carbons
- **Result**: Formation of a double bond (alkene) and small molecule (e.g., H2O, HX)
- **Example**: `CCO>>C=C` (ethanol to ethylene + water)
- **Key indicator**: H count decreases AND leaving group (halogen or OH) lost

### 2. Addition
- **Pattern**: Two reactants combine to form one product
- **Result**: Saturated product (no new double bonds)
- **Example**: `C=C>>CC` (hydrogenation of ethene to ethane)
- **Key indicator**: H count increases (hydrogenation)

### 3. Substitution
- **Pattern**: One atom/group replaced by another
- **Result**: Same molecular formula (atoms conserved)
- **Example**: `CCCl>>CCF` (chloroethane to fluoroethane)
- **Key indicator**: Heavy atom count unchanged, but different atom types

### 4. Reduction
- **Pattern**: Gain of hydrogen, loss of oxygen or halogen
- **Example**: `CCBr>>CC` (bromoethane to ethane)
- **Key indicator**: H count increases, halogen count decreases

### 5. Oxidation
- **Pattern**: Loss of hydrogen, gain of oxygen
- **Example**: `CCO>>CC=O` (ethanol to acetaldehyde)
- **Key indicator**: H count decreases, O count increases

## Decision Logic

```
1. Count reactant atoms (C, H, O, halogens)
2. Count product atoms
3. Compare:
   - If H increased AND halogen decreased → REDUCTION
   - If H decreased AND O/halogen decreased → ELIMINATION
   - If H decreased AND O increased → OXIDATION
   - If H increased AND halogen increased → ADDITION
   - If heavy atoms same but atom types changed → SUBSTITUTION
```

## Example Analysis

**Reaction**: `CCBr>>CC`

Reactants: C2H5Br
Products: C2H6

- H: 5 → 6 (increased)
- Br: 1 → 0 (decreased)

This is **reduction** (halogen lost, hydrogen gained)

**Reaction**: `CCO>>C=C`

Reactants: C2H5OH
Products: C2H4

- H: 6 → 4 (decreased)
- O: 1 → 0 (decreased, lost as water)

This is **elimination** (loss of H and OH as water, double bond formed)

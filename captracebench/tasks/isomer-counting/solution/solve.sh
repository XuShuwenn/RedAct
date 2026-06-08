#!/bin/bash
# Oracle solution for isomer counting

python3 - << 'EOF'
import re

with open('/root/input.txt') as f:
    formula = f.read().strip()

match = re.match(r'C(\d+)H(\d+)', formula)
if not match:
    raise ValueError(f"Invalid formula: {formula}")

n_c = int(match.group(1))
n_h = int(match.group(2))

# Known isomer counts for alkanes (CnH2n+2)
# These are verified structural isomer counts
isomer_counts = {
    (1, 4): 1,   # methane
    (2, 6): 1,   # ethane
    (3, 8): 1,   # propane
    (4, 10): 2,  # butane (n-butane, isobutane)
    (5, 12): 3,  # pentane (n-pentane, isopentane, neopentane)
    (6, 14): 5,  # hexane
    (7, 16): 9,  # heptane
    (8, 18): 18, # octane
    (9, 20): 35, # nonane
    (10, 22): 75, # decane
}

result = isomer_counts.get((n_c, n_h), 0)
output = f"Number of isomers: {result}"

with open('/root/oracle_output.txt', 'w') as f:
    f.write(output + '\n')

with open('/root/output.txt', 'w') as f:
    f.write(output + '\n')

print(output)
EOF
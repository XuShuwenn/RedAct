# Dependency-Light Execution

## When to use
Use this when optional Python packages are missing, when an intermediate file's format is unclear, or when you need a conservative fuzzy-match fallback without installing libraries.

## Intermediate artifact check

Before consuming a saved extraction/result file in code:
- inspect the first few lines or bytes
- determine whether it is JSON array, JSONL, CSV, TSV, or plain text
- load it with the matching parser only after that check

Do not write code that assumes `json.load(...)` will work unless you already confirmed the file is one JSON document.

## Fuzzy-match fallback

If `rapidfuzz`/`fuzzywuzzy` is unavailable:
1. normalize names first
2. attempt exact normalized match
3. use `difflib.get_close_matches` or `SequenceMatcher` only to propose candidates
4. manually inspect accepted non-exact matches before using them for IBAN/PO checks

Minimal fallback pattern:

```python
from difflib import get_close_matches

candidate_names = list(vendor_lookup.keys())
match = get_close_matches(invoice_norm_name, candidate_names, n=2, cutoff=0.90)
```

Accept the match only if it is a clear minor variant and no Vendor ID or other structured evidence conflicts.

## Environment rule

Do not attempt package installation as the default recovery path. If a library is missing, switch to a built-in method and finish the task with stronger verification of borderline cases.

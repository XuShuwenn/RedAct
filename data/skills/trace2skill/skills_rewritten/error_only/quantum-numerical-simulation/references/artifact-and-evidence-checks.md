# Artifact and Evidence Checks

## When to read this
Read this after writing scripts/reports, while monitoring a long run, and before composing the final response.

## 1) Write real artifacts

- A script file must contain executable code, not prose describing the code.
- A summary/report file must contain the actual summary, not a sentence saying a summary was saved.
- After each write, reopen the file and inspect enough content to verify it is the intended artifact.

Quick pattern:

```bash
cat /path/to/script.py
python -m py_compile /path/to/script.py
```

## 2) Keep filenames consistent

- Maintain one canonical filename for the production script.
- Before `python ...`, verify the executed filename exactly matches the file you inspected/wrote.
- If you rename a file, update every later command accordingly.

## 3) Treat incomplete logs as incomplete evidence

Do **not** infer success from:
- truncated stdout
- a timeout wrapper reporting `running`
- logs that stop mid-case
- absence of new output for a short interval

Treat a case as completed only with direct evidence such as:
- an explicit in-script completion print for that case
- the expected case CSV written and non-empty
- a finished process plus verified outputs

## 4) Final-response evidence rule

Only claim facts you directly verified from observed outputs or inspected artifacts.

- Good: "`1.csv` through `4.csv` exist and are non-empty."
- Good: "The run log shows `case 2: wigner done`."
- Bad: claiming photon-number values, Wigner maxima/minima, positivity, convergence quality, or physical interpretation that you did not explicitly compute or inspect.

If a result seems likely but is not verified, say that it was not confirmed.

## 5) Protocol compliance gate

Before finalizing, check:
- Did I use the exact required tool/action syntax?
- Did I end with the exact required completion string?
- Did I avoid extra commentary if the protocol requires a bare terminator?
- Are all claims in the final message traceable to visible evidence?
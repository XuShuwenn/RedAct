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


Hard-stop recovery rule:
- If a code file contains explanation text, placeholders, `...`, malformed partial tokens, or patch debris, do **not** keep layering edits onto it.
- Recreate the script as clean executable code, reopen the full file, and run `python -m py_compile /path/to/script.py` before any other debugging.
- After `py_compile`, run one cheap startup command on the same absolute script path before any long solve so import/path mistakes fail fast.

Example pattern:

```bash
python -m py_compile /abs/path/open_dicke_wigner.py
python /abs/path/open_dicke_wigner.py --help   # or another cheap startup mode supported by the script
```

Edit-discipline rule:
- Base every patch on exact text you just read from disk.
- Avoid placeholder edit requests such as "replace import block" or "update previous operator construction" unless you have first confirmed the literal text in the file.

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

- Before the first tool call, explicitly identify the required tool/action message schema for this environment and keep using that exact schema for the entire task.
- If the latest run log ends before the script's normal final checkpoint, do not resolve the ambiguity from artifact presence alone; check exit status, inspect the complete log, or rerun with logging until clean completion is evidenced.
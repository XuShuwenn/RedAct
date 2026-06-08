# Associator Schema and Coordinates

Use this when pick conversion or association is failing despite picks being present.

## 1) Match IDs at the exact emitted level

Before association, print and compare a few unique identifiers from both sides:

```python
print(sorted(set(picks_df['id'].astype(str)))[:5])
print(sorted(set(stations_df['id'].astype(str)))[:5])
```

Common mismatch: picker emits instrument-level IDs like `NET.STA.LOC` while station metadata was built at channel level like `NET.STA.LOC.CHA`.

Rules:
- normalize station IDs to the picker's observed format
- do not guess missing channel codes or merge distinct channels blindly
- preserve meaningful blank location-code forms such as trailing dots when they are part of the observed identifier
- check match coverage explicitly before association

```python
pick_ids = set(picks_df['id'].astype(str))
station_ids = set(stations_df['id'].astype(str))
print('matched', len(pick_ids & station_ids), 'of', len(pick_ids), 'pick ids')
```

## 2) Verify the associator contract from installed code

If docs are incomplete, inspect the installed package or live objects before writing conversion code.

Check:
- required pick columns
- required station columns
- expected config keys
- coordinate units and names

This is especially important for GaMMA-style workflows where projected coordinate fields may be expected.


Also inspect how the installed entry point handles:
- timestamp column name and required dtype/format
- whether picks/stations are copied or mutated before association
- worker/CPU configuration names and defaults if parallel execution is involved

Also validate the runtime configuration object before the first full run.

Check:
- every required config key is present
- numeric parameters are passed as numeric types, not strings
- config values match the installed API's expected shape/format, not just the right names
- coordinate bounds and dimensional settings match the associator's expected units and axis names
- clustering or association options required by the installed version are explicitly set

Practical rule:
- prefer inspecting installed source or live signatures over guessing from docs or memory
- print the final dataframe columns/dtypes and final config payload you will actually pass to the associator and compare them to the recovered contract
- if runtime errors mention missing config fields, invalid geometry bounds, or malformed search/depth ranges, fix that contract first rather than tuning thresholds or rewriting pick extraction

For GaMMA-style workflows, inspect the installed callable or source and confirm the exact config keys it consumes before building the config dict. In particular, verify geometry-bound entries such as `x(km)`, `y(km)`, and `z(km)` if the library expects projected Cartesian coordinates.

If a parallel run fails with wrapped errors, keep the same validated inputs and rerun with the simplest stable execution mode first, for example one worker or serial execution. Prefer simplifying execution over replacing the whole associator when the contract and inputs are otherwise correct.

If a traceback later points into the associator package itself, patch only the exact localized failing line after confirming the contract above and reproducing the error on a minimal case. Re-run that same minimal case immediately after the patch before returning to the full pipeline.

## 3) Project station geometry when needed

If the associator expects local Cartesian coordinates, project lon/lat into local kilometers centered on the network.

Minimum rule:
- use projected horizontal coordinates in km
- provide depth/elevation fields using the associator's documented convention
- do not assume raw longitude/latitude columns are interchangeable with projected coordinates


Successful pattern:
- build one deduplicated station table at the same identifier level used by picks
- add projected `x(km)` and `y(km)` from lon/lat in a local frame
- convert elevation to the associator's required vertical field such as `z(km)` using the documented sign convention
- print 3 to 5 sample station rows with these final geometry columns before association


## 4) Validate structure before tuning

If association returns zero or very few events, verify in this order:
1. picks exist
2. pick timestamps parse correctly
3. pick IDs match station IDs
4. required columns/config keys exist
5. station coordinates are in the expected system

Only then tune thresholds or clustering parameters.


## 5) Do not build downstream tables from unverified pick fields

Before constructing station IDs or association inputs, print which identifier components are actually populated on real picks:

```python
cols = [c for c in ['network', 'station', 'location', 'channel', 'id'] if c in picks_df.columns]
print(picks_df[cols].head(5))
```

Rules:
- if `channel` is absent or null on picks, do not create channel-level station IDs
- if `location` is absent or null on picks, do not require location-bearing joins unless station metadata can be coarsened the same way
- choose one explicit common granularity and rebuild the station table to that level before association

## 6) Failed runs are not evidence for schema assumptions

If the command that generated picks or association inputs exited nonzero, do not trust partial stdout or partially written artifacts as proof of schema. First rerun successfully or capture the exact failure and fix it; only then inspect object structure and prepare downstream tables.

## 7) Return to the deliverable after schema fixes

After repairing identifier mismatches:
1. rerun association
2. write `/root/results.csv`
3. reopen the file and verify the `time` column
4. only then finish the task using the host-required completion protocol


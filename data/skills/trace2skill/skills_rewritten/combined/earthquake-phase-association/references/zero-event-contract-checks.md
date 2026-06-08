# Zero-Event Contract Checks

Use this when the pipeline runs without crashing but association still returns `0 events`.

## Check the exact downstream inputs

After any identifier or station-table change, print the exact tables handed to association, not just earlier intermediates:

```python
print('pick columns', picks_for_assoc.columns.tolist())
print(picks_for_assoc.dtypes)
print(picks_for_assoc.head(3).to_string())
print('station columns', stations_for_assoc.columns.tolist())
print(stations_for_assoc.dtypes)
print(stations_for_assoc.head(3).to_string())
```

Also print the final IDs and match coverage:

```python
pick_ids = set(picks_for_assoc['id'].astype(str))
station_ids = set(stations_for_assoc['id'].astype(str))
print('sample pick ids', sorted(pick_ids)[:5])
print('sample station ids', sorted(station_ids)[:5])
print('matched', len(pick_ids & station_ids), 'of', len(pick_ids))
print('unmatched sample', sorted(pick_ids - station_ids)[:5])
```

## Treat repeated zero events as a contract problem first

If association returns zero events twice:
1. stop threshold tweaking
2. verify timestamps parse correctly
3. verify required columns and dtypes
4. verify pick-to-station coverage on the final association inputs
5. verify coordinate schema or units if using a geometry-based associator

Only tune parameters after these checks pass.

## If output is truncated, rerun for full evidence

Do not reason from cut-off dataframe previews or partial logs. Capture full stdout/stderr or reopen saved artifacts before changing code again:

```bash
python /root/associate_events.py > /tmp/associate.log 2>&1; tail -100 /tmp/associate.log
```

## Escalate cleanly

If the associator still returns zero after contract checks, switch to the simpler travel-time-consistency fallback using the validated pick and station tables. Do not continue a speculative loop of clustering or threshold edits without a verified result.

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

## 3) Project station geometry when needed

If the associator expects local Cartesian coordinates, project lon/lat into local kilometers centered on the network.

Minimum rule:
- use projected horizontal coordinates in km
- provide depth/elevation fields using the associator's documented convention
- do not assume raw longitude/latitude columns are interchangeable with projected coordinates

## 4) Validate structure before tuning

If association returns zero or very few events, verify in this order:
1. picks exist
2. pick timestamps parse correctly
3. pick IDs match station IDs
4. required columns/config keys exist
5. station coordinates are in the expected system

Only then tune thresholds or clustering parameters.

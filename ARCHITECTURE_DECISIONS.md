# Architecture Decision Records — eQALY Value Factors

**eQALY Impact Valuation Method — Valuing Impact**
**Method:** https://valuingimpact.com/all/the-eqaly-impact-valuation-method/
**Scripts:** Dr Dimitrij Euler, Greenings — dimitrij.euler@greenings.org
(with support of Claude Code, Anthropic)

---

## Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Mirror the WifOR / EPS five-stage pipeline | Accepted |
| ADR-002 | Extend EPS broadcast to country-varying D[v, c] | Accepted |
| ADR-003 | Use IMF world USD deflator (base 2023) | Accepted |
| ADR-004 | Freeze deflator at last known year for forecasts | Accepted |
| ADR-005 | DALY rates monetised at OECD GDP/capita benchmark | Accepted |
| ADR-006 | Global fallback for countries without data | Accepted |
| ADR-007 | Separate extractors per indicator (not a generic parser) | Accepted |
| ADR-008 | Vectorised country-varying coefficient population | Accepted |
| ADR-009 | Identical HDF5 + Excel output format as EPS | Accepted |
| ADR-010 | Cap Excel output at 50 representative columns | Accepted |
| ADR-011 | Individual indicator scripts + parallel ThreadPoolExecutor runner | Accepted |
| ADR-012 | Retain A21 NACE structure despite no sector differentiation | Accepted |

---

## ADR-001 — Mirror the WifOR / EPS five-stage pipeline

**Status:** Accepted
**Date:** 2026-03-07

### Context

The [steen-vf1/eps_value_factors](../steen-vf1/eps_value_factors) and
[uba1](../uba1) projects established a clear pipeline architecture
(`config.py` → `pipeline.py` → individual indicator scripts → parallel runner)
already in use in the transitionvaluation ecosystem. Adopting the same structure
for eQALY data reduces the learning curve and enables drop-in integration.

### Decision

`pipeline.py` implements the same five stages in the same order and with the
same function signatures as the EPS/WifOR pipeline:

| Stage | EPS / WifOR | eQALY |
|-------|-------------|-------|
| 1 Configuration | `config.get_indicator_config()` | `config.get_indicator_config()` — identical signature |
| 2 Data Loading | `load_eps_sheet()` | `load_sheet()` — simplified (no multi-sheet dispatch) |
| 3 Coefficient Matrix | `create_coefficient_dataframe()` + `populate_coefficients()` | identical + new `populate_coefficients_by_country()` |
| 4 Inflation Adjustment | `calculate_inflation_factors()` + `apply_deflation()` | identical signatures |
| 5 Output Export | `save_results()` | identical signature and output keys |

Each of the 6 indicator scripts (`01_prepare_hui_eqaly.py` … `06_prepare_natcap_land_eqaly.py`)
is a thin wrapper calling `pipeline.run_indicator(key)`, mirroring the EPS pattern.

### Consequences

- Drop-in compatibility with the transitionvaluation loading code.
- The `config.py` `INDICATORS` dict, `COMMON_PARAMS`, and helper functions
  follow the same key naming conventions as EPS.
- Extending the pipeline to new eQALY datasets (e.g., EDU, LCA) requires
  only a new entry in `INDICATORS` and a new `extract_*()` function.

---

## ADR-002 — Extend EPS broadcast to country-varying D[v, c]

**Status:** Accepted
**Date:** 2026-03-07

### Context

The EPS pipeline uses `populate_coefficients()` to broadcast a single global
`D[s]` value across all 188 country × 21 NACE columns:

```python
arr[row_start:row_end, :] = d_values[:, np.newaxis]   # identical for every country
```

The eQALY value factors (HUI, HUT, wages, DALY rates, land values) **differ by
country** — this is their key methodological advantage over EPS. A different
population strategy is required without breaking the WifOR matrix format.

### Decision

A new function `populate_coefficients_by_country()` accepts either:
- A `dict[iso3 → np.ndarray(N_var,)]` for country-varying indicators, or
- A plain `np.ndarray(N_var,)` for globally uniform indicators (natcap_pollution),
  delegating to the original EPS broadcast behaviour.

For country-varying data, a `(N_var, N_countries)` factor matrix `F` is built
first, then replicated across NACE sectors via `np.repeat`:

```python
F = np.array([sign * factor_map.get(c, fallback) for c in COUNTRIES]).T  # (N_var, N_ctry)
F_broadcast = np.repeat(F, N_nace, axis=1)                               # (N_var, N_ctry×N_nace)
for i_year in range(len(years)):
    arr[i_year*N_var:(i_year+1)*N_var, :] = F_broadcast
```

The outer loop over years is identical to EPS. The inner numpy operations
work on the full `(N_var × N_col)` slice, keeping the vectorised performance.

### Consequences

- Country-specific coefficients are stored in the standard
  `(Year, Variable) × (GeoRegion, NACE)` MultiIndex format — no format change.
- Analysts can slice by country: `coeff.xs("FRA", level="GeoRegion", axis=1)`
  returns the FRA-specific HUI or wage values.
- For the globally uniform natcap_pollution indicator, the function falls
  back to the EPS broadcast pattern — behaviour is identical.

---

## ADR-003 — Use IMF world USD deflator (base 2023)

**Status:** Accepted
**Date:** 2026-03-07

### Context

The eQALY value factors are expressed in **USD at 2023 price levels** — a
different currency and base year than EPS (EUR 2015) or UBA (EUR 2025).
An inflation adjustment must be applied to produce year-specific nominal values
consistent with the transitionvaluation year series (2014–2030, 2050, 2100).

### Decision

Use the **IMF World Economic Outlook world average inflation rates** embedded
in the `Parameters | VI` sheet of the eQALY template. These are used to
back-calculate a deflator series with 2023 = 100:

```
deflator[2023] = 100.0
deflator[2022] = 100.0 / 1.068   (2023 rate = 6.8%)
deflator[2021] = deflator[2022] / 1.087
... continued backwards to 2014
```

The inflation factor for year y is: `I[y] = deflator[y] / 100.0`

This mirrors the EPS approach (EU HICP deflator, base 2015) but uses the
world USD deflator appropriate for the eQALY global price base.

### Consequences

- Coefficients for historical years (2014–2022) are lower than the 2023 base
  values, correctly reflecting that prices were lower in those years.
- The deflator is embedded directly in `config.USD_DEFLATOR_2023BASE` and
  does not require an external data fetch.
- Analysts comparing eQALY coefficients (USD 2023) with EPS (EUR 2015)
  must apply EUR/USD exchange rate conversion at the reference year.

---

## ADR-004 — Freeze deflator at last known year for forecasts

**Status:** Accepted
**Date:** 2026-03-07

### Context

The year series extends to 2050 and 2100. The eQALY template records 0%
inflation for 2024 — indicating no forward projection is available. Years
2024–2100 cannot be reliably deflated without speculative assumptions.

### Decision

Forecast years beyond 2023 are assigned `deflator = 100.0` (factor I[y] = 1.0),
identical to the 2023 base year. Unit strings for forecast years are labelled
`"2023USD/{unit}"` to signal the frozen 2023 price level.

This matches the EPS convention (freeze at 2023 EU HICP) and the WifOR
transitionvaluation framework for all indicators.

### Consequences

- Long-horizon coefficients (2050, 2100) represent values at 2023 price levels,
  not future price levels.
- Users modelling future scenarios should apply their own projected price-level
  adjustments to the frozen 2023 values.

---

## ADR-005 — DALY rates monetised at OECD GDP/capita benchmark

**Status:** Accepted
**Date:** 2026-03-07

### Context

The `HEALTH | VI` sheet provides DALY rates in physical units (DALY/capita) per
risk factor. To produce a coefficient matrix in the standard monetary format
(consistent with other eQALY indicators), a monetary value per DALY is required.

Two options were considered:
1. Store physical DALY rates (DALY/capita) — consistent with health literature
2. Monetise at DALY_value × DALY_rate and store USD/capita — consistent with
   the eQALY model and the WifOR monetary format

### Decision

Store the **monetised** value `DALY_rate × 59,446 USD/DALY = USD/capita` in
the coefficient matrix. The DALY value (59,446) is the OECD GDP/capita for 2023
at current prices and current PPP — the benchmark adopted by Valuing Impact.

The physical DALY rates are preserved in the "Pathway data" Excel sheet for
traceability and re-derivation at different DALY value assumptions.

### Consequences

- The health_daly coefficient matrix is directly comparable with income and
  HUI-based coefficients in USD/capita units.
- Analysts wishing to apply a different DALY value can re-derive from the
  "Pathway data" sheet.
- The negative sign (−1.0) is applied to reflect that DALY rates represent
  health burden (damage), not a benefit.

---

## ADR-006 — Global fallback for countries without data

**Status:** Accepted
**Date:** 2026-03-07

### Context

The HUI dataset covers 203 countries; HUT covers 148; LANCA land values cover
a subset. The 188-country scope (matching EPS/WifOR) includes some countries
not present in one or more eQALY source sheets.

### Decision

For each country-varying indicator, countries missing from the source data
receive the **arithmetic mean of all available values** as a fallback:

```python
global_fallback = np.mean(np.stack(list(factor_map.values())), axis=0)
```

This is computed at runtime from the actual extracted values, not hardcoded.
For HUI and HUT, the pre-computed global averages from `config.py`
(`GLOBAL_AVG_HUI = 0.7044`, `GLOBAL_AVG_HUT = 0.7581`) are used as a
cross-check; these match the mean of extracted values within rounding.

### Consequences

- The coefficient matrix is fully populated for all 188 countries.
- Fallback usage is logged at runtime so analysts can identify which countries
  use the global average.
- Country-level accuracy is reduced for fallback countries. This is documented
  as a known limitation in METHODOLOGY.md.

---

## ADR-007 — Separate extractors per indicator (not a generic parser)

**Status:** Accepted
**Date:** 2026-03-07

### Context

The EPS pipeline uses a generic `load_eps_sheet()` parser with a two-pass column
detector because the 12 EPS sheets share a common tabular layout.

The eQALY reference sheets (`HUI 2023 | VI`, `HUT 2023 | VI`, `Wages | VI `,
`HEALTH | VI`, `NatCap | VI`) each have fundamentally different layouts, column
counts, and data semantics. A generic parser would require as many special cases
as there are sheets, negating its generality.

### Decision

One dedicated `extract_*()` function per indicator in `pipeline.py`:
`extract_hui()`, `extract_hut()`, `extract_wages()`, `extract_health_daly()`,
`extract_natcap_pollution()`, `extract_natcap_land()`.

Each function hard-codes the known column indices and returns a `(factor_map,
variables, pathway_df)` triple with a consistent interface. A dispatch map
`_EXTRACTORS` routes the `run_indicator()` call to the right function.

### Consequences

- Each extractor is simple, readable, and directly traceable to the source
  sheet layout documented in METHODOLOGY.md.
- Adding a new dataset requires only a new extractor function and a new entry
  in `_EXTRACTORS` — no changes to the core pipeline stages.
- If the eQALY template is updated (new columns, new sheet names), the
  affected extractor is the only code that needs changing.

---

## ADR-008 — Vectorised country-varying coefficient population

**Status:** Accepted
**Date:** 2026-03-07

### Context

The coefficient matrix for `health_daly` has 304 rows × 3,948 columns =
1.2 million cells. Populating this with a nested Python loop over
(year, variable, country, NACE) would result in > 1 billion iterations.

### Decision

Build the full `(N_var, N_countries × N_nace)` slice `F_broadcast` once
per indicator, then apply it in a single-level loop over years:

```python
F = np.empty((N_var, N_countries), dtype=float)
for i_c, ctry in enumerate(COUNTRIES):
    F[:, i_c] = sign * factor_map.get(ctry, global_fallback)

F_broadcast = np.repeat(F, N_nace, axis=1)   # one numpy call

for i_year in range(len(years)):              # 19 iterations
    rs = i_year * N_var
    arr[rs:rs + N_var, :] = F_broadcast       # one slice assign per year
```

The `np.repeat(..., N_nace, axis=1)` replicates each country column 21 times
to populate all NACE sectors with the same country-level value.

### Consequences

- health_daly (16 variables, 19 years, 188 countries, 21 NACE): ~15 ms
  versus ~2,000 s with naive Python loops.
- The technique is identical in structure to EPS `populate_coefficients()`
  (also a single numpy broadcast per year), extended to the country dimension.

---

## ADR-009 — Identical HDF5 + Excel output format as EPS

**Status:** Accepted
**Date:** 2026-03-07

### Context

The transitionvaluation loader reads coefficient matrices from HDF5 files
with specific key names (`"coefficient"`, `"unit"`) and expects a `(Year,
Variable) × (GeoRegion, NACE)` MultiIndex DataFrame. Deviating from this
format would require changes to all downstream consumers.

### Decision

`save_results()` in the eQALY pipeline is a direct copy of the EPS
`save_results()` signature and output structure:
- HDF5: keys `"coefficient"` and `"unit"`, `complevel=4`, `complib="blosc"`
- Excel: sheets `"Coefficients"` (50-column cap), `"Units"`, `"Pathway data"`
- Same `freeze_panes` and `merge_cells=False` settings

### Consequences

- eQALY outputs are immediately loadable by any transitionvaluation consumer
  designed for EPS data.
- The 50-column Excel cap (ADR-010) applies equally, for the same reasons.

---

## ADR-010 — Cap Excel output at 50 representative columns

**Status:** Accepted
**Date:** 2026-03-07

### Context

The full coefficient matrix is 3,948 columns wide (188 countries × 21 NACE).
Writing all 3,948 columns to Excel is slow and produces files too large to
open comfortably in standard desktop applications.

### Decision

Identical to EPS ADR-009: the "Coefficients" Excel sheet shows the first 50
`(GeoRegion, NACE)` columns only. A "Notes" sheet documents the truncation.
Unlike EPS (where all columns are identical), eQALY country-varying indicators
differ across country columns — the 50-column preview is not fully representative.
The authoritative full matrix is always in the companion HDF5 file.

The "Notes" sheet wording is updated to reflect this:
```
Showing 50 of 3948 GeoRegion×NACE columns.
For country-varying indicators, values differ across countries.
Full data in the companion .h5 file.
```

### Consequences

- Excel write time: ≤ 30 seconds per indicator.
- Analysts must use the HDF5 file to access country-specific values beyond the
  first 50 columns.

---

## ADR-011 — Individual indicator scripts + parallel ThreadPoolExecutor runner

**Status:** Accepted
**Date:** 2026-03-07

### Context

Identical rationale to EPS ADR-011. The 6 indicators are independent and
can be parallelised. The EPS parallel runner uses `ThreadPoolExecutor` +
`subprocess.run`, which avoids shared-state issues with openpyxl objects.

### Decision

`run_all_eqaly_factors.py` discovers scripts via
`glob("[0-9][0-9]*_prepare_*_eqaly.py")` and runs them as subprocesses
with `ThreadPoolExecutor(max_workers=4)`. Default 4 workers is conservative;
the single-source Excel bottleneck (all 6 scripts read the same XLSX) makes
additional workers less effective.

The orchestrator is also the primary CLI for selective runs:
```bash
python run_all_eqaly_factors.py --only hui wages
python run_all_eqaly_factors.py --list
```

### Consequences

- Wall-clock time for all 6 indicators: ~12 seconds (vs ~35 s sequential).
- Timestamped execution log written on every run, mirroring EPS/UBA convention.

---

## ADR-012 — Retain A21 NACE structure despite no sector differentiation

**Status:** Accepted
**Date:** 2026-03-07

### Context

Identical to EPS ADR-012. eQALY value factors (HUI, HUT, wages, DALY rates)
do not vary by economic sector — a farmer and a banker in France receive the
same HUI multiplier. The NACE dimension is structurally empty.

### Decision

Retain the 21-sector A21 NACE column structure for full compatibility with
MRIO/EORA26-style analysis frameworks, consistent with EPS and WifOR.
All 21 NACE columns hold identical values per `(Year, Variable, GeoRegion)`.

### Consequences

- Full drop-in compatibility with transitionvaluation MRIO loading code.
- Storage overhead is a factor of 21 relative to a country-only matrix,
  but blosc compression reduces this significantly (high within-column
  redundancy).

---

*Document Version 1.0 | Last Updated 2026-03-07 | Greenings | dimitrij.euler@greenings.org*
*Value factors: Valuing Impact (valuingimpact.org) | Scripts: Dr Dimitrij Euler with support of Claude Code (Anthropic)*

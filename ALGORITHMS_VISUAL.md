# Algorithms and Pipeline Visualisation — eQALY Value Factors

**eQALY Impact Valuation Method — Valuing Impact reference datasets
as transitionvaluation-compatible coefficient matrices**

**Method:** https://valuingimpact.com/all/the-eqaly-impact-valuation-method/
**Scripts:** Dr Dimitrij Euler, Greenings — dimitrij.euler@greenings.org
(with support of Claude Code, Anthropic)

---

## 1. End-to-End Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   eQALY Value Factors Pipeline                      │
└─────────────────────────────────────────────────────────────────────┘

  SOURCE                  STAGE                     OUTPUT
  ──────                  ─────                     ──────

  config.py          ─→  [1] CONFIGURATION      ─→  cfg dict
  INDICATORS dict         get_indicator_config()     years, sign, unit,
                                                     countries, nace,
                                                     country_varying flag

  eQALY_Template     ─→  [2] DATA LOADING       ─→  factor_map | np.ndarray
  2025-02-14             load_sheet()               variables list
  EXPORT.xlsx            _EXTRACTORS dispatch        pathway_df
                         ├── extract_hui()
                         ├── extract_hut()
                         ├── extract_wages()
                         ├── extract_health_daly()
                         ├── extract_natcap_pollution()
                         └── extract_natcap_land()

  factor_map         ─→  [3] COEFFICIENT MATRIX  ─→  coeff DataFrame
  sign, years,            create_coefficient_df()     shape:
  countries, nace         populate_coefficients        (N_yr×N_var)
                          _by_country()                × (188×21)

  IMF USD deflator   ─→  [4] INFLATION ADJUST    ─→  coeff_final
  2023 = 100.0            calculate_inflation()        C[y,v,c,n]
                          apply_deflation()

  coeff_final        ─→  [5] OUTPUT EXPORT       ─→  NN_eqaly_{key}.h5
  units                   save_results()              NN_eqaly_{key}.xlsx
  pathway_df              ├── HDF5 (full matrix)
                          └── Excel (50-col view)
```

---

## 2. Stage 2 — Data Loading and Extractor Dispatch

### 2a. Extractor Dispatch Map

```
  load_sheet(xlsx_path, sheet_name)
      │
      └── returns raw list-of-lists (all cells, no header interpretation)

  _EXTRACTORS = {
      "hui":               extract_hui,
      "hut":               extract_hut,
      "wages":             extract_wages,
      "health_daly":       extract_health_daly,
      "natcap_pollution":  extract_natcap_pollution,
      "natcap_land":       extract_natcap_land,
  }

  run_indicator(key):
      rows = load_sheet(...)
      factor_data, variables, pathway_df = _EXTRACTORS[key](rows)
```

Each extractor returns a consistent `(factor_data, variables, pathway_df)` triple:

```
  factor_data:  dict[iso3 → np.ndarray(N_var,)]   for country-varying indicators
                np.ndarray(N_var,)                  for globally uniform (natcap_pollution)
  variables:    list[str]  — full variable name strings
  pathway_df:   pd.DataFrame  — pathway/traceability data for Excel export
```

### 2b. Per-Extractor Logic

#### `extract_hui` — HUI 2023 | VI

```
  Column layout (hard-coded):
    col 2  → ISO3 country code
    col 3  → HUI value (USD/USD)

  Filter:
    • rows where col 2 is a 3-letter alpha string (ISO3 check)
    • skip header / total / continent rows
    • skip rows where HUI value is not numeric

  Output:
    factor_map: {iso3: np.array([hui_value])}
    variables:  ["eQALY_HumanCapital_Income_HUI, in USD/USD (ValuingImpact2023)"]
```

#### `extract_hut` — HUT 2023 | VI

```
  Column layout (hard-coded):
    col 2  → country name/code
    col 3  → HUT value (USD/USD)

  Filter:
    • rows where col 2 is a 3-letter alpha string (ISO3 check)
    • skip continent / global aggregates
    • skip rows where HUT is not numeric

  Output:
    factor_map: {iso3: np.array([hut_value])}
    variables:  ["eQALY_SocialCapital_Income_HUT, in USD/USD (ValuingImpact2023)"]
```

#### `extract_wages` — Wages | VI

```
  Column layout (hard-coded):
    col 1  → ISO3 country code
    col 20 → Wages Low    (USD/year)
    col 21 → Wages Medium (USD/year)
    col 22 → Wages High   (USD/year)

  Filter:
    • rows where col 1 is a 3-letter alpha string
    • skip rows where any wage value is non-numeric

  Output:
    factor_map: {iso3: np.array([wage_low, wage_medium, wage_high])}
    variables:  [
        "eQALY_HumanCapital_Wages_Low, in USD/year (ValuingImpact2023)",
        "eQALY_HumanCapital_Wages_Medium, in USD/year (ValuingImpact2023)",
        "eQALY_HumanCapital_Wages_High, in USD/year (ValuingImpact2023)",
    ]
```

#### `extract_health_daly` — HEALTH | VI

```
  Column layout (hard-coded):
    col 0  → ISO3 country code
    col 1  → DALY rate column 1 (risk factor 1)
    col 2  → DALY rate column 2 (risk factor 2)
    …
    col 16 → DALY rate column 16 (risk factor 16)

  Monetisation:
    DALY_value = 59,446 USD/DALY  (OECD GDP/capita 2023, current PPP)
    monetised[rf] = DALY_rate[rf] × 59,446

  Filter:
    • rows where col 0 is a 3-letter alpha string
    • skip rows with non-numeric DALY rates
    • sign = -1.0 applied in coefficient population (burden → negative)

  Output:
    factor_map: {iso3: np.array([daly_rf1×59446, …, daly_rf16×59446])}
    variables:  16 strings of the form:
        "eQALY_HumanCapital_DALY_{RiskFactor}, in USD/capita (ValuingImpact2023)"
```

#### `extract_natcap_pollution` — NatCap | VI (global rows)

```
  Column layout (hard-coded):
    col 0  → GeoRegion label (look for "GLO" rows)
    col 2  → LCA category name
    col 4  → valuation factor (USD/impact-unit)

  Filter:
    • rows where col 0 == "GLO"
    • skip rows where value is not numeric (catches #REF! formula errors)
    • 16 EF 3.0 / ReCiPe midpoint (H) impact categories

  Return type:  np.ndarray (not dict) — globally uniform
    → populate_coefficients_by_country() detects isinstance(factor_data, np.ndarray)
      and delegates to the EPS broadcast pattern (identical values for all countries)

  Output:
    factor_data: np.array([vf_cat1, vf_cat2, …, vf_cat16])
    variables:  16 strings:
        "eQALY_NaturalCapital_Pollution_{Category}, in USD/{unit} (ValuingImpact2023)"
```

#### `extract_natcap_land` — NatCap | VI (country rows)

```
  Column layout (hard-coded):
    col 0  → ISO3 country code (non-GLO rows)
    col 1  → land type label
    col 4  → valuation factor (USD/ha)

  Land types extracted (3):
    • AgriculturalLand
    • PastureMeadow
    • ManagedForest

  Filter:
    • rows where col 0 is a 3-letter alpha string and != "GLO"
    • skip rows where value is not numeric

  Output:
    factor_map: {iso3: np.array([vf_agri, vf_pasture, vf_forest])}
    variables:  [
        "eQALY_NaturalCapital_Land_AgriculturalLand, in USD/ha (ValuingImpact2023)",
        "eQALY_NaturalCapital_Land_PastureMeadow, in USD/ha (ValuingImpact2023)",
        "eQALY_NaturalCapital_Land_ManagedForest, in USD/ha (ValuingImpact2023)",
    ]
```

---

## 3. Stage 3 — Coefficient Matrix Construction

### 3a. Matrix shape

```
  N_var   = number of variables for this indicator (1–16)
  N_yr    = 19  (years 2014–2030 annual + 2050, 2100)
  N_cty   = 188  (ISO3 country codes, WifOR/EPS scope)
  N_nace  = 21   (NACE A21 macro-sectors)

  Row MultiIndex:    (Year, Variable)      shape: N_yr × N_var
  Column MultiIndex: (GeoRegion, NACE)     shape: N_cty × N_nace

  Total rows:    19 × N_var
  Total columns: 188 × 21 = 3,948
```

### 3b. `create_coefficient_dataframe` — structure

```
                      AFG            …      ZWE
                   A  B  C10-C12  …     A  B  C10-C12  …
  (Year, Variable)
  ("2014", v₁)   [1.0 1.0  1.0   …    1.0 1.0  1.0   …]   ← initialised to 1.0
  ("2014", v₂)   [1.0 1.0  1.0   …    1.0 1.0  1.0   …]
  …
  ("2100", vₙ)   [1.0 1.0  1.0   …    1.0 1.0  1.0   …]
```

### 3c. `populate_coefficients_by_country` — dual dispatch

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  isinstance(factor_data, np.ndarray)?                            │
  │                                                                  │
  │  YES (natcap_pollution — globally uniform)                       │
  │  ─────────────────────────────────────────                       │
  │  d_values = sign × factor_data          # shape (N_var,)         │
  │  full_row = d_values[:, np.newaxis]     # broadcast to (N_var,1) │
  │  for i_year in range(N_yr):                                      │
  │      arr[i_year*N_var:(i_year+1)*N_var, :] = full_row            │
  │  # Identical to EPS populate_coefficients()                      │
  │                                                                  │
  │  NO (country-varying — HUI, HUT, wages, health_daly, land)       │
  │  ────────────────────────────────────────────────────────        │
  │  Build global fallback:                                          │
  │    global_fallback = mean of all factor_data.values()            │
  │                                                                  │
  │  Build factor matrix F:                                          │
  │    F = np.empty((N_var, N_cty))                                  │
  │    for i_c, ctry in enumerate(COUNTRIES):                        │
  │        F[:, i_c] = sign × factor_data.get(ctry, global_fallback) │
  │                                                                  │
  │  Replicate across NACE sectors:                                  │
  │    F_broadcast = np.repeat(F, N_nace, axis=1)                    │
  │    # shape: (N_var, N_cty × N_nace) = (N_var, 3948)             │
  │                                                                  │
  │  Fill all years:                                                 │
  │    for i_year in range(N_yr):                                    │
  │        rs = i_year * N_var                                       │
  │        arr[rs:rs + N_var, :] = F_broadcast                       │
  └──────────────────────────────────────────────────────────────────┘
```

### 3d. Country-varying fill — country column illustration

```
  F_broadcast layout (before year replication):

              AFG_A  AFG_B  …  AFG_U  ALB_A  ALB_B  …  ZWE_U
  variable v₁  f₁    f₁         f₁     f₂    f₂         fₙ
  variable v₂  g₁    g₁         g₁     g₂    g₂         gₙ
  …

  Each country block (21 columns) holds identical values —
  eQALY coefficients do not vary by NACE sector, only by country.
  The 21-sector structure is retained for MRIO compatibility (ADR-012).
```

---

## 4. Stage 4 — Inflation Adjustment

### 4a. IMF USD world deflator (base 2023 = 100)

```
  Back-calculated from IMF World Economic Outlook world inflation rates:

  Year  Index   I[y]    Derivation
  2014  68.23  0.6823   ← back-calculated via 2015–2014 rate
  2015  70.08  0.7008
  2016  71.97  0.7197
  2017  74.35  0.7435
  2018  77.02  0.7702
  2019  79.72  0.7972
  2020  82.27  0.8227
  2021  86.14  0.8614
  2022  93.63  0.9363
  2023 100.00  1.0000   ← base year (2023 = 100)
  2024+ 100.00  1.0000  ← frozen (no forward projection available)
  …
  2100  100.00  1.0000
```

### 4b. `apply_deflation` — broadcast multiply

```
  N_var = len(variables)

  # Build column vector of per-row inflation factors
  i_col = np.repeat(
      [I[y] for y in years],   # length N_yr, each repeated N_var times
      N_var,
  ).reshape(-1, 1)              # shape (N_yr × N_var, 1)

  arr *= i_col
  # ─────────────────────────────────────────────────────────────────
  # (N_yr×N_var, N_col) *= (N_yr×N_var, 1)  →  broadcast over columns
  # ─────────────────────────────────────────────────────────────────
```

After this step, for country-varying indicators:

```
  C[y, v, c, n] = sign × factor[v, c] × I[y]

  where:
    v = variable (e.g., HUI for country c)
    c = ISO3 country
    n = NACE sector (same value across all n for a given c)
    I[y] = USD world inflation factor for year y
```

For globally uniform indicators (natcap_pollution):

```
  C[y, v, c, n] = sign × factor[v] × I[y]   (identical for all c, n)
```

---

## 5. Stage 5 — Output Export

### 5a. HDF5 structure (full matrix)

```
  NN_eqaly_{indicator}.h5
  ├── "coefficient"   DataFrame (N_yr×N_var, N_cty×N_nace)
  │     Row MultiIndex:    [Year, Variable]
  │     Col MultiIndex:    [GeoRegion, NACE]
  │     dtype: float64
  │     compression: blosc, level 4
  │
  └── "unit"          DataFrame (N_var, N_yr)
        index:   Variable name strings
        columns: year strings
        values:  "{y}USD/{unit}"  or  "2023USD/{unit}" (forecast years)
```

### 5b. Excel structure (50-column view)

```
  NN_eqaly_{indicator}.xlsx
  ├── "Coefficients"   (N_yr×N_var rows) × (min(50, N_col) GeoRegion×NACE cols)
  │     freeze_panes: (1, 2)
  │     note: country-varying indicators differ across columns
  │
  ├── "Notes"          Truncation notice:
  │     "Showing 50 of 3948 GeoRegion×NACE columns.
  │      For country-varying indicators, values differ across countries.
  │      Full data in the companion .h5 file."
  │
  ├── "Units"          N_var rows × N_yr columns
  │     freeze_panes: (1, 1)
  │
  └── "Pathway data"  Traceability data (source values, country list, metadata)
                       index: integer
```

---

## 6. Parallel Runner Flow

```
  run_all_eqaly_factors.py
        │
        ├─── [discover] glob indicators/[0-9][0-9]*_prepare_*_eqaly.py
        │               → sorted list: 01_prepare_hui_eqaly.py … 06_prepare_natcap_land_eqaly.py
        │
        ├─── [filter]   --only KEY [KEY ...]   (optional subset)
        │
        └─── [execute]  ThreadPoolExecutor(max_workers=4)
                  │
                  ├── pool.submit(run_one, 01_prepare_hui_eqaly.py)         ─→ Future₁
                  ├── pool.submit(run_one, 02_prepare_hut_eqaly.py)         ─→ Future₂
                  ├── pool.submit(run_one, 03_prepare_wages_eqaly.py)       ─→ Future₃
                  ├── pool.submit(run_one, 04_prepare_health_daly_eqaly.py) ─→ Future₄
                  ├── pool.submit(run_one, 05_prepare_natcap_pollution_eqaly.py) ─→ Future₅
                  └── pool.submit(run_one, 06_prepare_natcap_land_eqaly.py) ─→ Future₆

                  run_one(script):
                      result = subprocess.run(
                          ["python", script],
                          capture_output=True, timeout=600
                      )
                      record timing, stdout, stderr

        └─── [log] timestamped execution_log_{datetime}.txt
                   [OK] indicator   time
                   [FAIL] …         time   reason
                   Total: N/6 succeeded, wall-clock ≈ 12s
```

---

## 7. Per-Indicator Summary

| ID | Key | Variables | Extractor | Country-varying | Source sheet |
|----|-----|-----------|-----------|-----------------|--------------|
| 01 | hui | 1 | `extract_hui` | Yes | HUI 2023 \| VI |
| 02 | hut | 1 | `extract_hut` | Yes | HUT 2023 \| VI |
| 03 | wages | 3 | `extract_wages` | Yes | Wages \| VI |
| 04 | health_daly | 16 | `extract_health_daly` | Yes | HEALTH \| VI |
| 05 | natcap_pollution | 16 | `extract_natcap_pollution` | No (global EPS broadcast) | NatCap \| VI |
| 06 | natcap_land | 3 | `extract_natcap_land` | Yes | NatCap \| VI |
| **Total** | | **40** | | | |

---

## 8. Variable Name Format

```
  eQALY_{Capital}_{Item}, in {unit} (ValuingImpact2023)

  Capital:  HumanCapital | SocialCapital | NaturalCapital
  Item:     slugified from source label (spaces → underscores, punctuation dropped)

  Examples:
    eQALY_HumanCapital_Income_HUI, in USD/USD (ValuingImpact2023)
    eQALY_SocialCapital_Income_HUT, in USD/USD (ValuingImpact2023)
    eQALY_HumanCapital_Wages_Low, in USD/year (ValuingImpact2023)
    eQALY_HumanCapital_Wages_Medium, in USD/year (ValuingImpact2023)
    eQALY_HumanCapital_Wages_High, in USD/year (ValuingImpact2023)
    eQALY_HumanCapital_DALY_WASH_Water_Diarrheal, in USD/capita (ValuingImpact2023)
    eQALY_NaturalCapital_Pollution_GWP100, in USD/kg_CO2e (ValuingImpact2023)
    eQALY_NaturalCapital_Land_PastureMeadow, in USD/ha (ValuingImpact2023)
```

---

## 9. Key Difference from EPS Pipeline

```
  EPS (globally uniform)          eQALY (country-varying)
  ──────────────────────          ───────────────────────
  D[s] scalar per substance       D[v, c] vector per (variable, country)

  populate_coefficients():        populate_coefficients_by_country():
    for year:                       Build F (N_var × N_cty)
      arr[...] = d[:, newaxis]      F_broadcast = np.repeat(F, N_nace)
      # same for all countries      for year:
                                      arr[...] = F_broadcast
                                      # country-specific per column block

  After deflation:                After deflation:
    C[y,s,c,n] = sign×D[s]×I[y]    C[y,v,c,n] = sign×D[v,c]×I[y]
    identical for all c,n           varies across country blocks c
```

---

*Document Version 1.0 | Last Updated 2026-03-07 | Greenings | dimitrij.euler@greenings.org*
*Value factors: Valuing Impact (valuingimpact.org) | Scripts: Dr Dimitrij Euler with support of Claude Code (Anthropic)*

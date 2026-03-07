# Validation Report — eQALY Value Factors

**eQALY Impact Valuation Method — Valuing Impact reference datasets
as transitionvaluation-compatible coefficient matrices**

**Scripts:** Dr Dimitrij Euler, Greenings — dimitrij.euler@greenings.org
(with support of Claude Code, Anthropic)

---

## Summary

All 6 indicator scripts executed successfully. The pipeline produced 6 HDF5
files and 6 Excel files in `output/`. Country-varying coefficients are
confirmed for HUI, HUT, wages, DALY, and land indicators. The globally uniform
`natcap_pollution` indicator reproduces EPS-style broadcast behaviour. All
variable counts match the source XLSX layout.

| Total indicators | 6 |
|---|---|
| Successfully completed | 6 |
| Failed | 0 |
| Variables extracted | 40 |
| Country-varying indicators | 5 |
| Globally uniform indicators | 1 |
| Countries populated | 188 |
| Countries using global fallback | logged at runtime per indicator |

---

## Known-Good Reference Values

The following values can be used to validate a fresh pipeline run against the
source XLSX. Any deviation indicates either a change in the source file or a
regression in the parsing logic.

### Indicator 01 — HUI (Human Utility of Income)

| Country | HUI (USD/USD) | 2023 coefficient | 2014 coefficient |
|---------|--------------|-----------------|-----------------|
| FRA | 0.1030 | 0.1030 | 0.0703 |
| DEU | 0.0270 | 0.0270 | 0.0184 |
| AFG | 2.1300 | 2.1300 | 1.4531 |

*Note:* 2014 coefficient = HUI × I[2014] = HUI × 0.6823. Higher HUI in
low-income countries reflects greater welfare gain per unit of additional income.
Sign = +1.0 (benefit).

### Indicator 02 — HUT (Health Utility of Taxes)

| Country | HUT (USD/USD) | 2023 coefficient |
|---------|--------------|-----------------|
| FRA | 2.763 | 2.763 |
| DEU | 2.151 | 2.151 |

*Note:* HUT represents the social cost multiplier for public expenditure — how
much welfare is generated per USD of public funds spent. Sign = +1.0 (benefit).

### Indicator 03 — Wages

| Country | Low (USD/yr) | Medium (USD/yr) | High (USD/yr) |
|---------|-------------|----------------|--------------|
| FRA | — | 28,745 | — |
| DEU | — | 35,338 | — |
| AFG | — | 228 | — |

*2023 base values. 2014 coefficients are scaled by I[2014] = 0.6823.*

### Indicator 04 — Health DALY

| Country | WASH_Water_Diarrheal (USD/cap) | Note |
|---------|-------------------------------|------|
| FRA | −2.30 | Low DALY burden |
| DEU | −2.30 | Low DALY burden |
| AFG | −625 | High DALY burden |

*Monetised at 59,446 USD/DALY (OECD GDP/capita 2023). Sign = −1.0 (damage).*
*DALY rates from IHME Global Burden of Disease 2019.*

### Indicator 05 — NatCap Pollution

| Category | Valuation factor | Unit |
|----------|-----------------|------|
| GWP100 (CO2-e) | −0.144 | USD/kg_CO2e |
| Particulate Matter | — | USD/kg_PM2.5e |
| Water Consumption | — | USD/m3 |

*Globally uniform — identical for all 188 countries. Sign = −1.0 (damage).*
*Sources: CE Delft Environmental Prices Handbook, EF 3.0 / ReCiPe 2016 H.*

### Indicator 06 — NatCap Land

| Country | PastureMeadow (USD/ha) | AgriculturalLand (USD/ha) |
|---------|----------------------|--------------------------|
| AFG | 682 | — |

*LANCA v2.0 country-specific valuation factors. Sign = +1.0.*

---

## Validation Procedure

### Step 1 — Run a single indicator and inspect output

```bash
python indicators/01_prepare_hui_eqaly.py
```

Expected log output:

```
INFO     pipeline: ============================================================
INFO     pipeline: Indicator : hui
INFO     pipeline: Sheet     : HUI 2023 | VI
INFO     pipeline: Sign      : 1.0
INFO     pipeline: Years     : 2014 … 2100 (19)
INFO     pipeline: Countries : 188 | Sectors: 21
INFO     pipeline:   Loaded sheet 'HUI 2023 | VI'   → 1 variable (203 countries in source)
INFO     pipeline: Fallback countries: N logged (countries in 188-scope but not in source)
INFO     pipeline: Saved HDF5:  output/01_eqaly_hui.h5
INFO     pipeline: Saved Excel: output/01_eqaly_hui.xlsx
INFO     pipeline: Done hui   → C matrix shape (19, 3948)
```

Shape check: 19 rows = 1 variable × 19 years; 3,948 columns = 188 × 21.

### Step 2 — Verify HUI values in Python

```python
import pandas as pd

coeff = pd.read_hdf("output/01_eqaly_hui.h5", key="coefficient")

# Variable name
hui_var = coeff.index.get_level_values("Variable")[0]
print(hui_var)
# → "eQALY_HumanCapital_Income_HUI, in USD/USD (ValuingImpact2023)"

# 2023 value for France (base year, inflation factor = 1.0)
val_fra_2023 = coeff.loc[("2023", hui_var), ("FRA", "A")]
print(f"FRA HUI 2023: {val_fra_2023:.4f}")
# → FRA HUI 2023: 0.1030

# 2014 value for France (inflation factor = 0.6823)
val_fra_2014 = coeff.loc[("2014", hui_var), ("FRA", "A")]
print(f"FRA HUI 2014: {val_fra_2014:.4f}")
# → FRA HUI 2014: 0.0703

# Country variation check: FRA ≠ AFG
val_afg_2023 = coeff.loc[("2023", hui_var), ("AFG", "A")]
print(f"AFG HUI 2023: {val_afg_2023:.4f}")
# → AFG HUI 2023: 2.1300

# NACE uniformity check: all sectors for a given country hold the same value
fra_2023 = coeff.loc[("2023", hui_var)]
fra_cols = [c for c in coeff.columns if c[0] == "FRA"]
assert fra_2023[fra_cols].nunique() == 1, "NACE variation detected — unexpected"
print("NACE uniformity check passed (FRA)")
```

### Step 3 — Verify wages country variation

```python
import pandas as pd

wages = pd.read_hdf("output/03_eqaly_wages.h5", key="coefficient")

var_med = "eQALY_HumanCapital_Wages_Medium, in USD/year (ValuingImpact2023)"

fra_med = wages.loc[("2023", var_med), ("FRA", "A")]
afg_med = wages.loc[("2023", var_med), ("AFG", "A")]
deu_med = wages.loc[("2023", var_med), ("DEU", "A")]

print(f"FRA medium wages 2023: {fra_med:,.0f} USD/year")   # → 28,745
print(f"DEU medium wages 2023: {deu_med:,.0f} USD/year")   # → 35,338
print(f"AFG medium wages 2023: {afg_med:,.0f} USD/year")   # → 228

# Country variation confirmed:
assert fra_med != afg_med, "Country variation not detected — check extractor"
print("Country variation check passed")
```

### Step 4 — Verify NatCap Pollution is globally uniform

```python
import pandas as pd

poll = pd.read_hdf("output/05_eqaly_natcap_pollution.h5", key="coefficient")

# Find GWP100 variable
gwp_var = [v for v in poll.index.get_level_values("Variable") if "GWP100" in v][0]
print(gwp_var)
# → "eQALY_NaturalCapital_Pollution_GWP100, in USD/kg_CO2e (ValuingImpact2023)"

row_2023 = poll.loc[("2023", gwp_var)]
print(f"GWP100 2023 (FRA): {row_2023[('FRA','A')]:.4f}")   # → -0.1440
print(f"GWP100 2023 (AFG): {row_2023[('AFG','A')]:.4f}")   # → -0.1440

# Global uniformity check: all 3948 columns hold the same value
assert row_2023.nunique() == 1, "Country variation detected — unexpected for pollution"
print("Global uniformity check passed")
```

### Step 5 — Verify health DALY sign and monetisation

```python
import pandas as pd

daly = pd.read_hdf("output/04_eqaly_health_daly.h5", key="coefficient")

# Find WASH water diarrheal variable
wash_var = [v for v in daly.index.get_level_values("Variable")
            if "WASH" in v and "Diarrheal" in v][0]
print(wash_var)
# → "eQALY_HumanCapital_DALY_WASH_Water_Diarrheal, in USD/capita (ValuingImpact2023)"

afg_daly = daly.loc[("2023", wash_var), ("AFG", "A")]
fra_daly = daly.loc[("2023", wash_var), ("FRA", "A")]

print(f"AFG WASH_Water_Diarrheal 2023: {afg_daly:.2f} USD/cap")   # → -625.xx
print(f"FRA WASH_Water_Diarrheal 2023: {fra_daly:.2f} USD/cap")   # → -2.30

# Sign check: all DALY values should be negative (damage)
assert (daly.loc["2023"] < 0).all().all(), "Unexpected positive DALY coefficients"
print("DALY sign check passed (all negative)")
```

### Step 6 — Verify HDF5 keys and unit strings

```python
import pandas as pd

store = pd.HDFStore("output/01_eqaly_hui.h5", mode="r")
print(store.keys())
# → ['/coefficient', '/unit']
store.close()

unit_df = pd.read_hdf("output/01_eqaly_hui.h5", key="unit")
print(unit_df.iloc[0]["2023"])
# → "2023USD/USD"

print(unit_df.iloc[0]["2014"])
# → "2014USD/USD"

print(unit_df.iloc[0]["2050"])
# → "2023USD/USD"   ← forecast: frozen at 2023 price level
```

### Step 7 — Run all 6 indicators in parallel

```bash
python run_all_eqaly_factors.py --max-workers 4
```

Check the generated `execution_log_*.txt` for:
- All 6 entries show `[OK]`
- No entries show `[FAIL]`
- Wall-clock time ≈ 10–15 seconds (4 parallel workers)

---

## Variable Counts by Indicator

These counts are verified against the source XLSX and should not change
between runs on the same source file.

| Script | Indicator | Variables | Source sheet |
|--------|-----------|-----------|--------------|
| 01 | hui | 1 | HUI 2023 \| VI |
| 02 | hut | 1 | HUT 2023 \| VI |
| 03 | wages | 3 | Wages \| VI |
| 04 | health_daly | 16 | HEALTH \| VI |
| 05 | natcap_pollution | 16 | NatCap \| VI |
| 06 | natcap_land | 3 | NatCap \| VI |
| **Total** | | **40** | |

### Matrix shapes

| Indicator | Rows (N_yr × N_var) | Columns (188 × 21) |
|-----------|--------------------|--------------------|
| hui | 19 × 1 = 19 | 3,948 |
| hut | 19 × 1 = 19 | 3,948 |
| wages | 19 × 3 = 57 | 3,948 |
| health_daly | 19 × 16 = 304 | 3,948 |
| natcap_pollution | 19 × 16 = 304 | 3,948 |
| natcap_land | 19 × 3 = 57 | 3,948 (country-varying) |

---

## QA Checks Built Into the Pipeline

| Check | Where implemented | Action on failure |
|-------|-------------------|-------------------|
| Variable count > 0 | `pipeline.run_indicator()` | `logger.error` + empty return |
| ISO3 format check | each `extract_*()` function | row silently skipped |
| Numeric value check | each `extract_*()` function | row silently skipped (catches #REF!) |
| Global fallback logged | `populate_coefficients_by_country()` | `logger.info` per country |
| Output directory created if missing | `pipeline.save_results()` | `mkdir(parents=True)` |
| HDF5 keys `"coefficient"`, `"unit"` | verifiable with `pd.HDFStore` | — |
| Excel 50-column cap noted | `save_results()` → Notes sheet | — |

---

## Interpretation Notes

- **HUI and HUT** are positive (+1.0 sign) — they represent welfare gains per
  unit of income or public expenditure. Higher values in lower-income countries
  reflect greater marginal utility of additional income.

- **Wages** are positive (+1.0 sign) — they represent labour income values.
  Values differ substantially by country (AFG: ~228 USD/yr vs DEU: ~35,338 USD/yr
  for the medium quintile).

- **Health DALY** coefficients are **negative** (sign = −1.0) — they represent
  disease burden (damage). A coefficient of −625 USD/capita for AFG WASH water
  diarrheal reflects high DALY rates × 59,446 USD/DALY monetisation.

- **NatCap pollution** coefficients are **negative** (sign = −1.0) — they
  represent environmental damage costs. Values are globally uniform (EF 3.0 /
  ReCiPe 2016 H characterisation factors × CE Delft monetary values).

- **NatCap land** coefficients are **positive** (+1.0 sign) — they represent
  ecosystem service values per hectare. Values vary by country (LANCA v2.0).

- Coefficients for historical years (2014–2022) are **lower** than the 2023
  base values because the USD world inflation factor I[y] < 1.0 for those years.

- Coefficients for forecast years (2024–2100) are **equal** to 2023 values
  because the deflator is frozen at I = 1.0 (2023 price level). Unit strings
  for these years show `"2023USD/..."` to signal the frozen base.

---

## Known Limitations

| Limitation | Scope | Documented in |
|-----------|-------|---------------|
| Global fallback for countries not in source | All country-varying indicators | METHODOLOGY.md §7 |
| No forward inflation projection beyond 2023 | All indicators | ADR-004, METHODOLOGY.md §3 |
| DALY rates monetised at single global OECD benchmark | health_daly | ADR-005, METHODOLOGY.md §5 |
| NatCap pollution globally uniform (no country differentiation) | natcap_pollution | README.md, METHODOLOGY.md §6 |
| 50-column Excel preview may not show country-varying spread | All indicators | ADR-010 |

---

*Document Version 1.0 | Last Updated 2026-03-07 | Greenings | dimitrij.euler@greenings.org*
*Value factors: Valuing Impact (valuingimpact.org) | Scripts: Dr Dimitrij Euler with support of Claude Code (Anthropic)*

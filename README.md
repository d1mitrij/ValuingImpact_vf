# eQALY Value Factors

**eQALY Impact Valuation Method — Valuing Impact reference datasets
as transitionvaluation-compatible coefficient matrices**

**Value factors:** [Valuing Impact](https://www.valuingimpact.org) —
eQALY_Template_2025-02-14_EXPORT.xlsx / WIVF — WASH Impact Valuation Framework 2024

**Scripts:** Dr Dimitrij Euler, [Greenings](https://greenings.org) — dimitrij.euler@greenings.org,
with support of [Claude Code](https://claude.ai/claude-code) (Anthropic)

---

## Overview

This module extracts the six core reference datasets from the **eQALY Impact Valuation
Method** (Valuing Impact, 2025) and transfers them into the value-factor pipeline
architecture established by the
[transitionvaluation](https://github.com/Greenings/transitionvaluation) project.

The eQALY method provides a multi-capital framework for quantifying and monetising
social, human, and natural capital impacts — covering health (DALY), income (wages,
HUI), public finance (HUT), and environmental externalities (NatCap/LCA). This module
makes all six reference datasets available as structured coefficient matrices in the
same `(Year, Variable) × (GeoRegion, NACE)` format used by the EPS and UBA value
factor pipelines.

The extraction scripts and documentation were written by Dr Dimitrij Euler (Greenings)
with support of Claude Code (Anthropic). The underlying value factor data is the
intellectual property of Valuing Impact and their cited sources (IHME, ILO, World Bank,
CE Delft, LANCA, WRI, OECD — see METHODOLOGY.md for full attribution).

### Framework reference

| Field | Value |
|---|---|
| Method | eQALY — enhanced Quality-Adjusted Life Year valuation |
| Template | eQALY_Template_2025-02-14_EXPORT.xlsx |
| Framework | WIVF — WASH Impact Valuation Framework 2024 |
| Author of value factors | Valuing Impact (valuingimpact.org) |
| Price base | USD_2023 |
| Reference year | 2023 |
| DALY value | 59,446 USD/DALY (OECD GDP/capita 2023, current PPP) |

### Core formula

```
Footprint          = Output × Outcome_rate × Baseline × Drop-off × Attribution × Duration
Societal_valuation = Footprint × Valuation_factor
```

The six datasets extracted here provide the **Valuation_factor** layer for each capital
type in the eQALY model.

---

## Indicators

| ID | Key | Capital | Variables | Unit | Country-varying |
|----|-----|---------|-----------|------|-----------------|
| 01 | `hui` | Human Capital | 1 | USD/USD | Yes |
| 02 | `hut` | Social Capital | 1 | USD/USD | Yes |
| 03 | `wages` | Human Capital | 3 | USD/year | Yes |
| 04 | `health_daly` | Human Capital | 16 | USD/capita | Yes |
| 05 | `natcap_pollution` | Natural Capital | 16 | USD/impact-unit | No (global) |
| 06 | `natcap_land` | Natural Capital | 3 | USD/ha | Yes |
| **Total** | | | **40** | | |

### Key difference from EPS

EPS 2015 characterisation factors are globally uniform — the same coefficient applies
to every country. eQALY coefficients **vary by country** for five of six indicators
(HUI, HUT, wages, DALY rates, land values), reflecting real cross-country differences
in welfare, income, and ecosystem conditions. The `natcap_pollution` global factors
(EF 3.0 / ReCiPe) are an exception and are broadcast uniformly like EPS.

---

## Output format

Each indicator produces two files in `output/`:

| File | Contents |
|---|---|
| `NN_eqaly_{key}.h5` | Full coefficient matrix (HDF5, keys: `coefficient`, `unit`) |
| `NN_eqaly_{key}.xlsx` | Excel: `Coefficients` sheet (50 representative columns), `Units`, `Pathway data` |

### HDF5 structure (identical to WifOR/EPS convention)

```
key: "coefficient"
  DataFrame shape: (N_years × N_variables)  ×  (188 countries × 21 NACE sectors)
  Row MultiIndex:    ["Year", "Variable"]
  Column MultiIndex: ["GeoRegion", "NACE"]
  Values: float64  (year-specific USD value, USD world deflator adjusted)

key: "unit"
  DataFrame index:   Variable name strings
  DataFrame columns: year strings
  Values: strings like "2023USD/USD", "2014USD/year"
```

### Variable name convention

```
eQALY_{Capital}_{Item}, in {unit} (ValuingImpact2023)
```

Examples:
- `eQALY_HumanCapital_Income_HUI, in USD/USD (ValuingImpact2023)`
- `eQALY_HumanCapital_Wages_Medium, in USD/year (ValuingImpact2023)`
- `eQALY_HumanCapital_DALY_WASH_Water_Diarrheal, in USD/capita (ValuingImpact2023)`
- `eQALY_NaturalCapital_Pollution_GWP100, in USD/kg_CO2e (ValuingImpact2023)`
- `eQALY_NaturalCapital_Land_PastureMeadow, in USD/ha (ValuingImpact2023)`

### Sample values (2023 base year)

| Variable | FRA | DEU | AFG | Note |
|---|---|---|---|---|
| HUI (USD/USD) | 0.103 | 0.027 | 2.130 | Lower income → higher welfare gain per USD |
| HUT (USD/USD) | 2.763 | 2.151 | — | Social cost multiplier for public funds |
| Wages, medium (USD/yr) | 28,745 | 35,338 | 228 | ILO-based quintile model |
| DALY WASH_Water (USD/cap) | −2.30 | −2.30 | −625 | High burden in low-income countries |
| GWP100 (USD/kg CO₂-e) | −0.144 | −0.144 | −0.144 | Global uniform (EF 3.0) |
| Land, PastureMeadow (USD/ha) | — | — | 682 | LANCA v2.0, country-specific |

---

## Usage

### Run all indicators (parallel)

```bash
pip install pandas openpyxl tables numpy
python run_all_eqaly_factors.py --max-workers 4
```

### Run a single indicator

```bash
python indicators/01_prepare_hui_eqaly.py
python indicators/04_prepare_health_daly_eqaly.py
```

### Filter to specific indicators

```bash
python run_all_eqaly_factors.py --only hui hut wages
```

### List available indicators

```bash
python run_all_eqaly_factors.py --list
```

### Read outputs in Python

```python
import pandas as pd

# Load HUI coefficient matrix
coeff = pd.read_hdf("output/01_eqaly_hui.h5", key="coefficient")
units = pd.read_hdf("output/01_eqaly_hui.h5", key="unit")

# HUI for France in 2023
hui_fra_2023 = coeff.loc[
    ("2023", "eQALY_HumanCapital_Income_HUI, in USD/USD (ValuingImpact2023)"),
    ("FRA", "A")
]
print(f"FRA HUI 2023: {hui_fra_2023:.4f}")   # → 0.1030

# Load wages and compare countries
wages = pd.read_hdf("output/03_eqaly_wages.h5", key="coefficient")
var_med = "eQALY_HumanCapital_Wages_Medium, in USD/year (ValuingImpact2023)"
print(wages.loc[("2023", var_med), ("FRA", "A")])   # → 28,745
print(wages.loc[("2023", var_med), ("AFG", "A")])   # → 228
```

### Apply to a societal valuation calculation

```python
# Example: monetise employment impact for France
n_employees   = 100
wage_medium   = wages.loc[("2023", var_med), ("FRA", "A")]   # 28,745 USD/year
baseline      = 1.0
attribution   = 1.0
duration      = 1.0   # year

hui = coeff.loc[("2023", "eQALY_HumanCapital_Income_HUI, in USD/USD (ValuingImpact2023)"),
                ("FRA", "A")]   # 0.1030

footprint           = n_employees * wage_medium * baseline * attribution * duration
societal_valuation  = footprint * hui
print(f"Societal valuation: {societal_valuation:,.0f} USD")   # → 295,981 USD
```

---

## Dependencies

```bash
pip install pandas openpyxl tables numpy
```

---

## Source and attribution

### Value factor data

> Valuing Impact (2025). *eQALY Impact Valuation Method.*
> eQALY_Template_2025-02-14_EXPORT.xlsx. valuingimpact.org

> WIVF — WASH Impact Valuation Framework 2024. Valuing Impact.

The value factors embedded in the eQALY template draw on the following primary sources
(see METHODOLOGY.md for per-indicator attribution):

| Dataset | Source |
|---|---|
| HUI / HUT | Valuing Impact (2023) |
| Wages | ILO + World Bank quintile model, Valuing Impact (2023) |
| DALY rates | IHME Global Burden of Disease 2019 |
| DALY value | OECD GDP/capita 2023 (current prices, current PPP) |
| NatCap pollution | CE Delft Environmental Prices Handbook; WRI (water) |
| Land use | LANCA v2.0 characterisation factors |
| LCA factors | Ecoinvent 3.10; ReCiPe 2016 midpoint (H) |
| Inflation | IMF World Economic Outlook (world inflation rates) |

### Script authorship

The extraction scripts, pipeline architecture, and documentation were produced by:

**Dr Dimitrij Euler** — [Greenings](https://greenings.org) — dimitrij.euler@greenings.org
with support of [Claude Code](https://claude.ai/claude-code) (Anthropic)

---

## Relation to steen-vf1 / uba1 / transitionvaluation

| steen-vf1 (EPS) | uba1 (UBA) | eqaly_value_factors | Note |
|---|---|---|---|
| `config.py` → `INDICATORS` | `config.py` → `TABLE_GROUPS` | `config.py` → `INDICATORS` | Same pattern |
| `pipeline.run_indicator(key)` | `pipeline.run_table(key)` | `pipeline.run_indicator(key)` | Same signature |
| `indicators/NNN_*_eps.py` | `tables/NN_*.py` | `indicators/NN_*_eqaly.py` | Same thin-wrapper |
| `run_all_eps_factors.py` | `extract_uba_values.py` | `run_all_eqaly_factors.py` | Same orchestrator |
| HDF5 + Excel | CSV + Excel | HDF5 + Excel | eQALY uses full matrix like EPS |
| Global D[s] broadcast | Flat CSV | Country-varying D[s,c] | eQALY adds country dimension |
| EU HICP deflator | No deflation | IMF USD world deflator | Different currency/base |
| `execution_log_*.txt` | `execution_log_*.txt` | `execution_log_*.txt` | Same format |

---

**Value factors author:** Valuing Impact (valuingimpact.org)

**Scripts author:** Dr Dimitrij Euler, Greenings — dimitrij.euler@greenings.org
(with support of [Claude Code](https://claude.ai/claude-code), Anthropic)

# eQALY Value Factors — Methodology

**Organisation:** Greenings
**Value factors:** Valuing Impact (valuingimpact.org)
**eQALY method:** https://valuingimpact.com/all/the-eqaly-impact-valuation-method/
**Version:** 1.0
**Last Updated:** 2026-03-07
**Contact:** dimitrij.euler@greenings.org

---

## 1. Conceptual Foundation: Multi-Capital Impact Valuation

### 1.1 Theoretical Basis

The **eQALY** (enhanced Quality-Adjusted Life Year) method, developed by
**Valuing Impact**, quantifies the societal value created or destroyed by
activities across four capital types: Human, Social, Natural, and Business.
For full method documentation see:
https://valuingimpact.com/all/the-eqaly-impact-valuation-method/

Unlike single-metric damage-cost frameworks, eQALY integrates
both benefit and cost pathways within a unified welfare-economics model.

The core valuation formula (from the Model sheet of the eQALY template):

```
Footprint          = Output × Outcome_rate × Baseline × Drop-off × Attribution × Duration
Societal_valuation = Footprint × Valuation_factor
```

| Parameter | Description | Example |
|---|---|---|
| `Output` | Physical activity result | 100 employees/year |
| `Outcome_rate` | Impact rate per output unit | 0.0027 DALY/employee |
| `Baseline [%]` | Share of output where the outcome occurs | 1.0 |
| `Drop-off [%]` | Persistence of outcome over time | 1.0 |
| `Attribution [%]` | Fraction causally attributed to this activity | 1.0 |
| `Duration` | Period over which the outcome applies | 1 year |
| `Footprint` | Physical impact quantity | 0.27 DALY |
| `Valuation_factor` | Monetary value per footprint unit | 59,446 USD/DALY |
| `Societal_valuation` | Total societal value (USD) | 16,050 USD |

### 1.2 Capital Types

| Capital Type | Pathways | Sign | Valuation basis |
|---|---|---|---|
| **Human Capital** | Health (DALY), Income (wages), Education, Skills | + (benefit) or − (damage) | DALY value; wage × HUI |
| **Social Capital** | Taxes, Costs to society, Public revenue | + or − | Revenue × HUT |
| **Natural Capital** | Ecosystem services, LCA environmental externalities | + or − | USD/ha × HUT; LCA impact × NatCap VF |
| **Business value** | Staff retention, productivity, reputation | + | Direct USD (1:1 ratio) |

---

## 2. Global Reference Parameters

All six indicators share the following reference parameters (from the
`Parameters | VI` sheet of the eQALY template):

| Parameter | Value | Unit | Source |
|---|---|---|---|
| DALY value | 59,446 | USD/DALY | OECD GDP/capita 2023, current prices, current PPP |
| Reference year | 2023 | — | — |
| Average HUT | 0.7581 | USD/USD | Valuing Impact, average across countries |
| Average HUI | 0.7044 | USD/USD | Valuing Impact, average across countries |
| USD/EUR exchange rate | 1.0638 | USD/EUR | Internet average 2023 |

### USD World Deflator (IMF, base 2023 = 100.0)

Built from IMF world inflation rates embedded in the `Parameters | VI` sheet.
Applied to convert 2023 USD values to year-specific nominal values.
Years beyond 2023 are frozen at 100.0 (no projection of future inflation).

| Year | Deflator index (2023 = 100) | Inflation factor I[y] |
|------|------|------|
| 2014 | 68.23 | 0.6823 |
| 2015 | 70.08 | 0.7008 |
| 2016 | 71.97 | 0.7197 |
| 2017 | 74.35 | 0.7435 |
| 2018 | 77.02 | 0.7702 |
| 2019 | 79.72 | 0.7972 |
| 2020 | 82.27 | 0.8227 |
| 2021 | 86.14 | 0.8614 |
| 2022 | 93.63 | 0.9363 |
| 2023 | 100.0 | 1.0000 (base) |
| 2024+ | 100.0 | 1.0000 (frozen) |

Source: IMF World Economic Outlook inflation rates as tabulated in
`Parameters | VI` of the eQALY template.

---

## 3. Mathematical Framework

### 3.1 Coefficient matrix formula

For each indicator, the value factor coefficient is expressed as:

```
C[y, v, c, n]  =  Sign(v) × VF[v, c] × I[y]

where:
  y        =  year (2014–2030 annual + 2050, 2100)
  v        =  variable (valuation factor identifier)
  c        =  ISO3 country code (188 countries)
  n        =  NACE sector code (A21, 21 sectors; no sector differentiation)
  Sign(v)  =  +1.0 (benefit) or −1.0 (damage)
  VF[v, c] =  country-specific valuation factor (or globally uniform for natcap_pollution)
  I[y]     =  USD deflator[y] / USD deflator[2023]
```

This is the direct eQALY equivalent of the EPS formula
`C[y, s, c, n] = Sign(s) × EPS_index[s] × I[y]`, extended to include
country variation in `VF[v, c]`.

### 3.2 Country-varying vs. globally uniform

| Indicator | VF[v, c] |
|---|---|
| `hui` | HUI[country] — 203 country-specific values; 188 in scope |
| `hut` | HUT[country] — 148 country-specific values; remainder use global average |
| `wages` | Wage[country, skill] — 218 country-skill values in source |
| `health_daly` | DALY_rate[country, risk] × DALY_value — 200+ countries × 16 risk factors |
| `natcap_pollution` | Global uniform (EF 3.0) — same for all countries |
| `natcap_land` | Land_VF[country, land_type] — LANCA v2.0 country values |

Countries in the 188-country scope without data in the source sheet receive
the arithmetic mean of available values as a fallback.

---

## 4. Indicator-Specific Methodology

### 01 — Health Utility of Income (HUI)

**Source sheet:** `HUI 2023 | VI`
**Capital:** Human Capital
**Sign:** +1.0 (benefit — higher income improves welfare)

**Methodology:**
The HUI multiplier translates a monetary income impact into its equivalent welfare
value. It is derived from the relationship between income, disability-adjusted life
expectancy, and living-wage benchmarks for each country:

```
HUI[country]  =  DALY_per_work_year[country] / living_wage[country]
               expressed in USD/USD (welfare-adjusted value per USD of income)
```

Economically: HUI reflects that an additional USD of income yields greater welfare
gain in a low-income country (high disease burden, low wages) than in a high-income
country. The ratio ranges from ~0.03 (Australia) to ~2.1 (Afghanistan).

**Application in the eQALY model:**
```
Societal_value_income = Income_footprint_USD × HUI[country]
```

**Source:** Valuing Impact (2023), HUI 2023 | VI dataset.
Country income classification: World Bank Atlas method 2022–23.
Living wage benchmark: Global Living Wage 2023–24 dataset (Valuing Impact).

---

### 02 — Health Utility of Taxes (HUT)

**Source sheet:** `HUT 2023 | VI`
**Capital:** Social Capital
**Sign:** +1.0 (benefit — tax revenue funds public welfare)

**Methodology:**
The HUT multiplier is the Social Return on Investment (SROI) of public spending —
the welfare value generated per USD of tax revenue collected and redistributed
through public health, education, and social programmes:

```
HUT[country]  =  SROI_of_taxes[country]
               =  health_expenditure_DALY_saved × DALY_value / tax_revenue
               expressed in USD/USD
```

The HUT is used for two pathway types:
- Tax-funded public revenue impacts (e.g. additional tax collected by employing a
  formerly unemployed person)
- Societal cost of inaction (e.g. avoided unemployment benefit payments)

**Application:**
```
Societal_value_tax = Revenue_footprint_USD × HUT[country]
```

The global average HUT (0.7581) is used as the ecosystem services multiplier for
natural capital pathways where geographic specificity is not available.

**Source:** Valuing Impact (2023), HUT 2023 | VI dataset.

---

### 03 — Wages

**Source sheet:** `Wages | VI `
**Capital:** Human Capital
**Sign:** +1.0 (benefit — employment and training generate income)
**Variables:** Low-skill, Medium-skill, High-skill annual wages (USD/year)

**Methodology:**
A proprietary wage model developed by Valuing Impact uses ILO income-share data
and World Bank GDP statistics to estimate the annual income for three skill tiers
in each country. The model is based on quintile income shares:

```
Q1–Q5 income shares × GDP_per_capita × income_pct_GDP × labour_force_ratio
→ income per quintile decile [USD/year]

Low  = median of Q1–Q2   (low-skill proxy)
Med  = Q3 midpoint       (medium-skill proxy)
High = Q5 upper bound    (high-skill proxy)
```

**Application:**
```
Income_footprint_USD = n_employees × Wage[country, skill] × Baseline × Attribution × Duration
Societal_value       = Income_footprint_USD × HUI[country]
```

**Source:** Valuing Impact (2023), Wages | VI dataset.
ILO income-share quintile data; World Bank GDP 2022 (current USD).

---

### 04 — Health DALY Rates

**Source sheet:** `HEALTH | VI`
**Capital:** Human Capital
**Sign:** −1.0 (negative — health burden = societal damage)
**Variables:** 16 risk-factor categories (WASH, OHS, diet, smoking)
**Unit:** USD/capita (DALY rate monetised at 59,446 USD/DALY)

**Methodology:**
The DALY rate for each risk factor and country is monetised by multiplying by the
OECD GDP/capita benchmark value of a DALY:

```
Monetary_DALY[country, risk] = DALY_rate_per_capita[country, risk] × DALY_value
                              = DALY/capita × 59,446 USD/DALY
                              = USD/capita
```

The 16 risk factors covered, by category:

| Category | Risk factors |
|---|---|
| WASH | No handwashing facility (diarrheal); Unsafe sanitation (diarrheal); Unsafe water source (diarrheal); No handwashing (respiratory) |
| Occupational health | Second-hand smoke; Occupational PM/gases/fumes; Occupational injuries |
| Diet | Processed meat; Red meat; Sodium; Sugary beverages; Trans fats; Low vegetables; Low whole grains; Dietary risks (aggregate) |
| Lifestyle | Smoking |

**Application:**
```
Health_footprint_DALY = n_beneficiaries × DALY_rate[country, risk]
                       × Baseline × Drop-off × Attribution × Duration
Societal_damage_USD   = Health_footprint_DALY × 59,446
```

Equivalent: the coefficient C[y, "DALY_WASH_Water_Diarrheal", "AFG", "A"] = −625 USD/capita
means that in Afghanistan, the WASH water pathway causes 625 USD of societal health
damage per capita per year at 2023 price levels.

**Source:** IHME Global Burden of Disease 2019; per-capita rates from the
`HEALTH | VI` dataset (Valuing Impact). Country income classification and CHE per
capita: World Bank / WHO 2021–23.

---

### 05 — NatCap Pollution (Environmental Externalities)

**Source sheet:** `NatCap | VI`
**Capital:** Natural Capital
**Sign:** −1.0 (negative — environmental pollution = damage)
**Variables:** 16 LCA midpoint impact categories (EF 3.0 / global)
**Country-varying:** No — globally uniform (same as EPS broadcast behaviour)

**Methodology:**
These valuation factors convert LCA midpoint impact scores into monetary damage costs.
They are based on the Environmental Footprint (EF) 3.0 method combined with the
CE Delft Environmental Prices Handbook for European context, adjusted to 2023 USD:

```
Societal_damage_USD = LCA_impact[impact_category] × VF[impact_category]
```

| Impact category | Indicator | Valuation factor | Unit |
|---|---|---|---|
| Climate change | GWP100 | 0.144 | USD/kg CO₂-e |
| Acidification | Accumulated exceedance (AE) | 0.148 | USD/mol H⁺-Eq |
| Ecotoxicity, freshwater | CTUe | 0.00199 | USD/CTUe |
| Resource use, fossils | ADP fossil fuels | 0.00963 | USD/MJ |
| Eutrophication, freshwater | P fraction | 1.778 | USD/kg P-Eq |
| Eutrophication, marine | N fraction | 2.973 | USD/kg N-Eq |
| Eutrophication, terrestrial | AE | 0.297 | USD/mol N-Eq |
| Human toxicity, cancer | CTUh | 696,013 | USD/CTUh |
| Human toxicity, non-cancer | CTUh | 150,339 | USD/CTUh |
| Ionising radiation | U235-Eq | 0.000503 | USD/kBq U235-Eq |
| Land use | Soil quality index | 0.00153 | USD/dimensionless |
| Resource use, minerals/metals | ADP elements | 0.128 | USD/kg Sb-Eq |
| Ozone depletion | ODP | 29.57 | USD/kg CFC-11-Eq |
| Particulate matter | Disease incidence | 55,681 | USD/disease incidence |
| Photochemical ozone formation | NMVOC-Eq | 1.245 | USD/kg NMVOC-Eq |
| Water use | User deprivation potential | 0.000457 | USD/m³ |

These factors are applied in combination with the `LCA | DB` characterisation
factors (Ecoinvent 3.10, ReCiPe 2016 H) embedded in the eQALY template:

```
LCA_impact[activity, category] = Reference_amount × CF[activity, category]
Societal_damage_USD             = LCA_impact × VF[category]
```

**Source:** CE Delft Environmental Prices Handbook (European context);
WRI (water use, adjusted for inflation); Valuing Impact (2023 USD price level).

---

### 06 — NatCap Land Use

**Source sheet:** `NatCap | VI`
**Capital:** Natural Capital
**Sign:** +1.0 (benefit — nature conservation generates ecosystem services)
**Variables:** Pasture meadow, Permanent crops, Arable land (USD/ha)
**Country-varying:** Yes — LANCA v2.0 country-specific values

**Methodology:**
Land use valuation factors represent the ecosystem service value per hectare for
different land cover types, derived from the LANCA v2.0 characterisation method:

```
Ecosystem_service_value_USD = Area_ha × VF_land[country, land_type] × HUT_avg
```

Countries without LANCA data in the source sheet fall back to the global average
embedded in the eQALY template (GLO row values):

| Land type | Global average (USD/ha) |
|---|---|
| Pasture meadow | 791.74 |
| Permanent crops | 962.26 |
| Arable land | 962.26 |

**Source:** LANCA v2.0 land use characterisation factors (Bach et al.);
NatCap | VI dataset (Valuing Impact, 2023 USD price level).

---

## 5. Value Transfer Mechanism

The eQALY method applies a structured **welfare-adjusted value transfer** to derive
country-specific monetary impact values from global reference data. This is the
defining architectural feature that distinguishes eQALY from globally-uniform
LCIA methods (EPS, EF 3.0).

### 5.1 HUI — welfare transfer for income impacts

The Human Utility of Income (HUI) multiplier adjusts the monetary value of an income
impact based on the welfare conditions prevailing in the country:

```
Societal_value = Income_USD × HUI[country]

HUI[country] = DALY_per_work_year[country] / living_wage[country]
```

This means: an additional USD of income yields greater societal welfare in a country
with high disease burden and low wages (e.g., Afghanistan: HUI ≈ 2.1) than in a
wealthy country with low disease burden (e.g., Germany: HUI ≈ 0.027).

**Transfer direction:** Global reference income (USD) → country welfare value (USD/USD)
**Key external sources:** World Bank (living wage); IHME GBD 2019 (DALY rates)

### 5.2 HUT — welfare transfer for public revenue impacts

The Health Utility of Taxes (HUT) multiplier expresses the Social Return on Investment
of public spending — how much welfare value is generated per USD of tax revenue
collected and redistributed through public services:

```
Societal_value = Revenue_USD × HUT[country]

HUT[country] ≈ health_expenditure_DALY_saved × DALY_value / tax_revenue
```

**Transfer direction:** Global reference revenue (USD) → country welfare value (USD/USD)
**Used for:** Social capital pathways; natural capital ecosystem service scaling (global avg)
**Key external sources:** WHO Current Health Expenditure (2023); World Bank fiscal data

### 5.3 DALY value — temporal and geographic transfer

The DALY value (59,446 USD/DALY) is anchored to the **OECD GDP/capita 2023 in
current purchasing power parity**. This constitutes a temporal transfer:

```
DALY_value[y] = DALY_value_2023 × I[y]   (inflation-adjusted per year)
```

Geographic transfer from this global OECD average to country-specific conditions is
performed implicitly through the DALY rate data itself (country-specific incidence from
IHME GBD 2019) rather than through the DALY value parameter.

### 5.4 NatCap pollution — no country transfer

The 16 LCA midpoint valuation factors for natural capital pollution are derived from
CE Delft Environmental Prices Handbook and WRI water cost data. **No country-specific
transfer is applied** — these are broadcast globally (identical to EPS/EF 3.0 convention).

### 5.5 NatCap land — country transfer via LANCA v2.0

Land use ecosystem service values are country-specific using LANCA v2.0
characterisation factors (Bach et al. 2016):

```
Ecosystem_service_USD = Area_ha × LANCA_VF[country, land_type] × HUT_avg
```

Countries without LANCA entries fall back to the global average embedded in the
eQALY template (GLO row). The HUT_avg (0.7581) scales the physical ecosystem
service value to its societal welfare equivalent.

**Transfer direction:** Physical land area (ha) → societal welfare value (USD)
**Key external sources:** LANCA v2.0 (Bach et al. 2016, Fraunhofer IBP)

### 5.6 Summary: value transfer by indicator

| Indicator | Transfer type | Transfer factor | Source of VF |
|---|---|---|---|
| `hui` | Welfare (income → utility) | HUI[country] | Valuing Impact (2023) |
| `hut` | Welfare (revenue → utility) | HUT[country] | Valuing Impact (2023) |
| `wages` | Geographic (income level) | Wage[country, skill] | ILO + World Bank (via Valuing Impact) |
| `health_daly` | Geographic + temporal | DALY_rate[c,r] × DALY_value × I[y] | IHME GBD 2019; OECD 2023 |
| `natcap_pollution` | None (global uniform) | EF 3.0 / CE Delft | CE Delft (2023); WRI (2015) |
| `natcap_land` | Geographic | LANCA_VF[country] × HUT_avg | LANCA v2.0; Valuing Impact |

---

## 6. Data Processing Pipeline

The five-stage pipeline is implemented in `pipeline.py` and called from each indicator script.

```python
# Stage 1 — Configuration
cfg = config.get_indicator_config("health_daly")
years, sign, unit, sheet = cfg["years"], cfg["sign"], cfg["unit"], cfg["sheet"]

# Stage 2 — Data Loading
rows = load_sheet(cfg["source_xlsx"], sheet)

# Stage 3 — Factor Extraction (indicator-specific)
factor_map, variables, pathway_df = extract_health_daly(rows)
# factor_map: dict[iso3 → np.ndarray(N_var,)]

# Stage 4a — Coefficient Matrix (vectorised, country-varying)
coeff = create_coefficient_dataframe(years, variables, COUNTRIES, NACE_SECTORS)
global_fallback = np.mean(np.stack(list(factor_map.values())), axis=0)
coeff = populate_coefficients_by_country(
    coeff, factor_map, years, variables, sign, global_fallback
)

# Stage 4b — Inflation Adjustment
inflation_factors = calculate_inflation_factors(years)    # I[y] = deflator[y]/100
coeff_final = apply_deflation(coeff, inflation_factors, years, variables)
units = build_unit_frame(variables, years, unit)

# Stage 5 — Output Export
save_results(coeff_final, units, pathway_df,
             hdf5_path=cfg["hdf5_path"], excel_path=cfg["excel_path"])
```

**Output DataFrame dimensions (health_daly example):**

```
coeff_final:
  rows:    N_years × N_variables  =  19 × 16 = 304
  columns: N_countries × N_sectors = 188 × 21 = 3,948
  index:   MultiIndex ["Year", "Variable"]
  columns: MultiIndex ["GeoRegion", "NACE"]
  dtype:   float64, year-nominal USD
```

### Key difference from EPS: country-varying coefficient population

EPS broadcasts a single `D[s]` value across all countries:
```python
arr[row_start:row_end, :] = d_values[:, np.newaxis]   # EPS: same for all countries
```

eQALY builds a `(N_var, N_countries)` factor matrix and repeats across NACE sectors:
```python
F = np.array([sign * factor_map.get(c, fallback) for c in COUNTRIES]).T
F_broadcast = np.repeat(F, N_nace, axis=1)                       # (N_var, N_countries × N_nace)
arr[row_start:row_end, :] = F_broadcast                          # eQALY: country-specific
```

This approach is fully vectorised: the inner loop over years
(N_years = 19 iterations) sets one `(N_var × N_col)` array slice per iteration —
the same pattern as EPS, extended to the country dimension.

---

## 7. Quality Assurance

### 6.1 Validation checks performed

| Check | Implementation | Outcome |
|---|---|---|
| Country coverage | Count of ISO3 codes matched to 188-country scope | HUI: 203→188; HUT: 148; wages: 218→188 |
| Global fallback use | Log count of countries using fallback | Confirmed at runtime |
| Sign convention | Damage indicators (health_daly, natcap_pollution) | All coefficients ≤ 0 at base year |
| Benefit indicators | HUI, HUT, wages, natcap_land | All coefficients ≥ 0 at base year |
| Country variation | Compare FRA vs AFG vs DEU values | Confirmed to differ for indicators 01–04, 06 |
| Global uniformity | Compare FRA vs AFG for natcap_pollution | Confirmed identical (EF 3.0 global) |
| Inflation at base year | I[2023] | 1.0000 |
| Year coverage | Output index | 19 years: 2014–2030, 2050, 2100 ✓ |
| Matrix dimensions | Shape assertion | 188 × 21 = 3,948 columns ✓ |
| HDF5 keys | Read-back after write | "coefficient" and "unit" both present ✓ |

### 6.2 Known limitations

- **No sector variation.** The 21 NACE sectors receive identical coefficients
  for a given (year, variable, country). The sector dimension is maintained for
  multi-sector analysis frameworks that require this structure.

- **Forecast years frozen.** Years 2024–2100 use the 2023 USD deflator value (I[y]=1.0).
  Future inflation is not projected.

- **Countries without data.** The HUT dataset covers 148 countries. The remaining
  40 in the 188-country scope receive the arithmetic mean of available HUT values.
  Country-level accuracy for these jurisdictions is lower.

- **eQALY reference year 2023.** The DALY value (59,446 USD), wage model, HUI/HUT,
  and NatCap factors are all expressed at 2023 price levels. Users comparing with
  other value factor systems should apply appropriate exchange-rate and inflation
  adjustments at the point of integration.

- **LCA characterisation factors limited to two reference activities.** The `LCA | DB`
  sheet in the eQALY template contains only two Ecoinvent 3.10 activities (FR
  low-voltage electricity; GLO petrol passenger transport). Full LCA-based
  environmental monetisation for other activities requires the full Ecoinvent database
  and the NatCap pollution valuation factors from indicator 05.

---

## 8. References

### Primary value factor source

> Valuing Impact (2025). *eQALY Impact Valuation Method.*
> eQALY_Template_2025-02-14_EXPORT.xlsx. valuingimpact.org
> Full method documentation: https://valuingimpact.com/all/the-eqaly-impact-valuation-method/

> Valuing Impact (2024). *WIVF — WASH Impact Valuation Framework 2024.*
> WIVF_Wash-Impact-Valuation-Framework-2024d.pdf. valuingimpact.org

### Health and demographic data

> Institute for Health Metrics and Evaluation (2019). *Global Burden of Disease 2019.*
> Global Health Data Exchange (GHDx). healthdata.org

> World Health Organization (2023). *Current health expenditure (CHE) per capita.*
> Global Health Expenditure Database.

### Income and wage data

> World Bank (2023). *Gross national income per capita, Atlas method and PPP.*
> World Bank Open Data. data.worldbank.org

> International Labour Organization (2023). *ILOSTAT — income quintile share data.*
> ilostat.ilo.org

### Environmental valuation

> CE Delft (2023). *Environmental Prices Handbook.* CE Delft, Delft, Netherlands.

> Frischknecht, R. et al. (2016). *The ecoinvent database: overview and methodology.*
> ecoinvent 3.10. ecoinvent.org

> Huijbregts, M.A.J. et al. (2017). *ReCiPe 2016: A harmonized life cycle impact
> assessment method at midpoint and endpoint level.* International Journal of Life
> Cycle Assessment.

> World Resources Institute (2015). *Achieving Abundance — Water Scarcity.*
> WRI, Washington DC. (Water cost factors adjusted to 2023 USD.)

> Bach, V. et al. (2016). *LANCA v2.0 — land use characterisation factors.*
> Fraunhofer IBP, Stuttgart.

### Inflation data

> IMF (2024). *World Economic Outlook — world average inflation rates.*
> As tabulated in eQALY_Template Parameters | VI sheet.

> OECD (2023). *Nominal gross domestic product per capita, current prices, PPP.*
> OECD Data. (Source for DALY value 59,446 USD/DALY.)

### Related documentation

- See ARCHITECTURE_DECISIONS.md for pipeline design rationale
- See ALGORITHMS_VISUAL.md for pipeline flowcharts and data-flow diagrams
- See VALIDATION_REPORT.md for completed validation checklists
- See README.md for usage examples and output format reference

---

*Document Version 1.0 | Last Updated 2026-03-07 | Greenings | dimitrij.euler@greenings.org*
*Value factors: Valuing Impact (valuingimpact.org) | Scripts: Dr Dimitrij Euler with support of Claude Code (Anthropic)*

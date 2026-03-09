# Input Files Methodology — vf_valuingimpact (eQALY)

**eQALY Impact Valuation Method — Valuing Impact reference datasets
as structured coefficient matrices**

**Pipeline author:** Dr Dimitrij Euler (Greenings), with the support of Claude Code (Anthropic)

---

## 1. Primary Source File

### eQALY_Template_2025-02-14_EXPORT.xlsx

| Field | Value |
|---|---|
| File | `eQALY_Template_2025-02-14_EXPORT.xlsx` |
| Location | `../eqaly-impact-valuation-method/` (sibling directory) |
| Author / publisher | Valuing Impact (valuingimpact.org) |
| Version date | 2025-02-14 |
| Framework | WIVF — WASH Impact Valuation Framework 2024 |
| Price base | USD 2023 |
| Reference year | 2023 |
| DALY value embedded | 59,446 USD/DALY (OECD GDP/capita 2023, current PPP) |

This Excel workbook is the single runtime input to the pipeline. It contains
all reference datasets and configuration parameters needed to produce the
six indicator coefficient matrices.

---

## 2. XLSX Workbook Structure

The eQALY template contains the following sheets relevant to this pipeline:

### 2.1 Reference data sheets (direct pipeline inputs)

| Sheet name | Indicator | Content | Pipeline indicator |
|---|---|---|---|
| `HUI 2023 \| VI` | `hui` | Health Utility of Income per country (203 countries) | 01 |
| `HUT 2023 \| VI` | `hut` | Health Utility of Taxes per country (148 countries) | 02 |
| `Wages \| VI` | `wages` | Low / medium / high skill wages per country (218 countries) | 03 |
| `HEALTH \| VI` | `health_daly` | DALY rates per capita per risk factor per country (16 risk factors, 200+ countries) | 04 |
| `NatCap \| VI` | `natcap_pollution` | LCA midpoint valuation factors, EF 3.0 global (16 categories) | 05 |
| `NatCap \| VI` | `natcap_land` | LANCA v2.0 land use values per country, 3 land types | 06 |
| `Parameters \| VI` | all | Global reference parameters: DALY value, HUT avg, HUI avg, USD/EUR, world deflator | all |

### 2.2 Additional sheets (not directly parsed by this pipeline)

| Sheet | Content | Notes |
|---|---|---|
| `Model \| VI` | eQALY impact model template | User-facing calculation model; not a data source |
| `LCA \| DB` | Ecoinvent 3.10 characterisation factors for 2 reference activities | Used in eQALY model; not parsed here (NatCap VFs in NatCap sheet are sufficient) |
| `WIVF \| VI` | WASH Impact Valuation Framework pathway definitions | Framework reference, not a data table |

---

## 3. External Data Sources Embedded in the eQALY Template

The eQALY template embeds data from multiple external primary sources. These are
inputs to Valuing Impact, not direct inputs to this pipeline. Understanding their
provenance and licenses is important for downstream use compliance.

### 3.1 IHME Global Burden of Disease 2019

| Attribute | Detail |
|---|---|
| **Used for** | DALY rates per capita per risk factor per country (indicator 04 `health_daly`) |
| **Source** | Institute for Health Metrics and Evaluation (IHME), University of Washington |
| **Dataset** | Global Burden of Disease 2019 (GBD 2019) |
| **License** | **IHME Free-of-Charge Non-Commercial User Agreement** |
| **Commercial use** | ✗ Explicitly prohibited |
| **Attribution required** | Yes — specific citation format required |
| **Redistribution** | ✗ Cannot redistribute raw data to third parties |
| **License URL** | https://www.healthdata.org/data-tools-practices/data-practices/ihme-free-charge-non-commercial-user-agreement |

**Citation:**
> Institute for Health Metrics and Evaluation (IHME). Global Burden of Disease
> Study 2019 (GBD 2019) Data Resources. Seattle, United States of America: IHME, 2020.

**License implication:** The `health_daly` coefficient matrix embeds country-level
DALY rates derived from IHME GBD 2019. This imposes a **non-commercial restriction**
on the `health_daly` output files specifically. Commercial users must either obtain
separate IHME data access or use only the remaining five indicators.

### 3.2 ILO ILOSTAT — Income Quintile Share Data

| Attribute | Detail |
|---|---|
| **Used for** | Wages indicator (03): quintile income shares → low/medium/high wage model |
| **Source** | International Labour Organization (ILO), ILOSTAT database |
| **License** | **CC-BY 4.0** |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — "Source: ILOSTAT" |
| **Redistribution** | ✓ Allowed; derived datasets permitted |
| **License URL** | https://ilostat.ilo.org/resources/ilostat-terms-of-use/ |

**Citation:**
> International Labour Organization (ILO). ILOSTAT — income quintile share data.
> Geneva: ILO, 2023. https://ilostat.ilo.org

### 3.3 World Bank Open Data — GDP, GNI, Living Wage

| Attribute | Detail |
|---|---|
| **Used for** | HUI derivation (living wage benchmark, GNI per capita); wages model (GDP per capita); HUT (current health expenditure) |
| **Source** | World Bank Open Data — World Development Indicators |
| **License** | **CC-BY 4.0** |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — "Source: World Bank, [indicator name], [year]" |
| **Redistribution** | ✓ Allowed |
| **License URL** | https://data.worldbank.org/summary-terms-of-use |

**Citation:**
> World Bank (2023). World Development Indicators: GNI per capita, Atlas method;
> GDP per capita (current USD). Washington DC: World Bank. data.worldbank.org

### 3.4 OECD — GDP/Capita (DALY Value Basis)

| Attribute | Detail |
|---|---|
| **Used for** | DALY monetary value: 59,446 USD = OECD GDP/capita 2023, current prices, current PPP |
| **Source** | OECD National Accounts Statistics |
| **License** | **OECD Proprietary** (data values from OECD.Stat are more permissive than OECD publications) |
| **Commercial use** | Unclear — data values may be cited; charts/publications require permission |
| **Attribution required** | Yes — "Source: OECD" |
| **Redistribution** | Restricted for publications; data values generally citable |
| **License URL** | https://www.oecd.org/en/about/terms-conditions.html |

**Citation:**
> OECD (2023). Nominal gross domestic product per capita, current prices, current PPP
> (USD). OECD Data. https://data.oecd.org

### 3.5 LANCA v2.0 — Land Use Characterisation Factors

| Attribute | Detail |
|---|---|
| **Used for** | NatCap land (06): ecosystem service value per hectare per country, 3 land types |
| **Source** | Bach, V., Lehmann, A., Görmer, M., Finkbeiner, M. (2017). Fraunhofer IBP / TU Berlin |
| **License** | **CC-BY 4.0** (Int. J. Life Cycle Assess. open access + Zenodo dataset) |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — cite Bach et al. 2017 |
| **Redistribution** | ✓ Allowed; adapted datasets must attribute original |
| **License URL** | https://doi.org/10.1007/s11367-016-1228-3 |

**Citation:**
> Bach, V., Lehmann, A., Görmer, M., Finkbeiner, M. (2017). Product environmental
> footprint (PEF) pilot phase — comparability over flexibility? *International Journal
> of Life Cycle Assessment*, 22(7), 1059–1070.
> Also: Bach, V. et al. (2016). LANCA v2.0 Characterisation Factors for Land Use
> Impacts on Soil Quality. Fraunhofer IBP, Stuttgart.

### 3.6 IMF World Economic Outlook — World Inflation Rates

| Attribute | Detail |
|---|---|
| **Used for** | USD world deflator (all indicators): converts 2023 USD values to year-specific nominal values |
| **Source** | IMF World Economic Outlook database |
| **License** | **IMF Proprietary** with permissive terms for non-commercial citation |
| **Commercial use** | Unclear — non-commercial use explicitly free; commercial reproduction requires permission |
| **Attribution required** | Yes — "Source: IMF World Economic Outlook, [year]" |
| **Redistribution** | Non-commercial with attribution; database redistribution not permitted |
| **License URL** | https://www.imf.org/external/terms.htm |

**Citation:**
> IMF (2024). World Economic Outlook — world average inflation rates.
> Washington DC: International Monetary Fund.

### 3.7 CE Delft Environmental Prices Handbook — NatCap Pollution Values

| Attribute | Detail |
|---|---|
| **Used for** | NatCap pollution (05): 14 of 16 LCA midpoint valuation factors |
| **Source** | CE Delft Environmental Prices Handbook (European context, adjusted to 2023 USD) |
| **License** | **Proprietary — CE Delft, All Rights Reserved** |
| **Commercial use** | ✗ No without permission from CE Delft |
| **Attribution required** | Yes — cite CE Delft handbook |
| **Redistribution** | Restricted |
| **License URL** | https://ce.nl/en/publications/environmental-prices-handbook/ |

**Citation:**
> De Vries, J., De Bruyn, S. et al. (2025). *Environmental Prices Handbook 2024:
> EU27 version*. CE Delft, Delft.

### 3.8 WRI — Water Scarcity Cost Factors

| Attribute | Detail |
|---|---|
| **Used for** | NatCap pollution (05): water use valuation factor (indicator: user deprivation potential) |
| **Source** | World Resources Institute (WRI) Aqueduct / Water Scarcity research |
| **License** | **CC-BY 4.0** |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — "Source: WRI" |
| **Redistribution** | ✓ Allowed |
| **License URL** | https://www.wri.org/data/aqueduct-water-risk-atlas |

**Citation:**
> World Resources Institute (2015). Achieving Abundance: Understanding the Cost of a
> Sustainable Water Future. WRI, Washington DC.

### 3.9 ReCiPe 2016 / EF 3.0 — LCA Characterisation Factors

| Attribute | Detail |
|---|---|
| **Used for** | NatCap pollution (05): 16 EF 3.0 midpoint impact categories; `LCA \| DB` sheet in eQALY template |
| **Source** | Huijbregts, M.A.J. et al. (2017) ReCiPe 2016; EC JRC EF 3.0 |
| **License** | **CC-BY 4.0** (ReCiPe 2016 article and RIVM dataset) |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — cite Huijbregts et al. 2017 |
| **Redistribution** | ✓ Allowed |
| **License URL** | https://doi.org/10.1007/s11367-016-1246-z; https://www.rivm.nl/en/life-cycle-assessment-lca/recipe |

### 3.10 Valuing Impact — HUI, HUT, Wages Model

| Attribute | Detail |
|---|---|
| **Used for** | All six indicators — the HUI, HUT, and wages datasets are proprietary Valuing Impact products |
| **Source** | Valuing Impact (valuingimpact.org), HUI/HUT/Wages | VI datasets 2023 |
| **License** | **Proprietary — Valuing Impact, All Rights Reserved** |
| **Commercial use** | Unclear — check current terms at valuingimpact.org |
| **Attribution required** | Yes |
| **Redistribution** | Likely restricted — check terms |
| **License URL** | https://valuingimpact.org (see Terms of Use) |

**Citation:**
> Valuing Impact (2025). *eQALY Impact Valuation Method.*
> eQALY_Template_2025-02-14_EXPORT.xlsx. valuingimpact.org

---

## 4. Data Extraction Methodology

The pipeline reads each sheet of the eQALY template using `openpyxl` with
`read_only=True, data_only=True`:

```python
import openpyxl

wb = openpyxl.load_workbook(
    xlsx_path,
    read_only=True,    # memory-efficient streaming
    data_only=True,    # return cached cell values, not formula strings
)
ws = wb[sheet_name]
raw_rows = [tuple(cell.value for cell in row) for row in ws.iter_rows()]
wb.close()
```

**Important:** `data_only=True` requires that the XLSX was last saved with
Excel (or a compatible application that caches formula results). If opened
and re-saved from LibreOffice without updating, formula cells may return `None`.

Each indicator's extraction function (`extract_hui()`, `extract_hut()`, etc.)
processes the raw rows to build a `dict[iso3 → np.ndarray]` factor map,
which is then populated into the 188-country × 21-NACE coefficient matrix.

---

## 5. Country Coverage and Fallback Logic

| Indicator | Countries in source | In 188-country scope | Fallback used |
|---|---|---|---|
| `hui` | 203 | 188 | No (all 188 covered) |
| `hut` | 148 | 148 | Yes — 40 countries use global mean |
| `wages` | 218 | 188 | No (all 188 covered) |
| `health_daly` | 200+ | 188 | No (all 188 covered) |
| `natcap_pollution` | Global (uniform) | N/A | N/A — broadcast |
| `natcap_land` | ~100+ LANCA entries | Varies | Yes — GLO row values for missing countries |

Countries in the 188-country scope that are absent from the source sheet receive
the arithmetic mean of all available values as a fallback. The number of countries
using fallback is logged at runtime.

---

## 6. License Model — This Pipeline's Outputs

### 6.1 License by indicator

The most restrictive applicable license governs each output file:

| Indicator | Most restrictive source | Output license |
|---|---|---|
| `01_eqaly_hui.h5/.xlsx` | Valuing Impact (proprietary) | Proprietary — cite Valuing Impact |
| `02_eqaly_hut.h5/.xlsx` | Valuing Impact (proprietary) | Proprietary — cite Valuing Impact |
| `03_eqaly_wages.h5/.xlsx` | Valuing Impact (proprietary) | Proprietary — cite Valuing Impact |
| `04_eqaly_health_daly.h5/.xlsx` | **IHME GBD 2019 (non-commercial)** | **Non-commercial only** |
| `05_eqaly_natcap_pollution.h5/.xlsx` | CE Delft (proprietary) + WRI CC-BY 4.0 | Non-commercial; cite CE Delft |
| `06_eqaly_natcap_land.h5/.xlsx` | LANCA v2.0 (CC-BY 4.0) + Valuing Impact | Proprietary (Valuing Impact); CC-BY for LANCA component |

### 6.2 Overall licensing position

The eQALY coefficient matrices are **derived works** of proprietary Valuing Impact
data and (for indicator 04) IHME non-commercial data. They are not redistributable
as open data without the consent of Valuing Impact and, for indicator 04, IHME.

Users should:
1. Obtain or confirm access rights to the eQALY template from Valuing Impact.
2. Not redistribute indicator 04 outputs in commercial products.
3. Always provide the full attribution chain (see §7 below).

---

## 7. Required Citations for This Pipeline's Outputs

When using any output from this pipeline, cite:

**Primary value factor source:**
> Valuing Impact (2025). *eQALY Impact Valuation Method.*
> eQALY_Template_2025-02-14_EXPORT.xlsx. https://valuingimpact.org

**Pipeline:**
> Euler, D. (2026). *eQALY Value Factor Pipeline* (vf_valuingimpact).
> Greenings. https://github.com/Greenings/transitionvaluation

**By indicator — cite the underlying data source:**

| Indicator | Cite additionally |
|---|---|
| `health_daly` | IHME GBD 2019 (https://healthdata.org) |
| `wages` | ILO ILOSTAT (https://ilostat.ilo.org); World Bank WDI |
| `hui`, `hut` | World Bank WDI; WHO CHE database |
| `natcap_pollution` | CE Delft (De Vries et al. 2025); WRI (2015); ReCiPe 2016 (Huijbregts et al. 2017) |
| `natcap_land` | Bach et al. 2017 (LANCA v2.0); Fraunhofer IBP |

---

## 8. Source File Validation Checklist

Before a pipeline run, verify:

- [ ] `eQALY_Template_2025-02-14_EXPORT.xlsx` is present in `../eqaly-impact-valuation-method/`
- [ ] File opens without error in Excel or openpyxl (not corrupted or password-protected)
- [ ] Sheet `Parameters | VI` contains DALY value ≈ 59,446 USD
- [ ] Sheet `HUI 2023 | VI` contains at least 188 country rows
- [ ] Sheet `HEALTH | VI` contains 16 risk-factor columns
- [ ] Sheet `NatCap | VI` contains GWP100 factor ≈ 0.144 USD/kg CO₂-e
- [ ] Sheet `NatCap | VI` contains LANCA land rows (Pasture meadow, Permanent crops, Arable land)
- [ ] Pipeline output: HUI for AFG (Afghanistan) ≈ 2.1 USD/USD (high burden, low wage)
- [ ] Pipeline output: GWP100 factor is identical across all countries (uniform global)

---

*Document Version 1.0 | Last Updated 2026-03-09 | Maintained by Greenings | dimitrij.euler@greenings.org*
*Value factors: Valuing Impact (valuingimpact.org) | IHME GBD 2019 | ILO | World Bank | LANCA v2.0 | CE Delft | WRI*
*Scripts: Dr Dimitrij Euler with support of Claude Code (Anthropic)*

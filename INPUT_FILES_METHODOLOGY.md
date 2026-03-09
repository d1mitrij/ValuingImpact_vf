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
| License | **Proprietary — Valuing Impact, All Rights Reserved** |

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

## 3. External Data Sources

The eQALY template embeds data from ten external primary sources. These are
inputs to Valuing Impact, not direct inputs to this pipeline. Their licenses
govern the downstream use of the coefficient matrices this pipeline produces.

### 3.1 IHME — Global Burden of Disease 2019

| Attribute | Detail |
|---|---|
| **Used for** | DALY rates per capita per risk factor per country — indicator 04 `health_daly` |
| **Full citation** | Institute for Health Metrics and Evaluation (IHME). *Global Burden of Disease Study 2019 (GBD 2019) Data Resources*. Seattle: IHME, University of Washington, 2020. |
| **License** | **IHME Free-of-Charge Non-Commercial User Agreement** |
| **Commercial use** | ✗ Explicitly prohibited |
| **Attribution required** | Yes — specific IHME citation format required |
| **Redistribution** | ✗ Cannot redistribute raw data to third parties |
| **License URL** | https://www.healthdata.org/data-tools-practices/data-practices/ihme-free-charge-non-commercial-user-agreement |
| **Critical note** | This is the **most restrictive** upstream license in this pipeline. The `health_daly` coefficient matrix embeds country-level DALY rates from IHME GBD 2019. This imposes a **non-commercial restriction** on the `04_eqaly_health_daly` output files. Commercial users must either obtain a commercial IHME license or use only the remaining five indicators. |

---

### 3.2 ILO — ILOSTAT Income Quintile Share Data

| Attribute | Detail |
|---|---|
| **Used for** | Wages indicator (03): income quintile shares → low / medium / high skill wage model per country |
| **Full citation** | International Labour Organization (ILO). *ILOSTAT — income by quintile share data*. Geneva: ILO, 2023. https://ilostat.ilo.org |
| **License** | **CC BY 4.0** |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — "Source: ILOSTAT, International Labour Organization" |
| **Redistribution** | ✓ Allowed; derived datasets permitted |
| **License URL** | https://ilostat.ilo.org/resources/ilostat-terms-of-use/ |

---

### 3.3 World Bank — World Development Indicators

| Attribute | Detail |
|---|---|
| **Used for** | HUI derivation (GNI per capita, living wage benchmark); wages model (GDP per capita); HUT (current health expenditure as % of GDP) |
| **Full citation** | World Bank (2023). *World Development Indicators*. Washington DC: World Bank. https://data.worldbank.org |
| **License** | **CC BY 4.0** |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — "Source: World Bank, [indicator name], [year]" |
| **Redistribution** | ✓ Allowed |
| **License URL** | https://data.worldbank.org/summary-terms-of-use |

---

### 3.4 OECD — GDP per Capita (DALY Value Basis)

| Attribute | Detail |
|---|---|
| **Used for** | DALY monetary value: 59,446 USD = OECD average GDP per capita 2023, current prices, current PPP |
| **Full citation** | OECD (2023). Nominal gross domestic product per capita, current prices, current PPP (USD). *OECD Data*. Paris: OECD. https://data.oecd.org |
| **License** | **OECD Proprietary** — data values from OECD.Stat are more permissive than OECD full publications; single data values may be cited freely with attribution |
| **Commercial use** | Data values: permissive with attribution. Reproduction of charts / tables in publications: requires OECD permission. |
| **Attribution required** | Yes — "Source: OECD" |
| **Redistribution** | Single statistical values: generally citable. Database redistribution: restricted. |
| **License URL** | https://www.oecd.org/en/about/terms-conditions.html |

---

### 3.5 LANCA v2.0 — Land Use Characterisation Factors

| Attribute | Detail |
|---|---|
| **Used for** | NatCap land (06): ecosystem service value per hectare per country, 3 land types (Pasture meadow, Permanent crops, Arable land) |
| **Full citation** | Bos, U., Horn, R., Beck, T., Lindner, J.P., Fischer, M. (2016). *LANCA® Characterization Factors for Life Cycle Impact Assessment, Version 2.0*. Fraunhofer Institute for Building Physics IBP, Stuttgart. |
| **License** | **Fraunhofer IBP copyright — free for research use** (no formal open CC license; characterisation factors available as free download from Fraunhofer IBP) |
| **Commercial use** | Not explicitly restricted for research applications; contact Fraunhofer IBP for commercial product integration |
| **Attribution required** | Yes — cite Bos et al. 2016 and Fraunhofer IBP |
| **Redistribution** | Free download from Fraunhofer IBP; redistribution in derived products should acknowledge source |
| **Note** | LANCA® is a registered trademark of Fraunhofer IBP. Version 2.5 (updated 2018) is also available and supersedes v2.0 for some impact categories. |
| **License URL** | https://www.ibp.fraunhofer.de/en/expertise/life-cycle-engineering/applied-methods/lanca.html |

---

### 3.6 IMF — World Economic Outlook (World Inflation / Deflator)

| Attribute | Detail |
|---|---|
| **Used for** | USD world deflator for all indicators: converts 2023 USD base values to year-specific nominal values across the time series |
| **Full citation** | IMF (2024). *World Economic Outlook Database* — World average inflation (CPI-based). Washington DC: International Monetary Fund. https://www.imf.org/en/Publications/WEO |
| **License** | **IMF data: permissive with attribution** (per IMF copyright and terms). Users may download, extract, copy, create derivative works, publish, distribute and sell IMF data provided the IMF is clearly attributed as source. |
| **Commercial use** | ✓ Yes — IMF statistical data may be redistributed and sold commercially with attribution |
| **Attribution required** | Yes — "Source: International Monetary Fund, World Economic Outlook Database, [year]" |
| **Redistribution** | ✓ Allowed with attribution; if selling as standalone product, must note it is freely available from IMF |
| **Note** | IMF *publications* (narrative content) are more restricted — non-commercial quotation up to 1,000 words or one-quarter only. The data values (statistical series) have the permissive policy described above. |
| **License URL** | https://www.imf.org/en/about/copyright-and-terms |

---

### 3.7 CE Delft — Environmental Prices Handbook (NatCap Pollution Values)

| Attribute | Detail |
|---|---|
| **Used for** | NatCap pollution (05): 14 of 16 LCA midpoint valuation factors (all except water scarcity) |
| **Full citation** | De Vries, J., De Bruyn, S., Boerdijk, S., Juijn, D., Bijleveld, M., Van der Giesen, C., Korteland, M., Odenhoven, N., Van Santen, W., Pápai, S. (2025). *Environmental Prices Handbook 2024: EU27 version* (Version 1.1, Reference 230107). CE Delft, Delft. |
| **License** | **Proprietary — CE Delft, All Rights Reserved** |
| **Commercial use** | ✗ No — requires written permission from CE Delft |
| **Attribution required** | Yes — cite CE Delft handbook |
| **Redistribution** | ✗ Restricted |
| **License URL** | https://ce.nl/en/publications/environmental-prices-handbook/ |

---

### 3.8 WRI — Aqueduct Water Scarcity Cost Factors

| Attribute | Detail |
|---|---|
| **Used for** | NatCap pollution (05): water use valuation factor (user deprivation potential — scarcity-weighted water cost) |
| **Full citation** | Luo, T., Young, R., Reig, P. (2015). *Aqueduct Projected Water Stress Country Rankings*. Technical Note. Washington DC: World Resources Institute. |
| **License** | **CC BY 4.0** |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — "Source: WRI Aqueduct, accessed [date]" with link to aqueduct.wri.org |
| **Redistribution** | ✓ Allowed; registration with WRI preferred |
| **License URL** | https://www.wri.org/aqueduct; https://github.com/wri/Aqueduct40 (license: CC BY 4.0) |

---

### 3.9 ReCiPe 2016 / EF 3.0 — LCA Characterisation Factors

| Attribute | Detail |
|---|---|
| **Used for** | NatCap pollution (05): 16 EF 3.0 midpoint impact categories; `LCA \| DB` sheet in eQALY template |
| **Full citation** | Huijbregts, M.A.J. et al. (2017). ReCiPe2016: a harmonised life cycle impact assessment method at midpoint and endpoint level. *International Journal of Life Cycle Assessment*, 22(2), 138–147. — and — Saouter, E. et al. (2018). *Supporting information to the characterisation factors of EF Life Cycle Impact Assessment methods*. JRC Technical Report JRC114822. |
| **License** | **CC BY 4.0** (ReCiPe 2016 open-access article; EC JRC EF 3.0 under EC Decision 2011/833/EU) |
| **Commercial use** | ✓ Yes |
| **Attribution required** | Yes — cite Huijbregts et al. 2017 (ReCiPe) and Saouter et al. 2018 (EF 3.0) |
| **Redistribution** | ✓ Allowed |
| **License URL** | https://doi.org/10.1007/s11367-016-1246-y; https://publications.jrc.ec.europa.eu/repository/handle/JRC114822 |

---

### 3.10 Valuing Impact — HUI, HUT, and Wages Model

| Attribute | Detail |
|---|---|
| **Used for** | All six indicators — the HUI, HUT, and wages reference datasets are proprietary Valuing Impact products; HUI and HUT welfare multipliers underpin all valuation calculations |
| **Full citation** | Valuing Impact (2025). *eQALY Impact Valuation Method*. eQALY_Template_2025-02-14_EXPORT.xlsx. https://valuingimpact.org |
| **License** | **Proprietary — Valuing Impact, All Rights Reserved** |
| **Commercial use** | ✗ Check current terms at valuingimpact.org |
| **Attribution required** | Yes |
| **Redistribution** | ✗ Restricted — check current Valuing Impact terms |
| **License URL** | https://valuingimpact.org (see Terms of Use) |

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

### 6.1 License-by-indicator summary

The most restrictive applicable upstream source governs each output file:

| Output file | Most restrictive upstream source | License | Commercial use |
|---|---|---|---|
| `01_eqaly_hui.h5/.xlsx` | Valuing Impact (proprietary) | Proprietary | ✗ Check Valuing Impact terms |
| `02_eqaly_hut.h5/.xlsx` | Valuing Impact (proprietary) | Proprietary | ✗ Check Valuing Impact terms |
| `03_eqaly_wages.h5/.xlsx` | Valuing Impact (proprietary) | Proprietary | ✗ Check Valuing Impact terms |
| `04_eqaly_health_daly.h5/.xlsx` | **IHME GBD 2019 (non-commercial)** | **Non-commercial only** | ✗ Explicitly prohibited |
| `05_eqaly_natcap_pollution.h5/.xlsx` | CE Delft (proprietary) | Non-commercial; cite CE Delft | ✗ Requires CE Delft permission |
| `06_eqaly_natcap_land.h5/.xlsx` | Valuing Impact (proprietary) + LANCA | Proprietary (Valuing Impact) | ✗ Check Valuing Impact terms |

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

**By indicator — additionally cite the underlying data source:**

| Indicator | Cite additionally |
|---|---|
| `health_daly` (04) | IHME. *GBD 2019 Data Resources*. Seattle: IHME, 2020. https://healthdata.org |
| `wages` (03) | ILO ILOSTAT. Geneva: ILO. https://ilostat.ilo.org; World Bank WDI. https://data.worldbank.org |
| `hui`, `hut` (01, 02) | World Bank WDI. https://data.worldbank.org; WHO CHE database. https://apps.who.int/nha/database |
| `natcap_pollution` (05) | De Vries et al. (2025). CE Delft; WRI Aqueduct (2015); Huijbregts et al. (2017) ReCiPe2016. |
| `natcap_land` (06) | Bos et al. (2016). *LANCA v2.0*. Fraunhofer IBP Stuttgart. |

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

*Document Version 2.0 | Last Updated 2026-03-09 | Maintained by Greenings | dimitrij.euler@greenings.org*
*Value factors: Valuing Impact (valuingimpact.org) | IHME GBD 2019 | ILO ILOSTAT | World Bank WDI | LANCA v2.0 | CE Delft | WRI Aqueduct | IMF WEO*
*Scripts: Dr Dimitrij Euler with support of Claude Code (Anthropic)*

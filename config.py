"""
config.py — eQALY / Valuing Impact value factor configuration.

Source: eQALY_Template_2025-02-14_EXPORT.xlsx  (Valuing Impact)
Framework: WIVF — WASH Impact Valuation Framework 2024

Mirrors steen-vf1/eps_value_factors/config.py and uba1/config.py:
  INDICATORS dict          → one entry per extractable value factor dataset
  get_years()              → same 19-element year series as EPS/WifOR
  COUNTRIES, NACE_SECTORS  → same 188-country × 21-sector scope as EPS
  get_indicator_config()   → merged flat config dict for one indicator

eQALY Core formula (Model sheet):
  Footprint          = Output × Outcome_rate × Baseline × Drop-off × Attribution × Duration
  Societal_valuation = Footprint × Valuation_factor

Coefficient matrix produced for each indicator:
  Rows:    MultiIndex (Year, Variable)    — same as WifOR/EPS
  Columns: MultiIndex (GeoRegion, NACE)  — same as WifOR/EPS
  Values:  Valuation_factor[variable, country] × inflation_factor[year]

Key difference from EPS: eQALY coefficients vary by country (HUI, HUT, wages,
DALY rates, land use), while EPS is globally uniform.
"""

from __future__ import annotations

import numpy as np
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR   = Path(__file__).parent
SOURCE_XLS = ROOT_DIR / "source" / "eQALY_Template_2025-02-14_EXPORT.xlsx"
OUTPUT_DIR = ROOT_DIR / "output"

# ── Publication metadata ───────────────────────────────────────────────────────
PUBLICATION = {
    "title":      "eQALY Impact Valuation Method",
    "source":     "Valuing Impact (valuingimpact.org)",
    "template":   "eQALY_Template_2025-02-14_EXPORT.xlsx",
    "framework":  "WIVF — WASH Impact Valuation Framework 2024",
    "price_base": "USD_2023",
    "ref_year":   2023,
}

# ── Global reference parameters (from 'Parameters | VI') ──────────────────────
DALY_VALUE_USD    = 59_446.0       # USD/DALY  (OECD GDP/capita 2023)
GLOBAL_AVG_HUT    = 0.7580891973   # USD/USD   average HUT across countries
GLOBAL_AVG_HUI    = 0.7043806177   # USD/USD   average HUI across countries
USD_EUR           = 1.0638297872   # exchange rate 2023 average
REF_YEAR          = 2023

# ── USD world deflator (IMF world inflation, base = 2023 = 100.0) ─────────────
# Built from Parameters | VI inflation rates (rate for year Y = change from Y-1 to Y).
# Back-calculated from 2023=100 using: deflator[Y] = deflator[Y+1] / (1 + rate[Y+1]/100)
# Years 2024+ frozen at 100.0 (no forward projection in the source data).
USD_DEFLATOR_2023BASE: dict[str, float] = {
    "2014": 68.23,
    "2015": 70.08,
    "2016": 71.97,
    "2017": 74.35,
    "2018": 77.02,
    "2019": 79.72,
    "2020": 82.27,
    "2021": 86.14,
    "2022": 93.63,
    "2023": 100.0,
}
USD_DEFLATOR_BASE_YEAR    = "2023"
USD_DEFLATOR_LAST_KNOWN   = "2023"   # freeze forecast years at this value

# ── Countries — ISO 3166-1 alpha-3 (same 188-country scope as EPS/WifOR) ──────
COUNTRIES = [
    "AFG","AGO","ALB","ARE","ARG","ARM","ATG","AUS","AUT","AZE",
    "BDI","BEL","BEN","BFA","BGD","BGR","BHR","BHS","BIH","BLR",
    "BLZ","BOL","BRA","BRB","BRN","BTN","BWA","CAF","CAN","CHE",
    "CHL","CHN","CIV","CMR","COD","COG","COL","COM","CPV","CRI",
    "CUB","CYP","CZE","DEU","DJI","DNK","DOM","DZA","ECU","EGY",
    "ERI","ESP","EST","ETH","FIN","FJI","FRA","FSM","GAB","GBR",
    "GEO","GHA","GIN","GMB","GNB","GNQ","GRC","GRD","GTM","GUY",
    "HND","HRV","HTI","HUN","IDN","IND","IRL","IRN","IRQ","ISL",
    "ISR","ITA","JAM","JOR","JPN","KAZ","KEN","KGZ","KHM","KIR",
    "KNA","KOR","KWT","LAO","LBN","LBR","LBY","LCA","LKA","LSO",
    "LTU","LUX","LVA","MAR","MDA","MDG","MDV","MEX","MHL","MKD",
    "MLI","MLT","MMR","MNE","MNG","MOZ","MRT","MUS","MWI","MYS",
    "NAM","NER","NGA","NIC","NLD","NOR","NPL","NRU","NZL","OMN",
    "PAK","PAN","PER","PHL","PLW","PNG","POL","PRT","PRY","PSE",
    "QAT","ROU","RUS","RWA","SAU","SDN","SEN","SGP","SLB","SLE",
    "SLV","SMR","SOM","SRB","SSD","STP","SUR","SVK","SVN","SWE",
    "SWZ","SYC","SYR","TCD","TGO","THA","TJK","TKM","TLS","TON",
    "TTO","TUN","TUR","TUV","TZA","UGA","UKR","URY","USA","UZB",
    "VCT","VEN","VNM","VUT","WSM","YEM","ZAF","ZMB","ZWE",
]

# ── NACE sectors A21 macro-classification (same as EPS/WifOR) ─────────────────
NACE_SECTORS = [
    "A", "B", "C10-C12", "C13-C15", "C16-C18", "C19", "C20-C21",
    "C22-C23", "C24-C25", "C26-C28", "C29-C30", "C31-C33",
    "D", "E", "F", "G-I", "J", "K", "L", "M-N", "O-U",
]

# ── Year series (same 19-element series as EPS/WifOR) ─────────────────────────
def get_years() -> list[str]:
    """Annual 2014–2030 + 2050 + 2100 (19 years). Matches EPS/WifOR convention."""
    annual = list(np.arange(2014, 2031, dtype=int).astype(str))
    return annual + ["2050", "2100"]


# ── Indicators (one per extractable eQALY value factor dataset) ───────────────
#
# Parallel to steen-vf1/config.INDICATORS and uba1/config.TABLE_GROUPS.
#
#   id              → zero-padded ID for filename ordering
#   sheet           → Excel source sheet name
#   capital         → eQALY capital type (Human / Social / Natural)
#   variable_prefix → prefix for WifOR-style variable names
#   unit            → valuation factor unit
#   country_varying → True = coefficients differ per country; False = globally uniform
#   sign            → +1.0 (benefit) or -1.0 (damage / cost)
#   description     → full description
INDICATORS: dict[str, dict] = {
    "hui": {
        "id":               "01",
        "sheet":            "HUI 2023 | VI",
        "capital":          "HumanCapital",
        "variable_prefix":  "eQALY_HumanCapital_Income",
        "unit":             "USD/USD",
        "country_varying":  True,
        "sign":             1.0,
        "description":      "Health Utility of Income (HUI) — welfare multiplier for income impacts. "
                            "Societal_value = Income_USD × HUI.  Source: Valuing Impact 2023.",
    },
    "hut": {
        "id":               "02",
        "sheet":            "HUT 2023 | VI",
        "capital":          "SocialCapital",
        "variable_prefix":  "eQALY_SocialCapital_Taxes",
        "unit":             "USD/USD",
        "country_varying":  True,
        "sign":             1.0,
        "description":      "Health Utility of Taxes (HUT) — welfare multiplier for public expenditure. "
                            "Societal_value = Tax_revenue_USD × HUT.  Source: Valuing Impact 2023.",
    },
    "wages": {
        "id":               "03",
        "sheet":            "Wages | VI ",
        "capital":          "HumanCapital",
        "variable_prefix":  "eQALY_HumanCapital_Wages",
        "unit":             "USD/year",
        "country_varying":  True,
        "sign":             1.0,
        "description":      "Annual wages by skill level (low / medium / high). "
                            "Used for employment, training and income impact valuation. "
                            "Source: ILO + World Bank quintile model, Valuing Impact 2023.",
    },
    "health_daly": {
        "id":               "04",
        "sheet":            "HEALTH | VI",
        "capital":          "HumanCapital",
        "variable_prefix":  "eQALY_HumanCapital_DALY",
        "unit":             "USD/capita",
        "country_varying":  True,
        "sign":             -1.0,
        "description":      "Monetised DALY impact per capita by risk factor "
                            "(= DALY_rate × 59,446 USD/DALY). Negative = damage avoided. "
                            "Source: IHME GBD 2019, Valuing Impact 2023.",
    },
    "natcap_pollution": {
        "id":               "05",
        "sheet":            "NatCap | VI",
        "capital":          "NaturalCapital",
        "variable_prefix":  "eQALY_NaturalCapital_Pollution",
        "unit":             "USD/impact-unit",
        "country_varying":  False,
        "sign":             -1.0,
        "description":      "Environmental pollution valuation factors (EF 3.0, global). "
                            "Applied to LCA midpoint impacts to compute external costs. "
                            "Source: CE Delft Environmental Prices Handbook, WRI, Valuing Impact 2023.",
    },
    "natcap_land": {
        "id":               "06",
        "sheet":            "NatCap | VI",
        "capital":          "NaturalCapital",
        "variable_prefix":  "eQALY_NaturalCapital_Land",
        "unit":             "USD/ha",
        "country_varying":  True,
        "sign":             1.0,
        "description":      "Land-use ecosystem service values by country and land type "
                            "(LANCA v2.0). Applied as: Societal_value = Area_ha × VF × HUT_avg. "
                            "Source: LANCA v2.0, Valuing Impact 2023.",
    },
}

# ── Common parameters (parallel to EPS/WifOR COMMON_PARAMS) ───────────────────
COMMON_PARAMS = {
    "row_index_names":           ["Year", "Variable"],
    "col_index_names":           ["GeoRegion", "NACE"],
    "variable_template":         "eQALY_{capital}_{item}, in {unit} (ValuingImpact2023)",
    "hdf5_coeff_key":            "coefficient",
    "hdf5_unit_key":             "unit",
    "excel_sheet_coefficients":  "Coefficients",
    "excel_sheet_units":         "Units",
    "excel_sheet_pathway":       "Pathway data",
    "excel_freeze_coefficients": (1, 2),
    "excel_freeze_units":        (1, 1),
    "inflation_reference":       "USD_world_IMF",
    "source_reference":          "Valuing Impact eQALY 2023 / WIVF 2024",
    "daly_value_usd":            DALY_VALUE_USD,
    "global_avg_hut":            GLOBAL_AVG_HUT,
    "global_avg_hui":            GLOBAL_AVG_HUI,
}


# ── Public helpers ─────────────────────────────────────────────────────────────

def get_indicator_config(key: str) -> dict:
    """
    Return merged flat config dict for one indicator.

    Mirrors steen-vf1/config.get_indicator_config() and uba1/config.get_table_config().
    """
    if key not in INDICATORS:
        raise KeyError(f"Unknown indicator '{key}'. Valid keys: {list(INDICATORS)}")

    years   = get_years()
    out_dir = OUTPUT_DIR
    ind     = INDICATORS[key]
    num_id  = ind["id"]

    return {
        **ind,
        **COMMON_PARAMS,
        "years":       years,
        "countries":   COUNTRIES,
        "nace":        NACE_SECTORS,
        "source_xlsx": SOURCE_XLS,
        "hdf5_path":   str(out_dir / f"{num_id}_eqaly_{key}.h5"),
        "excel_path":  str(out_dir / f"{num_id}_eqaly_{key}.xlsx"),
        "publication": PUBLICATION,
    }


def list_indicators() -> list[tuple[str, str, str]]:
    """Return (key, id, description) tuples for all indicators."""
    return [(k, v["id"], v["description"]) for k, v in INDICATORS.items()]

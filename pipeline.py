"""
pipeline.py — eQALY / Valuing Impact value factor computation pipeline.

Five-stage pipeline (mirrors steen-vf1/eps_value_factors/pipeline.py):

  Stage 1  Configuration      config.get_indicator_config()
  Stage 2  Data Loading       load_sheet() → raw rows from Excel
  Stage 3  Factor Extraction  extract_*() → factor map per country (or global)
  Stage 4  Coefficient Matrix create_coefficient_dataframe()
                              populate_coefficients_by_country() | populate_coefficients_global()
                              calculate_inflation_factors() + apply_deflation()
  Stage 5  Output Export      save_results() → HDF5 + Excel

Coefficient matrix format (identical to WifOR/EPS convention):
  Rows:    MultiIndex (Year, Variable)   — Year = str, Variable = "eQALY_..."
  Columns: MultiIndex (GeoRegion, NACE)  — GeoRegion = ISO 3-letter, NACE = A21
  Values:  Valuation_factor[country] × inflation_factor[year]

Key difference from EPS:
  EPS coefficients are globally uniform → same D[substance] for every country.
  eQALY coefficients are country-varying for HUI, HUT, wages, DALY rates, land.
  For countries with no data the global average / fallback is used.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import openpyxl
import pandas as pd

from config import (
    COUNTRIES, NACE_SECTORS,
    USD_DEFLATOR_2023BASE, USD_DEFLATOR_BASE_YEAR, USD_DEFLATOR_LAST_KNOWN,
    DALY_VALUE_USD, GLOBAL_AVG_HUI, GLOBAL_AVG_HUT,
)

logger = logging.getLogger(__name__)

_EXCEL_MAX_COLS = 50   # compact view in Excel (same as EPS)


# ═══════════════════════════════════════════════════════════════════════════════
# Stage 2 — Data Loading
# ═══════════════════════════════════════════════════════════════════════════════

def load_sheet(xlsx_path: Path | str, sheet_name: str) -> list[tuple]:
    """Read one worksheet and return all rows as a list of value tuples."""
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        wb.close()
        raise ValueError(f"Sheet '{sheet_name}' not found in {Path(xlsx_path).name}")
    ws = wb[sheet_name]
    rows = [tuple(cell.value for cell in row) for row in ws.iter_rows()]
    wb.close()
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# Stage 3 — Factor Extraction
# Returns: (factor_map, pathway_df)
#   factor_map  →  dict[country_code, np.ndarray shape (N_var,)]  (country-varying)
#              OR  np.ndarray shape (N_var,)                        (global uniform)
#   pathway_df  →  full source data for the "Pathway data" Excel sheet
# ═══════════════════════════════════════════════════════════════════════════════

def _slugify(text: str) -> str:
    """Convert a label to a safe slug for variable names."""
    text = re.sub(r"[^A-Za-z0-9 _]", "", str(text))
    return re.sub(r"\s+", "_", text.strip())


def _make_variable_name(capital: str, item: str, unit: str) -> str:
    """Build WifOR-style variable name. Mirrors EPS _make_variable_name()."""
    return f"eQALY_{capital}_{_slugify(item)}, in {unit} (ValuingImpact2023)"


# ── HUI (Human Capital — Income welfare multiplier) ───────────────────────────

def extract_hui(rows: list[tuple]) -> tuple[dict, list[str], pd.DataFrame]:
    """
    Extract Health Utility of Income (HUI) by country.

    Returns:
      factor_map  — dict[iso3: str → array([hui_usd_usd])]
      variables   — ["eQALY_HumanCapital_Income_HUI, in USD/USD (ValuingImpact2023)"]
      pathway_df  — full HUI table for Excel pathway sheet
    """
    variables = [_make_variable_name("HumanCapital", "Income_HUI", "USD/USD")]
    records, pathway_records = [], []

    for row in rows[1:]:
        if not any(v is not None for v in row):
            continue
        if len(row) < 8:
            continue
        name, code, region, income, _, _, _, hui_usd = row[:8]
        if not (isinstance(code, str) and len(code) == 3):
            continue
        if not isinstance(hui_usd, (int, float)):
            continue
        records.append((code, float(hui_usd)))
        pathway_records.append({
            "country": name, "country_code": code,
            "region_wb": region, "income_level": income,
            "hui_usd_per_usd": float(hui_usd),
            "unit": "USD/USD", "source": "HUI 2023 | VI — Valuing Impact",
        })

    factor_map = {code: np.array([val]) for code, val in records}
    pathway_df = pd.DataFrame(pathway_records)
    logger.info("  HUI: %d countries", len(factor_map))
    return factor_map, variables, pathway_df


# ── HUT (Social Capital — Tax welfare multiplier) ─────────────────────────────

def extract_hut(rows: list[tuple]) -> tuple[dict, list[str], pd.DataFrame]:
    """
    Extract Health Utility of Taxes (HUT) by country.
    Skips continent/region aggregate rows (keeps only 'Country' type).
    """
    variables = [_make_variable_name("SocialCapital", "Taxes_HUT", "USD/USD")]
    records, pathway_records = [], []

    for row in rows[1:]:
        if not any(v is not None for v in row):
            continue
        if len(row) < 7:
            continue
        name, code, region_type, region_wb, income, _, hut_usd = row[:7]
        if region_type != "Country":
            continue
        if not (isinstance(code, str) and len(code) == 3):
            continue
        if not isinstance(hut_usd, (int, float)):
            continue
        records.append((code, float(hut_usd)))
        pathway_records.append({
            "country": name, "country_code": code,
            "region_wb": region_wb, "income_level": income,
            "hut_usd_per_usd": float(hut_usd),
            "unit": "USD/USD", "source": "HUT 2023 | VI — Valuing Impact",
        })

    factor_map = {code: np.array([val]) for code, val in records}
    pathway_df = pd.DataFrame(pathway_records)
    logger.info("  HUT: %d countries", len(factor_map))
    return factor_map, variables, pathway_df


# ── Wages (Human Capital — skill-level wages) ─────────────────────────────────

def extract_wages(rows: list[tuple]) -> tuple[dict, list[str], pd.DataFrame]:
    """
    Extract wages by country and skill level (low / medium / high).
    Variables ordered: Low, Medium, High.
    """
    skill_labels = [
        ("Low",    "Wages_Low"),
        ("Medium", "Wages_Medium"),
        ("High",   "Wages_High"),
    ]
    variables = [_make_variable_name("HumanCapital", label, "USD/year") for _, label in skill_labels]
    records, pathway_records = [], []

    for row in rows[1:]:
        if not any(v is not None for v in row):
            continue
        if len(row) < 23:
            continue
        country, code, region, income_group = row[0], row[1], row[2], row[3]
        if not (isinstance(code, str) and len(code) == 3):
            continue
        wages = [row[20], row[21], row[22]]
        if not all(isinstance(w, (int, float)) for w in wages):
            continue
        records.append((code, np.array([float(w) for w in wages])))
        for (skill_name, _), wage in zip(skill_labels, wages):
            pathway_records.append({
                "country": country, "country_code": code,
                "region": region, "income_group": income_group,
                "skill_level": skill_name, "wage_usd_year": float(wage),
                "unit": "USD/year", "source": "Wages | VI — Valuing Impact (ILO + World Bank)",
            })

    factor_map = dict(records)
    pathway_df = pd.DataFrame(pathway_records)
    logger.info("  Wages: %d countries", len(factor_map))
    return factor_map, variables, pathway_df


# ── Health DALY (Human Capital — monetised health impact per capita) ───────────

_HEALTH_RISK_FACTORS = [
    (5,  "WASH_Handwashing_Diarrheal"),
    (6,  "WASH_Sanitation_Diarrheal"),
    (7,  "WASH_Water_Diarrheal"),
    (8,  "WASH_Handwashing_Respiratory"),
    (9,  "OHS_Secondhand_Smoke"),
    (10, "OHS_Occupational_PM"),
    (11, "OHS_Occupational_Injuries"),
    (13, "Diet_Processed_Meat"),
    (14, "Diet_Red_Meat"),
    (15, "Diet_Sodium"),
    (16, "Diet_Sugary_Beverages"),
    (17, "Diet_Trans_Fats"),
    (18, "Diet_Low_Vegetables"),
    (19, "Diet_Low_Whole_Grains"),
    (20, "Diet_Risks_Total"),
    (21, "Smoking"),
]


def extract_health_daly(rows: list[tuple]) -> tuple[dict, list[str], pd.DataFrame]:
    """
    Extract monetised DALY impact per capita by risk factor and country.

    Value = DALY_rate [DALY/capita] × DALY_value [59,446 USD/DALY]
    Unit: USD/capita  (negative sign applied in pipeline → damage = cost)
    """
    variables = [
        _make_variable_name("HumanCapital", f"DALY_{label}", "USD/capita")
        for _, label in _HEALTH_RISK_FACTORS
    ]
    N_var = len(variables)
    records, pathway_records = [], []

    for row in rows[1:]:
        if not any(v is not None for v in row):
            continue
        country, code, region, income = row[0], row[1], row[2], row[3]
        if not isinstance(code, str) or len(code) < 2:
            continue
        vals = []
        for col_idx, _ in _HEALTH_RISK_FACTORS:
            v = row[col_idx] if col_idx < len(row) else None
            vals.append(float(v) if isinstance(v, (int, float)) else 0.0)
        # Monetise: DALY_rate × DALY_value
        monetary = np.array(vals) * DALY_VALUE_USD
        records.append((code, monetary))
        for (col_idx, label), daly_rate, mon_val in zip(_HEALTH_RISK_FACTORS, vals, monetary):
            pathway_records.append({
                "country": country, "country_code": code,
                "region": region, "income_group": income,
                "risk_factor": label,
                "daly_rate_per_capita": daly_rate,
                "daly_value_usd": DALY_VALUE_USD,
                "monetary_usd_per_capita": mon_val,
                "unit": "USD/capita",
                "source": "HEALTH | VI — IHME GBD 2019, Valuing Impact",
            })

    factor_map = dict(records)
    pathway_df = pd.DataFrame(pathway_records)
    logger.info("  Health DALY: %d countries × %d risk factors", len(factor_map), N_var)
    return factor_map, variables, pathway_df


# ── NatCap Pollution (Natural Capital — global EF 3.0 valuation factors) ──────

_NATCAP_POLLUTION_CATEGORIES = [
    ("Climate change",                     "GWP100",              "USD/kg_CO2e"),
    ("Acidification",                      "Acidification_AE",    "USD/mol_Hplus_Eq"),
    ("Ecotoxicity, freshwater",            "Ecotox_Freshwater",   "USD/CTUe"),
    ("Resource use, fossils",              "ResourceUse_Fossils", "USD/MJ"),
    ("Eutrophication, freshwater",         "Eutro_Freshwater",    "USD/kg_P_Eq"),
    ("Eutrophication, marine",             "Eutro_Marine",        "USD/kg_N_Eq"),
    ("Eutrophication, terrestrial",        "Eutro_Terrestrial",   "USD/mol_N_Eq"),
    ("Human toxicity, cancer",             "HumanTox_Cancer",     "USD/CTUh"),
    ("Human toxicity, non-cancer",         "HumanTox_NonCancer",  "USD/CTUh"),
    ("Ionising radiation, human health",   "IonisingRadiation",   "USD/kBq_U235_Eq"),
    ("Land use",                           "LandUse_SQI",         "USD/dimensionless"),
    ("Resource use, minerals and metals",  "ResourceUse_Minerals","USD/kg_Sb_Eq"),
    ("Ozone depletion",                    "OzoneDepletion",      "USD/kg_CFC11_Eq"),
    ("Particulate matter",                 "ParticulateMatter",   "USD/disease_incidence"),
    ("Photochemical ozone formation, human health", "HOFP",       "USD/kg_NMVOC_Eq"),
    ("Water use",                          "WaterUse",            "USD/m3"),
]


def extract_natcap_pollution(rows: list[tuple]) -> tuple[np.ndarray, list[str], pd.DataFrame]:
    """
    Extract global EF 3.0 pollution valuation factors (globally uniform, GLO rows).

    Returns a 1-D np.ndarray of shape (N_var,) instead of a country dict,
    since these factors are globally uniform — same as EPS behaviour.
    """
    # Index GLO rows by impact category name
    glo_map: dict[str, float] = {}
    pathway_records = []

    for row in rows[1:]:
        if not any(v is not None for v in row):
            continue
        if len(row) < 11:
            continue
        country, code, _region, _income, method, year, category, ind_type, indicator, vf, vf_unit = row[:11]
        if code != "GLO":
            continue
        if not isinstance(vf, (int, float)):
            continue
        cat_clean = str(category).strip()
        if cat_clean not in glo_map:
            glo_map[cat_clean] = float(vf)
            pathway_records.append({
                "country_code": "GLO", "method": method, "year": year,
                "impact_category": category, "indicator_type": ind_type,
                "indicator_name": indicator,
                "valuation_factor_usd": float(vf), "unit": vf_unit,
                "source": "NatCap | VI — CE Delft, WRI, Valuing Impact 2023",
            })

    variables = [
        _make_variable_name("NaturalCapital", f"Pollution_{slug}", unit)
        for _, slug, unit in _NATCAP_POLLUTION_CATEGORIES
    ]
    global_values = np.array([
        glo_map.get(cat, 0.0) for cat, _, _ in _NATCAP_POLLUTION_CATEGORIES
    ])

    pathway_df = pd.DataFrame(pathway_records)
    logger.info("  NatCap pollution: %d global factors extracted", int((global_values != 0).sum()))
    return global_values, variables, pathway_df


# ── NatCap Land (Natural Capital — ecosystem service value per ha) ─────────────

_LAND_TYPES = [
    ("Pasture meadow",   "PastureMeadow"),
    ("Permanent crops",  "PermanentCrops"),
    ("Arable land",      "ArableLand"),
]

# GLO average land values (from NatCap | VI GLO rows)
_GLO_LAND_FALLBACKS = {
    "Pasture meadow":  791.74,
    "Permanent crops": 962.26,
    "Arable land":     962.26,
}


def extract_natcap_land(rows: list[tuple]) -> tuple[dict, list[str], pd.DataFrame]:
    """
    Extract country-level land use ecosystem service values (LANCA v2.0).
    Falls back to global average for countries not in the dataset.
    """
    variables = [
        _make_variable_name("NaturalCapital", f"Land_{slug}", "USD/ha")
        for _, slug in _LAND_TYPES
    ]
    N_var = len(variables)

    # Build country → {land_type: value}
    country_land: dict[str, dict[str, float]] = {}
    pathway_records = []

    for row in rows[1:]:
        if not any(v is not None for v in row):
            continue
        if len(row) < 11:
            continue
        country, code, region, income, method, year, cat, land_type, _, vf, vf_unit = row[:11]
        if code == "GLO":
            continue
        if not (isinstance(code, str) and len(code) >= 2):
            continue
        if not isinstance(vf, (int, float)):
            continue
        land_str = str(land_type).strip()
        if land_str not in {lt for lt, _ in _LAND_TYPES}:
            continue
        country_land.setdefault(code, {})[land_str] = float(vf)
        pathway_records.append({
            "country": country, "country_code": code,
            "region": region, "income_group": income,
            "method": method, "year": year,
            "land_type": land_type, "valuation_factor_usd_ha": float(vf),
            "unit": vf_unit, "source": "NatCap | VI — LANCA v2.0, Valuing Impact",
        })

    # Build factor map: array ordered by _LAND_TYPES
    factor_map: dict[str, np.ndarray] = {}
    for code, land_dict in country_land.items():
        arr = np.array([
            land_dict.get(lt, _GLO_LAND_FALLBACKS[lt])
            for lt, _ in _LAND_TYPES
        ])
        factor_map[code] = arr

    pathway_df = pd.DataFrame(pathway_records)
    logger.info("  NatCap land: %d countries × %d land types", len(factor_map), N_var)
    return factor_map, variables, pathway_df


# ── Dispatch map ──────────────────────────────────────────────────────────────
_EXTRACTORS = {
    "hui":               extract_hui,
    "hut":               extract_hut,
    "wages":             extract_wages,
    "health_daly":       extract_health_daly,
    "natcap_pollution":  extract_natcap_pollution,
    "natcap_land":       extract_natcap_land,
}

# ── Global fallback values (used when a country has no data) ─────────────────
_GLOBAL_FALLBACKS = {
    "hui":              np.array([GLOBAL_AVG_HUI]),
    "hut":              np.array([GLOBAL_AVG_HUT]),
    "wages":            None,  # built at runtime from global mean
    "health_daly":      None,  # built at runtime
    "natcap_land":      None,  # built at runtime from GLO averages
}


# ═══════════════════════════════════════════════════════════════════════════════
# Stage 4 — Coefficient Matrix  (mirrors steen-vf1/pipeline.py Stages 3+4)
# ═══════════════════════════════════════════════════════════════════════════════

def create_coefficient_dataframe(
    years: list[str],
    variables: list[str],
    countries: list[str],
    nace_sectors: list[str],
    initial_value: float = 0.0,
) -> pd.DataFrame:
    """
    Create the empty coefficient matrix C[y, variable, country, sector].

    Shape: (len(years) × len(variables))  ×  (len(countries) × len(nace_sectors))

    Identical signature to steen-vf1/pipeline.create_coefficient_dataframe().
    """
    row_idx = pd.MultiIndex.from_product([years, variables], names=["Year", "Variable"])
    col_idx = pd.MultiIndex.from_product([countries, nace_sectors], names=["GeoRegion", "NACE"])
    return pd.DataFrame(initial_value, index=row_idx, columns=col_idx, dtype=float)


def populate_coefficients_by_country(
    coeff: pd.DataFrame,
    factor_map: dict,          # dict[iso3 → np.ndarray(N_var,)] or np.ndarray(N_var,) for global
    years: list[str],
    variables: list[str],
    sign: float,
    global_fallback: np.ndarray,
) -> pd.DataFrame:
    """
    Fill the coefficient matrix with country-varying or globally uniform values.

    For country-varying factors (eQALY HUI, HUT, wages, DALY, land):
      C[y, var, country, nace] = sign × factor[country, var]
      Countries with no data use global_fallback.

    For global factors (eQALY natcap_pollution, or EPS-style):
      factor_map is a plain np.ndarray → broadcast across all countries.

    Vectorised: for each year block, builds a (N_var, N_countries × N_nace)
    slice and assigns in one operation.  Mirrors EPS populate_coefficients().
    """
    N_var   = len(variables)
    N_nace  = len(NACE_SECTORS)
    arr     = coeff.to_numpy(copy=False)

    if isinstance(factor_map, np.ndarray):
        # Global uniform: broadcast across all countries (same as EPS)
        d_values = sign * factor_map          # (N_var,)
        full_row = np.repeat(d_values[:, np.newaxis], arr.shape[1], axis=1)  # (N_var, N_cols)
        for i_year in range(len(years)):
            rs = i_year * N_var
            arr[rs:rs + N_var, :] = full_row

    else:
        # Country-varying: build (N_var, N_countries) factor matrix F
        # then broadcast to (N_var, N_countries × N_nace) via np.repeat
        N_countries = len(COUNTRIES)
        F = np.empty((N_var, N_countries), dtype=float)
        for i_c, ctry in enumerate(COUNTRIES):
            F[:, i_c] = sign * factor_map.get(ctry, global_fallback)
        # Repeat each country's column N_nace times → (N_var, N_countries × N_nace)
        F_broadcast = np.repeat(F, N_nace, axis=1)
        for i_year in range(len(years)):
            rs = i_year * N_var
            arr[rs:rs + N_var, :] = F_broadcast

    return coeff


def calculate_inflation_factors(years: list[str]) -> pd.Series:
    """
    Compute year-specific USD inflation factors (2023 = 1.0).

    I[y] = USD_DEFLATOR[y] / USD_DEFLATOR[base_year]

    Years beyond the last known deflator are frozen at the last known value.
    Mirrors steen-vf1/pipeline.calculate_inflation_factors().
    """
    last_val = USD_DEFLATOR_2023BASE[USD_DEFLATOR_LAST_KNOWN]
    base_val = USD_DEFLATOR_2023BASE[USD_DEFLATOR_BASE_YEAR]
    factors  = {}
    for year in years:
        raw = USD_DEFLATOR_2023BASE.get(year, last_val)
        factors[year] = raw / base_val
    return pd.Series(factors, name="inflation_factor")


def apply_deflation(
    coeff: pd.DataFrame,
    inflation_factors: pd.Series,
    years: list[str],
    variables: list[str],
) -> pd.DataFrame:
    """
    Apply I[y] to each year slice of the coefficient matrix.

    After this step: C[y, var, c, n] = sign × factor[var, c] × I[y]

    Mirrors steen-vf1/pipeline.apply_deflation() exactly.
    """
    coeff_final = coeff.copy()
    arr  = coeff_final.to_numpy(copy=False)
    N_var = len(variables)

    i_col = np.repeat(
        [inflation_factors[y] for y in years], N_var
    ).reshape(-1, 1)
    arr *= i_col
    return coeff_final


def build_unit_frame(
    variables: list[str],
    years: list[str],
    unit_base: str,
) -> pd.DataFrame:
    """
    Build units metadata DataFrame.

    For years with known deflator: "2023USD/{unit_base}"
    For forecast years:            "2023USD/{unit_base}" (frozen at last known)

    Mirrors steen-vf1/pipeline.build_unit_frame().
    """
    known_years = set(USD_DEFLATOR_2023BASE)
    last_known  = USD_DEFLATOR_LAST_KNOWN
    rows = {}
    for var in variables:
        rows[var] = {
            y: f"{y}USD/{unit_base}" if y in known_years
               else f"{last_known}USD/{unit_base}"
            for y in years
        }
    return pd.DataFrame(rows).T


# ═══════════════════════════════════════════════════════════════════════════════
# Stage 5 — Output Export  (mirrors steen-vf1/pipeline.save_results())
# ═══════════════════════════════════════════════════════════════════════════════

def save_results(
    coeff_final: pd.DataFrame,
    units: pd.DataFrame,
    pathway_df: pd.DataFrame,
    hdf5_path: str | Path,
    excel_path: str | Path,
    hdf5_coeff_key: str = "coefficient",
    hdf5_unit_key:  str = "unit",
    excel_sheet_coeff:   str = "Coefficients",
    excel_sheet_units:   str = "Units",
    excel_sheet_pathway: str = "Pathway data",
    freeze_coeff: tuple = (1, 2),
    freeze_units: tuple = (1, 1),
) -> None:
    """
    Persist coefficient matrix and unit metadata to HDF5 and Excel.

    HDF5 keys (identical to WifOR/EPS):
      "coefficient"  → full coeff_final DataFrame (all GeoRegion × NACE columns)
      "unit"         → units DataFrame

    Excel sheets (identical to WifOR/EPS):
      "Coefficients" → compact view (first _EXCEL_MAX_COLS country columns)
      "Units"        → units metadata
      "Pathway data" → full source factor table

    Mirrors steen-vf1/pipeline.save_results() exactly.
    """
    hdf5_path  = Path(hdf5_path)
    excel_path = Path(excel_path)
    hdf5_path.parent.mkdir(parents=True, exist_ok=True)
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    # ── HDF5 ─────────────────────────────────────────────────────────────────
    coeff_final.to_hdf(hdf5_path, key=hdf5_coeff_key, mode="w", complevel=4, complib="blosc")
    units.to_hdf(hdf5_path, key=hdf5_unit_key, mode="a")
    logger.info("  Saved HDF5 : %s", hdf5_path.name)

    # ── Excel ─────────────────────────────────────────────────────────────────
    n_cols = coeff_final.shape[1]
    coeff_excel = (
        coeff_final.iloc[:, :_EXCEL_MAX_COLS] if n_cols > _EXCEL_MAX_COLS else coeff_final
    )
    col_note = (
        f"Showing {_EXCEL_MAX_COLS} of {n_cols} GeoRegion×NACE columns. "
        f"Full data in companion .h5 file."
        if n_cols > _EXCEL_MAX_COLS else None
    )

    with pd.ExcelWriter(excel_path, engine="openpyxl", mode="w") as writer:
        coeff_excel.to_excel(
            writer, sheet_name=excel_sheet_coeff,
            merge_cells=False, freeze_panes=freeze_coeff,
        )
        if col_note:
            pd.DataFrame({"Note": [col_note]}).to_excel(
                writer, sheet_name="Notes", index=False
            )
        units.to_excel(
            writer, sheet_name=excel_sheet_units,
            merge_cells=False, freeze_panes=freeze_units,
        )
        if not pathway_df.empty:
            pathway_df.to_excel(writer, sheet_name=excel_sheet_pathway, index=False)

    logger.info("  Saved Excel: %s", excel_path.name)


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience: full indicator run  (called by individual indicator scripts)
# ═══════════════════════════════════════════════════════════════════════════════

def run_indicator(indicator_key: str) -> dict:
    """
    Run the full 5-stage pipeline for one eQALY indicator.

    Mirrors steen-vf1/pipeline.run_indicator() exactly.

    Returns dict with keys: coeff_final, units, pathway_df, variables.
    """
    import config  # local import so indicator scripts don't need sys.path tricks

    # Stage 1 — Configuration
    cfg          = config.get_indicator_config(indicator_key)
    years        = cfg["years"]
    sign         = cfg["sign"]
    unit_base    = cfg["unit"]
    sheet_name   = cfg["sheet"]
    country_vary = cfg["country_varying"]

    logger.info("=" * 60)
    logger.info("Indicator : %s", indicator_key)
    logger.info("Sheet     : %s", sheet_name)
    logger.info("Capital   : %s", cfg["capital"])
    logger.info("Sign      : %+.1f", sign)
    logger.info("By country: %s", country_vary)
    logger.info("Years     : %s … %s (%d)", years[0], years[-1], len(years))
    logger.info("Countries : %d | Sectors: %d", len(COUNTRIES), len(NACE_SECTORS))

    # Stage 2 — Data Loading
    rows = load_sheet(cfg["source_xlsx"], sheet_name)

    # Stage 3 — Factor Extraction
    extractor = _EXTRACTORS[indicator_key]
    factor_data, variables, pathway_df = extractor(rows)

    if not variables:
        logger.error("No factors extracted for '%s'", indicator_key)
        return {}

    # Build global fallback for country-varying indicators
    if country_vary and isinstance(factor_data, dict) and factor_data:
        global_fallback = np.mean(np.stack(list(factor_data.values())), axis=0)
    elif indicator_key == "hui":
        global_fallback = np.array([GLOBAL_AVG_HUI])
    elif indicator_key == "hut":
        global_fallback = np.array([GLOBAL_AVG_HUT])
    else:
        global_fallback = np.zeros(len(variables))

    logger.info("  Variables : %d extracted", len(variables))

    # Stage 4 — Coefficient Matrix
    coeff = create_coefficient_dataframe(years, variables, COUNTRIES, NACE_SECTORS)
    coeff = populate_coefficients_by_country(
        coeff, factor_data, years, variables, sign, global_fallback
    )
    inflation_factors = calculate_inflation_factors(years)
    coeff_final = apply_deflation(coeff, inflation_factors, years, variables)
    units = build_unit_frame(variables, years, unit_base)

    # Stage 5 — Output Export
    save_results(
        coeff_final, units, pathway_df,
        hdf5_path=cfg["hdf5_path"],
        excel_path=cfg["excel_path"],
        hdf5_coeff_key=cfg["hdf5_coeff_key"],
        hdf5_unit_key=cfg["hdf5_unit_key"],
        excel_sheet_coeff=cfg["excel_sheet_coefficients"],
        excel_sheet_units=cfg["excel_sheet_units"],
        excel_sheet_pathway=cfg["excel_sheet_pathway"],
        freeze_coeff=cfg["excel_freeze_coefficients"],
        freeze_units=cfg["excel_freeze_units"],
    )

    logger.info("Done %-20s → C matrix %s", indicator_key, coeff_final.shape)

    return {
        "coeff_final":  coeff_final,
        "units":        units,
        "pathway_df":   pathway_df,
        "variables":    variables,
    }

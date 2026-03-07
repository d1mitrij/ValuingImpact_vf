"""
03_prepare_wages_eqaly.py — eQALY Value Factor script: wages

Pipeline
────────
  Stage 1  Configuration  config.get_indicator_config("wages")
  Stage 2  Data Loading   pipeline.load_sheet()
  Stage 3  Extraction     pipeline.extract_wages()
  Stage 4  Coefficients   pipeline.create_coefficient_dataframe()
                          pipeline.populate_coefficients_by_country()
                          pipeline.calculate_inflation_factors()
                          pipeline.apply_deflation()
  Stage 5  Output         pipeline.save_results()

Outputs
───────
  output/03_eqaly_wages.h5     HDF5: keys "coefficient" and "unit"
  output/03_eqaly_wages.xlsx   Excel: "Coefficients", "Units", "Pathway data"

Source
──────
  Valuing Impact — eQALY_Template_2025-02-14_EXPORT.xlsx
  Framework: WIVF — WASH Impact Valuation Framework 2024
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(name)s: %(message)s")

if __name__ == "__main__":
    pipeline.run_indicator("wages")

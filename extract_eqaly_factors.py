"""
extract_eqaly_factors.py — eQALY / Valuing Impact value factor extractor.

Orchestrator script — mirrors steen-vf1/eps_value_factors/run_all_eps_factors.py
and uba1/extract_uba_values.py.

Reads the eQALY_Template Excel (Valuing Impact, 2025) and extracts all
reference valuation factor datasets into structured CSV and Excel outputs.

eQALY core formula applied to each pathway:
  Footprint          = Output × Outcome_rate × Baseline × Drop-off × Attribution × Duration
  Societal_valuation = Footprint × Valuation_factor

Framework reference:
  WIVF_Wash-Impact-Valuation-Framework-2024d.pdf

Usage:
    python extract_eqaly_factors.py                   # extract all 7 pathways
    python extract_eqaly_factors.py --only hui hut     # selective extraction
    python extract_eqaly_factors.py --list             # list available pathways
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config
import pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _list_pathways() -> None:
    print(f"\n{'ID':<4} {'Key':<22} {'Capital':<18} {'Title'}")
    print("-" * 75)
    for key, cfg in config.PATHWAYS.items():
        print(f"{cfg['id']:<4} {key:<22} {cfg['capital']:<18} {cfg['title']}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract eQALY / Valuing Impact value factors to CSV + Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Output: vf_valuingimpact/eqaly_value_factors/output/NN_eqaly_<key>.csv\n"
            "Source: eQALY_Template_2025-02-14_EXPORT.xlsx — Valuing Impact\n"
            "Framework: WIVF — WASH Impact Valuation Framework 2024"
        ),
    )
    parser.add_argument(
        "--only", nargs="+", metavar="KEY",
        help="Extract only these pathways (space-separated keys)",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all available pathways and exit",
    )
    args = parser.parse_args()

    if args.list:
        _list_pathways()
        return

    keys = list(config.PATHWAYS.keys())
    if args.only:
        unknown = [k for k in args.only if k not in config.PATHWAYS]
        if unknown:
            logger.error("Unknown pathway(s): %s", unknown)
            _list_pathways()
            sys.exit(1)
        keys = args.only

    pub = config.PUBLICATION
    gp  = config.GLOBAL_PARAMS
    print(f"\n{pub['title']}")
    print(f"Source  : {pub['source']}")
    print(f"Template: {pub['template']}")
    print(f"Framework: {pub['framework']}")
    print(f"Price base: {pub['price_base']}  |  Ref year: {pub['ref_year']}")
    print(f"\nGlobal parameters:")
    print(f"  DALY value       : {gp['daly_value_usd']:,} USD/DALY  (OECD GDP/capita 2023)")
    print(f"  Average HUT      : {gp['avg_hut_usd_usd']:.4f} USD/USD  (ecosystem services multiplier)")
    print(f"  Average HUI      : {gp['avg_hui_usd_usd']:.4f} USD/USD  (income welfare multiplier)")
    print(f"\nExtracting {len(keys)} pathway(s) → {config.OUTPUT_DIR}/\n")

    if not config.SOURCE_XLS.exists():
        logger.error("Source Excel not found: %s", config.SOURCE_XLS)
        sys.exit(1)

    t0 = time.time()
    results: dict[str, Path] = {}
    errors:  dict[str, Exception] = {}

    for key in keys:
        try:
            t1  = time.time()
            out = pipeline.run_pathway(key)
            elapsed = time.time() - t1
            results[key] = out
            print(f"  [OK]   {key:<22}  {elapsed:.2f}s  →  {out.name}")
        except Exception as exc:
            errors[key] = exc
            print(f"  [FAIL] {key:<22}  {exc}")
            logger.exception("Pathway '%s' failed", key)

    wall   = time.time() - t0
    n_ok   = len(results)
    n_fail = len(errors)

    print(f"\n{'─' * 60}")
    print(f"Done: {n_ok}/{len(keys)} succeeded, {n_fail} failed  ({wall:.1f}s)\n")

    if results:
        print("Output files:")
        for key, path in results.items():
            rows = sum(1 for _ in open(path, encoding="utf-8")) - 1
            print(f"  {path.name:<48} {rows:>5} rows")

    if errors:
        print("\nFailed:")
        for key, exc in errors.items():
            print(f"  {key}: {exc}")

    # Timestamped execution log (mirrors steen-vf1 and uba1 pattern)
    log_path = config.THIS_DIR / f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_path, "w", encoding="utf-8") as lf:
        lf.write(f"eQALY Execution Log — {datetime.now().isoformat()}\n")
        lf.write(f"{'─' * 60}\n")
        for key in keys:
            if key in results:
                lf.write(f"[OK]   {key}\n")
            else:
                lf.write(f"[FAIL] {key}  —  {errors[key]}\n")
        lf.write(f"{'─' * 60}\n")
        lf.write(f"Total: {n_ok}/{len(keys)} succeeded  wall-clock {wall:.1f}s\n")
    print(f"\nExecution log: {log_path.name}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

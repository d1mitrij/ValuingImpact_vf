"""
run_all_eqaly_factors.py — Parallel runner for all eQALY Value Factor scripts.

Mirrors steen-vf1/eps_value_factors/run_all_eps_factors.py exactly:
  - Discovers indicator scripts via glob on indicators/*.py
  - Runs each as a subprocess with ThreadPoolExecutor
  - Logs execution time and status per script
  - Writes a timestamped execution log

Usage
─────
  python run_all_eqaly_factors.py                              # all indicators
  python run_all_eqaly_factors.py --max-workers 4
  python run_all_eqaly_factors.py --only hui hut wages
  python run_all_eqaly_factors.py --list
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from config import list_indicators

logger = logging.getLogger(__name__)


def _discover_scripts(only: list[str] | None = None) -> list[tuple[str, Path]]:
    """Return (indicator_key, script_path) pairs, optionally filtered."""
    indicators_dir = ROOT / "indicators"
    all_scripts = sorted(indicators_dir.glob("[0-9][0-9]*_prepare_*_eqaly.py"))

    results = []
    for script in all_scripts:
        # Extract key from filename: 001_prepare_hui_eqaly.py → hui
        stem  = script.stem
        parts = stem.split("_prepare_", 1)
        if len(parts) < 2:
            continue
        key = parts[1].removesuffix("_eqaly")
        if only and key not in only:
            continue
        results.append((key, script))
    return results


def _run_script(key: str, script: Path, timeout: int, verbose: bool) -> dict:
    """Run one indicator script as a subprocess; return status dict."""
    start = time.monotonic()
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=not verbose,
            timeout=timeout,
            text=True,
        )
        elapsed = time.monotonic() - start
        if result.returncode != 0:
            err = (result.stderr or "").strip()
            return {"key": key, "ok": False, "elapsed": elapsed, "error": err}
        return {"key": key, "ok": True, "elapsed": elapsed, "error": None}
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return {"key": key, "ok": False, "elapsed": elapsed,
                "error": f"Timeout after {timeout}s"}
    except Exception as exc:
        elapsed = time.monotonic() - start
        return {"key": key, "ok": False, "elapsed": elapsed, "error": str(exc)}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

    parser = argparse.ArgumentParser(
        description="Run all eQALY Value Factor indicator scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Each script produces:\n"
            "  output/NN_eqaly_<key>.h5    — HDF5 coefficient matrix\n"
            "  output/NN_eqaly_<key>.xlsx  — Excel (Coefficients, Units, Pathway data)\n\n"
            "Source: eQALY_Template_2025-02-14_EXPORT.xlsx — Valuing Impact\n"
            "Framework: WIVF — WASH Impact Valuation Framework 2024"
        ),
    )
    parser.add_argument("--max-workers", type=int, default=4,
                        help="Max parallel subprocess workers (default: 4)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Timeout per script in seconds (default: 600)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show subprocess stdout/stderr in real time")
    parser.add_argument("--only", nargs="+", metavar="KEY",
                        help="Run only these indicator keys")
    parser.add_argument("--list", action="store_true",
                        help="List all available indicators and exit")
    args = parser.parse_args()

    if args.list:
        print(f"\n{'ID':<4} {'Key':<22} {'Description'}")
        print("-" * 80)
        for key, ind_id, desc in list_indicators():
            print(f"{ind_id:<4} {key:<22} {desc[:55]}")
        print()
        return

    scripts = _discover_scripts(args.only)
    if not scripts:
        logger.error("No indicator scripts found in %s/indicators/", ROOT)
        sys.exit(1)

    print(f"\neQALY Value Factors — Parallel Runner")
    print(f"Indicators : {len(scripts)}")
    print(f"Workers    : {args.max_workers}")
    print(f"Output     : {ROOT / 'output'}/\n")

    t0 = time.monotonic()
    futures = {}
    results: list[dict] = []

    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        for key, script in scripts:
            future = pool.submit(_run_script, key, script, args.timeout, args.verbose)
            futures[future] = key

        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            status = "[OK]  " if res["ok"] else "[FAIL]"
            print(f"  {status} {res['key']:<22}  {res['elapsed']:.1f}s"
                  + (f"  ERROR: {res['error']}" if not res["ok"] else ""))

    wall   = time.monotonic() - t0
    n_ok   = sum(1 for r in results if r["ok"])
    n_fail = len(results) - n_ok

    print(f"\n{'─' * 60}")
    print(f"Done: {n_ok}/{len(results)} succeeded, {n_fail} failed  ({wall:.1f}s)")

    if n_ok:
        print("\nOutput files:")
        from config import OUTPUT_DIR, INDICATORS
        for key, _ in scripts:
            if any(r["key"] == key and r["ok"] for r in results):
                ind_id = INDICATORS[key]["id"]
                for ext in (".h5", ".xlsx"):
                    p = OUTPUT_DIR / f"{ind_id}_eqaly_{key}{ext}"
                    if p.exists():
                        size = p.stat().st_size // 1024
                        print(f"  {p.name:<48} {size:>6} KB")

    # Execution log
    log_path = ROOT / f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_path, "w", encoding="utf-8") as lf:
        lf.write(f"eQALY Execution Log — {datetime.now().isoformat()}\n")
        lf.write(f"{'─' * 60}\n")
        for res in sorted(results, key=lambda r: r["key"]):
            tag = "[OK]  " if res["ok"] else "[FAIL]"
            lf.write(f"{tag} {res['key']:<22}  {res['elapsed']:.1f}s\n")
            if not res["ok"]:
                lf.write(f"       Error: {res['error']}\n")
        lf.write(f"{'─' * 60}\n")
        lf.write(f"Total: {n_ok}/{len(results)} succeeded  wall-clock {wall:.1f}s\n")
    print(f"\nExecution log: {log_path.name}")

    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()

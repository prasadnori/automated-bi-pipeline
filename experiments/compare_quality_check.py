"""Compare the same non-negative employee-count check in three approaches.

Run:
  python experiments/compare_quality_check.py path/to/Visadataset.csv

Requires:
  pip install -r requirements.txt
  pip install pandera

The script reports execution time and whether each approach identifies the same
invalid rows. Execution time is NOT a measure of development effort.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import statistics
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from automated_bi.profiling import DataQualityProfiler  # noqa: E402


def framework_check(df: pd.DataFrame) -> list[str]:
    report = DataQualityProfiler(
        numeric_rules={"no_of_employees": {"min": 0}}
    ).profile(df)
    finding = next(
        (item for item in report["data_quality_findings"]
         if item["column"] == "no_of_employees"
         and item["rule"] == "numeric_range"),
        None,
    )
    return [] if finding is None else [str(x) for x in finding["record_ids"]]


def pandas_check(df: pd.DataFrame) -> list[str]:
    values = pd.to_numeric(df["no_of_employees"], errors="coerce")
    bad = df.loc[values < 0]
    if "case_id" in bad.columns:
        return bad["case_id"].astype(str).tolist()
    return bad.index.astype(str).tolist()


def pandera_check(df: pd.DataFrame) -> list[str]:
    try:
        import pandera.pandas as pa
    except ImportError as exc:
        raise RuntimeError(
            "Pandera is not installed. Run: pip install pandera"
        ) from exc

    schema = pa.DataFrameSchema(
        {"no_of_employees": pa.Column(float, checks=pa.Check.ge(0), nullable=True)},
        strict=False,
        coerce=True,
    )
    try:
        schema.validate(df, lazy=True)
        return []
    except pa.errors.SchemaErrors as exc:
        failures = exc.failure_cases
        # Pandera reports the failing row index for series-level checks.
        bad_indices = set()
        if "index" in failures.columns:
            for value in failures.loc[failures["column"] == "no_of_employees", "index"]:
                if pd.notna(value):
                    try:
                        bad_indices.add(int(value))
                    except (TypeError, ValueError):
                        pass
        bad = df.loc[df.index.isin(bad_indices)]
        if "case_id" in bad.columns:
            return bad["case_id"].astype(str).tolist()
        return bad.index.astype(str).tolist()


def benchmark(label, fn, df, warmups: int, repeats: int):
    # Warm up each implementation, then report repeated timings. Keep correctness
    # output separate from runtime so a fast but incorrect method cannot pass.
    result = fn(df)
    for _ in range(warmups):
        fn(df)
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        repeated_result = fn(df)
        samples.append(time.perf_counter() - start)
        if set(repeated_result) != set(result):
            raise RuntimeError(f"{label} returned inconsistent results between runs.")
    return {
        "approach": label,
        "invalid_count": len(result),
        "record_ids": result,
        "runtime_repeats_seconds": [round(x, 6) for x in samples],
        "runtime_median_seconds": round(statistics.median(samples), 6),
        "runtime_min_seconds": round(min(samples), 6),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", help="CSV containing no_of_employees; case_id is recommended")
    parser.add_argument("--output", default="results/quality_comparison.json")
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()

    if args.warmups < 0 or args.repeats < 1:
        raise SystemExit("--warmups must be >= 0 and --repeats must be >= 1.")

    df = pd.read_csv(args.csv)
    if "no_of_employees" not in df.columns:
        raise SystemExit("Input must contain a 'no_of_employees' column.")

    results = [
        benchmark("Proposed framework", framework_check, df, args.warmups, args.repeats),
        benchmark("Plain pandas", pandas_check, df, args.warmups, args.repeats),
        benchmark("Pandera validation library", pandera_check, df, args.warmups, args.repeats),
    ]
    expected = set(results[1]["record_ids"])
    for item in results:
        item["matches_pandas_result"] = set(item["record_ids"]) == expected
    if not all(item["matches_pandas_result"] for item in results):
        raise SystemExit("Correctness check failed: approaches returned different record IDs.")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "dataset": str(Path(args.csv)),
        "row_count": len(df),
        "check": "no_of_employees >= 0",
        "results": results,
        "interpretation_note": (
            "Runtime uses warmups and repeated measurements; report the median. "
            "Execution time is runtime only, not development effort. "
            "Record implementation time separately using the protocol in "
            "experiments/DEVELOPMENT_EFFORT_PROTOCOL.md."
        ),
    }, indent=2), encoding="utf-8")
    print(f"Rows checked: {len(df):,}; warmups={args.warmups}; repeats={args.repeats}")
    for item in results:
        print(f"{item['approach']}: {item['invalid_count']} invalid rows; "
              f"matches pandas={item['matches_pandas_result']}; "
              f"median runtime={item['runtime_median_seconds']}s; "
              f"min runtime={item['runtime_min_seconds']}s")
    print(f"Results written to: {out}")


if __name__ == "__main__":
    main()

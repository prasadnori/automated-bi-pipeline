import argparse
from src_path_fix import ensure_src_path
ensure_src_path()

from automated_bi.pipeline import AutomatedBIPipeline
from automated_bi.profiling import DataQualityProfiler

def main():
    parser = argparse.ArgumentParser(description="Run the automated BI pipeline.")
    parser.add_argument("csv", help="Path to input CSV file")
    parser.add_argument("--column", required=True, help="Column for frequency table and chart")
    parser.add_argument("--output", default="results", help="Output directory")
    parser.add_argument("--quality", action="store_true", help="Use the extended data-quality profiler")
    args = parser.parse_args()
    profiler = (
        DataQualityProfiler(numeric_rules={"no_of_employees": {"min": 0}})
        if args.quality else None
    )
    pipeline = AutomatedBIPipeline(profiler=profiler)
    result = pipeline.run(args.csv, args.column, args.output)
    print(f"Rows processed: {result['profile']['row_count']}")
    print(f"Columns found: {result['profile']['column_count']}")
    print(f"Outputs written to: {args.output}")

if __name__ == "__main__":
    main()

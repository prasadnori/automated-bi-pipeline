"""Report basic profile counts for the normalized UCI Adult CSV."""
import argparse
import json
from pathlib import Path
import pandas as pd

SOURCE = "https://archive.ics.uci.edu/dataset/2/adult"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="?", default="datasets/adult_normalized.csv")
    parser.add_argument("--output", default="results/adult_dataset_evaluation.json")
    args = parser.parse_args()
    data = pd.read_csv(args.csv)
    report = {
        "dataset": "UCI Adult training data (normalized copy)",
        "source": SOURCE,
        "preprocessing": "Literal '?' markers replaced with missing values; rows and all other values retained.",
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "numeric_columns": int(len(data.select_dtypes(include="number").columns)),
        "categorical_columns": int(len(data.select_dtypes(exclude="number").columns)),
        "missing_cells_after_normalization": int(data.isna().sum().sum()),
        "duplicate_rows": int(data.duplicated().sum()),
        "column_missing_counts": {str(k): int(v) for k, v in data.isna().sum().items() if v},
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

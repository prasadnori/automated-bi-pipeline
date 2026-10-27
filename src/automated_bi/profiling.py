import pandas as pd

class DataProfiler:
    """Base class for profiling a dataset."""
    def profile(self, data: pd.DataFrame) -> dict:
        return {
            "row_count": int(len(data)),
            "column_count": int(len(data.columns)),
            "columns": list(data.columns),
            "missing_by_column": data.isna().sum().astype(int).to_dict(),
            "data_types": data.dtypes.astype(str).to_dict(),
        }

class DataQualityProfiler(DataProfiler):
    """Adds checks for missing cells, duplicate rows, and configured rules."""
    def __init__(self, numeric_rules=None):
        # Example: {"no_of_employees": {"min": 0}}
        self.numeric_rules = numeric_rules or {}

    def profile(self, data: pd.DataFrame) -> dict:
        report = super().profile(data)
        report["duplicate_rows"] = int(data.duplicated().sum())
        report["missing_cells"] = int(data.isna().sum().sum())
        report["numeric_summary"] = data.select_dtypes(include="number").describe().to_dict()

        findings = []
        for column, rule in self.numeric_rules.items():
            if column not in data.columns:
                findings.append({
                    "column": column,
                    "rule": "column_exists",
                    "message": f"Configured column '{column}' was not found.",
                    "affected_rows": 0,
                    "record_ids": [],
                })
                continue

            values = pd.to_numeric(data[column], errors="coerce")
            invalid_mask = pd.Series(False, index=data.index)
            if "min" in rule:
                invalid_mask |= values < rule["min"]
            if "max" in rule:
                invalid_mask |= values > rule["max"]

            affected = data.loc[invalid_mask]
            record_ids = (
                affected["case_id"].astype(str).tolist()
                if "case_id" in affected.columns
                else affected.index.astype(str).tolist()
            )
            if len(affected):
                bounds = []
                if "min" in rule:
                    bounds.append(f"minimum {rule['min']}")
                if "max" in rule:
                    bounds.append(f"maximum {rule['max']}")
                findings.append({
                    "column": column,
                    "rule": "numeric_range",
                    "message": f"Values outside configured range ({', '.join(bounds)}). Review before changing data.",
                    "affected_rows": int(len(affected)),
                    "record_ids": record_ids,
                })

        report["data_quality_findings"] = findings
        return report

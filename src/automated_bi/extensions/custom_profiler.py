from __future__ import annotations

import pandas as pd
from automated_bi.profiling import DataProfiler


class MissingAndRangeProfiler(DataProfiler):
    """Example extension: add missing/duplicate statistics and configurable numeric rules.

    This extension uses the existing DataProfiler contract and can be injected into
    AutomatedBIPipeline without changing the pipeline implementation.
    """
    def __init__(self, numeric_rules=None, record_id_column=None):
        self.numeric_rules = numeric_rules or {}
        self.record_id_column = record_id_column

    def profile(self, data: pd.DataFrame) -> dict:
        report = super().profile(data)
        report["missing_cells"] = int(data.isna().sum().sum())
        report["duplicate_rows"] = int(data.duplicated().sum())
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
            mask = pd.Series(False, index=data.index)
            if "min" in rule:
                mask |= values < rule["min"]
            if "max" in rule:
                mask |= values > rule["max"]
            affected = data.loc[mask]
            id_col = self.record_id_column
            if id_col and id_col in affected.columns:
                ids = affected[id_col].astype(str).tolist()
            else:
                ids = affected.index.astype(str).tolist()
            if len(affected):
                findings.append({
                    "column": column,
                    "rule": "numeric_range",
                    "message": f"Values outside configured range {rule}.",
                    "affected_rows": int(len(affected)),
                    "record_ids": ids,
                })
        report["data_quality_findings"] = findings
        return report

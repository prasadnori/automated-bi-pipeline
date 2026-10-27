import sys
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from automated_bi.pipeline import AutomatedBIPipeline
from automated_bi.profiling import DataProfiler, DataQualityProfiler
from automated_bi.transformation import FrequencyTable

def test_frequency_table_counts_missing_values():
    data = pd.DataFrame({"group": ["A", "B", "A", None]})
    table = FrequencyTable().transform(data, "group")
    counts = dict(zip(table["value"].astype(str), table["count"]))
    assert counts["A"] == 2
    assert counts["B"] == 1
    assert counts["None"] == 1

def test_quality_profiler_adds_checks():
    data = pd.DataFrame({"x": [1, None, 1], "kind": ["a", "b", "a"]})
    report = DataQualityProfiler().profile(data)
    assert report["missing_cells"] == 1
    assert report["duplicate_rows"] == 1
    assert report["row_count"] == 3

def test_custom_profiler_can_be_injected(tmp_path):
    data_path = tmp_path / "sample.csv"
    pd.DataFrame({"kind": ["a", "b", "a"], "amount": [10, None, 30]}).to_csv(data_path, index=False)
    pipeline = AutomatedBIPipeline(profiler=DataQualityProfiler())
    result = pipeline.run(data_path, "kind", tmp_path / "out")
    assert result["profile"]["missing_cells"] == 1
    assert (tmp_path / "out" / "profile.json").is_file()
    assert (tmp_path / "out" / "frequency_kind.csv").is_file()
    assert (tmp_path / "out" / "frequency_kind.png").is_file()

def test_missing_column_fails_clearly():
    with pytest.raises(KeyError):
        FrequencyTable().transform(pd.DataFrame({"x": [1]}), "missing")

def test_quality_profiler_flags_negative_employee_counts():
    data = pd.DataFrame({
        "case_id": ["EZYV1", "EZYV2", "EZYV3"],
        "no_of_employees": [100, -25, 20],
    })
    profiler = DataQualityProfiler(numeric_rules={"no_of_employees": {"min": 0}})
    report = profiler.profile(data)
    finding = next(f for f in report["data_quality_findings"]
                   if f["column"] == "no_of_employees")
    assert finding["affected_rows"] == 1
    assert finding["record_ids"] == ["EZYV2"]


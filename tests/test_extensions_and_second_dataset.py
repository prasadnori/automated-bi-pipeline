from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from automated_bi.pipeline import AutomatedBIPipeline
from automated_bi.extensions.custom_profiler import MissingAndRangeProfiler


def test_extension_is_injected_without_pipeline_modification(tmp_path):
    source = tmp_path / "different.csv"
    pd.DataFrame({
        "department": ["Sales", "IT", "IT", None],
        "age": [25, 31, None, 42],
        "salary": [50000, -1, 65000, 70000],
        "performance_rating": [4, 3, 5, 4],
        "region": ["East", "West", "West", "North"],
    }).to_csv(source, index=False)

    profiler = MissingAndRangeProfiler(numeric_rules={"salary": {"min": 0}})
    pipeline = AutomatedBIPipeline(profiler=profiler)
    result = pipeline.run(source, "department", tmp_path / "out")

    assert result["profile"]["row_count"] == 4
    assert result["profile"]["column_count"] == 5
    assert result["profile"]["missing_cells"] == 2
    finding = next(item for item in result["profile"]["data_quality_findings"]
                   if item["column"] == "salary")
    assert finding["affected_rows"] == 1
    assert finding["record_ids"] == ["1"]
    assert (tmp_path / "out" / "frequency_department.png").exists()


def test_second_dataset_fixture_has_expected_structure():
    path = ROOT / "datasets" / "second_dataset.csv"
    data = pd.read_csv(path)
    assert {"department", "age", "salary", "performance_rating", "region"}.issubset(data.columns)
    assert data.isna().sum().sum() >= 1
    assert data.select_dtypes(include="number").shape[1] >= 2

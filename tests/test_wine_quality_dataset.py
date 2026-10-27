from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from automated_bi.pipeline import AutomatedBIPipeline
from automated_bi.profiling import DataQualityProfiler


def test_wine_quality_dataset_runs_with_dataset_specific_rule(tmp_path):
    source = ROOT / "datasets" / "winequality_red.csv"
    data = pd.read_csv(source)
    assert data.shape == (1599, 12)
    assert "quality" in data.columns
    assert "no_of_employees" not in data.columns

    profiler = DataQualityProfiler(numeric_rules={"quality": {"min": 0, "max": 10}})
    pipeline = AutomatedBIPipeline(profiler=profiler)
    result = pipeline.run(source, "quality", tmp_path / "out")

    assert result["profile"]["row_count"] == 1599
    assert result["profile"]["column_count"] == 12
    assert result["profile"]["missing_cells"] == 0
    assert result["profile"]["duplicate_rows"] == 240
    assert not any(
        item.get("rule") == "column_exists"
        for item in result["profile"]["data_quality_findings"]
    )
    assert (tmp_path / "out" / "frequency_quality.csv").exists()
    assert (tmp_path / "out" / "frequency_quality.png").exists()

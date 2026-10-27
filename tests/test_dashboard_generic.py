from pathlib import Path
import pandas as pd
from interactive_dashboard import build_dashboard


def test_dashboard_titles_are_dataset_generic(tmp_path):
    source = tmp_path / "winequality_red.csv"
    pd.DataFrame({"quality": [5, 6, 6, 7], "alcohol": [9.4, 10.1, 10.2, 11.0], "pH": [3.4, 3.3, 3.2, 3.1]}).to_csv(source, index=False)
    out = build_dashboard(source, tmp_path / "dashboard.html", category="quality", measure="alcohol")
    html = out.read_text(encoding="utf-8")
    assert "Application outcomes" not in html
    assert "Applications by" not in html
    assert "Average" in html and "CONFIG.measure" in html
    assert "Dataset Analytics Dashboard" in html

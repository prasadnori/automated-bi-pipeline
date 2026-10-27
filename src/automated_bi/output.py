import json
from pathlib import Path

class ReportWriter:
    """Write a profile report as readable JSON."""
    def write_json(self, report: dict, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return output_path

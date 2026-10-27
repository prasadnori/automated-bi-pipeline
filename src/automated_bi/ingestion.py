from pathlib import Path
import pandas as pd

class DataIngestor:
    """Read a CSV file into a pandas DataFrame."""
    def read(self, path):
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")
        if path.suffix.lower() != ".csv":
            raise ValueError("This first version supports CSV files only.")
        return pd.read_csv(path)

import pandas as pd

class FrequencyTable:
    """Create a frequency table for a selected column."""
    def transform(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        if column not in data.columns:
            raise KeyError(f"Column not found: {column}")
        result = data[column].value_counts(dropna=False).rename_axis("value").reset_index(name="count")
        return result

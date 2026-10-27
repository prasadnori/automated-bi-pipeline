from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

class ChartMaker:
    """Save a bar chart from a frequency table."""
    def create_bar_chart(self, frequency_table: pd.DataFrame, output_path):
        if not {"value", "count"}.issubset(frequency_table.columns):
            raise ValueError("Expected a frequency table with 'value' and 'count' columns.")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        labels = frequency_table["value"].astype(str)
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(labels, frequency_table["count"])
        ax.set_xlabel("Value")
        ax.set_ylabel("Count")
        ax.set_title("Frequency by value")
        ax.tick_params(axis="x", labelrotation=35)
        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        return output_path

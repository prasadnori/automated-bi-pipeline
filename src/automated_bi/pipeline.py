from pathlib import Path
from .ingestion import DataIngestor
from .profiling import DataProfiler
from .transformation import FrequencyTable
from .visualization import ChartMaker
from .output import ReportWriter

class AutomatedBIPipeline:
    """Coordinate the pipeline while allowing components to be replaced."""
    def __init__(self, ingestor=None, profiler=None, transformer=None, visualizer=None, writer=None):
        self.ingestor = ingestor or DataIngestor()
        self.profiler = profiler or DataProfiler()
        self.transformer = transformer or FrequencyTable()
        self.visualizer = visualizer or ChartMaker()
        self.writer = writer or ReportWriter()

    def run(self, input_path, column, output_dir="results"):
        output_dir = Path(output_dir)
        data = self.ingestor.read(input_path)
        profile = self.profiler.profile(data)
        frequency = self.transformer.transform(data, column)
        self.writer.write_json(profile, output_dir / "profile.json")
        frequency.to_csv(output_dir / f"frequency_{column}.csv", index=False)
        self.visualizer.create_bar_chart(frequency, output_dir / f"frequency_{column}.png")
        return {"profile": profile, "frequency_table": frequency}

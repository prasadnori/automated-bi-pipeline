# Automated BI Pipeline — Revised Research Implementation

This is a working development version intended to address the implementation gaps raised in the paper review. It is not yet a replacement for the original GitHub repository.

## What is included
- Separate components for reading data, profiling, creating a frequency table, drawing a chart, and writing a report.
- A base `DataProfiler` and a working `DataQualityProfiler` extension.
- A pipeline that accepts components through its constructor, so a component can be replaced without editing the pipeline itself.
- Automated tests and a second sample dataset with numeric and categorical columns, missing values, and a duplicate row.

## Setup
Use Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Run
```bash
python run_pipeline.py datasets/second_dataset.csv --column department --quality
```

Outputs are written to `results/`: a JSON profile, a frequency-table CSV, and a PNG chart.

## Tests
```bash
pytest -q
```

## Public second dataset: UCI Adult

The repository includes `datasets/adult_normalized.csv`, a normalized copy of the UCI Adult training data (32,561 rows, 15 columns). The source is https://archive.ics.uci.edu/dataset/2/adult. In this copy, literal `?` markers are converted to standard missing values; rows and all other values are retained. The evaluation script `experiments/evaluate_adult_dataset.py` reports the row/column counts, numeric and categorical column counts, missing values, and duplicate rows. Its recorded output is saved in `results/adult_dataset_evaluation.json`.

Run the pipeline on this dataset with:

```bash
python run_pipeline.py datasets/adult_normalized.csv --column education --output results/adult_profile_run
python experiments/evaluate_adult_dataset.py datasets/adult_normalized.csv
```

This dataset is used to check that the same general profiling code runs with a different schema. It is not used for the EasyVisa-specific employee-count rule.

## Research note
The included dataset is a small test fixture, not evidence of performance on a real business dataset. The original EasyVisa dataset should be added for the first evaluation, and a second real or well-documented public dataset should be selected before writing results. Benchmark claims should be based on recorded experiments, not assumptions.


## Dashboard with four chart types

Create a single HTML dashboard that opens in your browser:

```bash
python dashboard.py datasets/Visadataset.csv
open results/dashboard.html
```

For the included sample dataset:

```bash
python dashboard.py datasets/second_dataset.csv --bar-column department
open results/dashboard.html
```

The dashboard includes summary metrics and bar, pie, line, and donut charts. It is a static HTML report with charts embedded in the file, so the report does not need a separate local server.


## Interactive dashboard

Install dependencies and run:

```bash
pip install -r requirements.txt
python interactive_dashboard.py datasets/Visadataset.csv
open results/dashboard.html
```

This version uses Plotly. You can hover over charts for values and percentages, zoom, and use the chart toolbar. The HTML embeds the chart library, so the generated report can be opened locally without starting a server.


## Controlled comparison for the paper

Install dependencies, including Pandera for the third comparison:

```bash
pip install -r requirements.txt
```

Run this with the EasyVisa CSV (which must contain `no_of_employees`):

```bash
python experiments/compare_quality_check.py datasets/Visadataset.csv
```

The script compares the framework, plain pandas, and Pandera for the same non-negative employee-count rule. It warms up each approach, runs repeated timing measurements (10 by default), checks that all approaches return identical record IDs, and writes `results/quality_comparison.json`. Use `--repeats 30` for a longer run. Runtime is not development effort; follow `experiments/DEVELOPMENT_EFFORT_PROTOCOL.md` for a fair implementation-time study. Because the current author has already seen these implementations, a stopwatch timing by the same author is not a blinded controlled study. Do not report development-effort claims until valid observations are collected.


## Architecture and extension test (reviewer follow-up)

The implementation separates five responsibilities into modules:
1. `ingestion.py` — CSV ingestion
2. `profiling.py` — baseline and data-quality profiling
3. `transformation.py` — frequency-table transformation
4. `visualization.py` — chart generation
5. `output.py` — report output

`pipeline.py` coordinates these components through constructor injection. The new example extension in `src/automated_bi/extensions/custom_profiler.py` subclasses `DataProfiler`; it adds missing/duplicate counts and configurable numeric range rules. The test `test_extension_is_injected_without_pipeline_modification` verifies that this custom profiler can be supplied to the existing pipeline and run against a dataset with different columns, missing values, numeric fields, and a negative salary value.

Run all tests from the project root:

```bash
pytest -q
```

This test demonstrates a working extension seam and a cross-schema test fixture. It does **not** by itself establish broad generality or production-scale performance. The included second dataset is a small synthetic fixture; for the paper, add a second independent public dataset and document its provenance and characteristics.

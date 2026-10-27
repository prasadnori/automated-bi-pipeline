# Automated BI Pipeline: Reproducible Research Package

This repository contains a Python prototype for reusable exploratory data analysis (EDA) and business-intelligence-style dashboard output. It separates ingestion, profiling, transformation, visualization, and output, and allows a custom profiler to be injected into the pipeline.

## What is included

- `src/automated_bi/`: pipeline components and the custom data-quality profiler extension.
- `tests/`: automated tests for the pipeline, extension behavior, datasets, and dashboard.
- `datasets/winequality_red.csv`: red Wine Quality dataset used for the dashboard example.
- `datasets/second_dataset.csv`: small synthetic fixture used to test mixed column types, missing values, and extension behavior. It is a test fixture, not an independent real-world benchmark.
- `experiments/compare_quality_check.py`: correctness and runtime comparison for one non-negative employee-count rule.
- `experiments/DEVELOPMENT_EFFORT_PROTOCOL.md`: protocol for a future development-effort study. Its results table is intentionally unfilled; no development-effort result is claimed.
- `dashboard.py` and `interactive_dashboard.py`: static and interactive dashboard generators.
- `results/wine_quality_dashboard.html`: example interactive dashboard output.

## Requirements and setup

Use Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate     # Windows
python -m pip install -r requirements.txt
```

## Run the pipeline

```bash
python run_pipeline.py datasets/second_dataset.csv --column department --quality
```

Example using the Wine Quality data:

```bash
python run_pipeline.py datasets/winequality_red.csv --column quality --quality --rule-column quality --min 0 --max 10
```

## Generate dashboards

```bash
python dashboard.py datasets/second_dataset.csv --bar-column department
python interactive_dashboard.py datasets/winequality_red.csv --category quality --measure alcohol --output results/wine_quality_dashboard.html
```

Open `results/wine_quality_dashboard.html` in a browser. The interactive dashboard loads Plotly from a CDN, so an internet connection is needed for its interactive charts. The dashboard summarizes records, columns, missing values, and duplicates, and provides category charts and numeric distributions. Category selections can filter the linked charts; use Reset filters to clear selections.

## Run tests

From the repository root:

```bash
pytest -q
```

Record the Python version and test output when reproducing results. Tests establish the behavior covered by the test suite; they do not by themselves establish production readiness, scalability, or general performance.

## Runtime comparison

The comparison script checks one custom rule (`no_of_employees >= 0`) across the framework, pandas, and Pandera. It expects an EasyVisa CSV with a `no_of_employees` column:

```bash
python experiments/compare_quality_check.py /path/to/Visadataset.csv --repeats 30
```

The script verifies matching flagged record IDs and measures runtime. In the reported run on a 25,480-row EasyVisa dataset, all three approaches identified 33 invalid records; median runtimes were 19.634 ms for the framework, 0.132 ms for pandas, and 3.952 ms for Pandera. These are results from the reported run, not a guarantee that another machine will produce identical timings. Direct pandas was fastest in this single-rule test. Runtime is not development effort.

## Dataset availability and reproducibility limitations

The Wine Quality CSV and the synthetic test fixture are included. The EasyVisa and Adult Census Income datasets used in the manuscript are not included in this package. Obtain them from their original sources and follow the same preprocessing described in the paper before attempting to reproduce those results. In particular, Adult Census Income missing-value counts depend on normalizing `?` values to missing values.

Because the EasyVisa and Adult datasets and a single end-to-end reproduction script are not bundled here, this repository does **not** currently reproduce every dataset-level result from the manuscript from a fresh checkout alone. The manuscript should state this limitation accurately unless the missing materials and preprocessing instructions are added.

## Development-effort study

No controlled development-effort results are reported. `experiments/DEVELOPMENT_EFFORT_PROTOCOL.md` describes a proposed procedure; its `TBD` fields are intentionally unfilled. Do not treat runtime results as evidence of reduced coding effort.

## Scope

This is a research prototype for structured tabular data. The current evaluation does not establish distributed processing, production-scale throughput, or superiority over dedicated EDA tools. Claims should be limited to the tested component structure, extension behavior, datasets, and checks.

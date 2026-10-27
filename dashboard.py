import argparse
import base64
import io
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from html import escape

def fig_to_data_uri(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")

def categorical_column(data, preferred=None):
    if preferred and preferred in data.columns:
        return preferred
    cols = list(data.select_dtypes(include=["object", "category", "bool"]).columns)
    return cols[0] if cols else data.columns[0]

def make_dashboard(csv_path, output_path, bar_column=None):
    data = pd.read_csv(csv_path)
    if data.empty:
        raise ValueError("The input CSV has no rows.")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cat_cols = list(data.select_dtypes(include=["object", "category", "bool"]).columns)
    num_cols = list(data.select_dtypes(include="number").columns)
    bar_col = categorical_column(data, bar_column)
    pie_col = "case_status" if "case_status" in data.columns else bar_col
    donut_col = "continent" if "continent" in data.columns else (cat_cols[1] if len(cat_cols) > 1 else pie_col)

    # Bar chart: most common values in selected category
    counts = data[bar_col].fillna("(Missing)").astype(str).value_counts().head(12)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    counts.sort_values().plot(kind="barh", ax=ax)
    ax.set_title(f"Records by {bar_col}")
    ax.set_xlabel("Number of records")
    ax.set_ylabel(bar_col)
    bar_uri = fig_to_data_uri(fig)

    # Pie chart: case status when available; otherwise selected category
    pie_counts = data[pie_col].fillna("(Missing)").astype(str).value_counts().head(8)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.pie(pie_counts.values, labels=pie_counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title(f"{pie_col}: share of records")
    pie_uri = fig_to_data_uri(fig)

    # Line chart: numeric distribution grouped into bins, or row counts if no numeric data
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    if num_cols:
        line_col = "prevailing_wage" if "prevailing_wage" in num_cols else num_cols[0]
        values = pd.to_numeric(data[line_col], errors="coerce").dropna()
        if len(values) and values.nunique() > 1:
            bin_count = min(12, max(5, int(values.nunique() ** 0.5)))
            hist, edges = __import__("numpy").histogram(values, bins=bin_count)
            centers = (edges[:-1] + edges[1:]) / 2
            ax.plot(centers, hist, marker="o")
            ax.set_xlabel(line_col + " (bin midpoint)")
            ax.set_ylabel("Number of records")
            ax.set_title(f"Distribution of {line_col}")
        else:
            ax.text(0.5, 0.5, "Not enough numeric variation for a line chart", ha="center", va="center")
            ax.set_axis_off()
    else:
        row_counts = data[bar_col].fillna("(Missing)").astype(str).value_counts().sort_index()
        ax.plot(row_counts.index, row_counts.values, marker="o")
        ax.set_title(f"Counts by {bar_col}")
        ax.set_ylabel("Number of records")
        ax.tick_params(axis="x", rotation=35)
    line_uri = fig_to_data_uri(fig)

    # Donut chart: category shares
    donut_counts = data[donut_col].fillna("(Missing)").astype(str).value_counts().head(8)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.pie(donut_counts.values, labels=donut_counts.index, autopct="%1.1f%%",
           startangle=90, wedgeprops={"width": 0.42})
    ax.set_title(f"{donut_col}: share of records")
    donut_uri = fig_to_data_uri(fig)

    missing_cells = int(data.isna().sum().sum())
    duplicate_rows = int(data.duplicated().sum())
    cards = [
        ("Rows", f"{len(data):,}"),
        ("Columns", f"{len(data.columns):,}"),
        ("Missing cells", f"{missing_cells:,}"),
        ("Duplicate rows", f"{duplicate_rows:,}"),
    ]
    card_html = "".join(
        f'<div class="metric"><div class="metric-label">{escape(label)}</div><div class="metric-value">{value}</div></div>'
        for label, value in cards
    )
    line_col_label = "prevailing_wage" if "prevailing_wage" in num_cols else (num_cols[0] if num_cols else bar_col)
    chart_html = "".join(
        f'<section class="panel"><h2>{escape(title)}</h2><img alt="{escape(title)}" src="{uri}"></section>'
        for title, uri in [
            (f"Bar chart — {bar_col}", bar_uri),
            (f"Pie chart — {pie_col}", pie_uri),
            (f"Line chart — {line_col_label}", line_uri),
            (f"Donut chart — {donut_col}", donut_uri),
        ]
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Automated BI Dashboard</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#f4f6f8;color:#202833;font-family:Arial,Helvetica,sans-serif}}
header{{padding:26px 32px;background:#172b4d;color:white}} header h1{{margin:0 0 8px;font-size:26px}}
header p{{margin:0;color:#dbe5f4}} main{{max-width:1200px;margin:24px auto;padding:0 18px}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}}
.metric,.panel{{background:white;border:1px solid #e1e6ed;border-radius:12px;box-shadow:0 2px 8px #172b4d0d}}
.metric{{padding:18px}} .metric-label{{font-size:13px;color:#657286}} .metric-value{{font-size:28px;font-weight:700;margin-top:8px}}
.charts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}
.panel{{padding:16px;min-width:0}} .panel h2{{font-size:16px;margin:0 0 10px}} .panel img{{width:100%;height:auto;display:block}}
footer{{color:#657286;font-size:12px;padding:24px 0}}
@media(max-width:760px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}.charts{{grid-template-columns:1fr}} header{{padding:22px}}}}
</style></head><body>
<header><h1>Automated BI Dashboard</h1><p>Dataset: {escape(Path(csv_path).name)} · Automatically generated summary and charts</p></header>
<main><div class="metrics">{card_html}</div><div class="charts">{chart_html}</div>
<footer>Charts are generated from the supplied CSV. Review data-quality findings before making business decisions.</footer></main></body></html>"""
    output_path.write_text(document, encoding="utf-8")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Create a browser-based dashboard from a CSV file.")
    parser.add_argument("csv", help="Input CSV path")
    parser.add_argument("--output", default="results/dashboard.html", help="HTML output path")
    parser.add_argument("--bar-column", default=None, help="Categorical column for the bar chart")
    args = parser.parse_args()
    path = make_dashboard(args.csv, args.output, args.bar_column)
    print(f"Dashboard created: {path}")

if __name__ == "__main__":
    main()

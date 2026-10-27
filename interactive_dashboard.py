import argparse
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def choose_category(data, preferred=None):
    if preferred and preferred in data.columns:
        return preferred
    candidates = [c for c in data.select_dtypes(include=["object", "category", "bool"]).columns
                  if c.lower() not in {"case_id", "id", "record_id"}]
    return candidates[0] if candidates else data.columns[0]


def build_dashboard(csv_path, output_path, category=None):
    import json
    data = pd.read_csv(csv_path)
    if data.empty:
        raise ValueError("The input CSV has no rows.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cat = choose_category(data, category)
    status = "case_status" if "case_status" in data.columns else cat
    continent = "continent" if "continent" in data.columns else cat
    wage = "prevailing_wage" if "prevailing_wage" in data.columns else next(
        iter(data.select_dtypes(include="number").columns), None
    )

    # Convert CSV rows to browser-safe JSON records. Missing values become null.
    clean_data = data.where(pd.notna(data), None)
    records = clean_data.to_dict(orient="records")
    records_json = json.dumps(records, default=str).replace("</", "<\\/")

    missing = int(data.isna().sum().sum())
    duplicates = int(data.duplicated().sum())
    total = len(data)
    certified_rate = None
    denied_rate = None
    if status in data.columns:
        norm = data[status].astype("string").str.lower()
        if (norm == "certified").any() or (norm == "denied").any():
            certified_rate = 100 * (norm == "certified").sum() / total
            denied_rate = 100 * (norm == "denied").sum() / total

    metrics = [
        ("Total applications", f"{total:,}"),
        ("Columns", f"{len(data.columns):,}"),
        ("Missing cells", f"{missing:,}"),
        ("Duplicate rows", f"{duplicates:,}"),
    ]
    if certified_rate is not None:
        metrics.append(("Certified", f"{certified_rate:.1f}%"))
    if denied_rate is not None:
        metrics.append(("Denied", f"{denied_rate:.1f}%"))
    metric_html = "".join(
        f'<div class="metric"><span>{label}</span><strong>{value}</strong></div>'
        for label, value in metrics
    )

    # Values are used by the browser to redraw all charts after each selection.
    columns_json = json.dumps(list(data.columns))
    config_json = json.dumps({"category": cat, "status": status, "continent": continent, "wage": wage})

    html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Interactive Automated BI Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#f4f6f9;color:#202b3c;font-family:Arial,Helvetica,sans-serif}}
header{{padding:24px 30px;background:#172b4d;color:white}}header h1{{margin:0 0 7px;font-size:26px}}header p{{margin:0;color:#dce6f5}}
main{{max-width:1440px;margin:22px auto;padding:0 18px}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;margin-bottom:18px}}
.metric{{background:#fff;border:1px solid #e0e6ef;border-radius:10px;padding:16px;box-shadow:0 2px 8px #172b4d0a}}
.metric span{{display:block;font-size:12px;color:#69778b;margin-bottom:8px}}.metric strong{{font-size:24px}}
.toolbar{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px;background:#fff;padding:14px;border:1px solid #e0e6ef;border-radius:10px}}
button{{border:0;border-radius:7px;padding:10px 15px;background:#1769aa;color:white;font-weight:600;cursor:pointer}}button:hover{{background:#10558d}}
#filter-status{{color:#56657a;font-size:14px}}.charts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}
.chart{{background:white;border:1px solid #e0e6ef;border-radius:12px;padding:8px;box-shadow:0 2px 8px #172b4d0a;min-width:0}}
.chart > div{{width:100%;height:390px}}footer{{padding:20px 0;color:#657286;font-size:12px}}
@media(max-width:760px){{header{{padding:20px}}main{{padding:0 8px}}.charts{{grid-template-columns:1fr}}.chart > div{{height:350px}}.metric strong{{font-size:20px}}}}
</style></head><body>
<header><h1>Automated BI Dashboard</h1><p>Dataset: {Path(csv_path).name} · Click a bar or pie/donut segment to filter all charts. Click the selection again or use Reset filters to clear.</p></header>
<main><section class="metrics">{metric_html}</section>
<section class="toolbar"><button id="reset-filters">Reset filters</button><span id="filter-status">Showing all {total:,} applications.</span></section>
<section class="charts">
<div class="chart"><div id="bar-chart"></div></div>
<div class="chart"><div id="pie-chart"></div></div>
<div class="chart"><div id="line-chart"></div></div>
<div class="chart"><div id="donut-chart"></div></div>
</section>
<footer>Click a category in the bar chart or an outcome/category slice in the pie or donut chart to filter the other charts. Numerical distribution shows a distribution, not a trend over time. Review data-quality findings before making decisions.</footer>
</main>
<script>
const ALL_ROWS = {records_json};
const CONFIG = {config_json};
const COLORS = {{blue:'#2878b5',orange:'#f28e2b',green:'#2ca25f',red:'#d9534f'}};
let activeFilter = null; // {{column, value}}

function valueOf(row, col) {{
  const value = row[col];
  return value === null || value === undefined || value === '' ? '(Missing)' : String(value);
}}
function filteredRows() {{
  if (!activeFilter) return ALL_ROWS;
  return ALL_ROWS.filter(row => valueOf(row, activeFilter.column) === activeFilter.value);
}}
function countBy(rows, col, limit=12) {{
  const counts = new Map();
  rows.forEach(row => {{
    const key = valueOf(row, col);
    counts.set(key, (counts.get(key) || 0) + 1);
  }});
  return [...counts.entries()].sort((a,b) => b[1]-a[1]).slice(0,limit);
}}
function commonLayout(title) {{
  return {{
    title:{{text:title,font:{{size:16}}}},
    margin:{{l:55,r:20,t:55,b:65}},
    paper_bgcolor:'#ffffff',plot_bgcolor:'#ffffff',
    font:{{family:'Arial, sans-serif',color:'#27364b'}},
    clickmode:'event+select',
    showlegend:false,
    autosize:true
  }};
}}
function handleCategoryClick(column, value) {{
  if (activeFilter && activeFilter.column === column && activeFilter.value === value) {{
    activeFilter = null;
  }} else {{
    activeFilter = {{column, value}};
  }}
  renderAll();
}}
function renderAll() {{
  const rows = filteredRows();
  document.getElementById('filter-status').textContent = activeFilter
    ? `Filtered to ${{activeFilter.column}} = ${{activeFilter.value}} · ${{rows.length.toLocaleString()}} applications. Click the selected value again or reset to clear.`
    : `Showing all ${{rows.length.toLocaleString()}} applications.`;

  const catCounts = countBy(rows, CONFIG.category, 12).reverse();
  Plotly.react('bar-chart', [{{
    type:'bar',orientation:'h',x:catCounts.map(x=>x[1]),y:catCounts.map(x=>x[0]),
    marker:{{color:catCounts.map(x => activeFilter && activeFilter.column===CONFIG.category && activeFilter.value===x[0] ? COLORS.orange : COLORS.blue)}},
    customdata:catCounts.map(x=>x[0]),hovertemplate:`${{CONFIG.category}}: %{{y}}<br>Applications: %{{x:,}}<extra>Click to filter</extra>`
  }}], {{...commonLayout(`Applications by ${{CONFIG.category}}`),xaxis:{{title:'Applications'}},yaxis:{{title:CONFIG.category,automargin:true}}}}, {{responsive:true,displaylogo:false}});

  const statusCounts = countBy(rows, CONFIG.status, 10);
  Plotly.react('pie-chart', [{{
    type:'pie',labels:statusCounts.map(x=>x[0]),values:statusCounts.map(x=>x[1]),
    textinfo:'percent',textposition:'inside',sort:false,
    marker:{{line:{{color:'#ffffff',width:2}}}},
    hovertemplate:'%{{label}}<br>%{{value:,}} applications<br>%{{percent}}<extra>Click to filter</extra>'
  }}], {{...commonLayout(`Application outcomes (${{
    CONFIG.status
  }})`),showlegend:true,legend:{{orientation:'h',y:-0.15}},margin:{{l:20,r:20,t:55,b:60}}}}, {{responsive:true,displaylogo:false}});

  if (CONFIG.wage) {{
    const nums = rows.map(r=>Number(r[CONFIG.wage])).filter(v=>Number.isFinite(v));
    Plotly.react('line-chart', [{{
      type:'histogram',x:nums,nbinsx:25,marker:{{color:COLORS.green}},
      hovertemplate:`${{CONFIG.wage}} range: %{{x}}<br>Applications: %{{y:,}}<extra></extra>`
    }}], {{...commonLayout(`Distribution of ${{CONFIG.wage}}`),xaxis:{{title:CONFIG.wage}},yaxis:{{title:'Applications'}}}}, {{responsive:true,displaylogo:false}});
  }} else {{
    Plotly.react('line-chart', [{{
      type:'scatter',mode:'lines+markers',x:catCounts.map(x=>x[0]),y:catCounts.map(x=>x[1]),
      line:{{color:COLORS.green}},marker:{{size:8}}
    }}], {{...commonLayout('Counts by category'),xaxis:{{title:CONFIG.category}},yaxis:{{title:'Applications'}}}}, {{responsive:true,displaylogo:false}});
  }}

  const continentCounts = countBy(rows, CONFIG.continent, 10);
  Plotly.react('donut-chart', [{{
    type:'pie',labels:continentCounts.map(x=>x[0]),values:continentCounts.map(x=>x[1]),
    hole:0.58,textinfo:'percent',textposition:'inside',sort:false,
    marker:{{line:{{color:'#ffffff',width:2}}}},
    hovertemplate:'%{{label}}<br>%{{value:,}} applications<br>%{{percent}}<extra>Click to filter</extra>'
  }}], {{...commonLayout(`Applications by ${{CONFIG.continent}}`),showlegend:true,legend:{{orientation:'h',y:-0.15}},margin:{{l:20,r:20,t:55,b:60}}}}, {{responsive:true,displaylogo:false}});

  document.getElementById('bar-chart').on('plotly_click', event => {{
    const point = event.points && event.points[0];
    if (point) handleCategoryClick(CONFIG.category, String(point.y));
  }});
  document.getElementById('pie-chart').on('plotly_click', event => {{
    const point = event.points && event.points[0];
    if (point) handleCategoryClick(CONFIG.status, String(point.label));
  }});
  document.getElementById('donut-chart').on('plotly_click', event => {{
    const point = event.points && event.points[0];
    if (point) handleCategoryClick(CONFIG.continent, String(point.label));
  }});
}}
document.getElementById('reset-filters').addEventListener('click', () => {{ activeFilter=null; renderAll(); }});
renderAll();
</script></body></html>"""
    output_path.write_text(html_doc, encoding="utf-8")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Create an interactive browser dashboard from a CSV.")
    parser.add_argument("csv", help="Input CSV path")
    parser.add_argument("--output", default="results/dashboard.html", help="HTML output path")
    parser.add_argument("--category", default=None, help="Categorical column for the bar chart")
    args = parser.parse_args()
    result = build_dashboard(args.csv, args.output, args.category)
    print(f"Interactive dashboard created: {result}")

if __name__ == "__main__":
    main()

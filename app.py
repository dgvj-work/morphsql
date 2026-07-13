"""
MigrationIQ / SQLShift AI — Hugging Face Space Demo

An interactive migration intelligence platform for data warehouse modernization.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import gradio as gr
import plotly.graph_objects as go

from sqlshift import __product_name__, __version__
from sqlshift.lineage.builder import build_lineage_graph, format_lineage_tree
from sqlshift.models import Dialect, MigrationObject, ObjectType
from sqlshift.pipeline import MigrationPipeline
from sqlshift.translator.engine import translate_sql
from sqlshift.validation.reconciliation import generate_incremental_strategy

EXAMPLE_SQL = """-- Vertica stored procedure: customer daily metrics
CREATE OR REPLACE PROCEDURE SP_BUILD_CUSTOMER_DAILY(load_date DATE) AS $$
BEGIN
    CREATE LOCAL TEMP TABLE tmp_txns ON COMMIT PRESERVE ROWS AS
    SELECT customer_id, order_id, order_amount,
           ZEROIFNULL(discount_amount) AS discount_amount
    FROM staging.customer_transactions
    WHERE order_date = load_date;

    DELETE FROM analytics.customer_daily WHERE activity_date = load_date;

    INSERT INTO analytics.customer_daily
    SELECT customer_id, load_date,
           COUNT(DISTINCT order_id) AS order_count,
           SUM(order_amount) AS total_spend,
           CASE WHEN COUNT(*) >= 5 AND SUM(order_amount) > 500
                THEN 'HIGH_VALUE' ELSE 'STANDARD' END AS segment
    FROM tmp_txns GROUP BY customer_id;
END; $$;"""

EXAMPLES_DIR = Path(__file__).parent / "examples" / "vertica_legacy"


def analyze_sql(sql: str, source: str, target: str) -> tuple[str, str, go.Figure | None]:
    """Analyze a single SQL input."""
    if not sql.strip():
        return "Please enter SQL to analyze.", "", None

    source_d = Dialect(source)
    target_d = Dialect(target)

    obj = MigrationObject(
        name="USER_INPUT",
        object_type=ObjectType.SQL_SCRIPT,
        source_sql=sql,
    )

    pipeline = MigrationPipeline(source=source_d, target=target_d)
    from sqlshift.risk.scorer import score_object, extract_business_rules
    from sqlshift.parser.sql_parser import count_sql_complexity, detect_unsupported_features

    obj = score_object(obj, source_d, target_d)
    obj.business_rules = extract_business_rules(sql)
    complexity = count_sql_complexity(sql, source_d)
    unsupported = detect_unsupported_features(sql, source_d, target_d)
    incremental = generate_incremental_strategy(sql)

    summary = f"""## Migration Assessment: USER_INPUT

| Metric | Value |
|--------|-------|
| **Complexity Score** | {obj.complexity_score}/100 |
| **Risk Level** | {obj.risk_level.value.upper()} |
| **Migration Category** | {obj.migration_category.value.replace('_', ' ')} |
| **Lines of SQL** | {complexity.get('lines', 0)} |
| **CTEs** | {complexity.get('ctes', 0)} |
| **Joins** | {complexity.get('joins', 0)} |
| **Temp Tables** | {complexity.get('temp_tables', 0)} |
| **Dynamic SQL** | {complexity.get('dynamic_sql', 0)} |
| **Window Functions** | {complexity.get('window_functions', 0)} |

### Risk Factors
{chr(10).join(f'- {rf.description} (+{rf.score})' for rf in obj.risk_factors) or '- None detected'}

### Unsupported Features
{chr(10).join(f'- {f}' for f in unsupported) or '- None detected'}

### Incremental Strategy Recommendation
{chr(10).join(f'- **{k}**: {v}' for k, v in incremental.items())}
"""

    details = ""
    if obj.business_rules:
        details += "### Business Rules Extracted\n" + "\n".join(obj.business_rules) + "\n\n"

    fig = _risk_gauge(obj.complexity_score)
    return summary, details, fig


def convert_sql(sql: str, source: str, target: str) -> tuple[str, str]:
    """Convert SQL between dialects."""
    if not sql.strip():
        return "Please enter SQL to convert.", ""

    source_d = Dialect(source)
    target_d = Dialect(target if target != "dbt-snowflake" else "snowflake")

    translated, confidence, auto_converted, requires_review = translate_sql(sql, source_d, target_d)

    meta = f"""### Conversion Report
- **Confidence**: {confidence:.0f}%
- **Auto-converted**: {', '.join(auto_converted[:8]) or 'N/A'}
- **Requires review**: {', '.join(requires_review[:8]) or 'None'}
"""
    return translated, meta


def analyze_repository(source: str, target: str) -> tuple[str, str, go.Figure | None, str]:
    """Analyze the example Vertica legacy repository."""
    source_d = Dialect(source)
    target_d = Dialect(target if target != "dbt-snowflake" else "snowflake")

    if not EXAMPLES_DIR.exists():
        return "Example repository not found.", "", None, ""

    pipeline = MigrationPipeline(source=source_d, target=target_d)
    report = pipeline.analyze(str(EXAMPLES_DIR))
    report = pipeline.convert(report)
    report = pipeline.validate(report)

    d = report.dashboard
    summary = f"""## Repository Migration Dashboard

**Path**: `{EXAMPLES_DIR.name}/` | **{source.upper()} → {target.upper()}**

| Metric | Count |
|--------|-------|
| Total Objects | {d.total_objects} |
| Auto-Migratable | {d.auto_migratable} |
| Requires Review | {d.requires_review} |
| Manual Redesign | {d.requires_redesign} |
| Retire/Consolidate | {d.recommended_retirement} |
| Migration Risk Score | {d.migration_risk_score:.0f}/100 |
| Conversion Complete | {d.conversion_completed_pct:.0f}% |
| Validation Passed | {d.validation_passed_pct:.0f}% |
| Lineage Coverage | {d.lineage_coverage_pct:.0f}% |
| Est. Annual Savings | ${d.estimated_annual_savings_usd[0]:,.0f} – ${d.estimated_annual_savings_usd[1]:,.0f} |
"""

    objects_table = "### Object Assessment\n\n"
    objects_table += "| Object | Type | Complexity | Risk | Confidence |\n"
    objects_table += "|--------|------|-----------|------|------------|\n"
    for obj in report.objects:
        objects_table += (
            f"| {obj.name} | {obj.object_type.value} | "
            f"{obj.complexity_score}/100 | {obj.risk_level.value} | "
            f"{obj.conversion_confidence:.0f}% |\n"
        )

    # Lineage
    graph = build_lineage_graph(report.objects, source_d)
    lineage_text = ""
    if report.objects:
        root = report.objects[0].name
        lineage_text = f"### Lineage Tree\n```\n{format_lineage_tree(graph, root)}\n```"

    # Chart
    fig = _dashboard_chart(report)

    # JSON export
    export = json.dumps({
        "dashboard": d.model_dump(),
        "objects": [
            {
                "name": o.name,
                "type": o.object_type.value,
                "complexity": o.complexity_score,
                "risk": o.risk_level.value,
                "confidence": o.conversion_confidence,
                "category": o.migration_category.value,
            }
            for o in report.objects
        ],
    }, indent=2)

    return summary, objects_table + "\n" + lineage_text, fig, export


def convert_and_show(sql: str, source: str, target: str) -> str:
    translated, meta = convert_sql(sql, source, target)
    return f"{meta}\n\n### Converted SQL\n```sql\n{translated}\n```"


def _risk_gauge(score: int) -> go.Figure:
    color = "green" if score < 30 else "orange" if score < 60 else "red"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Migration Risk Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 30], "color": "#d4edda"},
                {"range": [30, 60], "color": "#fff3cd"},
                {"range": [60, 100], "color": "#f8d7da"},
            ],
        },
    ))
    fig.update_layout(height=250, margin=dict(t=50, b=20, l=30, r=30))
    return fig


def _dashboard_chart(report) -> go.Figure:
    d = report.dashboard
    fig = go.Figure(data=[
        go.Bar(
            x=["Auto-Migrate", "Review", "Redesign", "Retire"],
            y=[d.auto_migratable, d.requires_review, d.requires_redesign, d.recommended_retirement],
            marker_color=["#4ade80", "#facc15", "#f87171", "#94a3b8"],
        )
    ])
    fig.update_layout(
        title="Migration Object Distribution",
        height=300,
        margin=dict(t=40, b=30),
    )
    return fig


# Build Gradio interface
with gr.Blocks(
    title=f"{__product_name__} — Migration Intelligence",
) as demo:
    gr.Markdown(f"""
# 🔄 {__product_name__} — AI Data Platform Migration Copilot

**Discover, translate, validate, and optimize** enterprise SQL workloads across cloud data warehouses.

> Upload a legacy data repository and receive a complete, validated migration package — not merely converted SQL.

**Supported**: Vertica → Snowflake/dbt | Oracle → Snowflake | Redshift → Snowflake

*Version {__version__} | Open-source migration intelligence*
    """)

    with gr.Tabs():
        with gr.Tab("🔍 Analyze SQL"):
            with gr.Row():
                with gr.Column(scale=2):
                    sql_input = gr.Textbox(
                        label="SQL Input",
                        lines=15,
                        value=EXAMPLE_SQL,
                        placeholder="Paste your legacy SQL here...",
                    )
                with gr.Column(scale=1):
                    source_dd = gr.Dropdown(
                        ["vertica", "oracle", "redshift", "bigquery"],
                        value="vertica", label="Source Platform",
                    )
                    target_dd = gr.Dropdown(
                        ["snowflake", "dbt-snowflake", "bigquery"],
                        value="snowflake", label="Target Platform",
                    )
                    analyze_btn = gr.Button("Analyze Migration Risk", variant="primary")
                    convert_btn = gr.Button("Convert SQL", variant="secondary")

            with gr.Row():
                analyze_output = gr.Markdown(label="Assessment")
                risk_chart = gr.Plot(label="Risk Score")

            details_output = gr.Markdown(label="Details")

            analyze_btn.click(
                analyze_sql,
                [sql_input, source_dd, target_dd],
                [analyze_output, details_output, risk_chart],
            )
            convert_btn.click(
                convert_and_show,
                [sql_input, source_dd, target_dd],
                [analyze_output],
            )

        with gr.Tab("📦 Repository Analysis"):
            gr.Markdown("Analyze the bundled **Vertica legacy repository** example (procedures, views, tables, queries).")
            with gr.Row():
                repo_source = gr.Dropdown(["vertica", "oracle"], value="vertica", label="Source")
                repo_target = gr.Dropdown(["snowflake", "dbt-snowflake"], value="snowflake", label="Target")
                repo_btn = gr.Button("Analyze Repository", variant="primary")

            with gr.Row():
                repo_summary = gr.Markdown()
                repo_chart = gr.Plot()

            repo_details = gr.Markdown()
            repo_json = gr.Code(label="Export JSON", language="json")

            repo_btn.click(
                analyze_repository,
                [repo_source, repo_target],
                [repo_summary, repo_details, repo_chart, repo_json],
            )

        with gr.Tab("📚 Features"):
            gr.Markdown("""
## MigrationIQ Capabilities

| Feature | Description |
|---------|-------------|
| **Repository Scanner** | Analyze entire SQL repos, zip files, dbt projects |
| **Column-Level Lineage** | Table and column dependency graphs |
| **Risk Scoring** | Complexity, unsupported syntax, dependency risk |
| **Hybrid Translation** | Rule-based + sqlglot + LLM-ready architecture |
| **dbt Decomposition** | Stored procedures → staging/intermediate/mart models |
| **Semantic Validation** | Row count, checksum, null rate reconciliation |
| **Behavior Intelligence** | Platform-specific NULL, timezone, merge differences |
| **Incremental Strategy** | Detect legacy patterns → recommend dbt strategies |
| **HTML Reports** | Review-ready migration assessment reports |
| **CLI & Python SDK** | `pip install sqlshift-ai` |

### CLI Quick Start
```bash
pip install sqlshift-ai

# Analyze a repository
sqlshift analyze ./legacy_sql --source vertica --target snowflake

# Convert with dbt generation
sqlshift convert ./legacy_sql --source vertica --target dbt-snowflake --generate-dbt

# Full migration pipeline
sqlshift migrate ./legacy_sql --output migration-package
```
            """)

    gr.Markdown("---\n*Built with ❤️ for the data engineering community | [GitHub](https://github.com/migrationiq/sqlshift-ai) | [PyPI](https://pypi.org/project/sqlshift-ai/)*")


if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(primary_hue="cyan"),
        css=".gradio-container {max-width: 1100px !important}",
    )

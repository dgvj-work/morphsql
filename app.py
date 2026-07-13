"""SQLShiftAI — Hugging Face Space: viral SQL Migration Agent playground."""

from __future__ import annotations

import gradio as gr

from sqlshift import __product_name__, __version__
from sqlshift.eval.pairs import ensure_pairs_file
from demo.handlers import (
    FEATURE_SQL_PATH,
    HERO_EXAMPLE,
    PLAYGROUND_EXAMPLES,
    analyze_sql_object,
    copilot_chat,
    get_leaderboard_md,
    get_sample_workbench,
    report_to_context,
    run_behavior_rag,
    run_eval_suite,
    run_feature_migration,
    run_hero_agent,
    run_migration_workbench,
    submit_eval_score,
)
from demo.theme import CUSTOM_CSS, build_theme

SOURCE_CHOICES = ["vertica", "oracle", "redshift", "bigquery", "snowflake"]
TARGET_CHOICES = ["snowflake", "dbt-snowflake", "bigquery"]

EXAMPLE_SQL = """CREATE OR REPLACE PROCEDURE SP_BUILD_CUSTOMER_DAILY(load_date DATE)
AS $$
BEGIN
    CREATE LOCAL TEMP TABLE tmp_txns ON COMMIT PRESERVE ROWS AS
    SELECT customer_id, order_id, order_amount,
           ZEROIFNULL(discount_amount) AS discount_amount
    FROM staging.customer_transactions
    WHERE order_date = load_date;
    INSERT INTO analytics.customer_daily
    SELECT customer_id, load_date, COUNT(DISTINCT order_id),
           SUM(order_amount - ZEROIFNULL(discount_amount))
    FROM tmp_txns GROUP BY customer_id, load_date;
END;
$$;"""

# Fast cold start: only light hero precompute (no full workbench scan)
ensure_pairs_file()
_HERO = run_hero_agent(HERO_EXAMPLE, "vertica", "snowflake")
_FEATURE_SRC = (
    FEATURE_SQL_PATH.read_text(encoding="utf-8") if FEATURE_SQL_PATH.exists() else HERO_EXAMPLE
)

# Lazy caches for Advanced lab
_SAMPLE = None
_SAMPLE_INSPECTOR = None
_FEATURE = None


def _sample():
    global _SAMPLE
    if _SAMPLE is None:
        _SAMPLE = get_sample_workbench()
    return _SAMPLE


def _inspector():
    global _SAMPLE_INSPECTOR
    if _SAMPLE_INSPECTOR is None:
        _SAMPLE_INSPECTOR = analyze_sql_object(EXAMPLE_SQL, "vertica", "snowflake")
    return _SAMPLE_INSPECTOR


def _feature():
    global _FEATURE
    if _FEATURE is None:
        _FEATURE = run_feature_migration("dbt-snowflake")
    return _FEATURE


def load_advanced_lab():
    """Populate Advanced lab widgets on first open (keeps Space boot fast)."""
    s = _sample()
    i = _inspector()
    f = _feature()
    return (
        report_to_context(s[11]),
        s[0],
        s[6],
        s[7],
        s[8],
        s[1],
        s[2],
        s[3],
        s[4],
        s[5],
        s[9],
        s[10],
        s[11],
        i[0],
        i[1],
        i[2],
        i[3],
        i[4],
        EXAMPLE_SQL,
        f[0],
        f[1],
        _FEATURE_SRC,
        "Advanced lab loaded · sample repo + inspector ready",
    )


def _build_demo() -> gr.Blocks:
    with gr.Blocks(title="SQLShiftAI — Convert legacy SQL in one click") as demo:
        report_state = gr.State(value=None)
        eval_state = gr.State(value={})

        gr.HTML(
            f"""
            <div class="header-block hero-viral">
                <div class="eyebrow">HUGGING FACE · SQL MIGRATION AGENT</div>
                <h1>{__product_name__}</h1>
                <p>Paste broken legacy warehouse SQL. Get Snowflake / dbt / BigQuery in one click —
                with confidence, behavior RAG, and optional dbt project emission.</p>
            </div>
            """
        )

        with gr.Tabs():
            # ========== PLAYGROUND (viral loop) ==========
            with gr.Tab("Playground"):
                gr.Markdown(
                    "**Before → After.** Click an example or paste your own. "
                    "No signup. Results appear instantly."
                )
                with gr.Row():
                    hero_source = gr.Dropdown(SOURCE_CHOICES, value="vertica", label="From", scale=1)
                    hero_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To", scale=1)
                    hero_run = gr.Button("Convert with Agent", variant="primary", scale=2)
                    hero_badge = gr.Textbox(
                        label="Score",
                        interactive=False,
                        value=_HERO[2],
                        scale=2,
                    )

                with gr.Row(equal_height=True):
                    hero_sql = gr.Code(
                        label="BEFORE · legacy SQL",
                        language="sql",
                        value=HERO_EXAMPLE,
                        lines=14,
                    )
                    hero_out = gr.Code(
                        label="AFTER · converted output",
                        language="sql",
                        lines=14,
                        interactive=False,
                        value=_HERO[1],
                    )

                with gr.Row():
                    hero_explain = gr.Markdown(value=_HERO[0])
                    hero_share = gr.Markdown(value=_HERO[3])

                gr.Examples(
                    examples=PLAYGROUND_EXAMPLES,
                    inputs=[hero_sql, hero_source, hero_target],
                    label="Try these (click → then Convert)",
                    examples_per_page=5,
                )

                hero_run.click(
                    run_hero_agent,
                    [hero_sql, hero_source, hero_target],
                    [hero_explain, hero_out, hero_badge, hero_share],
                )

            # ========== EVAL ==========
            with gr.Tab("Eval"):
                gr.Markdown(
                    "ML-style benchmark on the bundled pair dataset "
                    "(exact match · token F1 · fuzzy). Submit to the leaderboard."
                )
                with gr.Row():
                    eval_limit = gr.Slider(10, 200, value=40, step=10, label="Pairs")
                    eval_cat = gr.Dropdown(
                        ["all", "function", "date", "aggregate", "ddl", "ml_feature"],
                        value="all",
                        label="Category",
                    )
                    eval_run = gr.Button("Run eval", variant="primary")
                eval_summary = gr.Markdown("Run eval to score the hybrid translator.")
                eval_detail = gr.Markdown("")
                with gr.Row():
                    lb_name = gr.Textbox(label="Handle", value="hf-visitor")
                    lb_submit = gr.Button("Submit score")
                leaderboard_md = gr.Markdown(value=get_leaderboard_md())
                eval_run.click(
                    run_eval_suite,
                    [eval_limit, eval_cat],
                    [eval_summary, eval_detail, eval_state],
                )
                lb_submit.click(submit_eval_score, [lb_name, eval_state], [leaderboard_md])

            # ========== ADVANCED LAB (lazy) ==========
            with gr.Tab("Advanced Lab"):
                lab_status = gr.Markdown(
                    "Click **Load lab** once to hydrate workbench / inspector / ML samples "
                    "(kept lazy so the Space boots fast)."
                )
                lab_load = gr.Button("Load lab", variant="secondary")

                with gr.Tabs():
                    with gr.Tab("Behavior RAG"):
                        rag_q = gr.Textbox(
                            label="Ask about platform behavior",
                            value="How do empty strings and NULL differ on Oracle vs Snowflake?",
                            lines=2,
                        )
                        with gr.Row():
                            rag_source = gr.Dropdown(SOURCE_CHOICES, value="oracle", label="From")
                            rag_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To")
                            rag_run = gr.Button("Retrieve", variant="primary")
                        rag_out = gr.Markdown("Load lab or click Retrieve.")
                        rag_run.click(run_behavior_rag, [rag_q, rag_source, rag_target], [rag_out])

                    with gr.Tab("ML Feature SQL"):
                        feat_src = gr.Code(
                            label="Legacy feature SQL",
                            language="sql",
                            value="",
                            lines=12,
                            interactive=False,
                        )
                        feat_target = gr.Dropdown(
                            ["snowflake", "dbt-snowflake"],
                            value="dbt-snowflake",
                            label="Target",
                        )
                        feat_run = gr.Button("Migrate features", variant="primary")
                        feat_md = gr.Markdown("")
                        feat_out = gr.Code(
                            label="Migrated features / dbt mart",
                            language="sql",
                            lines=12,
                            interactive=False,
                            value="",
                        )
                        feat_run.click(run_feature_migration, [feat_target], [feat_md, feat_out])

                    with gr.Tab("Object Inspector"):
                        with gr.Row():
                            sql_input = gr.Code(label="Source SQL", language="sql", value="", lines=12)
                            with gr.Column(min_width=200):
                                obj_source = gr.Dropdown(SOURCE_CHOICES, value="vertica", label="From")
                                obj_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To")
                                obj_analyze = gr.Button("Assess & Convert", variant="primary")
                                obj_risk_badge = gr.Textbox(label="Score", interactive=False, value="")
                        obj_analysis = gr.Markdown("")
                        obj_risk_chart = gr.Plot(label="Risk")
                        obj_converted = gr.Code(
                            label="Output", language="sql", lines=10, interactive=False, value=""
                        )
                        obj_notes = gr.Markdown("")
                        obj_analyze.click(
                            analyze_sql_object,
                            [sql_input, obj_source, obj_target],
                            [obj_analysis, obj_risk_chart, obj_risk_badge, obj_converted, obj_notes],
                        )

                    with gr.Tab("Workbench"):
                        with gr.Row():
                            repo_upload = gr.File(
                                label="Zip upload", file_types=[".zip"], type="filepath"
                            )
                            use_sample = gr.Checkbox(label="Sample Vertica repo", value=True)
                        with gr.Row():
                            wb_source = gr.Dropdown(SOURCE_CHOICES, value="vertica", label="From")
                            wb_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To")
                            wb_run = gr.Button("Run scan", variant="primary")
                        wb_summary = gr.Markdown("")
                        wb_metrics = gr.Markdown("")
                        with gr.Row():
                            wb_risk = gr.Plot(label="Risk")
                            wb_dist = gr.Plot(label="Distribution")
                        wb_objects = gr.Markdown("")
                        wb_rational = gr.Markdown("")
                        wb_runbook = gr.Markdown("")
                        wb_dbt = gr.Markdown("")
                        wb_validation = gr.Markdown("")
                        wb_lineage = gr.Plot(label="Lineage")
                        wb_json = gr.Code(language="json", lines=8, label="Export", value="")
                        wb_run.click(
                            run_migration_workbench,
                            [repo_upload, use_sample, wb_source, wb_target],
                            [
                                wb_summary,
                                wb_objects,
                                wb_rational,
                                wb_runbook,
                                wb_dbt,
                                wb_validation,
                                wb_metrics,
                                wb_risk,
                                wb_dist,
                                wb_lineage,
                                wb_json,
                                report_state,
                            ],
                        )

                    with gr.Tab("Copilot"):
                        copilot_context = gr.Markdown("Load lab or run Workbench for scan context.")
                        copilot_chatbot = gr.Chatbot(
                            label="Copilot",
                            height=320,
                            value=[{
                                "role": "assistant",
                                "content": "Ask migration questions. Set HF_TOKEN for full LLM mode.",
                            }],
                        )
                        with gr.Row():
                            copilot_input = gr.Textbox(
                                label="Message",
                                placeholder="What should we migrate first?",
                                scale=4,
                            )
                            copilot_send = gr.Button("Send", variant="primary", scale=1)
                        copilot_sql = gr.Code(label="Optional SQL", language="sql", lines=4, value="")
                        with gr.Row():
                            copilot_source = gr.Dropdown(SOURCE_CHOICES, value="vertica", label="From")
                            copilot_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To")
                        report_state.change(report_to_context, [report_state], [copilot_context])
                        cin = [
                            copilot_input,
                            copilot_chatbot,
                            report_state,
                            copilot_sql,
                            copilot_source,
                            copilot_target,
                        ]
                        copilot_send.click(copilot_chat, cin, [copilot_chatbot, copilot_input])
                        copilot_input.submit(copilot_chat, cin, [copilot_chatbot, copilot_input])

                lab_load.click(
                    load_advanced_lab,
                    inputs=[],
                    outputs=[
                        copilot_context,
                        wb_summary,
                        wb_metrics,
                        wb_risk,
                        wb_dist,
                        wb_objects,
                        wb_rational,
                        wb_runbook,
                        wb_dbt,
                        wb_validation,
                        wb_lineage,
                        wb_json,
                        report_state,
                        obj_analysis,
                        obj_risk_chart,
                        obj_risk_badge,
                        obj_converted,
                        obj_notes,
                        sql_input,
                        feat_md,
                        feat_out,
                        feat_src,
                        lab_status,
                    ],
                )

        gr.Markdown(
            f"<p class='footer-viral'>{__product_name__} v{__version__} · Apache 2.0 · "
            "<a href='https://github.com/dgvj-work/sql_shift_ai'>GitHub</a> · "
            "Duplicate this Space and paste your SQL</p>"
        )

    return demo


demo = _build_demo()


if __name__ == "__main__":
    demo.launch(theme=build_theme(), css=CUSTOM_CSS)

"""MorphSQL — Hugging Face Space."""

from __future__ import annotations

import gradio as gr

from sqlshift import __product_name__, __version__
from sqlshift.ai.agent import chat_agent
from sqlshift.ai.pipeline import pipeline
from sqlshift.ai.risk_model import MODEL_PATH, train_and_save
from sqlshift.eval.pairs import ensure_pairs_file
from demo.handlers import (
    AGENT_PROMPTS,
    FEATURE_SQL_PATH,
    HERO_EXAMPLE,
    PLAYGROUND_EXAMPLE_LABELS,
    analyze_sql_object,
    get_leaderboard_md,
    get_sample_workbench,
    load_agent_example,
    load_and_convert_example,
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
SPACE_URL = "https://huggingface.co/spaces/dgvj-work/sqlshift-ai"

ensure_pairs_file()
train_and_save()  # no-op if model/risk_classifier.joblib already exists

_HERO = run_hero_agent(HERO_EXAMPLE, "vertica", "snowflake")
_RISK = pipeline("sql-risk-classification")(HERO_EXAMPLE)
_FEATURE_SRC = (
    FEATURE_SQL_PATH.read_text(encoding="utf-8") if FEATURE_SQL_PATH.exists() else HERO_EXAMPLE
)
_SAMPLE = None


def _sample():
    global _SAMPLE
    if _SAMPLE is None:
        _SAMPLE = get_sample_workbench()
    return _SAMPLE


def _build_demo() -> gr.Blocks:
    with gr.Blocks(title=f"{__product_name__} — SQL dialect converter") as demo:
        report_state = gr.State(value=None)
        eval_state = gr.State(value={})

        gr.HTML(
            f"""
            <div class="header-block hero-viral">
                <div class="eyebrow">VERTICA · ORACLE · REDSHIFT · BIGQUERY → SNOWFLAKE · DBT</div>
                <h1>{__product_name__}</h1>
                <p>Paste legacy SQL, pick a target, get Snowflake / BigQuery / dbt output with
                confidence and risk. Duplicate this Space to try your own queries.</p>
            </div>
            """
        )

        with gr.Tabs():
            # Playground first — viral BEFORE/AFTER loop
            with gr.Tab("Playground"):
                gr.Markdown(
                    "Click a preset below (or paste your own SQL), then review BEFORE → AFTER."
                )
                with gr.Row():
                    hero_source = gr.Dropdown(SOURCE_CHOICES, value="vertica", label="From")
                    hero_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To")
                    hero_run = gr.Button("Convert", variant="primary")
                    hero_badge = gr.Textbox(label="Score", value=_HERO[2], interactive=False)
                with gr.Row():
                    hero_sql = gr.Textbox(
                        label="BEFORE · legacy SQL",
                        value=HERO_EXAMPLE,
                        lines=10,
                        max_lines=24,
                    )
                    hero_out = gr.Textbox(
                        label="AFTER · converted output",
                        lines=10,
                        max_lines=24,
                        value=_HERO[1],
                    )
                hero_explain = gr.Markdown(value=_HERO[0])
                hero_share = gr.Markdown(value=_HERO[3])
                gr.Markdown("**Presets** — click once to load and convert")
                with gr.Row():
                    for i, label in enumerate(PLAYGROUND_EXAMPLE_LABELS):
                        b = gr.Button(label, size="sm")
                        b.click(
                            lambda idx=i: load_and_convert_example(idx),
                            outputs=[
                                hero_sql,
                                hero_source,
                                hero_target,
                                hero_explain,
                                hero_out,
                                hero_badge,
                                hero_share,
                            ],
                        )
                hero_run.click(
                    run_hero_agent,
                    [hero_sql, hero_source, hero_target],
                    [hero_explain, hero_out, hero_badge, hero_share],
                )

            with gr.Tab("Agent"):
                gr.Markdown(
                    "Ask MorphSQL to convert, score risk, retrieve dialect behavior notes, "
                    f"or emit dbt. Sample risk on the hero SQL: **{_RISK['label']}** "
                    f"({_RISK['score']:.2f})."
                )
                with gr.Row():
                    ag_source = gr.Dropdown(SOURCE_CHOICES, value="vertica", label="From")
                    ag_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To")
                    ag_badge = gr.Textbox(
                        label="Risk model",
                        value=f"{_RISK['label']} · {_RISK['score']:.2f}",
                        interactive=False,
                    )
                ag_sql = gr.Textbox(
                    label="SQL context",
                    value=HERO_EXAMPLE,
                    lines=8,
                    max_lines=20,
                )
                ag_chat = gr.Chatbot(
                    label="MorphSQL",
                    height=360,
                    value=[{
                        "role": "assistant",
                        "content": (
                            "Pick a preset, then send a message like "
                            "**Convert this and predict risk**."
                        ),
                    }],
                )
                with gr.Row():
                    ag_msg = gr.Textbox(
                        label="Message",
                        value="Convert this SQL and predict migration risk",
                        scale=4,
                        lines=2,
                    )
                    ag_send = gr.Button("Send", variant="primary", scale=1)
                ag_out = gr.Textbox(
                    label="Agent output (SQL / dbt)",
                    lines=10,
                    max_lines=30,
                    value=_HERO[1],
                )
                ag_send.click(
                    chat_agent,
                    [ag_msg, ag_chat, ag_sql, ag_source, ag_target],
                    [ag_chat, ag_msg, ag_out, ag_badge],
                )
                ag_msg.submit(
                    chat_agent,
                    [ag_msg, ag_chat, ag_sql, ag_source, ag_target],
                    [ag_chat, ag_msg, ag_out, ag_badge],
                )
                gr.Markdown("**Prompt presets**")
                with gr.Row():
                    for i, (prompt, _sql, _src, _tgt) in enumerate(AGENT_PROMPTS):
                        label = prompt if len(prompt) <= 40 else prompt[:39] + "…"
                        btn = gr.Button(label, size="sm")
                        btn.click(
                            lambda idx=i: load_agent_example(idx),
                            outputs=[ag_msg, ag_sql, ag_source, ag_target],
                        )

            with gr.Tab("Eval"):
                with gr.Row():
                    eval_limit = gr.Slider(10, 300, value=60, step=10, label="Pairs")
                    eval_cat = gr.Dropdown(
                        ["all", "function", "date", "aggregate", "ddl", "ml_feature"],
                        value="all",
                        label="Category",
                    )
                    eval_run = gr.Button("Run eval", variant="primary")
                eval_summary = gr.Markdown("Run eval to score conversion accuracy on the pair set.")
                eval_detail = gr.Markdown("")
                with gr.Row():
                    lb_name = gr.Textbox(label="Handle", value="hf-user")
                    lb_submit = gr.Button("Submit score")
                leaderboard_md = gr.Markdown(value=get_leaderboard_md())
                eval_run.click(
                    run_eval_suite,
                    [eval_limit, eval_cat],
                    [eval_summary, eval_detail, eval_state],
                )
                lb_submit.click(submit_eval_score, [lb_name, eval_state], [leaderboard_md])

            with gr.Tab("Lab"):
                lab_status = gr.Markdown(
                    "Load sample repo charts, RAG, and ML feature migration demos."
                )
                lab_load = gr.Button("Load lab", variant="secondary")
                with gr.Tabs():
                    with gr.Tab("RAG"):
                        rag_q = gr.Textbox(
                            value="Oracle empty string vs Snowflake NULL",
                            lines=2,
                        )
                        with gr.Row():
                            rag_source = gr.Dropdown(SOURCE_CHOICES, value="oracle", label="From")
                            rag_target = gr.Dropdown(TARGET_CHOICES, value="snowflake", label="To")
                            rag_run = gr.Button("Retrieve", variant="primary")
                        rag_out = gr.Markdown("")
                        rag_run.click(
                            run_behavior_rag,
                            [rag_q, rag_source, rag_target],
                            [rag_out],
                        )
                    with gr.Tab("ML Features"):
                        feat_src = gr.Code(language="sql", value="", lines=8)
                        feat_target = gr.Dropdown(
                            ["snowflake", "dbt-snowflake"],
                            value="dbt-snowflake",
                        )
                        feat_run = gr.Button("Migrate", variant="primary")
                        feat_md = gr.Markdown("")
                        feat_out = gr.Code(language="sql", lines=8, value="")
                        feat_run.click(
                            run_feature_migration,
                            [feat_target],
                            [feat_md, feat_out],
                        )
                    with gr.Tab("Inspector"):
                        sql_input = gr.Code(language="sql", value=HERO_EXAMPLE, lines=8)
                        with gr.Row():
                            obj_source = gr.Dropdown(SOURCE_CHOICES, value="vertica")
                            obj_target = gr.Dropdown(TARGET_CHOICES, value="snowflake")
                            obj_analyze = gr.Button("Assess", variant="primary")
                        obj_analysis = gr.Markdown("")
                        obj_risk_chart = gr.Plot()
                        obj_risk_badge = gr.Textbox(interactive=False)
                        obj_converted = gr.Code(language="sql", lines=6, value="")
                        obj_notes = gr.Markdown("")
                        obj_analyze.click(
                            analyze_sql_object,
                            [sql_input, obj_source, obj_target],
                            [
                                obj_analysis,
                                obj_risk_chart,
                                obj_risk_badge,
                                obj_converted,
                                obj_notes,
                            ],
                        )
                    with gr.Tab("Workbench"):
                        repo_upload = gr.File(file_types=[".zip"], type="filepath")
                        use_sample = gr.Checkbox(value=True, label="Sample repo")
                        with gr.Row():
                            wb_source = gr.Dropdown(SOURCE_CHOICES, value="vertica")
                            wb_target = gr.Dropdown(TARGET_CHOICES, value="snowflake")
                            wb_run = gr.Button("Scan", variant="primary")
                        wb_summary = gr.Markdown("")
                        wb_objects = gr.Markdown("")
                        wb_rational = gr.Markdown("")
                        wb_runbook = gr.Markdown("")
                        wb_dbt = gr.Markdown("")
                        wb_validation = gr.Markdown("")
                        wb_metrics = gr.Markdown("")
                        wb_risk = gr.Plot()
                        wb_dist = gr.Plot()
                        wb_lineage = gr.Plot()
                        wb_json = gr.Code(language="json", lines=5, value="")
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
                    with gr.Tab("Context"):
                        copilot_context = gr.Markdown("Load lab / run workbench for context.")

                def _load():
                    s = _sample()
                    f = run_feature_migration("dbt-snowflake")
                    return (
                        report_to_context(s[11]),
                        s[0],
                        s[1],
                        s[6],
                        s[7],
                        s[8],
                        s[9],
                        s[10],
                        s[11],
                        f[0],
                        f[1],
                        _FEATURE_SRC,
                        "Lab ready",
                    )

                lab_load.click(
                    _load,
                    outputs=[
                        copilot_context,
                        wb_summary,
                        wb_objects,
                        wb_metrics,
                        wb_risk,
                        wb_dist,
                        wb_lineage,
                        wb_json,
                        report_state,
                        feat_md,
                        feat_out,
                        feat_src,
                        lab_status,
                    ],
                )

        gr.Markdown(
            f"<p class='footer-viral'>{__product_name__} v{__version__} · "
            f"<a href='{SPACE_URL}'>Space</a> · "
            f"<a href='https://huggingface.co/dgvj-work/sqlshift-ai'>Model</a> · "
            f"<a href='https://huggingface.co/datasets/dgvj-work/vertica-snowflake-pairs'>Dataset</a> · "
            f"<a href='https://github.com/dgvj-work/sql_shift_ai'>GitHub</a> · "
            f"model file: <code>{MODEL_PATH.name}</code></p>"
        )
    return demo


demo = _build_demo()


if __name__ == "__main__":
    demo.launch(theme=build_theme(), css=CUSTOM_CSS)

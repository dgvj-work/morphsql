"""MorphSQL — Hugging Face Space (conversion-first product UI)."""

from __future__ import annotations

import gradio as gr

from sqlshift import __product_name__, __version__
from sqlshift.ai.risk_model import train_and_save
from sqlshift.eval.pairs import ensure_pairs_file
from demo.handlers import (
    HERO_EXAMPLE,
    PLAYGROUND_EXAMPLE_LABELS,
    SOURCE_DROPDOWN,
    TARGET_DROPDOWN,
    get_leaderboard_md,
    on_example_selected,
    run_behavior_rag,
    run_eval_suite,
    run_hero_agent,
    submit_eval_score,
)
from demo.theme import CUSTOM_CSS, build_theme

SPACE_URL = "https://huggingface.co/spaces/dgvj-work/sqlshift-ai"
GITHUB_URL = "https://github.com/dgvj-work/sql_shift_ai"

ensure_pairs_file()
train_and_save()

_HERO = run_hero_agent(HERO_EXAMPLE, "vertica", "pandas")


def _build_demo() -> gr.Blocks:
    with gr.Blocks(title=f"{__product_name__} — SQL converter") as demo:
        eval_state = gr.State(value={})
        eval_category = gr.State(value="all")

        gr.HTML(
            f"""
            <div class="header-block">
                <div class="eyebrow">SQL CONVERTER</div>
                <h1>{__product_name__}</h1>
                <p>Turn warehouse SQL into <strong>pandas</strong> Python, Snowflake SQL,
                BigQuery SQL, or a dbt project. One convert button. No setup.</p>
            </div>
            """
        )

        with gr.Tabs():
            with gr.Tab("Convert"):
                gr.Markdown(
                    "### How to use\n"
                    "1. Pick the **dialect your SQL is written in**.\n"
                    "2. Pick **what you want out** (pandas is the default).\n"
                    "3. Paste SQL — or choose an example — then click **Convert**."
                )

                example = gr.Dropdown(
                    choices=PLAYGROUND_EXAMPLE_LABELS,
                    value=PLAYGROUND_EXAMPLE_LABELS[0],
                    label="Load an example (optional)",
                    info="This fills the SQL, sets From/To, and converts immediately.",
                )

                with gr.Row():
                    source = gr.Dropdown(
                        choices=SOURCE_DROPDOWN,
                        value="vertica",
                        label="SQL is written for",
                        info="Dialect of the query you paste.",
                    )
                    target = gr.Dropdown(
                        choices=TARGET_DROPDOWN,
                        value="pandas",
                        label="Convert to",
                        info="pandas = Python · others = SQL or dbt files.",
                    )
                    convert_btn = gr.Button("Convert", variant="primary")

                status = gr.Textbox(
                    label="Status",
                    value=_HERO[2],
                    interactive=False,
                    max_lines=1,
                )

                with gr.Row():
                    sql_in = gr.Textbox(
                        label="Input SQL",
                        value=HERO_EXAMPLE,
                        lines=14,
                        max_lines=28,
                        placeholder="Paste a SELECT (or a procedure if converting to dbt)…",
                    )
                    sql_out = gr.Textbox(
                        label="Output",
                        value=_HERO[1],
                        lines=14,
                        max_lines=28,
                    )

                notes = gr.Markdown(value=_HERO[0])
                share = gr.Markdown(value=_HERO[3])

                example.change(
                    on_example_selected,
                    inputs=[example],
                    outputs=[sql_in, source, target, notes, sql_out, status, share],
                )
                convert_btn.click(
                    run_hero_agent,
                    inputs=[sql_in, source, target],
                    outputs=[notes, sql_out, status, share],
                )
                sql_in.submit(
                    run_hero_agent,
                    inputs=[sql_in, source, target],
                    outputs=[notes, sql_out, status, share],
                )

            with gr.Tab("Guide"):
                gr.Markdown(
                    f"""
## When to pick each output

| Convert to | Use when |
|---|---|
| **Python (pandas)** | You want notebook / script code from warehouse SQL |
| **Snowflake SQL** | You are moving queries onto Snowflake |
| **BigQuery SQL** | You are moving queries onto BigQuery |
| **dbt project** | You want staging / intermediate / marts from SQL or a procedure |

## Supported input dialects
Vertica · Oracle · Redshift · BigQuery · Snowflake

## What this product is
- A **deterministic** SQL rewriter (rules + sqlglot) with pandas codegen
- Not a hosted chatbot — conversion does not call an external LLM
- Complex procedures / cursors / dynamic SQL may need manual follow-up

## Python API
```python
from sqlshift.ai import pipeline
print(pipeline("sql-migration")(
    "SELECT ZEROIFNULL(a) FROM t",
    source="vertica",
    target="pandas",
))
```

[Open on Hugging Face]({SPACE_URL}) · [GitHub]({GITHUB_URL})
"""
                )

            with gr.Tab("More"):
                gr.Markdown("Power-user extras. Everyday use only needs **Convert**.")

                with gr.Accordion("Dialect behavior notes", open=False):
                    rag_q = gr.Textbox(
                        label="Question",
                        value="Oracle empty string vs Snowflake NULL",
                        lines=2,
                    )
                    with gr.Row():
                        rag_source = gr.Dropdown(
                            choices=SOURCE_DROPDOWN, value="oracle", label="From"
                        )
                        rag_target = gr.Dropdown(
                            choices=[
                                ("Snowflake SQL", "snowflake"),
                                ("BigQuery SQL", "bigquery"),
                            ],
                            value="snowflake",
                            label="To",
                        )
                        rag_run = gr.Button("Search", variant="secondary")
                    rag_out = gr.Markdown()
                    rag_run.click(
                        run_behavior_rag,
                        [rag_q, rag_source, rag_target],
                        [rag_out],
                    )

                with gr.Accordion("Offline conversion eval", open=False):
                    with gr.Row():
                        eval_limit = gr.Slider(10, 200, value=40, step=10, label="Pairs")
                        eval_run = gr.Button("Run eval", variant="secondary")
                    eval_summary = gr.Markdown()
                    eval_detail = gr.Markdown()
                    with gr.Row():
                        lb_name = gr.Textbox(label="Handle", value="hf-user")
                        lb_submit = gr.Button("Submit local score")
                    leaderboard_md = gr.Markdown(value=get_leaderboard_md())
                    eval_run.click(
                        run_eval_suite,
                        [eval_limit, eval_category],
                        [eval_summary, eval_detail, eval_state],
                    )
                    lb_submit.click(
                        submit_eval_score, [lb_name, eval_state], [leaderboard_md]
                    )

        gr.Markdown(
            f"<p class='footer-viral'>{__product_name__} v{__version__} · "
            f"<a href='{SPACE_URL}'>Space</a> · "
            f"<a href='{GITHUB_URL}'>GitHub</a> · Apache-2.0</p>"
        )
    return demo


demo = _build_demo()


if __name__ == "__main__":
    demo.launch(theme=build_theme(), css=CUSTOM_CSS)

---
title: SQLShiftAI
emoji: zap
colorFrom: yellow
colorTo: blue
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: true
license: apache-2.0
short_description: Paste legacy SQL → Snowflake / dbt / BigQuery in one click
tags:
  - agent
  - agents
  - llm
  - code
  - text-generation
  - sql
  - rag
  - evaluation
  - snowflake
  - dbt
  - machine-learning
---

# SQLShiftAI — convert legacy SQL in one click

**Before → After playground.** Paste Vertica / Oracle / Redshift / BigQuery SQL and get Snowflake, dbt, or BigQuery — with confidence, behavior RAG, and optional dbt project emission.

## 30-second demo
1. Stay on **Playground** (already open)
2. Click an example under the editors **or** hit **Convert with Agent**
3. Read the AFTER panel + share blurb

No signup. Duplicate this Space and try your own SQL.

## Why this Space
| Hook | Detail |
|------|--------|
| Instant wow | Side-by-side BEFORE / AFTER |
| Agent framing | Hybrid rules + sqlglot + RAG (+ optional HF LLM) |
| ML eval | Exact / token F1 / fuzzy + leaderboard |
| Dataset | `datasets/vertica_snowflake_pairs.jsonl` (publishable to Hub) |
| DS path | ML Feature SQL → dbt feature mart in Advanced Lab |

## Tabs
- **Playground** — the viral loop
- **Eval** — benchmark the translator
- **Advanced Lab** — RAG, ML features, inspector, repo workbench, copilot (lazy-loaded)

## Links
- GitHub: https://github.com/dgvj-work/sql_shift_ai
- Dataset publish: `python scripts/publish_dataset.py --repo <user>/vertica-snowflake-pairs`

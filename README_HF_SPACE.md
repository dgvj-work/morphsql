---
title: MorphSQL
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.49.1"
python_version: "3.11"
app_file: app.py
pinned: true
license: apache-2.0
short_description: Convert Vertica, Oracle, Redshift SQL to Snowflake, BigQuery, or dbt
tags:
  - sql
  - code
  - agent
  - chat
  - text-generation
  - text-classification
  - rag
  - evaluation
  - snowflake
  - dbt
  - data-engineering
models:
  - dgvj-work/sqlshift-ai
datasets:
  - dgvj-work/vertica-snowflake-pairs
suggested_hardware: cpu-basic
---

# MorphSQL

Convert legacy warehouse SQL (Vertica, Oracle, Redshift, BigQuery) into Snowflake, BigQuery, or a dbt project.

Built for data engineers migrating platforms — hybrid rewrite rules + sqlglot + a small risk classifier you can download from the Hub.

## Try it
1. Open **Playground**
2. Click a preset (e.g. Vertica → Snowflake)
3. See BEFORE / AFTER + confidence score
4. Optional: chat with the agent, run eval, or download the risk model

## Hub artifacts
- **Space:** this demo
- **Model:** [`dgvj-work/sqlshift-ai`](https://huggingface.co/dgvj-work/sqlshift-ai) (`risk_classifier.joblib`)
- **Dataset:** [`dgvj-work/vertica-snowflake-pairs`](https://huggingface.co/datasets/dgvj-work/vertica-snowflake-pairs)
- **Code:** [github.com/dgvj-work/sql_shift_ai](https://github.com/dgvj-work/sql_shift_ai)

## Python
```python
from sqlshift.ai import pipeline
print(pipeline("sql-migration")("SELECT ZEROIFNULL(a) FROM t"))
print(pipeline("sql-risk-classification")("EXECUTE IMMEDIATE 'x'"))
```

Author: Digvijay Waghela · Apache-2.0

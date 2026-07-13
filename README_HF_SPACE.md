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
short_description: Convert Vertica/Oracle/Redshift/BigQuery SQL to pandas, Snowflake, or dbt
tags:
  - sql
  - pandas
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

**SQL → pandas** (primary), plus Snowflake / BigQuery / dbt.

Paste Vertica, Oracle, Redshift, BigQuery, or Snowflake SQL and get runnable Python pandas code — or keep warehouse SQL / dbt output.

## Try it
1. Open **Playground** (default target: **pandas**)
2. Click a preset (Vertica / Oracle / Redshift / BigQuery / Snowflake → pandas)
3. Copy the generated Python, fill `tables[...]`, run

## Hub
- Space: this demo
- Model: [`dgvj-work/sqlshift-ai`](https://huggingface.co/dgvj-work/sqlshift-ai)
- Dataset: [`dgvj-work/vertica-snowflake-pairs`](https://huggingface.co/datasets/dgvj-work/vertica-snowflake-pairs)
- Code: [github.com/dgvj-work/sql_shift_ai](https://github.com/dgvj-work/sql_shift_ai)

```python
from sqlshift.ai import pipeline
print(pipeline("sql-migration")("SELECT ZEROIFNULL(a) FROM t", target="pandas"))
```

Author: Digvijay Waghela · Apache-2.0

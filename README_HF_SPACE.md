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
short_description: Convert Vertica/Oracle/Redshift SQL to pandas, Snowflake, BigQuery, or dbt
tags:
  - sql
  - pandas
  - code
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

Convert warehouse SQL into **pandas**, **Snowflake**, **BigQuery**, or a **dbt** project.

## Use it
1. Open the **Convert** tab
2. Choose input dialect + output type
3. Paste SQL (or load an example) → **Convert**

Default output is **Python (pandas)**.

```python
from sqlshift.ai import pipeline
print(pipeline("sql-migration")(
    "SELECT ZEROIFNULL(a) FROM t",
    source="vertica",
    target="pandas",
))
```

Author: Digvijay Waghela · Apache-2.0

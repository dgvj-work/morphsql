---
language: en
license: apache-2.0
library_name: sqlshift-ai
pipeline_tag: text-classification
tags:
  - agent
  - code
  - sql
  - text-generation
  - text-classification
  - rag
  - sklearn
  - migration
  - dbt
  - snowflake
datasets:
  - dgvj-work/vertica-snowflake-pairs
---

# MorphSQL

Convert Vertica / Oracle / Redshift / BigQuery SQL to Snowflake, BigQuery, or dbt.

## Artifacts
- `risk_classifier.joblib` — migration risk (`low` / `medium` / `high`)
- `rewrite_vocabulary.json` — rewrite lexicon
- `config.json` — dialect metadata

## Quick start

```python
from sqlshift.ai import pipeline

print(pipeline("sql-risk-classification")("EXECUTE IMMEDIATE 'x'"))
print(pipeline("sql-migration")("SELECT ZEROIFNULL(a) FROM t", source="vertica", target="snowflake"))
```

```python
from huggingface_hub import hf_hub_download
import joblib

path = hf_hub_download("dgvj-work/sqlshift-ai", "risk_classifier.joblib")
print(joblib.load(path).predict(["SELECT 1"]))
```

## Demo
https://huggingface.co/spaces/dgvj-work/sqlshift-ai

Author: Digvijay Waghela · Apache-2.0

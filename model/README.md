---
language: en
license: apache-2.0
library_name: sqlshift-ai
pipeline_tag: text-classification
tags:
  - code
  - sql
  - agent
  - text-generation
  - text-classification
  - rag
  - pytorch
  - sklearn
  - migration
  - llm
datasets:
  - dgvj-work/vertica-snowflake-pairs
metrics:
  - accuracy
  - f1
---

# MorphSQL — AI SQL Migration Agent (downloadable model)

This Hub model packages the **AI risk classifier** + **rewrite vocabulary** used by MorphSQL (`sqlshift-ai`).

## What's inside (downloads)
| File | Purpose |
|------|---------|
| `risk_classifier.joblib` | TF-IDF + LogisticRegression risk head (`low`/`medium`/`high`) |
| `rewrite_vocabulary.json` | Learned/curated SQL rewrite lexicon |
| `config.json` | Model card config + supported dialects |

## Quick start (downloads → inference)

```python
from huggingface_hub import hf_hub_download
import joblib

path = hf_hub_download(repo_id="dgvj-work/sqlshift-ai", filename="risk_classifier.joblib")
clf = joblib.load(path)
print(clf.predict_proba(["SELECT ZEROIFNULL(a) FROM t EXECUTE IMMEDIATE 'x'"]))
```

Or use the Python package pipeline:

```python
from sqlshift.ai import pipeline

risk = pipeline("sql-risk-classification")
print(risk("CREATE PROCEDURE p AS BEGIN EXECUTE IMMEDIATE 'x'; END;"))

migrate = pipeline("sql-migration")
print(migrate("SELECT ZEROIFNULL(a) FROM t", source="vertica", target="snowflake"))
```

## Agent tools
1. `convert_sql` — hybrid rules + sqlglot  
2. `predict_risk` — this classifier  
3. `retrieve_behavior` — behavior RAG  
4. `emit_dbt` — dbt project generation  

## Space
Interactive AI agent: https://huggingface.co/spaces/dgvj-work/sqlshift-ai

## Train locally
```bash
python -c "from sqlshift.ai import train_and_save; train_and_save()"
```

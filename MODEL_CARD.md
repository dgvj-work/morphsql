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
  - llm
  - sklearn
  - migration
  - dbt
datasets:
  - dgvj-work/vertica-snowflake-pairs
---

# MorphSQL — AI SQL Migration Agent

Downloadable **AI risk classifier** + agent toolchain (package: `sqlshift-ai`).

## Files (Hub downloads)
- `model/risk_classifier.joblib` — sklearn TF-IDF + LogisticRegression (`low`/`medium`/`high`)
- `model/rewrite_vocabulary.json` — SQL rewrite lexicon
- `model/config.json` — dialects + metadata

## Pipelines

```python
from sqlshift.ai import pipeline

# Risk classification (text-classification style)
risk = pipeline("sql-risk-classification")
print(risk("CREATE PROCEDURE p AS BEGIN EXECUTE IMMEDIATE 'x'; END;"))

# Full migration agent
migrate = pipeline("sql-migration")
print(migrate("SELECT ZEROIFNULL(a) FROM t", source="vertica", target="snowflake"))
```

```python
from huggingface_hub import hf_hub_download
import joblib
path = hf_hub_download("dgvj-work/sqlshift-ai", "risk_classifier.joblib")
print(joblib.load(path).predict(["SELECT 1"]))
```

## Agent tools
`convert_sql` · `predict_risk` · `retrieve_behavior` · `emit_dbt`

## Space
Chat UI: duplicate the MorphSQL Space and talk to the agent.

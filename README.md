# MorphSQL

Convert Vertica / Oracle / Redshift / BigQuery / Snowflake SQL to **pandas** or **PySpark** (notebook-ready), **Snowflake**, **BigQuery**, or **dbt**.

[![Space](https://img.shields.io/badge/🤗%20Space-MorphSQL-blue)](https://huggingface.co/spaces/dgvj-work/morphsql)
[![GitHub](https://img.shields.io/badge/GitHub-dgvj--work%2Fmorphsql-blue)](https://github.com/dgvj-work/morphsql)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)

Built for data scientists: upload or paste SQL → convert → sample preview → download `.py` / `.sql`.

## Naming

| Layer | Name |
|-------|------|
| **Product** | **MorphSQL** |
| Python import / CLI / PyPI | `morphsql` |
| Hugging Face Space / model | `dgvj-work/morphsql` |
| GitHub | `dgvj-work/morphsql` |

---

## Try it online (no install)

1. Open the Space: [huggingface.co/spaces/dgvj-work/morphsql](https://huggingface.co/spaces/dgvj-work/morphsql)
2. Choose **SQL is written for** + **Convert to** (start with **Python (pandas)**)
3. Paste SQL or upload `.sql` / `.zip`
4. Click **Convert** (or **Upload & Convert → Download**)
5. Review sample preview + download the converted file

---

## Local end-to-end runbook (clone → verify → run)

Requires **Python 3.10+**.

### 1. Download and install

```bash
git clone https://github.com/dgvj-work/morphsql.git
cd morphsql

python3 -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .\.venv\Scripts\Activate.ps1

pip install -U pip
pip install -e ".[dev,demo]"
```

### 2. Verify everything works (recommended)

This runs tests, CLI analyze/migrate on `examples/vertica_legacy`, Gradio handlers, and builds the UI:

```bash
chmod +x scripts/run_local.sh   # first time only (macOS/Linux)
./scripts/run_local.sh
```

Expect: **44 tests passed**, HTML report under `migration-output/`, and `All checks passed`.

Quick smoke checks (same venv):

```bash
morphsql version
python scripts/check_space.py
python -c "from morphsql.ai import pipeline; print(pipeline('sql-migration')('SELECT COALESCE(a,0) FROM t', source='snowflake', target='pandas')['converted_sql'][:80])"
```

### 3. Launch the interactive workbench

```bash
python app.py
```

Open the local URL Gradio prints (usually `http://127.0.0.1:7860`).

### 4. CLI recipes (same example repo)

Always pass `--source` / `--target` for the Vertica sample:

```bash
# Portfolio analyze → HTML + JSON
morphsql analyze ./examples/vertica_legacy \
  --source vertica --target snowflake -o ./migration-output

# Single-file convert → pandas / PySpark `.py` on disk
morphsql convert ./examples/vertica_legacy/queries/customer_lifetime_value.sql \
  --source vertica --target pandas -o ./migration-output/pandas

morphsql convert ./examples/vertica_legacy/queries/customer_lifetime_value.sql \
  --source vertica --target pyspark -o ./migration-output/pyspark

# Folder convert → HTML report for the whole sample repo
morphsql convert ./examples/vertica_legacy \
  --source vertica --target snowflake -o ./migration-output

# Full pipeline: analyze → convert → validate → report + dbt scaffold
morphsql migrate ./examples/vertica_legacy \
  --source vertica --target snowflake --output ./migration-output

# Open the report (macOS)
open ./migration-output/migration_report.html
```

Other useful commands: `morphsql convert … --generate-dbt`, `morphsql validate …`, `morphsql --help`.

### 5. Use in your own Python code

**A. One-liner migration pipeline (query → pandas / PySpark)**

```python
from morphsql.ai import pipeline

mig = pipeline("sql-migration")
print(mig("SELECT ZEROIFNULL(a) FROM t", source="vertica", target="pandas")["converted_sql"])
print(mig("SELECT ZEROIFNULL(a) FROM t", source="vertica", target="pyspark")["converted_sql"])
print(mig("SELECT ZEROIFNULL(a) FROM t", source="vertica", target="snowflake")["converted_sql"])
```

**B. Repository migration SDK**

```python
from morphsql.pipeline import MigrationPipeline
from morphsql.models import Dialect
from morphsql.intelligence.runbook import generate_runbook

pipe = MigrationPipeline(source=Dialect.VERTICA, target=Dialect.SNOWFLAKE)
report = pipe.analyze("./examples/vertica_legacy")
report = pipe.convert(report)
report = pipe.validate(report)

print(f"Objects: {len(report.objects)}")
print(generate_runbook(report)[:500])
```

**C. Direct translator (no agent wrapper)**

```python
from morphsql.translator.engine import translate_sql
from morphsql.models import Dialect

code, confidence, auto, review = translate_sql(
    "SELECT ZEROIFNULL(amount) FROM staging.orders",
    source=Dialect.VERTICA,
    target=Dialect.PANDAS,
)
print(code)
print(f"confidence={confidence}%  auto={auto}  review={review}")
```

---

## What makes this different from SQL converters

| Capability | SQL converters | MorphSQL |
|-----------|----------------|-------------|
| Single query translation | Yes | Yes |
| **SQL → pandas / PySpark codegen** | Rare | Yes |
| **Repository-level discovery** | No | Yes |
| **Dependency lineage graphs** | No | Yes |
| **Portfolio risk scoring** | Partial | Yes |
| **Workload rationalization** | No | Yes |
| **dbt project decomposition** | No | Yes |
| **Validation & reconciliation** | No | Yes |
| **Migration runbook generation** | No | Yes |
| **LLM copilot grounded in scan** | No | Yes |

---

## Platform capabilities

1. **Migration Workbench** — scan zip/dirs of SQL, procedures, views, dbt models  
2. **Dependency Lineage** — Plotly graph of read/write deps  
3. **Risk & Rationalization** — score 0–100; migrate / review / rewrite / retire  
4. **Hybrid Translation** — rules (ZEROIFNULL, DATEADD, …) + sqlglot  
5. **dbt Architecture** — procedures → staging / intermediate / mart  
6. **Validation Suite** — row counts, null rates, structural checks  
7. **Migration Runbook** — phased cutover plan  
8. **Migration Copilot** — HF Inference API, grounded in scan context  

---

## Hugging Face deployment (maintainers)

```bash
pip install -U "huggingface_hub[cli]"
hf auth login

# Create Space + model dgvj-work/morphsql once, then:
./scripts/deploy_hf.sh
# → https://huggingface.co/spaces/dgvj-work/morphsql
```

Preflight only (no upload):

```bash
python scripts/check_space.py
```

Space card metadata lives in `README_HF_SPACE.md` (copied to Space `README.md` on deploy).  
Optional Space secret: `MORPHSQL_MODEL` for the copilot model.

---

## Project structure

```
morphsql/           Core package (CLI, pipeline, translators)
demo/               Gradio handlers + theme
app.py              Local / Hugging Face Space entry
examples/           Sample Vertica legacy repo
scripts/run_local.sh  One-command local verification
PROJECT.md          Architecture + AI handoff
tests/
```

**For AI continuation:** read [`PROJECT.md`](PROJECT.md).

---

## Supported routes

| Source | Target | Status |
|--------|--------|--------|
| Vertica / Oracle / Redshift / BigQuery / Snowflake | **pandas** | Supported |
| Vertica / Oracle / Redshift / BigQuery / Snowflake | **PySpark** | Supported |
| Vertica | Snowflake / dbt-snowflake / BigQuery | Supported |
| Oracle | Snowflake / dbt-snowflake / BigQuery | Supported |
| Redshift | Snowflake / dbt-snowflake / BigQuery | Supported |
| BigQuery | Snowflake / dbt-snowflake | Supported |
| Snowflake | BigQuery | Supported |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `morphsql: command not found` | Activate `.venv`, then `pip install -e ".[dev,demo]"` |
| Gradio import / theme errors | Use Python 3.10–3.12 and reinstall `.[demo]` |
| Preview empty for procedures | Expected for some procedural SQL; try a `SELECT` query |
| sklearn / risk model warnings | Re-run `python -c "from morphsql.ai.risk_model import train_and_save; train_and_save(force=True)"` |
| `./scripts/run_local.sh` permission denied | `chmod +x scripts/run_local.sh` |

---

## Author

Digvijay Waghela · digvijay.vaghela@yahoo.com · Apache 2.0

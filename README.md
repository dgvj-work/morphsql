# 🔄 MigrationIQ / SQLShift AI

### AI-Powered Data Platform Migration Intelligence

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-blue)](https://huggingface.co/spaces/migrationiq/sqlshift-ai)
[![PyPI](https://img.shields.io/badge/PyPI-sqlshift--ai-blue)](https://pypi.org/project/sqlshift-ai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)

> **Upload a legacy data repository and receive a complete, validated migration package — not merely converted SQL.**

MigrationIQ is an open-source AI migration intelligence platform that **discovers, translates, validates, tests, documents, and optimizes** enterprise data workloads across cloud data platforms.

**Live Demo**: [🤗 Hugging Face Space](https://huggingface.co/spaces/migrationiq/sqlshift-ai)

---

## Why MigrationIQ?

Simple SQL translation is commoditized. Google BigQuery Migration Service, AWS Schema Conversion Tool, and Snowflake SnowConvert already handle basic conversion. MigrationIQ goes further:

| Capability | Basic Converters | MigrationIQ |
|-----------|-----------------|-------------|
| Single query translation | ✅ | ✅ |
| **Repository-level analysis** | ❌ | ✅ |
| **Column-level lineage** | ❌ | ✅ |
| **Migration risk scoring** | Partial | ✅ |
| **dbt project decomposition** | ❌ | ✅ |
| **Semantic equivalence validation** | ❌ | ✅ |
| **Behavior difference intelligence** | Partial | ✅ |
| **Workload rationalization** | ❌ | ✅ |
| **HTML migration reports** | Partial | ✅ |

---

## Quick Start

### Install

```bash
pip install sqlshift-ai

# With demo dependencies (Gradio)
pip install sqlshift-ai[demo]
```

### CLI

```bash
# Analyze a legacy SQL repository
sqlshift analyze ./examples/vertica_legacy \
  --source vertica \
  --target snowflake \
  --output migration-report

# Convert SQL with dbt generation
sqlshift convert ./examples/vertica_legacy \
  --source vertica \
  --target dbt-snowflake \
  --generate-dbt \
  --generate-tests

# Full migration pipeline
sqlshift migrate ./examples/vertica_legacy \
  --source vertica \
  --target snowflake \
  --output migration-package
```

### Python SDK

```python
from sqlshift.pipeline import MigrationPipeline
from sqlshift.models import Dialect

pipeline = MigrationPipeline(
    source=Dialect.VERTICA,
    target=Dialect.SNOWFLAKE,
)

# Full pipeline: analyze → convert → validate → report → dbt
report = pipeline.run_full_pipeline(
    "./examples/vertica_legacy",
    "./migration-output",
)

print(f"Objects discovered: {report.dashboard.total_objects}")
print(f"Auto-migratable: {report.dashboard.auto_migratable}")
print(f"Risk score: {report.dashboard.migration_risk_score}/100")
```

### Hugging Face Space

```bash
# Run locally
python app.py
```

### One-Command Local Test

```bash
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

This script will:
1. Create a virtual environment and install dependencies
2. Run all 12 unit tests
3. Execute the full migration pipeline on the example repo
4. Verify HTML report and dbt project outputs
5. Smoke-test the Gradio app functions

Then launch the interactive demo:

```bash
source .venv/bin/activate
python app.py
# Opens at http://127.0.0.1:7860
```

Open the generated report in your browser:

```bash
open migration-output/migration_report.html   # macOS
```

---

## Architecture

```
SQL Repository (GitHub / Zip / dbt / Airflow)
        ↓
┌─────────────────────────────────────────────┐
│           Discovery Agent                    │
│   Scan → Classify → Extract metadata         │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│           Lineage Agent                      │
│   Table + column dependency graphs           │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│           Translation Agent                  │
│   Rules → sqlglot AST → Target SQL           │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│     Risk + Validation + Architecture Agents  │
│   Score → Test → dbt decompose → Report       │
└─────────────────────────────────────────────┘
```

### Hybrid Translation Engine

```
SQL Parser (sqlglot)
   ↓
Abstract Syntax Tree
   ↓
Deterministic Conversion Rules (Vertica→Snowflake)
   ↓
Dialect Transpilation
   ↓
Behavior Difference Detection
   ↓
Target SQL + Confidence Score
```

---

## Features

### 1. Repository-Level Migration Analysis
Scans entire repositories: GitHub repos, zip files, dbt projects, stored procedure directories.

### 2. Column-Level Lineage
```
ORACLE.CUSTOMER_TRANSACTIONS
        ↓
SP_BUILD_CUSTOMER_DAILY
        ↓
VERTICA.CUSTOMER_DAILY
        ↓
DBT.CUSTOMER_METRICS
```

### 3. Migration Risk Scoring
```
Object: SP_CUSTOMER_METRICS
Complexity: 82/100 | Risk: HIGH
- 2,400 lines of procedural SQL
- 14 temporary tables
- Dynamic SQL detected
- 7 downstream dependencies
```

### 4. Stored Procedure → dbt Decomposition
```
SP_BUILD_CUSTOMER_DAILY/
├── models/staging/stg_customer_transactions.sql
├── models/intermediate/int_customer_daily.sql
├── models/marts/customer_metrics.sql
├── models/staging/_sources.yml
├── dbt_project.yml
└── analyses/migration_validation.sql
```

### 5. Semantic Validation
Generates reconciliation queries: row counts, checksums, null rates, metric tolerances.

### 6. Behavior Difference Intelligence
Detects 12+ platform behavioral differences: empty string vs NULL, timezone, merge semantics, integer division.

---

## Supported Platforms

| Phase | Source | Target | Status |
|-------|--------|--------|--------|
| **1** | Vertica | Snowflake / dbt | ✅ Ready |
| **2** | Oracle, Redshift, BigQuery | Snowflake / dbt | 🟡 Beta |
| **3** | Snowflake | BigQuery | 🔜 Planned |

---

## Example Output

```
Migration Dashboard
├── Objects: 5
├── Auto-migratable: 2
├── Requires review: 2
├── Manual redesign: 1
├── Risk score: 37/100
├── Conversion: 100%
├── Validation: 75%
└── Est. savings: $2,500 – $7,500/year
```

---

## Project Structure

```
sqlshift-ai/
├── sqlshift/               # Python package
│   ├── scanner/            # Repository discovery
│   ├── parser/             # SQL parsing (sqlglot)
│   ├── lineage/            # Dependency graphs
│   ├── translator/         # Hybrid SQL conversion
│   ├── risk/               # Complexity scoring
│   ├── dbt_generator/      # dbt project decomposition
│   ├── validation/         # Reconciliation tests
│   ├── knowledge/          # Platform behavior differences
│   ├── report/             # HTML report generation
│   ├── pipeline.py         # Agent orchestration
│   └── cli.py              # CLI interface
├── app.py                  # Hugging Face Gradio demo
├── examples/vertica_legacy/  # Sample legacy repository
├── tests/
├── MODEL_CARD.md
└── README.md
```

---

## Deploy to Hugging Face

```bash
# Create Space
huggingface-cli repo create sqlshift-ai --type space --space_sdk gradio

# Upload
huggingface-cli upload migrationiq/sqlshift-ai . --repo-type=space
```

---

## Contributing

Contributions welcome! Priority areas:
- Additional dialect support (Oracle PL/SQL, Redshift, BigQuery)
- Execution-based validation with database connectors
- LLM integration for complex procedural logic
- Airflow DAG migration

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

---

<p align="center">
  <strong>MigrationIQ</strong> — Because migration is more than translation.
</p>

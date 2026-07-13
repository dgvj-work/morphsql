"""Hugging Face-style pipeline API for SQL migration."""

from __future__ import annotations

from typing import Any

from sqlshift.ai.agent import SQLMigrationAgent
from sqlshift.ai.risk_model import get_risk_model
from sqlshift.models import Dialect
from sqlshift.translator.engine import translate_sql


def pipeline(task: str = "sql-migration", **kwargs):
    """
    Mimic transformers.pipeline entrypoint for Hub users.

    Examples:
        pipe = pipeline("sql-migration")
        pipe("SELECT ZEROIFNULL(a) FROM t", source="vertica", target="snowflake")

        pipe = pipeline("sql-risk-classification")
        pipe("CREATE PROCEDURE ...")
    """
    task = (task or "sql-migration").lower().replace("_", "-")
    if task in {"sql-migration", "sql-translation", "text2sql-migration"}:
        return SQLMigrationPipeline(**kwargs)
    if task in {"sql-risk-classification", "text-classification", "risk"}:
        return SQLRiskPipeline(**kwargs)
    raise ValueError(
        f"Unknown task '{task}'. Use 'sql-migration' or 'sql-risk-classification'."
    )


class SQLMigrationPipeline:
    def __init__(self, source: str = "vertica", target: str = "snowflake"):
        self.source = source
        self.target = target
        self.agent = SQLMigrationAgent()

    def __call__(
        self,
        sql: str,
        source: str | None = None,
        target: str | None = None,
        prompt: str = "Convert and explain",
        **_: Any,
    ) -> dict[str, Any]:
        source = source or self.source
        target = target or self.target
        result = self.agent.run(prompt, sql=sql, source=source, target=target)
        return result.to_dict()


class SQLRiskPipeline:
    def __init__(self):
        self.model = get_risk_model()

    def __call__(self, sql: str, **_: Any) -> dict[str, Any]:
        return self.model.predict(sql)


def migrate_sql(sql: str, source: str = "vertica", target: str = "snowflake") -> dict[str, Any]:
    """One-liner helper used in model card examples."""
    out_sql, conf, auto, review = translate_sql(sql, Dialect(source), Dialect(
        "snowflake" if target == "dbt-snowflake" else target
    ))
    risk = get_risk_model().predict(sql)
    return {
        "converted_sql": out_sql,
        "confidence": conf,
        "transforms": auto,
        "review": review,
        "risk": risk,
    }

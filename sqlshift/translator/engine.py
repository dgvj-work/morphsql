"""Hybrid SQL translation engine: rules + dialect conversion."""

from __future__ import annotations

import re

import sqlglot
from sqlglot import exp

from sqlshift.knowledge.behavior import get_behavior_warnings
from sqlshift.models import Dialect, MigrationObject
from sqlshift.parser.sql_parser import (
    detect_unsupported_features,
    get_sqlglot_dialect,
    parse_sql_multi,
)

# Deterministic Vertica → Snowflake function mappings
VERTICA_TO_SNOWFLAKE_FUNCTIONS: dict[str, str] = {
    "ZEROIFNULL": "COALESCE({args}, 0)",
    "NVL": "COALESCE",
    "NVL2": "IFF({args})",
    "ISNULL": "COALESCE",
    "TO_CHAR": "TO_VARCHAR",
    "TO_NUMBER": "TO_NUMBER",
    "SYSDATE": "CURRENT_TIMESTAMP()",
    "GETDATE": "CURRENT_TIMESTAMP()",
    "NOW": "CURRENT_TIMESTAMP()",
    "DATE": "CURRENT_DATE()",
    "LISTAGG": "LISTAGG",
    "STRING_AGG": "LISTAGG",
    "MEDIAN": "MEDIAN",
    "APPROXIMATE_COUNT_DISTINCT": "APPROX_COUNT_DISTINCT",
}

# Vertica-specific syntax replacements
VERTICA_SYNTAX_REPLACEMENTS: list[tuple[str, str]] = [
    (r"\bSEGMENTED\s+BY\s+HASH\s*\([^)]+\)\s*ALL\s*NODES", ""),
    (r"\bORDER\s+BY\s+[^;]+(?=\s*;|\s*$)", ""),
    (r"\bENCODED\s+BY\s+[^;]+", ""),
    (r"\bINCLUDE\s+SCHEMA\s+PRIVILEGES\b", ""),
    (r"\bLOCAL\s+TEMP\b", "TEMPORARY"),
    (r"\bPROJECTION\s+\w+\b", ""),
    (r"\bTIMESERIES\s+\w+\s+OVER\s*\(", "/* TIMESERIES - manual review required */"),
    (r"\bINTERPOLATE\s+\w+\s+VALUE\b", "/* INTERPOLATE - manual review required */"),
]


def translate_sql(
    sql: str,
    source: Dialect,
    target: Dialect,
) -> tuple[str, float, list[str], list[str]]:
    """
    Translate SQL using hybrid rule-based + sqlglot approach.

    Returns: (translated_sql, confidence, auto_converted, requires_review)
    """
    auto_converted: list[str] = []
    requires_review: list[str] = []
    confidence = 100.0

    # Step 1: Apply deterministic Vertica-specific replacements
    working_sql = sql
    if source == Dialect.VERTICA:
        for pattern, replacement in VERTICA_SYNTAX_REPLACEMENTS:
            if re.search(pattern, working_sql, re.IGNORECASE):
                working_sql = re.sub(pattern, replacement, working_sql, flags=re.IGNORECASE)
                auto_converted.append(f"Removed/replaced Vertica syntax: {pattern[:40]}")

    # Step 2: Apply function mappings
    if source == Dialect.VERTICA and target in (Dialect.SNOWFLAKE, Dialect.DBT_SNOWFLAKE):
        for func, replacement in VERTICA_TO_SNOWFLAKE_FUNCTIONS.items():
            pattern = rf"\b{func}\s*\("
            if re.search(pattern, working_sql, re.IGNORECASE):
                working_sql = re.sub(rf"\b{func}\b", replacement.split("(")[0], working_sql, flags=re.IGNORECASE)
                auto_converted.append(f"Function mapping: {func}")

    # Step 3: sqlglot dialect transpilation
    source_dialect = get_sqlglot_dialect(source)
    target_dialect = get_sqlglot_dialect(target)

    try:
        statements = parse_sql_multi(working_sql, source)
        if statements:
            translated_parts: list[str] = []
            for stmt in statements:
                try:
                    translated = stmt.sql(dialect=target_dialect, pretty=True)
                    translated_parts.append(translated)
                    auto_converted.append("sqlglot dialect transpilation")
                except Exception:
                    translated_parts.append(stmt.sql(dialect=source_dialect))
                    requires_review.append("Statement failed sqlglot transpilation")
                    confidence -= 10

            working_sql = ";\n\n".join(translated_parts)
        else:
            # Fallback: direct transpile
            working_sql = sqlglot.transpile(
                working_sql,
                read=source_dialect,
                write=target_dialect,
                pretty=True,
            )[0] if working_sql.strip() else working_sql
            auto_converted.append("sqlglot direct transpile")
    except Exception:
        requires_review.append("Full sqlglot transpilation failed — partial rule-based conversion applied")
        confidence -= 25

    # Step 4: Detect unsupported features
    unsupported = detect_unsupported_features(sql, source, target)
    for feature in unsupported:
        requires_review.append(f"Unsupported feature: {feature}")
        confidence -= 5

    # Step 5: Behavior warnings
    warnings = get_behavior_warnings(sql, source.value, target_dialect)
    for warning in warnings:
        requires_review.append(f"Behavior difference: {warning.name}")
        if warning.severity == "high":
            confidence -= 8
        elif warning.severity == "medium":
            confidence -= 4

    # Step 6: Detect patterns requiring manual review
    manual_patterns = {
        "Dynamic SQL": r"EXECUTE\s+IMMEDIATE|EXEC\s*\(",
        "Cursor processing": r"\bCURSOR\b",
        "Exception handling": r"\bEXCEPTION\s+WHEN\b",
        "Procedural block": r"\bBEGIN\b.*\bEND\b",
        "Dynamic table name": r"\|\||CONCAT\s*\([^)]*table",
    }
    for name, pattern in manual_patterns.items():
        if re.search(pattern, sql, re.IGNORECASE):
            requires_review.append(name)
            confidence -= 10

    confidence = max(0.0, min(100.0, confidence))
    return working_sql, confidence, list(set(auto_converted)), list(set(requires_review))


def translate_object(
    obj: MigrationObject,
    source: Dialect,
    target: Dialect,
) -> MigrationObject:
    """Translate a single migration object."""
    target_sql, confidence, auto_converted, requires_review = translate_sql(
        obj.source_sql, source, target
    )
    obj.target_sql = target_sql
    obj.conversion_confidence = confidence
    obj.auto_converted = auto_converted
    obj.requires_review = requires_review
    obj.unsupported_features = detect_unsupported_features(obj.source_sql, source, target)
    return obj


def translate_objects(
    objects: list[MigrationObject],
    source: Dialect,
    target: Dialect,
) -> list[MigrationObject]:
    """Translate all migration objects."""
    return [translate_object(obj, source, target) for obj in objects]

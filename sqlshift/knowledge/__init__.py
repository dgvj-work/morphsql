"""Knowledge base package."""

from sqlshift.knowledge.behavior import (
    BEHAVIOR_DIFFERENCES,
    BehaviorDifference,
    format_behavior_warning,
    get_behavior_warnings,
)

__all__ = [
    "BEHAVIOR_DIFFERENCES",
    "BehaviorDifference",
    "format_behavior_warning",
    "get_behavior_warnings",
]

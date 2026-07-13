"""dbt project generation package."""

from sqlshift.dbt_generator.decomposer import decompose_to_dbt, write_dbt_project

__all__ = ["decompose_to_dbt", "write_dbt_project"]

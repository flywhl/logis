from typing import Sequence

import jmespath

from jmespath.parser import ParsedResult
from pydantic import BaseModel

from logis.domain.git import ExperimentCommit

# SimpleQueryOp = Literal[">", "<", ">=", "<=", "=="]
# SimpleQueryValue = str | int | float
SimpleQueryOp = str
SimpleQueryValue = str | int | float


class Query(BaseModel):
    """A query to filter experiment commits."""

    expression: str

    def compile(self) -> ParsedResult:
        """Compile the JMESPath expression."""
        return jmespath.compile(self.expression)

    @staticmethod
    def from_expression(expr: str) -> "Query":
        """Create a query from a JMESPath expression."""
        return Query(expression=expr)

    @staticmethod
    def where(field: str, op: SimpleQueryOp, value: SimpleQueryValue) -> "Query":
        """Create a query that filters on a field value.

        $ logis viz "accuracy from ['lr', 'batch_size']"

        $ logis query "accuracy > 0.9"

        Example:
            Query.where("accuracy", ">", 0.9)
        """
        # Convert comparison operators to JMESPath
        match op:
            case ">":
                expr = f"[?{field} > `{value}`]"
            case "<":
                expr = f"[?{field} < `{value}`]"
            case ">=":
                expr = f"[?{field} >= `{value}`]"
            case "<=":
                expr = f"[?{field} <= `{value}`]"
            case "==":
                expr = f"[?{field} == `{value}`]"
            case _:
                raise ValueError(f"Invalid operator: {op}")

        return Query(expression=expr)


class QueryResult(BaseModel):
    """Result of executing a query."""

    commits: Sequence[ExperimentCommit]
    query: Query
    num_searched: int

    @property
    def is_empty(self) -> bool:
        return len(self.commits) == 0

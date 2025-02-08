from typing import Optional

from mthd.domain.experiment import ExperimentRun
from mthd.domain.git import Commit
from mthd.domain.query import Query, QueryResult, SimpleQueryOp, SimpleQueryValue
from mthd.service.git import GitService


class QueryService:
    """Service for querying experiment commits."""

    def __init__(self, git_service: GitService):
        self.git_service = git_service

    def execute(self, query: Query, limit: Optional[int] = None) -> QueryResult:
        """Execute a query against the experiment commit history.

        Args:
            query: The query to execute
            limit: Optional maximum number of results to return

        Returns:
            QueryResult containing matching commits
        """
        commits = self.git_service.get_all_commits()
        total = len(commits)

        # Convert regular commits to experiment commits where possible
        exp_commits = [
            exp_commit for commit in commits
            if (exp_commit := ExperimentCommit.from_commit(commit))
        ]

        # Query on the experiment_run field
        query_str = query.expression.replace("metrics.", "experiment_run.metrics.")
        modified_query = Query(expression=query_str)
        matching = modified_query.compile().search(exp_commits)

        results = matching or []
        if limit and limit > 0:
            results = results[:limit]

        return QueryResult(commits=results, query=query, num_searched=total)

    def execute_simple(
        self,
        metric: str,
        op: SimpleQueryOp,
        value: SimpleQueryValue,
        limit: Optional[int] = None,
    ) -> QueryResult:
        """Convenience method to find experiments by metric value.

        Args:
            metric: Name of the metric to filter on
            op: Comparison operator (">", "<", ">=", "<=", "==")
            value: Value to compare against
            limit: Optional maximum number of results

        Returns:
            QueryResult containing matching commits
        """
        query = Query.where(f"message.metrics.{metric}", op, value)
        return self.execute(query, limit=limit)

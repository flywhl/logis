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
        # Get all commits with experimental metadata
        commits = self.git_service.get_all_commits()
        commits_by_sha = {c.sha: c for c in commits}
        total = len(commits)

        exp_commits = [ExperimentRun.from_commit(commit) for commit in commits]
        # print(exp_commits)

        # Compile and execute the JMESPath query
        jmespath_query = query.compile()
        print(query)
        results: list[Commit] = jmespath_query.search(commits)

        # Handle limit
        # @todo: sort by commit date?
        if limit:
            results = results[:limit]

        return QueryResult(commits=results or [], query=query, num_searched=total)

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

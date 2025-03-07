from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from logis.domain.experiment import ExperimentRun
from logis.domain.git import Commit
from logis.domain.query import Query
from logis.service.git import GitService
from logis.service.query import QueryService


@pytest.fixture
def git_service():
    service = Mock(spec=GitService)
    commits = [
        Commit(
            sha="abc123",
            message='exp: Test 1\n\n---\n\n{"experiment": "test1", "hyperparameters": {}, "metrics": {"accuracy": 0.8, "loss": 0.2}}',
            date=datetime(2024, 1, 1),
        ),
        Commit(
            sha="def456",
            message='exp: Test 2\n\n---\n\n{"experiment": "test2", "hyperparameters": {}, "metrics": {"accuracy": 0.9, "loss": 0.1}}',
            date=datetime(2024, 1, 2),
        ),
    ]
    service.get_all_commits.return_value = commits
    return service


@pytest.fixture
def query_service(git_service: GitService):
    return QueryService(git_service)


# @patch("logis.domain.experiment.ExperimentRun.from_commit")
def test_execute_query(query_service: QueryService):
    # Setup mock experiments
    # mock_from_commit.side_effect = [
    #     ExperimentRun(experiment="test1", hyperparameters={}, metrics={"accuracy": 0.8, "loss": 0.2}),
    #     ExperimentRun(experiment="test2", hyperparameters={}, metrics={"accuracy": 0.9, "loss": 0.1}),
    # ]

    # Test query for high accuracy
    query = Query.where("metrics.accuracy", ">", 0.85)
    result = query_service.execute(query)

    assert len(result.commits) == 1
    assert result.num_searched == 2
    assert result.query == query


@patch("logis.domain.experiment.ExperimentRun.from_commit")
def test_execute_query_with_limit(mock_from_commit, query_service: QueryService):
    # Setup mock experiments
    mock_from_commit.side_effect = [
        ExperimentRun(experiment="test1", hyperparameters={}, metrics={"accuracy": 0.9}),
        ExperimentRun(experiment="test2", hyperparameters={}, metrics={"accuracy": 0.95}),
    ]

    # Test query with limit
    query = Query.where("metrics.accuracy", ">=", 0.9)
    result = query_service.execute(query, limit=1)

    assert len(result.commits) == 1
    assert result.num_searched == 2


@patch("logis.domain.experiment.ExperimentRun.from_commit")
def test_execute_simple(mock_from_commit, query_service: QueryService):
    # Setup mock experiments
    mock_from_commit.side_effect = [
        ExperimentRun(experiment="test1", hyperparameters={}, metrics={"accuracy": 0.9}),
        ExperimentRun(experiment="test2", hyperparameters={}, metrics={"accuracy": 0.95}),
    ]

    # Test query with limit
    result = query_service.execute_simple("metrics.accuracy", "<", 0.95, limit=1)

    assert len(result.commits) == 1
    assert result.num_searched == 2

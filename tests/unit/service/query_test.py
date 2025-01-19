from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from mthd.domain.git import Commit
from mthd.domain.query import Query
from mthd.service.git import GitService
from mthd.service.query import QueryService


@pytest.fixture
def git_service():
    service = Mock(spec=GitService)
    commits = [
        Commit(
            sha="abc123",
            message="Test 1",
            date=datetime(2024, 1, 1),
        ),
        Commit(
            sha="def456",
            message="Test 2", 
            date=datetime(2024, 1, 2),
        ),
    ]
    service.get_all_commits.return_value = commits
    return service


@pytest.fixture
def query_service(git_service):
    return QueryService(git_service)


@patch('mthd.domain.experiment.ExperimentState.parse')
def test_execute_query(mock_parse, query_service):
    # Setup mock parsed experiments
    mock_parse.side_effect = [
        {"accuracy": 0.8, "loss": 0.2},
        {"accuracy": 0.9, "loss": 0.1},
    ]
    
    # Test query for high accuracy
    query = Query.where("accuracy", ">", 0.85)
    result = query_service.execute(query)
    
    assert len(result.commits) == 1
    assert result.num_searched == 2
    assert result.query == query


@patch('mthd.domain.experiment.ExperimentState.parse')
def test_execute_simple_query(mock_parse, query_service):
    # Setup mock parsed experiments
    mock_parse.side_effect = [
        {"metrics": {"loss": 0.2}},
        {"metrics": {"loss": 0.1}},
    ]
    
    # Test simple query for low loss
    result = query_service.execute_simple("loss", "<", 0.15)
    
    assert len(result.commits) == 1
    assert result.num_searched == 2


@patch('mthd.domain.experiment.ExperimentState.parse')
def test_execute_query_with_limit(mock_parse, query_service):
    # Setup mock parsed experiments
    mock_parse.side_effect = [
        {"accuracy": 0.9},
        {"accuracy": 0.95},
    ]
    
    # Test query with limit
    query = Query.where("accuracy", ">=", 0.9)
    result = query_service.execute(query, limit=1)
    
    assert len(result.commits) == 1
    assert result.num_searched == 2

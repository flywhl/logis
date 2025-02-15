import os
import subprocess
import tempfile
import venv

from pathlib import Path
from typing import Generator

import git
import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for the test."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        old_cwd = os.getcwd()
        tmp_path = Path(tmp_dir)
        os.chdir(tmp_path)

        # Initialize git repo
        repo = git.Repo.init()

        # Configure git user for commits
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        # Create and activate a virtual environment
        venv_path = tmp_path / ".venv"
        venv.create(venv_path, with_pip=True)

        # Get the path to the Python executable in the virtual environment
        if os.name == "nt":  # Windows
            python_path = venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            python_path = venv_path / "bin" / "python"

        print(f"Python path: {python_path}")

        # Install logis package in editable mode in the virtual environment
        subprocess.run(
            [str(python_path), "-m", "pip", "install", "-e", str(Path(old_cwd))],
            check=True,
        )

        yield tmp_path
        os.chdir(old_cwd)


def create_experiment_file(temp_dir: Path, iteration: int) -> None:
    """Create or update the experiment file with new parameters."""
    content = f"""
from logis import commit
from pydantic import BaseModel

class Hyperparameters(BaseModel):
    learning_rate: float
    batch_size: int
    epochs: int

class Metrics(BaseModel):
    accuracy: float
    loss: float

@commit(hypers="hypers", implicit=True)
def train_model(hypers: Hyperparameters) -> Metrics:
    # Simulate training
    accuracy = 0.75 + ({iteration} * 0.05)  # Gradually improve accuracy
    loss = 0.5 - ({iteration} * 0.1)        # Gradually decrease loss
    
    return Metrics(
        accuracy=accuracy,
        loss=max(0.1, loss)
    )

if __name__ == "__main__":
    hypers = Hyperparameters(
        learning_rate=0.001 * ({iteration} + 1),
        batch_size=32 * ({iteration} + 1),
        epochs=10 * ({iteration} + 1)
    )
    metrics = train_model(hypers=hypers)
"""

    with open(temp_dir / "experiment.py", "w") as f:
        f.write(content)


def create_run_experiment_file(temp_dir: Path, iteration: int) -> None:
    """Create or update the experiment file using run-based API."""
    content = f"""
from logis import commit
from logis.decorator import Run

@commit
def train_model(run: Run):
    # Set hyperparameters
    run.set_hyperparameters({{
        "learning_rate": 0.001 * ({iteration} + 1),
        "batch_size": 32 * ({iteration} + 1),
        "epochs": 10 * ({iteration} + 1)
    }})
    
    # Simulate training
    accuracy = 0.75 + ({iteration} * 0.05)  # Gradually improve accuracy
    loss = 0.5 - ({iteration} * 0.1)        # Gradually decrease loss
    
    # Set metrics
    run.set_metrics({{
        "accuracy": accuracy,
        "loss": max(0.1, loss)
    }})

if __name__ == "__main__":
    train_model()
"""

    with open(temp_dir / "experiment.py", "w") as f:
        f.write(content)


def test_multiple_experiments(temp_dir: Path):
    """Test running multiple experiments and creating commits."""
    # Get the path to the Python executable in the virtual environment
    if os.name == "nt":  # Windows
        python_path = temp_dir / ".venv" / "Scripts" / "python.exe"
        python_path = temp_dir / ".venv" / "Scripts" / "logis.exe"
    else:  # Unix-like
        python_path = temp_dir / ".venv" / "bin" / "python"
        logis_path = temp_dir / ".venv" / "bin" / "logis"

    # Run multiple iterations of the experiment
    for i in range(4):
        create_experiment_file(temp_dir, i)

        # Run the experiment using the virtualenv python
        subprocess.run(
            [str(python_path), str(temp_dir / "experiment.py")],
            check=True,
        )

    # Verify the commits
    repo = git.Repo(temp_dir)
    commits = list(repo.iter_commits())

    # Should have 4 commits
    assert len(commits) == 4

    # All commits should be experiment commits
    for commit in commits:
        message = commit.message if isinstance(commit.message, str) else commit.message.decode("utf-8")

        assert message.startswith("exp: ")
        assert "metrics" in message
        assert "hyperparameters" in message

    # Test querying for experiments with high accuracy
    result = subprocess.run(
        [str(logis_path), "query", "metrics.accuracy > 0.8"],
        capture_output=True,
        text=True,
        cwd=temp_dir,
    )

    assert result.returncode == 0

    # Should find 2 commits (iterations 2 and 4 have accuracy > 0.8)
    output_lines = result.stdout.strip().split("\n")
    assert len(output_lines) > 0
    assert "Found 2 commit(s)" in output_lines[0]

    # Test querying for experiments with low loss
    result = subprocess.run(
        [str(logis_path), "query", "metrics.loss < 0.5"],
        capture_output=True,
        text=True,
        cwd=temp_dir,
    )

    assert result.returncode == 0

    # Should find 3 commits (iterations 2, 3, and 4 have loss < 0.5)
    output_lines = result.stdout.strip().split("\n")
    assert len(output_lines) > 0
    assert "Found 3 commit(s)" in output_lines[0]


def test_multiple_run_experiments(temp_dir: Path):
    """Test running multiple experiments using run-based API."""
    # Get the path to the Python executable in the virtual environment
    if os.name == "nt":  # Windows
        python_path = temp_dir / ".venv" / "Scripts" / "python.exe"
        logis_path = temp_dir / ".venv" / "Scripts" / "logis.exe"
    else:  # Unix-like
        python_path = temp_dir / ".venv" / "bin" / "python"
        logis_path = temp_dir / ".venv" / "bin" / "logis"

    # Run multiple iterations of the experiment
    for i in range(4):
        create_run_experiment_file(temp_dir, i)

        # Run the experiment using the virtualenv python
        subprocess.run(
            [str(python_path), str(temp_dir / "experiment.py")],
            check=True,
        )

    # Verify the commits
    repo = git.Repo(temp_dir)
    commits = list(repo.iter_commits())

    # Should have 4 commits
    assert len(commits) == 4

    # All commits should be experiment commits
    for commit in commits:
        message = commit.message if isinstance(commit.message, str) else commit.message.decode("utf-8")

        assert message.startswith("exp: ")
        assert "metrics" in message
        assert "hyperparameters" in message

    # Test querying for experiments with high accuracy
    result = subprocess.run(
        [str(logis_path), "query", "metrics.accuracy > 0.8"],
        capture_output=True,
        text=True,
        cwd=temp_dir,
    )

    assert result.returncode == 0

    # Should find 2 commits (iterations 2 and 4 have accuracy > 0.8)
    output_lines = result.stdout.strip().split("\n")
    assert len(output_lines) > 0
    assert "Found 2 commit(s)" in output_lines[0]

    # Test querying for experiments with low loss
    result = subprocess.run(
        [str(logis_path), "query", "metrics.loss < 0.5"],
        capture_output=True,
        text=True,
        cwd=temp_dir,
    )

    assert result.returncode == 0

    # Should find 3 commits (iterations 2, 3, and 4 have loss < 0.5)
    output_lines = result.stdout.strip().split("\n")
    assert len(output_lines) > 0
    assert "Found 3 commit(s)" in output_lines[0]

"""Shared pytest fixtures for Autobot tests."""

import json

import pytest


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory for testing."""
    project = tmp_path / "test_project"
    project.mkdir()
    return project


@pytest.fixture
def mock_claude_dir(temp_project):
    """Create a mock .claude directory."""
    claude_dir = temp_project / ".claude"
    claude_dir.mkdir()
    return claude_dir


@pytest.fixture
def mock_autobot_dir(temp_project):
    """Create a mock .autobot directory with standard files."""
    autobot_dir = temp_project / ".autobot"
    autobot_dir.mkdir()

    # Create minimal state files
    (autobot_dir / "task.json").write_text(
        json.dumps({"id": None, "status": "idle"}), encoding="utf-8"
    )
    (autobot_dir / "plan.json").write_text(
        json.dumps({"subtasks": []}), encoding="utf-8"
    )
    (autobot_dir / "metrics.json").write_text(
        json.dumps({"current_iteration": 0, "max_iterations": 50}), encoding="utf-8"
    )

    return autobot_dir

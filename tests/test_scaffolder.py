"""Tests for autobot.scaffolder module."""

import json

from autobot.scaffolder import check_existing_state, scaffold_project


class TestCheckExistingState:
    """Tests for check_existing_state function."""

    def test_no_directories(self, temp_project):
        """Returns False, False, None when nothing exists."""
        claude_exists, autobot_exists, active_task = check_existing_state(temp_project)
        assert claude_exists is False
        assert autobot_exists is False
        assert active_task is None

    def test_claude_only(self, temp_project):
        """Detects .claude directory without .autobot."""
        (temp_project / ".claude").mkdir()
        claude_exists, autobot_exists, _ = check_existing_state(temp_project)
        assert claude_exists is True
        assert autobot_exists is False

    def test_autobot_only(self, temp_project):
        """Detects .autobot directory without .claude."""
        (temp_project / ".autobot").mkdir()
        claude_exists, autobot_exists, _ = check_existing_state(temp_project)
        assert claude_exists is False
        assert autobot_exists is True

    def test_both_directories(self, temp_project):
        """Detects both directories."""
        (temp_project / ".claude").mkdir()
        (temp_project / ".autobot").mkdir()
        claude_exists, autobot_exists, _ = check_existing_state(temp_project)
        assert claude_exists is True
        assert autobot_exists is True

    def test_autobot_with_idle_task(self, temp_project, mock_autobot_dir):
        """Returns None for idle task."""
        (mock_autobot_dir / "task.json").write_text(
            json.dumps({"id": "task-1", "status": "idle"}), encoding="utf-8"
        )
        _, _, active_task = check_existing_state(temp_project)
        assert active_task is None

    def test_autobot_with_in_progress_task(self, temp_project, mock_autobot_dir):
        """Returns task dict for in_progress task."""
        task_data = {"id": "task-1", "title": "Test Task", "status": "in_progress"}
        (mock_autobot_dir / "task.json").write_text(
            json.dumps(task_data), encoding="utf-8"
        )
        _, _, active_task = check_existing_state(temp_project)
        assert active_task is not None
        assert active_task["status"] == "in_progress"
        assert active_task["title"] == "Test Task"

    def test_autobot_with_paused_task(self, temp_project, mock_autobot_dir):
        """Returns task dict for paused task."""
        task_data = {"id": "task-2", "title": "Paused Task", "status": "paused"}
        (mock_autobot_dir / "task.json").write_text(
            json.dumps(task_data), encoding="utf-8"
        )
        _, _, active_task = check_existing_state(temp_project)
        assert active_task is not None
        assert active_task["status"] == "paused"

    def test_autobot_with_completed_task(self, temp_project, mock_autobot_dir):
        """Returns None for completed task."""
        task_data = {"id": "task-1", "status": "completed"}
        (mock_autobot_dir / "task.json").write_text(
            json.dumps(task_data), encoding="utf-8"
        )
        _, _, active_task = check_existing_state(temp_project)
        assert active_task is None

    def test_autobot_with_invalid_json(self, temp_project, mock_autobot_dir):
        """Handles invalid JSON gracefully."""
        (mock_autobot_dir / "task.json").write_text("not valid json", encoding="utf-8")
        _, _, active_task = check_existing_state(temp_project)
        assert active_task is None


class TestScaffoldProject:
    """Tests for scaffold_project function."""

    def test_creates_claude_directory(self, temp_project):
        """Creates .claude directory."""
        scaffold_project(temp_project)
        assert (temp_project / ".claude").is_dir()

    def test_creates_autobot_directory(self, temp_project):
        """Creates .autobot directory."""
        scaffold_project(temp_project)
        assert (temp_project / ".autobot").is_dir()

    def test_creates_claude_md(self, temp_project):
        """Creates CLAUDE.md in project root."""
        scaffold_project(temp_project)
        assert (temp_project / "CLAUDE.md").is_file()

    def test_creates_settings_json(self, temp_project):
        """Creates .claude/settings.json."""
        scaffold_project(temp_project)
        settings_file = temp_project / ".claude" / "settings.json"
        assert settings_file.is_file()
        # Verify it's valid JSON
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        assert "hooks" in settings or "permissions" in settings

    def test_creates_hooks_directory(self, temp_project):
        """Creates .claude/hooks/ with Python files."""
        scaffold_project(temp_project)
        hooks_dir = temp_project / ".claude" / "hooks"
        assert hooks_dir.is_dir()
        # Should have at least one hook
        py_files = list(hooks_dir.glob("*.py"))
        assert len(py_files) > 0

    def test_returns_created_files_list(self, temp_project):
        """Returns list of created file paths."""
        created = scaffold_project(temp_project)
        assert isinstance(created, list)
        assert len(created) > 0
        # Should include settings.json
        assert any("settings.json" in f for f in created)

    def test_does_not_overwrite_without_force(self, temp_project):
        """Doesn't overwrite existing files without force flag."""
        # Create existing file with custom content
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.json"
        settings_file.write_text('{"custom": "data"}', encoding="utf-8")

        scaffold_project(temp_project, force=False)

        # Original content should be preserved
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        assert settings.get("custom") == "data"

    def test_overwrites_with_force(self, temp_project):
        """Overwrites existing files with force flag."""
        # Create existing file with custom content
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir()
        settings_file = claude_dir / "settings.json"
        settings_file.write_text('{"custom": "data"}', encoding="utf-8")

        scaffold_project(temp_project, force=True)

        # Original content should be replaced
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        assert "custom" not in settings

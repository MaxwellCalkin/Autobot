"""Tests for autobot.cli module."""

import json

from typer.testing import CliRunner

from autobot import __version__
from autobot.cli import app

runner = CliRunner()


class TestVersion:
    """Tests for version display."""

    def test_version_flag(self):
        """--version shows version and exits."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_short_version_flag(self):
        """-v shows version."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestNoArgs:
    """Tests for CLI with no arguments."""

    def test_no_args_shows_help(self):
        """No arguments shows help text (exit code 2 per Typer convention)."""
        result = runner.invoke(app, [])
        assert result.exit_code == 2
        assert "autobot" in result.output.lower()


class TestPositionalTaskShorthand:
    """Tests for 'autobot <task>' shorthand syntax."""

    def test_preprocess_args_inserts_start(self):
        """preprocess_args inserts 'start' for unknown first arg."""
        import sys
        from autobot.cli import preprocess_args

        # Save original argv
        original_argv = sys.argv.copy()

        try:
            # Test: task argument gets 'start' prepended
            sys.argv = ["autobot", "Build a feature"]
            preprocess_args()
            assert sys.argv == ["autobot", "start", "Build a feature"]

            # Test: known command is not modified
            sys.argv = ["autobot", "status"]
            preprocess_args()
            assert sys.argv == ["autobot", "status"]

            # Test: flags are not modified
            sys.argv = ["autobot", "--version"]
            preprocess_args()
            assert sys.argv == ["autobot", "--version"]
        finally:
            # Restore original argv
            sys.argv = original_argv


class TestStatus:
    """Tests for status command."""

    def test_status_not_initialized(self, temp_project, monkeypatch):
        """Shows not initialized message when no .claude or .autobot."""
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["status"])
        assert "not initialized" in result.output.lower()

    def test_status_with_claude_dir(self, temp_project, mock_claude_dir, monkeypatch):
        """Shows status when .claude exists."""
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["status"])
        assert ".claude/" in result.output

    def test_status_with_active_task(
        self, temp_project, mock_claude_dir, mock_autobot_dir, monkeypatch
    ):
        """Shows active task details."""
        # Create in_progress task
        task_data = {"id": "task-1", "title": "Test Task", "status": "in_progress"}
        (mock_autobot_dir / "task.json").write_text(
            json.dumps(task_data), encoding="utf-8"
        )

        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["status"])
        assert "Test Task" in result.output
        assert "in_progress" in result.output


class TestClean:
    """Tests for clean command."""

    def test_clean_nothing_to_remove(self, temp_project, monkeypatch):
        """Shows message when nothing to clean."""
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["clean"])
        assert "No Autobot files found" in result.output

    def test_clean_removes_autobot_dir(self, temp_project, mock_autobot_dir, monkeypatch):
        """Removes .autobot directory with confirmation."""
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["clean", "--yes"])
        assert not (temp_project / ".autobot").exists()
        assert "Removed .autobot/" in result.output

    def test_clean_all_removes_both(
        self, temp_project, mock_claude_dir, mock_autobot_dir, monkeypatch
    ):
        """--all removes both .claude and .autobot."""
        # Create CLAUDE.md too
        (temp_project / "CLAUDE.md").write_text("# Test", encoding="utf-8")

        monkeypatch.chdir(temp_project)
        runner.invoke(app, ["clean", "--all", "--yes"])
        assert not (temp_project / ".autobot").exists()
        assert not (temp_project / ".claude").exists()
        assert not (temp_project / "CLAUDE.md").exists()

    def test_clean_prompts_for_confirmation(self, temp_project, mock_autobot_dir, monkeypatch):
        """Prompts for confirmation without --yes."""
        monkeypatch.chdir(temp_project)
        # Simulate user saying "no"
        runner.invoke(app, ["clean"], input="n\n")
        # Directory should still exist
        assert (temp_project / ".autobot").exists()


class TestInit:
    """Tests for init command."""

    def test_init_creates_directories(self, temp_project, monkeypatch):
        """Creates .claude and .autobot directories."""
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["init"])
        assert (temp_project / ".claude").exists()
        assert (temp_project / ".autobot").exists()
        assert "Autobot initialized" in result.output

    def test_init_prompts_if_exists(self, temp_project, mock_claude_dir, monkeypatch):
        """Prompts for confirmation if directories exist."""
        monkeypatch.chdir(temp_project)
        # Simulate user saying "no"
        result = runner.invoke(app, ["init"], input="n\n")
        assert result.exit_code == 1


class TestStart:
    """Tests for start command."""

    def test_start_dry_run(self, temp_project, monkeypatch):
        """--dry-run shows what would be created without changes."""
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["start", "Test task", "--dry-run"])
        assert "Dry run" in result.output
        assert "Would create" in result.output
        # No directories should be created
        assert not (temp_project / ".claude").exists()
        assert not (temp_project / ".autobot").exists()

    def test_start_no_launch_scaffolds_only(self, temp_project, monkeypatch):
        """--no-launch scaffolds but doesn't launch Claude."""
        monkeypatch.chdir(temp_project)
        result = runner.invoke(app, ["start", "Test task", "--no-launch"])
        assert (temp_project / ".claude").exists()
        assert (temp_project / ".autobot").exists()
        assert "--no-launch specified" in result.output

    def test_start_prompts_reset_when_autobot_exists(
        self, temp_project, mock_autobot_dir, monkeypatch
    ):
        """Prompts to reset state when .autobot/ exists."""
        monkeypatch.chdir(temp_project)
        # Write some content to task.json that would be overwritten
        (mock_autobot_dir / "task.json").write_text(
            '{"id": "old-task", "status": "idle"}', encoding="utf-8"
        )

        # Say yes to reset, use --no-launch
        result = runner.invoke(app, ["start", "New task", "--no-launch"], input="y\n")
        assert result.exit_code == 0

        # task.json should be reset (overwritten with template)
        task_content = (mock_autobot_dir / "task.json").read_text(encoding="utf-8")
        assert "old-task" not in task_content

    def test_start_aborts_when_reset_declined(
        self, temp_project, mock_autobot_dir, monkeypatch
    ):
        """Aborts when user declines to reset state."""
        monkeypatch.chdir(temp_project)
        # Say no to reset
        result = runner.invoke(app, ["start", "New task", "--no-launch"], input="n\n")
        assert result.exit_code == 1

    def test_start_force_skips_prompts(
        self, temp_project, mock_autobot_dir, monkeypatch
    ):
        """--force skips all confirmation prompts."""
        monkeypatch.chdir(temp_project)
        # Write some content that would be overwritten
        (mock_autobot_dir / "task.json").write_text(
            '{"id": "old-task", "status": "idle"}', encoding="utf-8"
        )

        # Use --force, should not prompt
        result = runner.invoke(app, ["start", "New task", "--no-launch", "--force"])
        assert result.exit_code == 0

        # task.json should be overwritten
        task_content = (mock_autobot_dir / "task.json").read_text(encoding="utf-8")
        assert "old-task" not in task_content

"""Tests for autobot.launcher module."""

from unittest.mock import MagicMock, patch

from autobot.launcher import launch_claude_code


class TestLaunchClaudeCode:
    """Tests for launch_claude_code function."""

    @patch("autobot.launcher.subprocess.run")
    def test_launches_claude_with_task(self, mock_run, temp_project):
        """Calls claude with init-task command."""
        mock_run.return_value = MagicMock(returncode=0)

        result = launch_claude_code(temp_project, "Build something")

        assert result == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        # First positional arg should be the command list
        cmd = call_args[0][0]
        assert cmd[0] == "claude"
        assert "/init-task" in cmd[1]
        assert "Build something" in cmd[1]

    @patch("autobot.launcher.subprocess.run")
    def test_returns_claude_exit_code(self, mock_run, temp_project):
        """Returns exit code from claude subprocess."""
        mock_run.return_value = MagicMock(returncode=42)
        result = launch_claude_code(temp_project, "task")
        assert result == 42

    @patch("autobot.launcher.subprocess.run")
    def test_returns_zero_on_success(self, mock_run, temp_project):
        """Returns 0 on successful execution."""
        mock_run.return_value = MagicMock(returncode=0)
        result = launch_claude_code(temp_project, "task")
        assert result == 0

    @patch("autobot.launcher.subprocess.run")
    def test_uses_correct_working_directory(self, mock_run, temp_project):
        """Passes project_dir as cwd to subprocess."""
        mock_run.return_value = MagicMock(returncode=0)

        launch_claude_code(temp_project, "task")

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == temp_project

    @patch("autobot.launcher.subprocess.run")
    def test_does_not_capture_streams(self, mock_run, temp_project):
        """Does not redirect stdin/stdout/stderr."""
        mock_run.return_value = MagicMock(returncode=0)

        launch_claude_code(temp_project, "task")

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["stdin"] is None
        assert call_kwargs["stdout"] is None
        assert call_kwargs["stderr"] is None

    @patch("autobot.launcher.subprocess.run")
    @patch("autobot.launcher.IS_WINDOWS", False)
    def test_file_not_found_returns_1_unix(self, mock_run, temp_project):
        """Returns 1 when claude is not found on Unix."""
        mock_run.side_effect = FileNotFoundError()
        result = launch_claude_code(temp_project, "task")
        assert result == 1

    @patch("autobot.launcher.subprocess.run")
    @patch("autobot.launcher.IS_WINDOWS", True)
    def test_file_not_found_retries_with_shell_windows(self, mock_run, temp_project):
        """Retries with shell=True on Windows when FileNotFoundError."""
        # First call raises FileNotFoundError, second succeeds
        mock_run.side_effect = [FileNotFoundError(), MagicMock(returncode=0)]

        result = launch_claude_code(temp_project, "task")

        assert result == 0
        assert mock_run.call_count == 2
        # Second call should use shell=True
        second_call = mock_run.call_args_list[1]
        assert second_call[1]["shell"] is True

    @patch("autobot.launcher.subprocess.run")
    def test_keyboard_interrupt_returns_130(self, mock_run, temp_project):
        """Returns 130 on keyboard interrupt."""
        mock_run.side_effect = KeyboardInterrupt()
        result = launch_claude_code(temp_project, "task")
        assert result == 130

    @patch("autobot.launcher.subprocess.run")
    def test_prompt_includes_task(self, mock_run, temp_project):
        """Prompt includes the full task description."""
        mock_run.return_value = MagicMock(returncode=0)
        task = "Build a login system with OAuth support"

        launch_claude_code(temp_project, task)

        cmd = mock_run.call_args[0][0]
        assert task in cmd[1]

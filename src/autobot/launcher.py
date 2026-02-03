"""Launcher - Spawn Claude Code subprocess."""

import subprocess
import sys
from pathlib import Path

from rich.console import Console

IS_WINDOWS = sys.platform == "win32"

console = Console()


def launch_claude_code(project_dir: Path, task: str) -> int:
    """Launch Claude Code with the given task.

    Args:
        project_dir: The project directory (cwd for Claude)
        task: The task description to pass to Claude

    Returns:
        Exit code from Claude (0 on success)
    """
    # Build the prompt that includes the task
    # Use /init-task command to start an autonomous task
    prompt = f'/init-task {task}'

    console.print(f"[dim]Working dir: {project_dir}[/dim]")
    console.print()

    try:
        # Launch Claude interactively with the prompt as a positional argument
        # Using shell=False with a list ensures proper argument handling
        # The prompt is passed as a single argument, avoiding shell escaping issues
        result = subprocess.run(
            ["claude", "--dangerously-skip-permissions", prompt],
            cwd=project_dir,
            # Don't redirect any streams - let Claude inherit the terminal fully
            stdin=None,
            stdout=None,
            stderr=None,
            # On Windows, shell=True is needed for .cmd scripts but breaks arg passing
            # Try shell=False first which should work if claude is in PATH as .exe
            shell=False,
        )

        return result.returncode

    except FileNotFoundError:
        # If shell=False fails on Windows, claude might be a .cmd script
        # Try again with shell=True and quoted prompt
        if IS_WINDOWS:
            console.print("[dim]Retrying with shell mode...[/dim]")
            try:
                # For shell=True on Windows, we need to build a command string
                # Use subprocess.list2cmdline for proper escaping
                cmd_str = f'claude --dangerously-skip-permissions {subprocess.list2cmdline([prompt])}'
                result = subprocess.run(
                    cmd_str,
                    cwd=project_dir,
                    shell=True,
                )
                return result.returncode
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")

        console.print()
        console.print("[red]Error:[/red] 'claude' command not found.")
        console.print()
        console.print("Claude Code must be installed to use Autobot.")
        console.print("Install with: [bold]npm install -g @anthropic-ai/claude-code[/bold]")
        console.print()
        console.print("Or visit: https://claude.ai/code")
        return 1

    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Interrupted.[/yellow]")
        return 130

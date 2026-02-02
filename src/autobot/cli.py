"""Autobot CLI - Autonomous development with Claude Code."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from autobot import __version__

# Use ASCII fallback for Windows console encoding issues
if sys.platform == "win32":
    CHECK = "[green]OK[/green]"
    CROSS = "[red]X[/red]"
else:
    CHECK = "[green]\u2713[/green]"
    CROSS = "[red]\u2717[/red]"
from autobot.launcher import launch_claude_code
from autobot.scaffolder import check_existing_state, scaffold_project

app = typer.Typer(
    name="autobot",
    help="Autonomous development assistant for Claude Code",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]autobot[/bold blue] version {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    Autonomous development assistant for Claude Code.

    [bold]Example:[/bold]
        autobot "Build a login system with OAuth support"
    """
    # If a subcommand was invoked, let it handle things
    if ctx.invoked_subcommand is not None:
        return

    # No subcommand - show help
    console.print(ctx.get_help())


@app.command("run", hidden=True)
@app.command()
def start(
    task: str = typer.Argument(
        ...,
        help="The task description for Claude to work on autonomously",
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Overwrite existing .claude and .autobot directories",
    ),
    no_launch: bool = typer.Option(
        False, "--no-launch",
        help="Scaffold only, don't launch Claude Code",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Show what would be created without making changes",
    ),
) -> None:
    """
    Start an autonomous development task with Claude Code.

    [bold]Example:[/bold]
        autobot start "Build a login system with OAuth support"

    This will scaffold the project with Autobot configuration and launch
    Claude Code to work on the task autonomously.
    """

    project_dir = Path.cwd()

    # Show header
    console.print()
    console.print(Panel.fit(
        f"[bold blue]Autobot[/bold blue] v{__version__}\n"
        f"[dim]Task:[/dim] {task[:70]}{'...' if len(task) > 70 else ''}",
        border_style="blue",
    ))
    console.print()

    # Check for existing state
    claude_exists, autobot_exists, active_task = check_existing_state(project_dir)

    # Handle existing directories
    if active_task and not force:
        console.print(f"[red]Active task found:[/red] {active_task.get('title')}")
        console.print(f"Status: {active_task.get('status')}")
        console.print()
        console.print("Options:")
        console.print("  • Use [bold]/resume[/bold] in Claude Code to continue this task")
        console.print("  • Use [bold]/abort[/bold] in Claude Code to cancel it")
        console.print("  • Run [bold]autobot clean[/bold] to remove state")
        console.print("  • Run with [bold]--force[/bold] to overwrite")
        raise typer.Exit(1)

    if (claude_exists or autobot_exists) and not force and not dry_run:
        console.print("[yellow]Existing configuration found.[/yellow]")
        if not typer.confirm("Merge Autobot into existing project?"):
            raise typer.Exit(1)

    # Dry run - just show what would be created
    if dry_run:
        console.print("[yellow]Dry run - no files will be created[/yellow]")
        console.print()
        console.print("Would create:")
        console.print("  .claude/settings.json")
        console.print("  .claude/hooks/ (5 Python scripts)")
        console.print("  .claude/agents/ (4 subagent definitions)")
        console.print("  .claude/commands/ (5 slash commands)")
        console.print("  .claude/skills/ (3 skill definitions)")
        console.print("  .autobot/ (runtime state)")
        console.print("  CLAUDE.md")
        raise typer.Exit()

    # Scaffold the project
    console.print("[bold]Scaffolding project...[/bold]")
    try:
        created_files = scaffold_project(project_dir, force=force)
        console.print(f"{CHECK} Created {len(created_files)} files")
    except Exception as e:
        console.print(f"[red]Error scaffolding project:[/red] {e}")
        raise typer.Exit(1) from None

    console.print()

    if no_launch:
        console.print("[yellow]--no-launch specified.[/yellow]")
        console.print("Run [bold]claude[/bold] to start working.")
        raise typer.Exit()

    # Launch Claude Code
    console.print("[bold]Launching Claude Code...[/bold]")
    console.print()

    exit_code = launch_claude_code(project_dir, task)
    raise typer.Exit(exit_code)


@app.command()
def init(
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Overwrite existing configuration",
    ),
) -> None:
    """
    Initialize Autobot in the current directory without starting a task.

    This scaffolds .claude/ and .autobot/ directories but doesn't launch
    Claude Code. Use this to prepare a project for Autobot.
    """
    project_dir = Path.cwd()

    console.print()
    console.print(Panel.fit(
        f"[bold blue]Autobot Init[/bold blue]\n"
        f"[dim]Directory:[/dim] {project_dir}",
        border_style="blue",
    ))
    console.print()

    # Check for existing state
    claude_exists, autobot_exists, active_task = check_existing_state(project_dir)

    if (claude_exists or autobot_exists) and not force:
        console.print("[yellow]Existing configuration found.[/yellow]")
        if not typer.confirm("Overwrite?"):
            raise typer.Exit(1)

    # Scaffold
    console.print("[bold]Scaffolding...[/bold]")
    try:
        created_files = scaffold_project(project_dir, force=force)
        console.print(f"{CHECK} Created {len(created_files)} files")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None

    console.print()
    console.print("[green]Autobot initialized![/green]")
    console.print()
    console.print("Next steps:")
    console.print("  • Run [bold]autobot \"your task\"[/bold] to start a task")
    console.print("  • Or run [bold]claude[/bold] and use [bold]/init-task[/bold]")


@app.command()
def status() -> None:
    """
    Show Autobot status for the current project.

    Displays whether Autobot is initialized, any active tasks,
    and progress information.
    """
    project_dir = Path.cwd()

    console.print()

    claude_exists, autobot_exists, active_task = check_existing_state(project_dir)

    if not claude_exists and not autobot_exists:
        console.print("[yellow]Autobot not initialized in this directory.[/yellow]")
        console.print("Run [bold]autobot init[/bold] to set up.")
        raise typer.Exit()

    console.print(Panel.fit(
        f"[bold blue]Autobot Status[/bold blue]\n"
        f"[dim]Directory:[/dim] {project_dir}",
        border_style="blue",
    ))
    console.print()

    console.print(f"{CHECK} .claude/ exists" if claude_exists else f"{CROSS} .claude/ missing")
    console.print(f"{CHECK} .autobot/ exists" if autobot_exists else f"{CROSS} .autobot/ missing")

    if active_task:
        console.print()
        console.print(f"[bold]Active Task:[/bold] {active_task.get('title', 'Unknown')}")
        console.print(f"[bold]Status:[/bold] {active_task.get('status', 'unknown')}")

        # Try to load plan for progress
        plan_file = project_dir / ".autobot" / "plan.json"
        if plan_file.exists():
            import json
            plan = json.loads(plan_file.read_text())
            subtasks = plan.get("subtasks", [])
            completed = len([t for t in subtasks if t.get("status") == "completed"])
            total = len(subtasks)
            if total > 0:
                console.print(f"[bold]Progress:[/bold] {completed}/{total} subtasks")
    else:
        console.print()
        console.print("[dim]No active task.[/dim]")


@app.command()
def clean(
    all_: bool = typer.Option(
        False, "--all",
        help="Also remove .claude/ directory (not just .autobot/)",
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    Remove Autobot files from the current project.

    By default, only removes .autobot/ (runtime state).
    Use --all to also remove .claude/ (configuration).
    """
    project_dir = Path.cwd()
    autobot_dir = project_dir / ".autobot"
    claude_dir = project_dir / ".claude"
    claude_md = project_dir / "CLAUDE.md"

    console.print()

    if not autobot_dir.exists() and not claude_dir.exists():
        console.print("[yellow]No Autobot files found.[/yellow]")
        raise typer.Exit()

    # Show what will be removed
    console.print("[bold]Will remove:[/bold]")
    if autobot_dir.exists():
        console.print("  • .autobot/")
    if all_:
        if claude_dir.exists():
            console.print("  • .claude/")
        if claude_md.exists():
            console.print("  • CLAUDE.md")

    console.print()

    if not yes:
        if not typer.confirm("Continue?"):
            raise typer.Exit()

    # Remove directories
    import shutil

    if autobot_dir.exists():
        shutil.rmtree(autobot_dir)
        console.print(f"{CHECK} Removed .autobot/")

    if all_:
        if claude_dir.exists():
            shutil.rmtree(claude_dir)
            console.print(f"{CHECK} Removed .claude/")
        if claude_md.exists():
            claude_md.unlink()
            console.print(f"{CHECK} Removed CLAUDE.md")

    console.print()
    console.print("[green]Cleanup complete.[/green]")


if __name__ == "__main__":
    app()

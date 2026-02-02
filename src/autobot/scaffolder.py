"""Scaffolder - Copy template files to target project."""

import json
from importlib import resources
from importlib.abc import Traversable
from pathlib import Path


def check_existing_state(project_dir: Path) -> tuple[bool, bool, dict | None]:
    """Check for existing .claude and .autobot directories.

    Returns:
        (claude_exists, autobot_exists, active_task_or_none)
    """
    claude_dir = project_dir / ".claude"
    autobot_dir = project_dir / ".autobot"

    claude_exists = claude_dir.exists()
    autobot_exists = autobot_dir.exists()

    active_task = None
    if autobot_exists:
        task_file = autobot_dir / "task.json"
        if task_file.exists():
            try:
                task = json.loads(task_file.read_text(encoding="utf-8"))
                if task.get("status") in ("in_progress", "paused"):
                    active_task = task
            except (OSError, json.JSONDecodeError):
                pass

    return claude_exists, autobot_exists, active_task


def scaffold_project(project_dir: Path, force: bool = False) -> list[str]:
    """Copy all templates to the target project directory.

    Args:
        project_dir: Target directory to scaffold
        force: If True, overwrite existing files

    Returns:
        List of created file paths (relative to project_dir)
    """
    created_files = []

    # Get the templates directory from the package
    templates_path = resources.files("autobot.templates")

    # Scaffold .claude/ directory
    claude_source = templates_path.joinpath("claude")
    claude_dest = project_dir / ".claude"
    created_files.extend(
        _copy_template_tree(claude_source, claude_dest, project_dir, force)
    )

    # Scaffold .autobot/ directory
    autobot_source = templates_path.joinpath("autobot")
    autobot_dest = project_dir / ".autobot"
    created_files.extend(
        _copy_template_tree(autobot_source, autobot_dest, project_dir, force)
    )

    # Copy CLAUDE.md to project root
    claude_md_source = templates_path.joinpath("CLAUDE.md")
    claude_md_dest = project_dir / "CLAUDE.md"
    if _copy_template_file(claude_md_source, claude_md_dest, force):
        created_files.append("CLAUDE.md")

    return created_files


def _copy_template_tree(
    source: Traversable,
    dest: Path,
    project_dir: Path,
    force: bool,
) -> list[str]:
    """Recursively copy a template directory.

    Args:
        source: Source directory (importlib.resources Traversable)
        dest: Destination path
        project_dir: Project root (for relative paths)
        force: Overwrite existing files

    Returns:
        List of created file paths relative to project_dir
    """
    created_files = []
    dest.mkdir(parents=True, exist_ok=True)

    for item in source.iterdir():
        target = dest / item.name

        if item.is_dir():
            created_files.extend(
                _copy_template_tree(item, target, project_dir, force)
            )
        else:
            if _copy_template_file(item, target, force):
                rel_path = target.relative_to(project_dir)
                created_files.append(str(rel_path))

    return created_files


def _copy_template_file(source: Traversable, dest: Path, force: bool) -> bool:
    """Copy a single template file.

    Args:
        source: Source file (importlib.resources Traversable)
        dest: Destination path
        force: Overwrite existing files

    Returns:
        True if file was created, False if skipped
    """
    if dest.exists() and not force:
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)

    # Read content from package resource
    try:
        text_content = source.read_text(encoding="utf-8")
        dest.write_text(text_content, encoding="utf-8")
    except UnicodeDecodeError:
        # Binary file - use read_bytes
        binary_content = source.read_bytes()
        dest.write_bytes(binary_content)

    return True

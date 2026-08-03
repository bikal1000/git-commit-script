"""commit-lint: interactive git commit message helper with staged-diff analysis."""

from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from commitlint import __version__, git_utils
from commitlint.diff_analyzer import parse_name_status
from commitlint.llm import LLMError, suggest_subject_ai
from commitlint.rules import COMMIT_TYPES, suggest_scope, suggest_subject, suggest_type

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    name="commit-lint",
    help="Interactive git commit message helper with staged-diff analysis.",
    add_completion=False,
    invoke_without_command=True,
)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"commit-lint {__version__}")
        raise typer.Exit()


def _gather_analysis() -> tuple[str, str, str, str, str | None]:
    """Returns (suggested_type, suggested_scope, suggested_subject, branch, task_id)."""
    try:
        name_status = git_utils.staged_name_status()
    except git_utils.GitError as exc:
        err_console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if not name_status.strip():
        err_console.print(
            "[red]error:[/red] no staged changes found. Stage files with "
            "`git add` before running commit-lint."
        )
        raise typer.Exit(code=1)

    changes = parse_name_status(name_status)
    branch = git_utils.current_branch()
    task_id = git_utils.task_id_from_branch(branch)

    suggested_type = suggest_type(changes, branch)
    suggested_scope = suggest_scope(changes)
    suggested_subject = suggest_subject(changes)

    return suggested_type, suggested_scope, suggested_subject, branch, task_id


def _build_message(commit_type: str, scope: str, subject: str, task_id: str | None) -> str:
    message = f"{commit_type}({scope}): {subject}"
    if task_id:
        message += f" #{task_id}"
    return message


@app.command()
def commit(
    push: bool = typer.Option(
        False, "--push", "-p", help="Push the current branch after committing."
    ),
    ai: bool = typer.Option(
        False, "--ai", help="Use an OpenAI-compatible API to suggest the commit subject line."
    ),
) -> None:
    """Analyze staged changes and interactively build a commit message."""
    suggested_type, suggested_scope, suggested_subject, branch, task_id = _gather_analysis()

    if ai:
        try:
            suggested_subject = suggest_subject_ai(git_utils.staged_diff())
        except LLMError as exc:
            err_console.print(f"[yellow]warning:[/yellow] AI suggestion failed ({exc}); "
                               "falling back to rule-based subject.")

    console.print(Panel.fit(
        f"branch: [bold]{branch}[/bold]\n"
        f"task id: [bold]{task_id or '(none)'}[/bold]",
        title="commit-lint",
        border_style="cyan",
    ))

    commit_type = Prompt.ask(
        "Commit type", choices=COMMIT_TYPES, default=suggested_type, show_choices=True
    )
    scope = Prompt.ask("Scope", default=suggested_scope)
    scope = scope.strip().replace(" ", "-")
    if not scope:
        err_console.print("[red]error:[/red] scope cannot be empty.")
        raise typer.Exit(code=1)

    subject = Prompt.ask("Subject", default=suggested_subject)
    subject = subject.strip()
    if not subject:
        err_console.print("[red]error:[/red] commit message cannot be empty.")
        raise typer.Exit(code=1)

    message = _build_message(commit_type, scope, subject, task_id)

    console.print(Panel.fit(message, title="final commit message", border_style="green"))
    if not Confirm.ask("Commit with this message?", default=True):
        console.print("Aborted.")
        raise typer.Exit(code=1)

    try:
        git_utils.commit(message)
    except git_utils.GitError as exc:
        err_console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]committed:[/green] {message}")

    if push:
        try:
            git_utils.push(branch)
        except git_utils.GitError as exc:
            err_console.print(f"[red]error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"[green]pushed:[/green] origin/{branch}")


@app.command()
def suggest() -> None:
    """Print a rule-based suggested commit message, non-interactively.

    Used by the installed prepare-commit-msg git hook to pre-fill the
    commit message buffer. Prints nothing (and exits non-zero) if there
    are no staged changes.
    """
    try:
        name_status = git_utils.staged_name_status()
    except git_utils.GitError:
        raise typer.Exit(code=1) from None

    if not name_status.strip():
        raise typer.Exit(code=1)

    changes = parse_name_status(name_status)
    branch = git_utils.current_branch()
    task_id = git_utils.task_id_from_branch(branch)

    commit_type = suggest_type(changes, branch)
    scope = suggest_scope(changes)
    subject = suggest_subject(changes)

    sys.stdout.write(_build_message(commit_type, scope, subject, task_id) + "\n")


@app.command("install-hook")
def install_hook() -> None:
    """Install a prepare-commit-msg git hook that pre-fills suggestions."""
    try:
        hook_path = git_utils.install_prepare_commit_msg_hook()
    except git_utils.GitError as exc:
        err_console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]installed hook:[/green] {hook_path}")


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
    ),
) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(commit)


if __name__ == "__main__":
    app()

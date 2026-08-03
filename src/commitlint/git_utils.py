"""Thin wrappers around git plumbing used by commit-lint."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

TASK_ID_RE = re.compile(r"^([A-Z]+-\d+)")

PREPARE_COMMIT_MSG_HOOK = """#!/usr/bin/env bash
# Installed by commit-lint (https://github.com/bikal1000/git-commit-script)
# Pre-fills the commit message buffer with a rule-based suggestion.

COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="$2"

# Don't touch merges, amends, squashes, or messages passed via -m/-F.
if [[ -n "$COMMIT_SOURCE" ]]; then
    exit 0
fi

if command -v commit-lint >/dev/null 2>&1; then
    SUGGESTION=$(commit-lint suggest 2>/dev/null)
    if [[ -n "$SUGGESTION" ]]; then
        echo "$SUGGESTION" > "$COMMIT_MSG_FILE"
    fi
fi
"""


class GitError(RuntimeError):
    """Raised when a git command fails or the repo state is unusable."""


def _run(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found") from exc
    except subprocess.CalledProcessError as exc:
        raise GitError(exc.stderr.strip() or f"git {' '.join(args)} failed") from exc
    return result.stdout


def repo_root() -> Path:
    return Path(_run(["rev-parse", "--show-toplevel"]).strip())


def current_branch() -> str:
    return _run(["rev-parse", "--abbrev-ref", "HEAD"]).strip()


def task_id_from_branch(branch: str) -> str | None:
    match = TASK_ID_RE.match(branch)
    return match.group(1) if match else None


def staged_name_status() -> str:
    return _run(["diff", "--staged", "--name-status"])


def staged_diff(context_lines: int = 3) -> str:
    return _run(["diff", "--staged", f"-U{context_lines}"])


def has_staged_changes() -> bool:
    return bool(staged_name_status().strip())


def commit(message: str) -> None:
    _run(["commit", "-m", message])


def push(branch: str) -> None:
    _run(["push", "origin", branch])


def install_prepare_commit_msg_hook() -> Path:
    root = repo_root()
    hooks_dir = root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / "prepare-commit-msg"
    hook_path.write_text(PREPARE_COMMIT_MSG_HOOK)
    hook_path.chmod(0o755)
    return hook_path

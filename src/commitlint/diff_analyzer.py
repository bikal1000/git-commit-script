"""Parse `git diff --staged --name-status` output into structured file changes."""

from __future__ import annotations

from dataclasses import dataclass

STATUS_MAP = {
    "A": "added",
    "M": "modified",
    "D": "deleted",
    "R": "renamed",
    "C": "copied",
    "T": "type-changed",
    "U": "unmerged",
}


@dataclass(frozen=True)
class FileChange:
    status: str  # raw single-letter code: A, M, D, R, C, T, U
    path: str  # new/current path
    old_path: str | None = None  # only set for renames/copies

    @property
    def kind(self) -> str:
        return STATUS_MAP.get(self.status, "unknown")


def parse_name_status(output: str) -> list[FileChange]:
    """Parse `git diff --name-status` style output into FileChange objects.

    Rename/copy lines look like: "R100\told/path\tnew/path"
    Regular lines look like: "M\tpath"
    """
    changes: list[FileChange] = []
    for line in output.splitlines():
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        raw_status, *paths = parts
        status = raw_status[0]  # strip similarity score, e.g. R100 -> R
        if status in ("R", "C") and len(paths) >= 2:
            changes.append(FileChange(status=status, path=paths[1], old_path=paths[0]))
        else:
            changes.append(FileChange(status=status, path=paths[0]))
    return changes

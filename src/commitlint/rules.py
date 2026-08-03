"""Heuristic commit type/scope/subject suggestion from staged file changes."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import PurePosixPath

from commitlint.diff_analyzer import FileChange

COMMIT_TYPES = ["Update", "Add", "Change", "Fix", "Refactor", "Remove", "Test", "Docs"]

TEST_PATTERNS = (
    re.compile(r"(^|/)test_[^/]+\.py$"),
    re.compile(r"(^|/)[^/]+_test\.py$"),
    re.compile(r"(^|/)tests/"),
    re.compile(r"(^|/)__tests__/"),
    re.compile(r"\.test\.[jt]sx?$"),
    re.compile(r"\.spec\.[jt]sx?$"),
)

DOC_PATTERNS = (
    re.compile(r"\.md$", re.IGNORECASE),
    re.compile(r"\.rst$", re.IGNORECASE),
    re.compile(r"(^|/)docs/"),
)

FIX_BRANCH_PATTERN = re.compile(r"(fix|bug|hotfix)", re.IGNORECASE)


def _is_test_file(path: str) -> bool:
    return any(p.search(path) for p in TEST_PATTERNS)


def _is_doc_file(path: str) -> bool:
    return any(p.search(path) for p in DOC_PATTERNS)


def suggest_type(changes: list[FileChange], branch: str) -> str:
    if not changes:
        return "Change"

    if all(c.status == "A" for c in changes):
        return "Add"
    if all(c.status == "D" for c in changes):
        return "Remove"
    if all(_is_test_file(c.path) for c in changes):
        return "Test"
    if all(_is_doc_file(c.path) for c in changes):
        return "Docs"
    if FIX_BRANCH_PATTERN.search(branch or ""):
        return "Fix"
    return "Change"


def _top_level(path: str) -> str:
    parts = PurePosixPath(path).parts
    return parts[0] if len(parts) > 1 else ""


def suggest_scope(changes: list[FileChange]) -> str:
    if not changes:
        return "root"

    if len(changes) == 1:
        return PurePosixPath(changes[0].path).stem

    top_levels = [_top_level(c.path) for c in changes]
    non_root = [t for t in top_levels if t]

    if not non_root:
        return "root"

    counts = Counter(non_root)
    most_common, count = counts.most_common(1)[0]

    if len(non_root) != len(top_levels) or count != len(top_levels):
        # mixed: some files at repo root, or scattered across multiple directories
        if len(counts) == 1 and count == len(top_levels):
            return most_common
        return "root"

    return most_common


def suggest_subject(changes: list[FileChange]) -> str:
    if not changes:
        return "update files"

    verbs = {"A": "add", "M": "update", "D": "remove", "R": "rename", "C": "copy"}
    first = changes[0]
    verb = verbs.get(first.status, "update")
    name = PurePosixPath(first.path).name

    remaining = len(changes) - 1
    if remaining == 0:
        return f"{verb} {name}"
    if remaining == 1:
        return f"{verb} {name} and 1 other file"
    return f"{verb} {name} and {remaining} other files"

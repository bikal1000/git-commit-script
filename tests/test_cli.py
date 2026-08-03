from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from commitlint import git_utils
from commitlint.cli import app

runner = CliRunner()


@pytest.fixture
def mock_git(monkeypatch):
    # Patch functions on the real git_utils module so git_utils.GitError
    # (used in `except` clauses) stays the genuine exception class.
    monkeypatch.setattr(git_utils, "staged_name_status", MagicMock(
        return_value="M\tsrc/auth.py\nA\tsrc/login.py\n"
    ))
    monkeypatch.setattr(git_utils, "staged_diff", MagicMock(return_value=""))
    monkeypatch.setattr(git_utils, "current_branch", MagicMock(
        return_value="XP-1548-feature-branch"
    ))
    monkeypatch.setattr(git_utils, "task_id_from_branch", MagicMock(return_value="XP-1548"))
    monkeypatch.setattr(git_utils, "commit", MagicMock())
    monkeypatch.setattr(git_utils, "push", MagicMock())
    monkeypatch.setattr(git_utils, "install_prepare_commit_msg_hook", MagicMock())
    return git_utils


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "commit-lint" in result.stdout


def test_commit_no_staged_changes(mock_git):
    mock_git.staged_name_status.return_value = ""
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 1
    assert "no staged changes" in result.output


def test_commit_no_staged_changes_error_from_git(mock_git):
    mock_git.staged_name_status.side_effect = git_utils.GitError("not a git repository")
    result = runner.invoke(app, ["commit"])
    assert result.exit_code == 1
    assert "not a git repository" in result.output


def test_commit_accepts_suggestions_and_commits(mock_git):
    # Enter accepts each suggestion (type, scope, subject), then "y" confirms.
    result = runner.invoke(app, ["commit"], input="\n\n\ny\n")
    assert result.exit_code == 0
    mock_git.commit.assert_called_once()
    message = mock_git.commit.call_args[0][0]
    assert message == "Change(src): update auth.py and 1 other file #XP-1548"
    mock_git.push.assert_not_called()


def test_commit_override_all_fields(mock_git):
    result = runner.invoke(
        app, ["commit"], input="Fix\nauth\nhandle expired tokens\ny\n"
    )
    assert result.exit_code == 0
    message = mock_git.commit.call_args[0][0]
    assert message == "Fix(auth): handle expired tokens #XP-1548"


def test_commit_aborted_on_no_confirmation(mock_git):
    result = runner.invoke(app, ["commit"], input="\n\n\nn\n")
    assert result.exit_code == 1
    mock_git.commit.assert_not_called()


def test_commit_omits_task_id_when_branch_has_no_match(mock_git):
    mock_git.task_id_from_branch.return_value = None
    result = runner.invoke(app, ["commit"], input="\n\n\ny\n")
    assert result.exit_code == 0
    message = mock_git.commit.call_args[0][0]
    assert message == "Change(src): update auth.py and 1 other file"
    assert "#" not in message


def test_commit_with_push_flag(mock_git):
    result = runner.invoke(app, ["commit", "--push"], input="\n\n\ny\n")
    assert result.exit_code == 0
    mock_git.push.assert_called_once_with("XP-1548-feature-branch")


def test_commit_empty_scope_aborts(mock_git):
    result = runner.invoke(app, ["commit"], input="\n \n")
    assert result.exit_code == 1
    assert "scope cannot be empty" in result.output
    mock_git.commit.assert_not_called()


def test_suggest_prints_message(mock_git):
    result = runner.invoke(app, ["suggest"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "Change(src): update auth.py and 1 other file #XP-1548"


def test_suggest_no_staged_changes_exits_nonzero(mock_git):
    mock_git.staged_name_status.return_value = ""
    result = runner.invoke(app, ["suggest"])
    assert result.exit_code == 1
    assert result.stdout.strip() == ""


def test_install_hook(mock_git, tmp_path):
    mock_git.install_prepare_commit_msg_hook.return_value = tmp_path / "prepare-commit-msg"
    result = runner.invoke(app, ["install-hook"])
    assert result.exit_code == 0
    assert "installed hook" in result.stdout


def test_default_invocation_runs_commit(mock_git):
    result = runner.invoke(app, [], input="\n\n\ny\n")
    assert result.exit_code == 0
    mock_git.commit.assert_called_once()

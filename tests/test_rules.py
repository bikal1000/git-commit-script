from commitlint.diff_analyzer import FileChange
from commitlint.rules import suggest_scope, suggest_subject, suggest_type


def fc(status, path):
    return FileChange(status=status, path=path)


class TestSuggestType:
    def test_all_added_is_add(self):
        changes = [fc("A", "src/a.py"), fc("A", "src/b.py")]
        assert suggest_type(changes, "feature-branch") == "Add"

    def test_all_deleted_is_remove(self):
        changes = [fc("D", "src/a.py"), fc("D", "src/b.py")]
        assert suggest_type(changes, "feature-branch") == "Remove"

    def test_all_test_files_is_test(self):
        changes = [fc("M", "tests/test_foo.py"), fc("A", "tests/test_bar.py")]
        assert suggest_type(changes, "feature-branch") == "Test"

    def test_all_doc_files_is_docs(self):
        changes = [fc("M", "README.md"), fc("A", "docs/guide.rst")]
        assert suggest_type(changes, "feature-branch") == "Docs"

    def test_fix_branch_name_is_fix(self):
        changes = [fc("M", "src/a.py")]
        assert suggest_type(changes, "XP-1548-fix-login-bug") == "Fix"
        assert suggest_type(changes, "hotfix-payment") == "Fix"

    def test_default_is_change(self):
        changes = [fc("M", "src/a.py"), fc("A", "src/b.py")]
        assert suggest_type(changes, "feature-branch") == "Change"

    def test_no_changes_defaults_to_change(self):
        assert suggest_type([], "feature-branch") == "Change"

    def test_mixed_added_and_modified_is_not_add(self):
        changes = [fc("A", "src/a.py"), fc("M", "src/b.py")]
        assert suggest_type(changes, "feature-branch") == "Change"


class TestSuggestScope:
    def test_single_file_uses_stem(self):
        changes = [fc("M", "src/auth.py")]
        assert suggest_scope(changes) == "auth"

    def test_common_top_level_directory(self):
        changes = [fc("M", "src/a.py"), fc("M", "src/b.py"), fc("A", "src/c.py")]
        assert suggest_scope(changes) == "src"

    def test_mixed_top_level_dirs_is_root(self):
        changes = [fc("M", "src/a.py"), fc("M", "docs/b.md")]
        assert suggest_scope(changes) == "root"

    def test_root_level_files_is_root(self):
        changes = [fc("M", "README.md"), fc("M", "LICENSE")]
        assert suggest_scope(changes) == "root"

    def test_empty_changes_is_root(self):
        assert suggest_scope([]) == "root"


class TestSuggestSubject:
    def test_single_file_modified(self):
        changes = [fc("M", "src/auth.py")]
        assert suggest_subject(changes) == "update auth.py"

    def test_single_file_added(self):
        changes = [fc("A", "src/auth.py")]
        assert suggest_subject(changes) == "add auth.py"

    def test_two_files(self):
        changes = [fc("M", "src/auth.py"), fc("M", "src/login.py")]
        assert suggest_subject(changes) == "update auth.py and 1 other file"

    def test_many_files(self):
        changes = [fc("M", "src/auth.py"), fc("M", "src/b.py"), fc("M", "src/c.py")]
        assert suggest_subject(changes) == "update auth.py and 2 other files"

    def test_empty_changes(self):
        assert suggest_subject([]) == "update files"

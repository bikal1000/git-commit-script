from commitlint.diff_analyzer import FileChange, parse_name_status


def test_parses_added_modified_deleted():
    output = "A\tsrc/new_file.py\nM\tsrc/existing.py\nD\tsrc/old_file.py\n"
    changes = parse_name_status(output)
    assert changes == [
        FileChange(status="A", path="src/new_file.py"),
        FileChange(status="M", path="src/existing.py"),
        FileChange(status="D", path="src/old_file.py"),
    ]


def test_parses_rename_with_similarity_score():
    output = "R100\told/path.py\tnew/path.py\n"
    changes = parse_name_status(output)
    assert changes == [
        FileChange(status="R", path="new/path.py", old_path="old/path.py"),
    ]


def test_kind_property_maps_status_codes():
    changes = parse_name_status("A\tfoo.py\n")
    assert changes[0].kind == "added"


def test_ignores_blank_lines():
    output = "\nA\tfoo.py\n\n\nM\tbar.py\n"
    changes = parse_name_status(output)
    assert len(changes) == 2


def test_empty_output_returns_empty_list():
    assert parse_name_status("") == []


def test_unknown_status_code_kind():
    changes = parse_name_status("X\tweird.py\n")
    assert changes[0].kind == "unknown"

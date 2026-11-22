import json

import pytest

from marketcouncil.context import load_research_context_json


def test_loads_valid_context_object(tmp_path):
    path = tmp_path / "context.json"
    path.write_text(json.dumps({"fundamentals": {"revenue_growth": 0.2}, "sources": []}))
    assert load_research_context_json(path)["fundamentals"]["revenue_growth"] == 0.2


def test_rejects_non_object_root(tmp_path):
    path = tmp_path / "context.json"
    path.write_text('["not", "an", "object"]')
    with pytest.raises(ValueError, match="root must be an object"):
        load_research_context_json(path)


def test_rejects_nonstandard_nan(tmp_path):
    path = tmp_path / "context.json"
    path.write_text('{"value": NaN}')
    with pytest.raises(ValueError, match="non-standard JSON"):
        load_research_context_json(path)


def test_rejects_too_large_context(tmp_path):
    from marketcouncil.context import MAX_CONTEXT_BYTES

    path = tmp_path / "context.json"
    path.write_text(" " * (MAX_CONTEXT_BYTES + 1))
    with pytest.raises(ValueError, match="exceeds"):
        load_research_context_json(path)


def test_rejects_excessive_nesting(tmp_path):
    path = tmp_path / "context.json"
    path.write_text('{"a":' * 24 + '0' + '}' * 24)
    with pytest.raises(ValueError, match="nesting depth"):
        load_research_context_json(path)


def test_rejects_duplicate_object_keys(tmp_path):
    path = tmp_path / "context.json"
    path.write_text('{"fundamentals": {"revenue": 10, "revenue": 20}}')
    with pytest.raises(ValueError, match="duplicate JSON object key"):
        load_research_context_json(path)


def test_rejects_parser_recursion_before_tree_validation(tmp_path):
    path = tmp_path / "context.json"
    depth = 10_000
    path.write_text('{"a":' * depth + "0" + "}" * depth)
    with pytest.raises(ValueError, match="cannot parse research context JSON"):
        load_research_context_json(path)


def test_size_limit_is_checked_on_bytes_read(tmp_path):
    from marketcouncil.context import MAX_CONTEXT_BYTES

    path = tmp_path / "context.json"
    path.write_bytes(b" " * (MAX_CONTEXT_BYTES + 1))
    with pytest.raises(ValueError, match="exceeds"):
        load_research_context_json(path)

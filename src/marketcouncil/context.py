"""Safe, bounded loading of trader-supplied JSON research context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_CONTEXT_BYTES = 1_000_000
MAX_CONTEXT_DEPTH = 20
MAX_CONTEXT_NODES = 100_000


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant is not allowed: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate keys instead of silently accepting the last occurrence."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key is not allowed: {key}")
        result[key] = value
    return result


def _validate_tree(value: Any, *, depth: int = 0, counter: list[int] | None = None) -> None:
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > MAX_CONTEXT_NODES:
        raise ValueError("research context contains too many JSON values")
    if depth > MAX_CONTEXT_DEPTH:
        raise ValueError("research context exceeds the maximum nesting depth")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or len(key) > 256:
                raise ValueError("research context object keys must be strings of at most 256 characters")
            _validate_tree(item, depth=depth + 1, counter=counter)
    elif isinstance(value, list):
        for item in value:
            _validate_tree(item, depth=depth + 1, counter=counter)
    elif isinstance(value, str):
        if len(value) > 100_000:
            raise ValueError("research context string values cannot exceed 100,000 characters")
    elif value is None or isinstance(value, (bool, int, float)):
        if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
            raise ValueError("research context numeric values must be finite")
    else:
        raise ValueError(f"unsupported research context value: {type(value).__name__}")


def load_research_context_json(path: str | Path) -> dict[str, Any]:
    """Load a bounded JSON object; embedded text is treated as untrusted evidence."""
    source = Path(path)
    try:
        # Read one byte beyond the limit so a file that grows after an earlier
        # stat() cannot bypass the size check (TOCTOU).
        with source.open("rb") as handle:
            raw_bytes = handle.read(MAX_CONTEXT_BYTES + 1)
    except OSError as exc:
        raise ValueError(f"cannot access research context file: {exc}") from exc
    if len(raw_bytes) > MAX_CONTEXT_BYTES:
        raise ValueError(f"research context exceeds the {MAX_CONTEXT_BYTES}-byte limit")
    try:
        raw = raw_bytes.decode("utf-8")
        payload = json.loads(
            raw,
            parse_constant=_reject_constant,
            object_pairs_hook=_unique_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"cannot parse research context JSON: {type(exc).__name__}") from exc
    if not isinstance(payload, dict):
        raise ValueError("research context JSON root must be an object")
    _validate_tree(payload)
    return payload

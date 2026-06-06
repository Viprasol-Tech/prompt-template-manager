"""Unit tests for :mod:`prompt_template_manager.registry`."""

from __future__ import annotations

import pytest

from prompt_template_manager.registry import (
    DuplicateVersionError,
    PromptRegistry,
    TemplateNotFoundError,
)
from prompt_template_manager.template import PromptTemplate


def _registry() -> PromptRegistry:
    registry = PromptRegistry()
    registry.register(PromptTemplate(name="sum", version=1, body="v1 {text}"))
    registry.register(PromptTemplate(name="sum", version=3, body="v3 {text}"))
    registry.register(PromptTemplate(name="sum", version=2, body="v2 {text}"))
    return registry


def test_latest_returns_highest_version() -> None:
    registry = _registry()
    assert registry.latest("sum").version == 3
    assert registry.get("sum").version == 3


def test_get_specific_version() -> None:
    registry = _registry()
    assert registry.get("sum", version=2).body == "v2 {text}"


def test_list_versions_sorted() -> None:
    assert _registry().list_versions("sum") == [1, 2, 3]


def test_names() -> None:
    registry = _registry()
    registry.register(PromptTemplate(name="greet", version=1, body="hi {who}"))
    assert registry.names() == ["greet", "sum"]


def test_unknown_name_raises() -> None:
    registry = _registry()
    with pytest.raises(TemplateNotFoundError):
        registry.get("missing")
    with pytest.raises(TemplateNotFoundError):
        registry.list_versions("missing")


def test_unknown_version_raises() -> None:
    with pytest.raises(TemplateNotFoundError):
        _registry().get("sum", version=99)


def test_duplicate_version_raises() -> None:
    registry = _registry()
    with pytest.raises(DuplicateVersionError):
        registry.register(PromptTemplate(name="sum", version=1, body="dup {text}"))


def test_register_returns_template() -> None:
    registry = PromptRegistry()
    template = PromptTemplate(name="x", version=1, body="{a}")
    assert registry.register(template) is template

"""Unit tests for :mod:`prompt_template_manager.template`."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from prompt_template_manager.template import (
    MissingVariableError,
    PromptTemplate,
    extract_variables,
)


def test_extract_variables_detects_required() -> None:
    body = "Hello {name}, your order {order_id} for {name} ships {when}."
    assert extract_variables(body) == ["name", "order_id", "when"]


def test_extract_variables_ignores_escaped_braces() -> None:
    body = "Use {{literal}} braces but render {value}."
    assert extract_variables(body) == ["value"]


def test_required_variables_property() -> None:
    template = PromptTemplate(name="t", version=1, body="{a} and {b}")
    assert template.required_variables == ["a", "b"]


def test_render_substitutes_correctly() -> None:
    template = PromptTemplate(name="greet", version=1, body="Hi {name}, you are {age}.")
    assert template.render(name="Ada", age=36) == "Hi Ada, you are 36."


def test_render_collapses_escaped_braces() -> None:
    template = PromptTemplate(name="json", version=1, body='{{"key": {value}}}')
    assert template.render(value=7) == '{"key": 7}'


def test_render_missing_variable_raises() -> None:
    template = PromptTemplate(name="t", version=1, body="{a} {b}")
    with pytest.raises(MissingVariableError) as exc:
        template.render(a="x")
    assert exc.value.missing == ["b"]


def test_render_ignores_extra_variables() -> None:
    template = PromptTemplate(name="t", version=1, body="Just {a}.")
    assert template.render(a="one", unused="ignored") == "Just one."


def test_no_placeholder_renders_unchanged() -> None:
    template = PromptTemplate(name="t", version=1, body="No vars here.")
    assert template.required_variables == []
    assert template.render() == "No vars here."


def test_malformed_brace_rejected() -> None:
    with pytest.raises(ValidationError):
        PromptTemplate(name="t", version=1, body="dangling { brace")


def test_version_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        PromptTemplate(name="t", version=0, body="x")

"""Versioned, validated prompt templates with ``{variable}`` rendering.

A :class:`PromptTemplate` wraps a body string that uses ``{variable}``
placeholders. The set of required variables is parsed directly from the body,
literal braces are written as ``{{`` and ``}}``, and :meth:`PromptTemplate.render`
substitutes supplied values while raising on any missing required variable.

Part of Prompt Template Manager by Viprasol Tech Private Limited
(https://viprasol.com).
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

#: Matches a single ``{name}`` placeholder. Doubled braces (``{{`` / ``}}``)
#: are handled separately as escaped literals and never matched here.
_PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

#: A valid placeholder identifier (Python-style: letter/underscore then alnum).
_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class MissingVariableError(KeyError):
    """Raised when :meth:`PromptTemplate.render` is missing a required variable."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = sorted(missing)
        joined = ", ".join(self.missing)
        super().__init__(f"missing required variable(s): {joined}")


def extract_variables(body: str) -> list[str]:
    """Return the sorted, de-duplicated required variables found in ``body``.

    Placeholders are written ``{name}``. Literal braces are escaped by doubling
    (``{{`` and ``}}``) and are ignored. The result is sorted for determinism.

    Args:
        body: The template body to scan.

    Returns:
        Sorted list of unique variable names referenced by the body.
    """
    # Remove escaped literal braces first so ``{{name}}`` is not parsed as a
    # placeholder named ``name``.
    stripped = body.replace("{{", "").replace("}}", "")
    found = {match.group(1) for match in _PLACEHOLDER.finditer(stripped)}
    return sorted(found)


def _render_body(body: str, values: dict[str, str]) -> str:
    """Substitute ``{name}`` placeholders in ``body`` from ``values``.

    Escaped braces ``{{`` and ``}}`` collapse to single literal braces. All
    required names are assumed present in ``values`` (the caller validates).
    """

    def _replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token == "{{":
            return "{"
        if token == "}}":
            return "}"
        return values[match.group(1)]

    # One pass over escaped braces and real placeholders, left to right, so an
    # escaped brace adjacent to a placeholder is resolved unambiguously.
    pattern = re.compile(r"\{\{|\}\}|\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
    return pattern.sub(_replace, body)


class PromptTemplate(BaseModel):
    """A named, versioned prompt template with ``{variable}`` placeholders.

    Attributes:
        name: Logical name of the template (e.g. ``"summarize"``).
        version: Integer version, increasing over time (``>= 1``).
        body: Template text containing ``{variable}`` placeholders.
    """

    name: str = Field(min_length=1)
    version: int = Field(ge=1)
    body: str

    model_config = {"frozen": True}

    @field_validator("body")
    @classmethod
    def _validate_body(cls, value: str) -> str:
        """Reject bodies with unbalanced or malformed single braces."""
        # After removing escaped pairs and valid placeholders, no stray single
        # brace may remain — that would indicate a malformed placeholder.
        residue = value.replace("{{", "").replace("}}", "")
        residue = _PLACEHOLDER.sub("", residue)
        if "{" in residue or "}" in residue:
            raise ValueError(
                "unbalanced or malformed brace in body; use '{name}' for "
                "placeholders and '{{'/'}}' for literal braces"
            )
        return value

    @property
    def required_variables(self) -> list[str]:
        """Sorted list of variables this template requires for rendering."""
        return extract_variables(self.body)

    def render(self, **values: Any) -> str:
        """Render the template, substituting ``values`` into placeholders.

        Args:
            **values: Mapping of variable name to value. Each value is coerced
                to ``str``. Extra values not referenced by the body are ignored.

        Returns:
            The fully rendered string with all placeholders substituted and
            escaped braces collapsed to single literals.

        Raises:
            MissingVariableError: If any required variable is absent from
                ``values``.
        """
        required = set(self.required_variables)
        provided = set(values)
        missing = required - provided
        if missing:
            raise MissingVariableError(list(missing))
        coerced = {key: str(val) for key, val in values.items() if key in required}
        return _render_body(self.body, coerced)

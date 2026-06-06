"""Prompt Template Manager — versioned, validated prompt templates.

Part of Prompt Template Manager by Viprasol Tech Private Limited
(https://viprasol.com).
"""

from __future__ import annotations

from prompt_template_manager.registry import PromptRegistry
from prompt_template_manager.template import (
    MissingVariableError,
    PromptTemplate,
    extract_variables,
)

__version__ = "0.1.0"

__all__ = [
    "MissingVariableError",
    "PromptRegistry",
    "PromptTemplate",
    "__version__",
    "extract_variables",
]

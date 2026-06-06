"""A registry for managing multiple versions of named prompt templates.

:class:`PromptRegistry` stores templates keyed by name, keeping every
registered version. Callers can fetch the latest version of a name, a specific
version, or list all known versions.

Part of Prompt Template Manager by Viprasol Tech Private Limited
(https://viprasol.com).
"""

from __future__ import annotations

from prompt_template_manager.template import PromptTemplate


class TemplateNotFoundError(KeyError):
    """Raised when a requested template name or version is not registered."""


class DuplicateVersionError(ValueError):
    """Raised when registering a (name, version) pair that already exists."""


class PromptRegistry:
    """An in-memory store of versioned :class:`PromptTemplate` objects.

    Templates are grouped by :attr:`PromptTemplate.name`; within a name each
    :attr:`PromptTemplate.version` is stored once. The registry never mutates a
    template — it only indexes the immutable objects it is given.
    """

    def __init__(self) -> None:
        """Create an empty registry."""
        self._templates: dict[str, dict[int, PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> PromptTemplate:
        """Register ``template`` under its name and version.

        Args:
            template: The template to store.

        Returns:
            The same template, for convenient chaining.

        Raises:
            DuplicateVersionError: If this exact name and version already exists.
        """
        versions = self._templates.setdefault(template.name, {})
        if template.version in versions:
            raise DuplicateVersionError(
                f"template '{template.name}' version {template.version} already registered"
            )
        versions[template.version] = template
        return template

    def names(self) -> list[str]:
        """Return the sorted list of registered template names."""
        return sorted(self._templates)

    def list_versions(self, name: str) -> list[int]:
        """Return the sorted version numbers registered for ``name``.

        Args:
            name: The template name to inspect.

        Returns:
            Ascending list of version numbers.

        Raises:
            TemplateNotFoundError: If ``name`` is not registered.
        """
        if name not in self._templates:
            raise TemplateNotFoundError(f"no template named '{name}'")
        return sorted(self._templates[name])

    def get(self, name: str, version: int | None = None) -> PromptTemplate:
        """Fetch a template by name, defaulting to its latest version.

        Args:
            name: The template name to fetch.
            version: Specific version to fetch. When ``None`` (the default), the
                highest registered version is returned.

        Returns:
            The matching :class:`PromptTemplate`.

        Raises:
            TemplateNotFoundError: If the name, or the specific version, is not
                registered.
        """
        if name not in self._templates:
            raise TemplateNotFoundError(f"no template named '{name}'")
        versions = self._templates[name]
        if version is None:
            latest = max(versions)
            return versions[latest]
        if version not in versions:
            raise TemplateNotFoundError(
                f"template '{name}' has no version {version}; available: {sorted(versions)}"
            )
        return versions[version]

    def latest(self, name: str) -> PromptTemplate:
        """Return the highest-numbered version registered for ``name``.

        Args:
            name: The template name to fetch.

        Returns:
            The latest :class:`PromptTemplate` for ``name``.

        Raises:
            TemplateNotFoundError: If ``name`` is not registered.
        """
        return self.get(name, version=None)

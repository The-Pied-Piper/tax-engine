"""EnglishRendererRegistry: the English text of each trace line class, by line class.

A renderer registers itself with `@english_renderer`, in the module beside its line class's
feature (a jurisdiction package's own lines included); EnglishTraceRenderer looks renderers up by
the exact class of each line. Renderers are keyed by their line class's module and qualified
name.
"""

from __future__ import annotations

from typing import Any, Protocol, cast

from tax_calculator.adapters.inbound.trace_english.line_renderer import LineRenderer
from tax_calculator.domain.errors import DuplicateRegistrationError, UnknownRegistrationError
from tax_calculator.domain.registry import Registry
from tax_calculator.domain.trace import TraceLine


class RendererClass[L: TraceLine, R](Protocol):
    """A renderer class as `@english_renderer` sees it: its line class, `render` and constructor.

    Matching both `line_class` and `render` against one `L` is what lets mypy reject a renderer
    whose `render` takes another line class than its `line_class`; `line_class` must be a class
    attribute.
    """

    line_class: type[L]

    def render(self, renderer: R, line: L, /) -> str:
        """The class's `render`, unbound: called with an instance and a line of `line_class`."""
        ...

    def __call__(self) -> R:
        """Construct the renderer."""
        ...


class EnglishRendererRegistry(Registry[object]):
    """Holds one renderer per trace line class; lookups by `type[L]` give `LineRenderer[L]`.

    Its string keys are line classes' module and qualified names; register renderers with
    `register_class` or `@english_renderer`. A subclass of a registered line class has no
    renderer until one is registered for it.
    """

    def for_line_class[L: TraceLine](self, line_class: type[L]) -> LineRenderer[L]:
        """The renderer registered for exactly `line_class`."""
        key = self._key(line_class)
        try:
            found = self.get(key)
        except UnknownRegistrationError:
            raise UnknownRegistrationError(
                f"no English renderer is registered for trace line {line_class.__name__}"
            ) from None
        registered = getattr(found, "line_class", None)
        if registered is not line_class:
            other = "another class of that module and name" if registered else "no renderer"
            raise UnknownRegistrationError(
                f"no English renderer is registered for trace line {line_class.__name__}: "
                f"{key!r} holds {other}"
            )
        # Safe: the found object renders exactly `line_class`.
        return cast(LineRenderer[L], found)

    def register_class[L: TraceLine, R: LineRenderer[Any]](
        self, cls: RendererClass[L, R]
    ) -> type[R]:
        """Register an instance of `cls` under its line class and return the class unchanged."""
        key = self._key(cls.line_class)
        if key in self.identifiers():
            registered = getattr(self.get(key), "line_class", None)
            if registered is cls.line_class:
                raise DuplicateRegistrationError(
                    f"an English renderer for trace line {cls.line_class.__name__} is already "
                    "registered"
                )
            raise DuplicateRegistrationError(
                f"{key!r} is already registered, for another trace line class of that module "
                "and name"
            )
        renderer = cls()
        self.register(key, renderer)
        # `cls` is typed as the RendererClass protocol, not as a class; `type(renderer)` is the
        # same class at run time and gives mypy `type[R]`, with no cast.
        return type(renderer)

    @staticmethod
    def _key(line_class: type[TraceLine]) -> str:
        """The string key of `line_class`: its module and qualified name."""
        return f"{line_class.__module__}.{line_class.__qualname__}"


def english_renderer[L: TraceLine, R: LineRenderer[Any]](cls: RendererClass[L, R]) -> type[R]:
    """Class decorator registering an instance of a renderer class in the shared registry.

    A renderer whose `render` takes another line class than its `line_class` fails `mypy .` here
    with "Cannot infer value of type parameter".
    """
    return EnglishRendererRegistry.shared().register_class(cls)

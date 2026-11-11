"""English text for the trace line of `tax_engine.domain.trace.forms`:
one renderer class, registered
with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.names import EnglishNames, short_form_title
from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.adapters.inbound.trace_english.renderer import EnglishTraceRenderer
from tax_engine.domain.trace.forms import FormInstanceLine


@english_renderer
class FormInstanceRenderer:
    """English text for FormInstanceLine."""

    line_class = FormInstanceLine

    def render(self, line: FormInstanceLine, names: EnglishNames) -> str:
        """The English sentences for the run's lines, one per line, each prefixed.

        The prefix is the form's printed title (its name if it has none), then ", instance N" (N
        from 1). Inner lines are named from the worksheet of that run, else from the one `names`
        has, and use the shared registry.
        """
        printed = names.printed if line.printed is None else line.printed
        title = None if printed is None else printed.form_title
        form = f"Form {line.form}" if title is None else short_form_title(title)
        prefix = f"{form}, instance {line.position}: "
        sentences = EnglishTraceRenderer().render_all(line.lines, printed)
        names = EnglishNames(printed)
        return "\n".join(
            f"{prefix}{sentence}"
            if inner.label is None
            else f"{prefix}{_capitalised(names.of_label(inner.label))}: {sentence}"
            for inner, sentence in zip(line.lines, sentences, strict=True)
        )


def _capitalised(name: str) -> str:
    """`name` with its first letter capitalised."""
    return name[:1].upper() + name[1:]

"""English text for the trace line of `tax_engine.domain.trace.forms`:
one renderer class, registered
with `@english_renderer`.
"""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english.registry import english_renderer
from tax_engine.adapters.inbound.trace_english.renderer import EnglishTraceRenderer
from tax_engine.domain.trace.forms import FormInstanceLine


@english_renderer
class FormInstanceRenderer:
    """English text for FormInstanceLine."""

    line_class = FormInstanceLine

    def render(self, line: FormInstanceLine) -> str:
        """The English sentences for the run's lines, one per line, each prefixed.

        The prefix is the form, then ", instance N" (N is 1 for a form without an instances list).
        Inner lines use the shared registry: a renderer is built without the registry in use, so it
        is unreachable.
        """
        prefix = f"{line.form}, instance {line.position}: "
        sentences = EnglishTraceRenderer().render_all(line.lines)
        return "\n".join(f"{prefix}{sentence}" for sentence in sentences)

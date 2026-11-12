"""The Ontario trace lines: facts in the vocabulary of Ontario's own forms.

Surtax factor; each line's English text is in `tax_engine.jurisdictions.ca_on.trace_english`. The
generic lines are in `tax_engine.domain.trace`.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_engine.jurisdictions.ca_on.trace import surtax_factor
from tax_engine.jurisdictions.ca_on.trace.surtax_factor import *  # noqa: F403

__all__ = surtax_factor.__all__

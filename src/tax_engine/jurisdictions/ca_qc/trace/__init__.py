"""The Quebec trace lines: facts in the vocabulary of Quebec's own
forms.

Feature modules: lesser_of_counts. Each line's English text is in
`tax_engine.jurisdictions.ca_qc.trace_english`. The generic lines are in `tax_engine.domain.trace`.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_engine.jurisdictions.ca_qc.trace import lesser_of_counts
from tax_engine.jurisdictions.ca_qc.trace.lesser_of_counts import *  # noqa: F403

__all__ = lesser_of_counts.__all__

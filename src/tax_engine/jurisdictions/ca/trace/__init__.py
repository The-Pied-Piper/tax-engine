"""The federal Canada trace lines: facts in the vocabulary of Canada's own forms.

Amount by count, contribution tier, given amount and tapered amount; each line's English text is in
`tax_engine.jurisdictions.ca.trace_english`. The generic lines are in `tax_engine.domain.trace`.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_engine.jurisdictions.ca.trace import (
    amount_by_count,
    contribution_tier,
    given_amount,
    tapered_amount,
)
from tax_engine.jurisdictions.ca.trace.amount_by_count import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.contribution_tier import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.given_amount import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.tapered_amount import *  # noqa: F403

__all__ = (
    amount_by_count.__all__
    + contribution_tier.__all__
    + given_amount.__all__
    + tapered_amount.__all__
)

"""The Newfoundland and Labrador trace lines: facts in the vocabulary of Newfoundland and
Labrador's own forms.

Tax on taxable income; each line's English text is in
`tax_engine.jurisdictions.ca_nl.trace_english`. The generic lines are in `tax_engine.domain.trace`.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_engine.jurisdictions.ca_nl.trace import tax_on_taxable_income
from tax_engine.jurisdictions.ca_nl.trace.tax_on_taxable_income import *  # noqa: F403

__all__ = tax_on_taxable_income.__all__

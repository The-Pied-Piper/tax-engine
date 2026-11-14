"""The British Columbia trace lines: facts in the vocabulary of British Columbia's own forms.

Tax on taxable income; each line's English text is in
`tax_engine.jurisdictions.ca_bc.trace_english`. The generic lines are in `tax_engine.domain.trace`.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_engine.jurisdictions.ca_bc.trace import tax_on_taxable_income
from tax_engine.jurisdictions.ca_bc.trace.tax_on_taxable_income import *  # noqa: F403

__all__ = tax_on_taxable_income.__all__

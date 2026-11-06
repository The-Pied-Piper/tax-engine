"""The federal Canada trace lines: facts in the vocabulary of Canada's own forms.

Capital cost allowance, foreign tax, gains, dependants, logging and rentals; each line's English
text is in `tax_engine.jurisdictions.ca.trace_english`. The generic lines are in
`tax_engine.domain.trace`.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_engine.jurisdictions.ca.trace import (
    amount_by_count,
    apprenticeship,
    capital_cost,
    contribution_tier,
    dependants,
    farm_chart,
    foreign_tax,
    gains,
    home_renovation,
    logging_tax_credit,
    rentals,
    tapered_amount,
    vehicles,
)
from tax_engine.jurisdictions.ca.trace.amount_by_count import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.apprenticeship import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.capital_cost import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.contribution_tier import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.dependants import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.farm_chart import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.foreign_tax import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.gains import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.home_renovation import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.logging_tax_credit import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.rentals import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.tapered_amount import *  # noqa: F403
from tax_engine.jurisdictions.ca.trace.vehicles import *  # noqa: F403

__all__ = (
    amount_by_count.__all__
    + apprenticeship.__all__
    + capital_cost.__all__
    + contribution_tier.__all__
    + dependants.__all__
    + farm_chart.__all__
    + foreign_tax.__all__
    + gains.__all__
    + home_renovation.__all__
    + logging_tax_credit.__all__
    + rentals.__all__
    + tapered_amount.__all__
    + vehicles.__all__
)

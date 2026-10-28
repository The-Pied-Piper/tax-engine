"""The structured trace: what each capability did, recorded as facts.

A trace line holds the domain objects and amounts involved (`ArtifactKind`, `Rate`, `Credit`,
`Amount`, `ContributionTier`, `Taper`, `Factor`, `Fraction`, `RateTableRow`, `ClassRate`,
`RoundingRule`), never text; its `amount` is the figure the line is about. A count is an `int`
artifact kind and its `int` value; a chosen rate is a `Rate` artifact kind and its `Rate` value.
Lines in a jurisdiction's own vocabulary live in that jurisdiction's package
(`tax_calculator.jurisdictions.<package>.trace`). Rendering lines as human-readable text lives
outside the
domain, in the adapters.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_calculator.domain.trace import arithmetic, base, choices, forms, rate_tables, record_lists
from tax_calculator.domain.trace.arithmetic import *  # noqa: F403
from tax_calculator.domain.trace.base import *  # noqa: F403
from tax_calculator.domain.trace.choices import *  # noqa: F403
from tax_calculator.domain.trace.forms import *  # noqa: F403
from tax_calculator.domain.trace.rate_tables import *  # noqa: F403
from tax_calculator.domain.trace.record_lists import *  # noqa: F403

__all__ = (
    arithmetic.__all__
    + base.__all__
    + choices.__all__
    + forms.__all__
    + rate_tables.__all__
    + record_lists.__all__
)

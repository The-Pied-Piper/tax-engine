"""The Quebec artifact catalog: Quebec's own kinds, named
from the Quebec forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_qc import NAMESPACE

CATALOG = ArtifactCatalog(Namespace(NAMESPACE))

SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50 = CountKind.declare(
    CATALOG, "schedule_k_group_plan_covered_line_50", non_negative=True
)
"""Group drug plan answer, Schedule K line 50 "You were covered by basic prescription drug
insurance provided by a group insurance plan (see line 447 in the guide) of which you, your spouse,
your father or your mother was a member, and this plan covered the cost of medications": 1 for yes,
0 for no, read as 0 when the caller gives no answer."""

SCHEDULE_K_GROUP_PLAN_COVERED_CHECKED_LINE_50 = CountKind.declare(
    CATALOG, "schedule_k_group_plan_covered_checked_line_50", non_negative=True
)
"""Group drug plan answer, checked, Schedule K line 50: the answer, refused above 1 so that the
situation cannot be checked twice."""

SCHEDULE_K_MONTHS_JANUARY_TO_JUNE_BOX_60 = AmountKind.declare(
    CATALOG, "schedule_k_months_january_to_june_box_60", non_negative=True
)
"""Number of months checked from January to June, Schedule K box 60: 6 when line 50 is yes (the
answer means covered all year), 0 when no, in months."""

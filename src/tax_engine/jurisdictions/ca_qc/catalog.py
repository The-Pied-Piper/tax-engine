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

SOLIDARITY_QST_BASE_AMOUNT = AmountKind.declare(
    CATALOG, "solidarity_qst_base_amount", non_negative=True
)
"""Solidarity tax credit, QST component, base amount ("montant de base" 363, Table C.9 of fiche
110201, July 2026 to June 2027): the printed figure, claimed whole."""

SOLIDARITY_LIVING_ALONE_AMOUNT = AmountKind.declare(
    CATALOG, "solidarity_living_alone_amount", non_negative=True
)
"""Solidarity tax credit, QST component, living-alone amount ("montant pour personne vivant seule"
172, Table C.9 of fiche 110201, July 2026 to June 2027): the printed figure, claimed whole."""

SOLIDARITY_HOUSING_SINGLE_AMOUNT = AmountKind.declare(
    CATALOG, "solidarity_housing_single_amount", non_negative=True
)
"""Solidarity tax credit, housing component, basic housing amount for a single person or a
single-parent family ("montant de base pour frais de logement", 746, Table C.9 of fiche 110201,
July 2026 to June 2027): the printed figure, claimed whole."""

SOLIDARITY_HOUSING_MULTIPLE_AMOUNT = AmountKind.declare(
    CATALOG, "solidarity_housing_multiple_amount", non_negative=True
)
"""Solidarity tax credit, housing component, basic housing amount for multiple owners or tenants
("montant de base pour frais de logement", 906, Table C.9 of fiche 110201, July 2026 to June
2027): the printed figure before the division by the number of owners, tenants or subtenants (note
2), claimed whole."""

SOLIDARITY_REDUCTION_THRESHOLD = AmountKind.declare(
    CATALOG, "solidarity_reduction_threshold", non_negative=True
)
"""Solidarity tax credit, reduction threshold ("seuil de réduction", 43195, Table C.9 of fiche
110201, July 2026 to June 2027, note 4: rounded to the nearest $5): the printed figure, claimed
whole."""

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

SCHEDULE_K_MONTHS_JULY_TO_DECEMBER_BOX_61 = AmountKind.declare(
    CATALOG, "schedule_k_months_july_to_december_box_61", non_negative=True
)
"""Number of months checked from July to December, Schedule K box 61: 6 when line 50 is yes (the
answer means covered all year), 0 when no, in months."""

SCHEDULE_K_MONTHS_TOTAL_BOX_62 = AmountKind.declare(
    CATALOG, "schedule_k_months_total_box_62", non_negative=True
)
"""Months checked, Add boxes 60 and 61, Schedule K box 62: boxes 60 and 61 added, in months."""

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

SOLIDARITY_FAMILY_INCOME = AmountKind.declare(
    CATALOG, "solidarity_family_income", non_negative=True
)
"""Solidarity tax credit, family income (TP-1 line 275, fiche 110201): the income the reduction is
figured on, consumed here by name."""

SOLIDARITY_INCOME_OVER_THRESHOLD = AmountKind.declare(
    CATALOG, "solidarity_income_over_threshold", non_negative=True
)
"""Solidarity tax credit, family income over the reduction threshold (fiche 110201, Table C.9):
family income less the printed threshold, not below 0."""

SOLIDARITY_REDUCTION_AT_RATE = AmountKind.declare(
    CATALOG, "solidarity_reduction_at_rate", non_negative=True
)
"""Solidarity tax credit, reduction at 6% (fiche 110201, Table C.9): 6% of the family income over
the reduction threshold, rounded half-up to the cent."""

SOLIDARITY_REDUCTION_AT_ONE_COMPONENT_RATE = AmountKind.declare(
    CATALOG, "solidarity_reduction_at_one_component_rate", non_negative=True
)
"""Solidarity tax credit, reduction at 3% (fiche 110201, Table C.9): 3% of the family income over
the reduction threshold, rounded half-up to the cent, for a person who receives only one of the
three components."""

SOLIDARITY_HOUSING_RECEIVED = CountKind.declare(
    CATALOG, "solidarity_housing_received", non_negative=True
)
"""Solidarity tax credit, housing component received (fiche 110201): 1 when the housing component
is received, 0 when it is not; consumed here by name."""

SOLIDARITY_REDUCTION = AmountKind.declare(CATALOG, "solidarity_reduction", non_negative=True)
"""Solidarity tax credit, reduction chosen (fiche 110201, Table C.9): the 3% reduction when the
housing component is not received (one component only), else the 6% reduction."""

SOLIDARITY_MAXIMUM_BEFORE_REDUCTION = AmountKind.declare(
    CATALOG, "solidarity_maximum_before_reduction", non_negative=True
)
"""Solidarity tax credit, maximum before reduction (fiche 110201, Table C.9): the components
received added together; consumed here by name."""

SOLIDARITY_MAXIMUM_LESS_REDUCTION = AmountKind.declare(
    CATALOG, "solidarity_maximum_less_reduction", non_negative=True
)
"""Solidarity tax credit, maximum less the reduction (fiche 110201, Table C.9): the maximum before
reduction less the chosen reduction, not below 0."""

SOLIDARITY_QST_COMPONENT_AMOUNT = AmountKind.declare(
    CATALOG, "solidarity_qst_component_amount", non_negative=True
)
"""Solidarity tax credit, QST component amount (fiche 110201, Table C.9): the base amount plus the
living-alone amount when it applies; consumed here by name."""

SOLIDARITY_QST_COMPONENT_LESS_REDUCTION = AmountKind.declare(
    CATALOG, "solidarity_qst_component_less_reduction", non_negative=True
)
"""Solidarity tax credit, QST component less the 3% reduction (fiche 110201, Table C.9): the floor
of the credit, the QST component amount less the 3% reduction on the same excess, not below 0."""

SOLIDARITY_CREDIT_AFTER_REDUCTION = AmountKind.declare(
    CATALOG, "solidarity_credit_after_reduction", non_negative=True
)
"""Solidarity tax credit after the reduction (fiche 110201, Table C.9): the greater of the maximum
less the reduction and the QST component less the 3% reduction, so the credit never falls below
the QST-only credit."""

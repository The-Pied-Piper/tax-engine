"""The Quebec artifact catalog: Quebec's own kinds, named
from the Quebec forms.

Amounts are `Decimal`, non-negative unless the form prints no floor. Federal kinds come from
`tax_engine.jurisdictions.ca.catalog`; identifiers are stable.
"""

from __future__ import annotations

from tax_engine.domain.artifact import ArtifactCatalog
from tax_engine.domain.kinds import AmountKind
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

TP1_PENSIONABLE_SALARY_GIVEN_LINE_98_1 = AmountKind.declare(
    CATALOG, "tp1_pensionable_salary_given_line_98_1", non_negative=True
)
"""Pensionable salary or wages (QPP) as given, TP-1 line 98.1 "Pensionable salary or wages (QPP).
RL-1 slip, box G": the figure the caller copies from the RL-1 slip; blank when the caller does
not give it, and line 98.1 is then computed from the salary."""

TP1_PENSIONABLE_SALARY_LINE_98_1 = AmountKind.declare(
    CATALOG, "tp1_pensionable_salary_line_98_1", non_negative=True
)
"""Pensionable salary or wages (QPP), TP-1 line 98.1 "Pensionable salary or wages (QPP). RL-1 slip,
box G": the figure given, else the salary up to $81,200."""

TP1_QPP_CONTRIBUTION_GIVEN_LINE_98 = AmountKind.declare(
    CATALOG, "tp1_qpp_contribution_given_line_98", non_negative=True
)
"""QPP contribution as given, TP-1 line 98 "QPP contribution. RL-1 slip, box B.A": the figure the
caller copies from the RL-1 slip; blank when the caller does not give it, and line 98 is then
computed from the salary."""

TP1_QPP_CONTRIBUTION_LINE_98 = AmountKind.declare(
    CATALOG, "tp1_qpp_contribution_line_98", non_negative=True
)
"""QPP contribution, TP-1 line 98 "QPP contribution. RL-1 slip, box B.A": the figure given, else
6.40% from $3,500 to $71,300, at most $4,339.20."""

TP1_ADDITIONAL_QPP_CONTRIBUTION_GIVEN_LINE_98_2 = AmountKind.declare(
    CATALOG, "tp1_additional_qpp_contribution_given_line_98_2", non_negative=True
)
"""Additional contribution to the QPP as given, TP-1 line 98.2 "Additional contribution to the QPP.
RL-1, box B.B": the figure the caller copies from the RL-1 slip; blank when the caller does not
give it, and line 98.2 is then computed from the salary."""

TP1_ADDITIONAL_QPP_CONTRIBUTION_LINE_98_2 = AmountKind.declare(
    CATALOG, "tp1_additional_qpp_contribution_line_98_2", non_negative=True
)
"""Additional contribution to the QPP, TP-1 line 98.2 "Additional contribution to the QPP. RL-1, box
B.B": the figure given, else 4% from $71,300 to $81,200, at most $396.00."""

TP1_QPIP_PREMIUM_GIVEN_LINE_97 = AmountKind.declare(
    CATALOG, "tp1_qpip_premium_given_line_97", non_negative=True
)
"""QPIP premium as given, TP-1 line 97 "QPIP premium. RL-1 slip, box H": the figure the caller
copies from the RL-1 slip; blank when the caller does not give it, and line 97 is then computed
from the salary."""

TP1_QPIP_PREMIUM_LINE_97 = AmountKind.declare(
    CATALOG, "tp1_qpip_premium_line_97", non_negative=True
)
"""QPIP premium, TP-1 line 97 "QPIP premium. RL-1 slip, box H": the figure given, else 0.494% up to
$98,000, at most $484.12."""

TP1_OTHER_INCOME_LINES_105_TO_164 = AmountKind.declare(
    CATALOG, "tp1_other_income_lines_105_to_164", non_negative=True
)
"""The income of TP-1 lines 105 through 164, summed: the figure the caller gives for "Add lines 101
and 105 through 164"; blank when the caller has none, and line 199 reads it as 0."""

TP1_TOTAL_INCOME_LINE_199 = AmountKind.declare(
    CATALOG, "tp1_total_income_line_199", non_negative=True
)
"""Total income, TP-1 line 199 "Add lines 101 and 105 through 164. Total income": line 101, the
salary, plus the optional income of lines 105 through 164, rounded half-up to the cent."""

TP1_FOREST_PRODUCER_AVERAGING_LINE_276 = AmountKind.declare(
    CATALOG, "tp1_forest_producer_averaging_line_276", non_negative=True
)
"""The amount for income averaging for forest producers, included on TP-1 line 276, which Schedule F
line 10 adds to total income; blank when the caller has none, and line 10 reads it as 0."""


TP1_SCHEDULE_F_TOTAL_INCOME_LINE_199 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_total_income_line_199", non_negative=True
)
"""Total income of TP-1 line 199, as Schedule F line 10 reads it from the TP-1 income form."""


TP1_SCHEDULE_F_INCOME_LINE_10 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_income_line_10", non_negative=True
)
"""Schedule F line 10, "Total income (line 199 of your return) plus the amount for income averaging
for forest producers (included on line 276 of your return)": line 199 plus line 276, rounded
half-up to the cent."""


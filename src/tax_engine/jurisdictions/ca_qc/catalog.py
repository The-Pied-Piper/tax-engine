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

SCHEDULE_P_TP1_LINE_101 = AmountKind.declare(CATALOG, "schedule_p_tp1_line_101")
"""Schedule P (TP-1.D.P-V) line 10, first step: the amount from line 101 of the TP-1 return,
"Employment income, RL-1 slip, box A", read from the TP-1 income form as a record list and
totalled."""

TP1_LINE_105 = AmountKind.declare(CATALOG, "tp1_line_105")
"""The amount of TP-1 line 105 as the caller gives it, the figure Schedule P line 10 adds "if it is
positive"; blank when the caller has none, and the Schedule P step reads it as 0."""

SCHEDULE_P_LINE_105_IF_POSITIVE = AmountKind.declare(
    CATALOG, "schedule_p_line_105_if_positive", non_negative=True
)
"""Schedule P line 10, second step: the amount of TP-1 line 105 if it is positive, else 0, rounded
half-up to the cent."""

SCHEDULE_P_LINE_101_PLUS_105 = AmountKind.declare(CATALOG, "schedule_p_line_101_plus_105")
"""Schedule P line 10, third step: the amount of TP-1 line 101 plus the amount of line 105 if it is
positive, rounded half-up to the cent."""

RL1_BOX_211 = AmountKind.declare(CATALOG, "rl1_box_211", non_negative=True)
"""The amount of box 211 of the RL-1 slip as the caller gives it, which Schedule P line 10
subtracts "if applicable"; blank when the caller has none, and the step reads it as 0."""

SCHEDULE_P_LINE_10 = AmountKind.declare(CATALOG, "schedule_p_line_10")
"""Schedule P (TP-1.D.P-V) Part A line 10, "Amount from line 101 of your return, plus the amount
from line 105 if it is positive, minus the amount from box 211 of your RL-1 slip, if applicable",
rounded half-up to the cent."""

TP1_LINE_107 = AmountKind.declare(CATALOG, "tp1_line_107")
"""The amount of TP-1 line 107 as the caller gives it, which Schedule P line 12 copies ("Amount from
line 107 of the return"); blank when the caller has none, and line 18 reads it as 0."""

SCHEDULE_P_RESEARCH_GRANTS_LINE_13 = AmountKind.declare(
    CATALOG, "schedule_p_research_grants_line_13", non_negative=True
)
"""Schedule P line 13, "Net amount of research grants (see line 154, point 3(j), in the guide)", as
the caller gives it; blank when the caller has none, and line 18 reads it as 0."""

SCHEDULE_P_SCHEDULE_L_INCOME_LINE_14 = AmountKind.declare(
    CATALOG, "schedule_p_schedule_l_income_line_14", non_negative=True
)
"""Schedule P line 14, "Total of lines 22 through 26.1 of Schedule L. Do not include losses.", as
the caller gives it; blank when the caller has none, and line 18 reads it as 0."""

SCHEDULE_P_WEPP_PAYMENTS_LINE_15 = AmountKind.declare(
    CATALOG, "schedule_p_wepp_payments_line_15", non_negative=True
)
"""Schedule P line 15, "Wage Earner Protection Program (WEPP) payments (line 154, point 12)", as
the caller gives it; blank when the caller has none, and line 18 reads it as 0."""

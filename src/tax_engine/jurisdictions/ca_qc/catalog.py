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

WORK_CHART_201_LINE_105 = AmountKind.declare(CATALOG, "tp1_line_105", non_negative=True)
"""TP-1 line 105, as Work Chart 201 line 1 reads it ("lines 101, 107 and, if positive, 105"): an
optional input, blank when the caller has none and read as 0. A negative figure is refused:
the owner decided on the ticket (19 Nov 2026) that the chart's "if positive" test on line 105 is
moot, with no step for it."""

WORK_CHART_201_LINE_107 = AmountKind.declare(CATALOG, "tp1_line_107")
"""TP-1 line 107, as Work Chart 201 line 1 reads it: an optional input, blank when the caller has
none and read as 0."""

WORK_CHART_201_RL1_BOX_211 = AmountKind.declare(CATALOG, "rl1_slip_box_211")
"""RL-1 slip box 211, taken off by Work Chart 201 line 1 ("minus the amount from box 211 of your
RL-1 slip"): an optional input, blank when the caller has none and read as 0."""

WORK_CHART_201_ELIGIBLE_WORK_INCOME_BEFORE_BOX_211 = AmountKind.declare(
    CATALOG, "work_chart_201_eligible_work_income_before_box_211"
)
"""Work Chart 201 line 1, the sum before box 211 is taken off: lines 101, 107 and 105. Not a printed
line; the first operation of line 1."""

WORK_CHART_201_ELIGIBLE_WORK_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "work_chart_201_eligible_work_income_line_1"
)
"""Work Chart 201 line 1 "Eligible work income": lines 101, 107 and, if positive, 105, minus the
amount from box 211 of the RL-1 slip, rounded half-up to the cent. The form prints no floor, so it
is signed."""

WORK_CHART_201_WORK_INCENTIVE_AMOUNTS_LINE_2 = AmountKind.declare(
    CATALOG, "work_chart_201_work_incentive_amounts_line_2"
)
"""Work Chart 201 line 2 "Amounts received under a work-incentive project": an optional input,
blank when the caller has none and read as 0."""

WORK_CHART_201_RESEARCH_GRANTS_LINE_3 = AmountKind.declare(
    CATALOG, "work_chart_201_research_grants_line_3"
)
"""Work Chart 201 line 3 "Net amount of research grants": an optional input, blank when the caller
has none and read as 0."""

WORK_CHART_201_WEPP_PAYMENTS_LINE_4 = AmountKind.declare(
    CATALOG, "work_chart_201_wepp_payments_line_4"
)
"""Work Chart 201 line 4 "Wage Earner Protection Program (WEPP) payments": an optional input, blank
when the caller has none and read as 0."""

WORK_CHART_201_NET_BUSINESS_INCOME_LINE_5 = AmountKind.declare(
    CATALOG, "work_chart_201_net_business_income_line_5", non_negative=True
)
"""Work Chart 201 line 5 "Net business income (line 27 of Schedule L). If the result is negative,
enter 0": an optional input, taken as the form takes it, so never negative; blank when the caller
has none and read as 0."""

WORK_CHART_201_TOTAL_LINE_6 = AmountKind.declare(CATALOG, "work_chart_201_total_line_6")
"""Work Chart 201 line 6 "Add lines 1 through 5": the sum, rounded half-up to the cent. Signed, as
line 1 is."""

WORK_CHART_201_LINE_293_AMOUNT_LINE_7 = AmountKind.declare(
    CATALOG, "work_chart_201_line_293_amount_line_7"
)
"""Work Chart 201 line 7 "Amount included in the income above and entitling you to a deduction on
line 293": an optional input, blank when the caller has none and read as 0."""

WORK_CHART_201_LINE_8 = AmountKind.declare(CATALOG, "work_chart_201_line_8")
"""Work Chart 201 line 8 "Subtract line 7 from line 6": the difference, rounded half-up to the cent.
The form prints no floor, so it is signed."""

WORK_CHART_201_DEDUCTION_BEFORE_MAXIMUM = AmountKind.declare(
    CATALOG, "work_chart_201_deduction_before_maximum"
)
"""Work Chart 201 line 9, the first operation: line 8 multiplied by 6%, unrounded. Not a printed
line; the cap of line 9 rounds it once."""

WORK_CHART_201_DEDUCTION_FOR_WORKERS_LINE_9 = AmountKind.declare(
    CATALOG, "work_chart_201_deduction_for_workers_line_9"
)
"""Work Chart 201 line 9 "Deduction for workers" (maximum $1,420), the figure TP-1 line 201 reads:
6% of line 8, at most the printed maximum, rounded half-up to the cent. Signed, as line 8 is."""

T1_LINE_21 = AmountKind.declare(CATALOG, "t1_line_21")
"""Add lines 1 to 20, 5005-R line 21 "Line 21: Add lines 1 to 20.": the employment income of line 1
(`ca/employment_income`) and line 2 (`ca/other_employment_income`); lines 3 to 20 are not built (the
salary-only filer has none). Produced by one core/sum (`t1_taxable_income_line_21.yaml`)."""

NET_SELF_EMPLOYMENT_INCOME = AmountKind.declare(CATALOG, "net_self_employment_income")
"""Net self-employment income, 5005-R line 27 "Line 27: Add lines 22 to 26. Net self-employment
income =": the printed sum of the skipped block of lines 22 to 26, one optional input read as 0. Not
floored: the form prints no floor and a loss is shown in brackets."""

T1_LINE_28 = AmountKind.declare(CATALOG, "t1_line_28")
"""Line 21 plus line 27, 5005-R line 28 "Line 28: Line 21 plus line 27 =". Not floored: line 27 may
be a loss. Produced by one core/sum (`t1_taxable_income_line_28.yaml`)."""

T1_LINE_32 = AmountKind.declare(CATALOG, "t1_line_32")
"""Add lines 29 to 31, 5005-R line 32 and line 14700 "Line 32 and line 14700: Add lines 29 to 31":
the printed sum of the skipped block of workers' compensation, social assistance and net federal
supplements, one optional input read as 0."""

TOTAL_INCOME = AmountKind.declare(CATALOG, "total_income")
"""Total income, 5005-R line 33 and line 15000 "Line 33 and line 15000: Line 28 plus line 32 =".
Not floored, so a loss larger than the other income is shown in brackets as the form prints it.
Produced by one core/sum (`t1_taxable_income_line_15000.yaml`); Step 3 starts from it."""

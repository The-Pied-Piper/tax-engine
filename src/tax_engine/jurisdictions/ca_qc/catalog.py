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

SCHEDULE_U_LINE_11 = AmountKind.declare(CATALOG, "schedule_u_line_11", non_negative=True)
"""Schedule U line 11 "Multiply line 10 by 0.156250": line 10 (the TP-1 line 98 QPP contribution) at
the printed rate, rounded half-up to the cent."""

SCHEDULE_U_PENSIONABLE_SALARY_LINE_12 = AmountKind.declare(
    CATALOG, "schedule_u_pensionable_salary_line_12", non_negative=True
)
"""Schedule U line 12 "Pensionable salary or wages (QPP) (line 98.1 of your return) (maximum
$71,300)": the TP-1 line 98.1 figure, at most the printed $71,300."""

SCHEDULE_U_PERSONAL_QPP_EXEMPTION_LINE_13 = AmountKind.declare(
    CATALOG, "schedule_u_personal_qpp_exemption_line_13", non_negative=True
)
"""Schedule U line 13 "Personal QPP exemption": the printed $3,500 of the instructions for Part B
("enter $3,500", when none of the situations of Table 1 applied), claimed whole."""

SCHEDULE_U_LINE_14 = AmountKind.declare(CATALOG, "schedule_u_line_14")
"""Schedule U line 14 "Subtract line 13 from line 12": the pensionable salary (TP-1 line 98.1) less
the personal QPP exemption. The line prints no floor, so the figure can be negative."""

SCHEDULE_U_MAXIMUM_PENSIONABLE_EARNINGS_LINE_14_1 = AmountKind.declare(
    CATALOG, "schedule_u_maximum_pensionable_earnings_line_14_1", non_negative=True
)
"""Schedule U line 14.1 "Maximum pensionable earnings": the printed $71,300 of the instructions for
Part B ("enter $71,300", when none of the situations of Table 1 applied), claimed whole."""

SCHEDULE_U_LINE_14_3 = AmountKind.declare(CATALOG, "schedule_u_line_14_3", non_negative=True)
"""Schedule U line 14.3 "Subtract line 14.2 from line 14.1. If the result is negative, enter 0": the
maximum pensionable earnings less the personal QPP exemption, not below 0."""

SCHEDULE_U_LINE_14_4 = AmountKind.declare(CATALOG, "schedule_u_line_14_4")
"""Schedule U line 14.4 "Amount from line 14 or line 14.3, whichever is less"."""

SCHEDULE_U_LINE_15 = AmountKind.declare(CATALOG, "schedule_u_line_15")
"""Schedule U line 15 "Multiply line 14.4 by 1%": line 14.4 at the printed rate, rounded half-up to
the cent."""

SCHEDULE_U_LINE_16 = AmountKind.declare(CATALOG, "schedule_u_line_16")
"""Schedule U line 16 "Amount from line 11 or line 15, whichever is less": the QPP contribution
amount of Part B."""

SCHEDULE_U_LINE_17_2 = AmountKind.declare(CATALOG, "schedule_u_line_17_2")
"""Schedule U line 17.2 "Multiply line 17.1 by 6.4%": line 17.1 (a copy of line 14.4) at the printed
rate, rounded half-up to the cent. Line 14.4 can be negative, so the figure can be."""

SCHEDULE_U_LINE_17_3 = AmountKind.declare(CATALOG, "schedule_u_line_17_3", non_negative=True)
"""Schedule U line 17.3 "Subtract line 17.2 from line 17. If the result is negative, enter 0": the
QPP contribution (TP-1 line 98) less line 17.2, not below 0."""

SCHEDULE_U_LINE_17_5 = AmountKind.declare(CATALOG, "schedule_u_line_17_5", non_negative=True)
"""Schedule U line 17.5 "Add lines 17.3 and 17.4": the excess over the base contribution plus the
additional QPP contribution (TP-1 line 98.2), rounded half-up to the cent."""

SCHEDULE_U_LINE_18_7 = AmountKind.declare(CATALOG, "schedule_u_line_18_7", non_negative=True)
"""Schedule U line 18.7 "Subtract line 18.6 from line 18.5. If the result is negative, enter 0": the
pensionable salary (TP-1 line 98.1) less the maximum pensionable earnings, not below 0."""

SCHEDULE_U_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS_LINE_18_8 = AmountKind.declare(
    CATALOG, "schedule_u_additional_maximum_pensionable_earnings_line_18_8", non_negative=True
)
"""Schedule U line 18.8 "Additional maximum pensionable earnings": the printed $81,200 of the
instructions for Part B ("enter $81,200", when none of the situations of Table 1 applied), claimed
whole."""

SCHEDULE_U_LINE_19 = AmountKind.declare(CATALOG, "schedule_u_line_19", non_negative=True)
"""Schedule U line 19 "Subtract line 18.9 from line 18.8. If the result is negative, enter 0": the
additional maximum pensionable earnings less the maximum pensionable earnings, not below 0."""

SCHEDULE_U_LINE_20 = AmountKind.declare(CATALOG, "schedule_u_line_20", non_negative=True)
"""Schedule U line 20 "Amount from line 18.7 or line 19, whichever is less"."""

SCHEDULE_U_LINE_21 = AmountKind.declare(CATALOG, "schedule_u_line_21", non_negative=True)
"""Schedule U line 21 "Multiply line 20 by 4%": line 20 at the printed rate, rounded half-up to the
cent."""

SCHEDULE_U_LINE_22 = AmountKind.declare(CATALOG, "schedule_u_line_22", non_negative=True)
"""Schedule U line 22 "Amount from line 17.5 or line 21, whichever is less"."""

SCHEDULE_U_LINE_23 = AmountKind.declare(CATALOG, "schedule_u_line_23")
"""Schedule U line 23 "Add lines 22 and 22.1", "Deduction for QPP contributions on employment
income": the figure TP-1 line 248 takes, rounded half-up to the cent. Line 22.1 (a copy of line 16)
can be negative."""

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

PPIP_PREMIUMS_GIVEN = AmountKind.declare(CATALOG, "ppip_premiums_given", non_negative=True)
"""PPIP premiums paid as given, 5005-R line 91 "Line 91 and line 31205: Provincial parental
insurance plan (PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)": the figure the
caller gives, from the T4 slips; blank when the caller does not give it, and line 91 is then
computed."""

PPIP_PREMIUMS_PAID = AmountKind.declare(CATALOG, "ppip_premiums_paid", non_negative=True)
"""PPIP premiums paid, 5005-R line 91 "Line 91 and line 31205: Provincial parental insurance plan
(PPIP) premiums paid (box 55 of all T4 slips) (maximum $484.12)": the given figure
(`ca-qc/ppip_premiums_given`) or, when none is given, 0.494% of the employment income to the
$98,000 maximum insurable income (maximum $484.12). TP-1 line 97 (RL-1 box H) is the same figure."""

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

TP1_SCHEDULE_F_EMPLOYMENT_INCOME_LINE_12 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_employment_income_line_12", non_negative=True
)
"""Schedule F line 12, "Employment income (line 101)": TP-1 line 101, read from the TP-1 income
form."""

TP1_SCHEDULE_F_EMPLOYMENT_INCOME_CORRECTION_LINE_14 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_employment_income_correction_line_14"
)
"""Schedule F line 14, "Correction of employment income (line 105)", signed: a figure to subtract is
negative. Blank when the caller has none, and line 16 reads it as 0."""

TP1_SCHEDULE_F_EMPLOYMENT_INCOME_TOTAL_LINE_16 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_employment_income_total_line_16"
)
"""Schedule F line 16, "Add lines 12 and 14, or subtract line 14 from line 12, as applicable":
line 12 plus the signed line 14, rounded half-up to the cent."""

TP1_SCHEDULE_F_INCOME_LINE_18 = AmountKind.declare(CATALOG, "tp1_schedule_f_income_line_18")
"""Schedule F line 18, "Subtract line 16 from line 10": no floor is printed, so it can be
negative."""

TP1_SCHEDULE_F_LINES_20_TO_33_TOTAL_LINE_34 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_lines_20_to_33_total_line_34", non_negative=True
)
"""Schedule F line 34, "Add lines 20, 22 and 25 through 33": the printed sum of the skipped lines,
one optional input; blank when the caller has none, and line 36 reads it as 0."""

TP1_SCHEDULE_F_INCOME_LINE_36 = AmountKind.declare(CATALOG, "tp1_schedule_f_income_line_36")
"""Schedule F line 36, "Income": line 18 less line 34; no floor is printed, so it can be
negative."""

TP1_SCHEDULE_F_DEDUCTIONS_LINE_68 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_deductions_line_68", non_negative=True
)
"""Schedule F line 68, "Deductions": the printed sum of lines 41 through 62, which are skipped, as
one optional input; blank when the caller has none, and line 70 reads it as 0."""

TP1_SCHEDULE_F_INCOME_SUBJECT_LINE_70 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_income_subject_line_70"
)
"""Schedule F line 70, "Income subject to the contribution": line 36 less line 68; no floor is
printed, so it can be negative. Part B tests it against $18,130."""

SCHEDULE_P_TP1_LINE_101 = AmountKind.declare(CATALOG, "schedule_p_tp1_line_101")
"""Schedule P (TP-1.D.P-V) line 10, first step: the amount from line 101 of the TP-1 return,
"Employment income, RL-1 slip, box A", read from the TP-1 income form as a record list and
totalled."""

SCHEDULE_P_LINE_105_IF_POSITIVE = AmountKind.declare(
    CATALOG, "schedule_p_line_105_if_positive", non_negative=True
)
"""Schedule P line 10, second step: the amount of TP-1 line 105 if it is positive, else 0, rounded
half-up to the cent."""

SCHEDULE_P_LINE_101_PLUS_105 = AmountKind.declare(CATALOG, "schedule_p_line_101_plus_105")
"""Schedule P line 10, third step: the amount of TP-1 line 101 plus the amount of line 105 if it is
positive, rounded half-up to the cent."""

SCHEDULE_P_LINE_10 = AmountKind.declare(CATALOG, "schedule_p_line_10")
"""Schedule P (TP-1.D.P-V) Part A line 10, "Amount from line 101 of your return, plus the amount
from line 105 if it is positive, minus the amount from box 211 of your RL-1 slip, if applicable",
rounded half-up to the cent."""

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

SCHEDULE_P_LINE_18 = AmountKind.declare(CATALOG, "schedule_p_line_18")
"""Schedule P Part A line 18, "Add lines 10 through 15", column "You", rounded half-up to the
cent."""

SCHEDULE_P_DEDUCTIBLE_INCOME_LINE_22 = AmountKind.declare(
    CATALOG, "schedule_p_deductible_income_line_22", non_negative=True
)
"""Schedule P line 22, "Amount included in one of the above sources of income and entitling you to
a deduction on line 293 of your return", as the caller gives it; blank when the caller has none, and
line 29 reads it as 0."""

SCHEDULE_P_WORK_INCOME_LINE_29 = AmountKind.declare(CATALOG, "schedule_p_work_income_line_29")
"""Schedule P Part A line 29, "Subtract line 22 from line 18", "Work income", column "You", rounded
half-up to the cent. The form prints no floor."""

SCHEDULE_P_WORK_PREMIUM_INCOME_CEILING_LINE_66 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_income_ceiling_line_66", non_negative=True
)
"""Schedule P Part E, section 2, column 1 "Work premium", line 66: the printed 12,620, claimed
whole."""

SCHEDULE_P_WORK_PREMIUM_INCOME_LINE_68 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_income_line_68"
)
"""Schedule P Part E, section 2, column 1, line 68, "Amount from line 64 or line 66, whichever is
less": the work income of line 29 up to 12,620."""

SCHEDULE_P_WORK_PREMIUM_EXEMPT_AMOUNT_LINE_70 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_exempt_amount_line_70", non_negative=True
)
"""Schedule P Part E, section 2, column 1, line 70: the printed 2,400, claimed whole."""

SCHEDULE_P_WORK_PREMIUM_INCOME_OVER_EXEMPT_LINE_72 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_income_over_exempt_line_72", non_negative=True
)
"""Schedule P Part E, section 2, column 1, line 72, "Subtract line 70 from line 68. If the result
is negative, enter 0", rounded half-up to the cent."""

SCHEDULE_P_WORK_PREMIUM_BEFORE_REDUCTION_LINE_76 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_before_reduction_line_76", non_negative=True
)
"""Schedule P Part E, section 2, column 1, line 76, "Multiply line 72 by line 74 or line 75 (as
applicable)": the work premium before the family-income reduction, rounded half-up to the cent."""

T1_LINE_48 = AmountKind.declare(CATALOG, "t1_line_48", non_negative=True)
"""Deduction for CPP or QPP enhanced contributions on employment income, 5005-R line 48 and line
22215 "Deduction for CPP or QPP enhanced contributions on employment income (complete Schedule 8 or
Form RC381, whichever applies) (maximum $1,074.00)": the figure Schedule 8 line 28 exports
(`ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return`, a record list of one amount),
totalled by one core/record_total (`t1_taxable_income_line_22215.yaml`)."""

T1_LINE_54 = AmountKind.declare(CATALOG, "t1_line_54", non_negative=True)
"""Deductions from total income, 5005-R line 54 and line 23300 "Add lines 35 to 53.": line 48 alone,
the only deduction a salary-only filer has (lines 35 to 47 and 49 to 53 are blank and not built).
Produced by one core/sum (`t1_taxable_income_line_23300.yaml`)."""

T1_LINE_55 = AmountKind.declare(CATALOG, "t1_line_55")
"""Net income before adjustments, 5005-R line 55 and line 23400 "Line 34 minus line 54 (if negative,
show in brackets) Net income before adjustments =": total income (line 33, copied to line 34) less
line 54, not floored, so a deduction above income is shown in brackets as the form prints it.
Produced by one core/subtract (`t1_taxable_income_line_23400.yaml`)."""

NET_INCOME = AmountKind.declare(CATALOG, "net_income", non_negative=True)
"""Net income, 5005-R line 57 and line 23600 "Line 55 minus line 56 (if negative, enter "0") ...
Net income =": net income before adjustments (line 55) less the social benefits repayment (line
56), not below zero. Produced by one core/subtract_not_below_zero
(`t1_taxable_income_line_23600.yaml`); Step 4 starts from it."""

NET_INCOME_SIGNED = AmountKind.declare(CATALOG, "net_income_signed")
"""Net income before its floor, 5005-R line 57 and line 23600 "Line 55 minus line 56 (if negative,
enter "0")" as the shared Schedule 6 line 7 reads it: "Net income from line 23600 of the return (or
the amount you would have entered if the instructions on line 23600 said "if negative, show in
brackets")". Net income before adjustments (line 55) less the social benefits repayment (line 56),
signed. Produced by one core/subtract (`t1_taxable_income_line_23600_signed.yaml`) and supplied to
the neutral name `ca/t1_taxable_income.net_income_signed` by the form declaration."""

TP1_DEDUCTION_FOR_WORKERS_LINE_201 = AmountKind.declare(
    CATALOG, "tp1_deduction_for_workers_line_201"
)
"""TP-1 line 201 "Deduction for workers": the result of Work Chart 201 line 9, carried to the line
("Carry the result to line 201 of your return"). Signed, as the chart's line 9 is."""

TP1_QPP_DEDUCTION_LINE_248 = AmountKind.declare(CATALOG, "tp1_qpp_deduction_line_248")
"""TP-1 line 248 "Deduction for QPP and CPP contributions and QPIP premiums": Schedule U line 23,
the deduction for QPP contributions on employment income, carried to the line ("Carry the result to
line 248 of your return"). Signed, as Schedule U line 23 is."""

TP1_OTHER_DEDUCTIONS_LINES_205_TO_252 = AmountKind.declare(
    CATALOG, "tp1_other_deductions_lines_205_to_252", non_negative=True
)
"""The deductions of TP-1 lines 205 through 207, 214 through 231 and 234 through 252 (line 248.1
included), summed, line 248 apart: the figure the caller gives for "Add lines 201 through 207, 214
through 231, and 234 through 252" besides lines 201 and 248; blank when the caller has none, and
line 254 reads it as 0."""

TP1_TOTAL_DEDUCTIONS_LINE_254 = AmountKind.declare(CATALOG, "tp1_total_deductions_line_254")
"""Total deductions, TP-1 line 254 "Add lines 201 through 207, 214 through 231, and 234 through
252": line 201, line 248 and the other deductions, rounded half-up to the cent. Signed, as lines 201
and 248 are."""

TP1_NET_INCOME_TOTAL_INCOME_LINE_199 = AmountKind.declare(
    CATALOG, "tp1_net_income_total_income_line_199", non_negative=True
)
"""Total income of TP-1 line 199, as the net income lines read it ("Amount from line 199") from the
TP-1 income form."""

TP1_INCOME_LESS_DEDUCTIONS_LINE_256 = AmountKind.declare(
    CATALOG, "tp1_income_less_deductions_line_256"
)
"""TP-1 line 256 "Subtract line 254 from line 199": total income less total deductions, rounded
half-up to the cent. The form prints no floor, so the figure can be negative."""

TP1_INVESTMENT_EXPENSES_ADJUSTMENT_LINE_260 = AmountKind.declare(
    CATALOG, "tp1_investment_expenses_adjustment_line_260", non_negative=True
)
"""TP-1 line 260 "Adjustment of investment expenses. Complete Schedule N": an input a salary-only
caller does not give; line 275 reads it as 0 when it is left out."""

TP1_NET_INCOME_LINE_275 = AmountKind.declare(CATALOG, "tp1_net_income_line_275", non_negative=True)
"""Net income, TP-1 line 275 "Add lines 256 and 260. If the result is negative, enter 0": line 256
plus line 260, not below zero, rounded half-up to the cent."""

BASIC_PERSONAL_AMOUNT_NET_INCOME_LINE_3 = AmountKind.declare(
    CATALOG, "basic_personal_amount_net_income_line_3", non_negative=True
)
"""Federal Worksheet 5000-D1, line 30000 line 3 "Amount from line 23600 of your return": the
floored net income, read from the T1 taxable income export (`ca-qc/net_income`, 5005-R line 57 and
line 23600) into the taper of the basic personal amount. Produced by one core/record_total
(`t1_tax_and_credits_line_30000_line_3.yaml`)."""

BASIC_PERSONAL_AMOUNT = AmountKind.declare(CATALOG, "basic_personal_amount", non_negative=True)
"""Basic personal amount, 5005-R line 78 and line 30000 "If the amount on line 23600 is $177,882 or
less, enter $16,129. If the amount on line 23600 is $253,414 or more, enter $14,538. Otherwise, use
the Federal Worksheet to calculate the amount to enter. (maximum $16,129)": Federal Worksheet
5000-D1 lines 1 to 11, one ca/tapered_amount step over the dataset `ca/basic_personal_amount`
(`t1_tax_and_credits_line_30000.yaml`); the credit sums read it."""

TAXABLE_INCOME = AmountKind.declare(CATALOG, "taxable_income", non_negative=True)
"""Taxable income, 5005-R line 70 and line 26000 "Line 58 minus line 69 (if negative, enter "0")
Taxable income =": net income (line 58, a copy of line 57) less the deductions from net income (line
69, an optional input read as 0), not below zero. Produced by one core/subtract_not_below_zero
(`t1_taxable_income_line_26000.yaml`); the federal bracket columns (line 71 onward) start from
it."""

SCHEDULE_K_NET_INCOME_LINE_36 = AmountKind.declare(
    CATALOG, "schedule_k_net_income_line_36", non_negative=True
)
"""Net income, Schedule K line 36 "Amount from line 275 of your return": a copy of TP-1 line 275.
The amount arrives from the TP-1 net income form as a record list of one, so the one step is
core/record_total (`tp1_schedule_k_line_36.yaml`)."""

SCHEDULE_K_SPOUSE_NET_INCOME_LINE_37 = AmountKind.declare(
    CATALOG, "schedule_k_spouse_net_income_line_37", non_negative=True
)
"""Spouse's net income, Schedule K line 37 "Amount from line 275 of your spouse's return (spouse on
December 31, 2025)": an input, the spouse's TP-1 line 275. A single filer has no spouse, so the
caller leaves it out and line 40 reads it as 0."""

SCHEDULE_K_INCOME_LINE_40 = AmountKind.declare(
    CATALOG, "schedule_k_income_line_40", non_negative=True
)
"""Income, Schedule K line 40 "Add lines 36 and 37": the net income of the return and of the spouse,
added by one core/sum (`tp1_schedule_k_line_40.yaml`), line 37 read as 0 when left blank."""

SCHEDULE_K_AMOUNT_LINE_41 = AmountKind.declare(
    CATALOG, "schedule_k_amount_line_41", non_negative=True
)
"""Amount, Schedule K line 41 "If you had a spouse on December 31, 2025, enter $32,240; otherwise,
enter $19,890": the printed $19,890 of a filer without a spouse, a dataset figure
(`ca-qc/schedule_k_line_41_amount`) claimed whole by one core/credit_amount
(`tp1_schedule_k_line_41.yaml`)."""

SCHEDULE_K_DEPENDENT_CHILD_AMOUNT_LINE_42_OR_44 = AmountKind.declare(
    CATALOG, "schedule_k_dependent_child_amount_line_42_or_44", non_negative=True
)
"""Dependent child amount, Schedule K line 42 or line 44, the "as applicable" lines that line 46
adds to line 41: an input, the amount of whichever of the two lines applies. The take-home has no
dependent child, so the caller leaves it out and line 46 reads it as 0 (owner ruling, 19 Nov
2026)."""

SCHEDULE_K_TOTAL_LINE_46 = AmountKind.declare(
    CATALOG, "schedule_k_total_line_46", non_negative=True
)
"""Total, Schedule K line 46 "Add line 41 and, as applicable, line 42 or line 44": line 41 and the
dependent child input, added by one core/sum (`tp1_schedule_k_line_46.yaml`), the input read as 0
when left blank."""

SCHEDULE_K_PREMIUM_INCOME_LINE_48 = AmountKind.declare(
    CATALOG, "schedule_k_premium_income_line_48", non_negative=True
)
"""Income used to calculate the premium, Schedule K line 48 "Subtract line 46 from line 40. If the
result is negative, enter 0. In this case, you do not have to pay a premium": one
core/subtract_not_below_zero (`tp1_schedule_k_line_48.yaml`). The form exports it; Part C reads
it."""

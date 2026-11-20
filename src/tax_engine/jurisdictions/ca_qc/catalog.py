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

SCHEDULE_P_WORK_PREMIUM_REDUCTION_THRESHOLD_LINE_80 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_reduction_threshold_line_80", non_negative=True
)
"""Schedule P Part E, section 2, column 1 "Work premium", line 80: the printed 12,620, claimed
whole."""

SCHEDULE_P_FAMILY_INCOME_OVER_THRESHOLD_LINE_82 = AmountKind.declare(
    CATALOG, "schedule_p_family_income_over_threshold_line_82", non_negative=True
)
"""Schedule P Part E, section 2, column 1, line 82, "Subtract line 80 from line 78. If the result is
negative, enter 0", rounded half-up to the cent."""

SCHEDULE_P_WORK_PREMIUM_REDUCTION_LINE_83 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_reduction_line_83", non_negative=True
)
"""Schedule P Part E, section 2, column 1, line 83, "Multiply line 82 by 10%": the reduction of the
work premium by family income, rounded half-up to the cent."""

SCHEDULE_P_WORK_PREMIUM_LINE_87 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_line_87", non_negative=True
)
"""Schedule P Part E, section 2, column 1, line 84, "Subtract line 83 from line 76. If the result is
negative, enter 0", the work premium after the reduction, rounded half-up to the cent. Line 87
("Amount from line 84 in column 1 or column 2, whichever is greater") carries it to Part F: column 2
is left out, so line 87 is this figure."""

SCHEDULE_P_NET_INCOME_LINE_52 = AmountKind.declare(
    CATALOG, "schedule_p_net_income_line_52", non_negative=True
)
"""Schedule P Part C line 52, "Amount from line 275 of your return": the net income of TP-1 line
275, read from the TP-1 net income form as a record list and totalled."""

SCHEDULE_P_SPOUSE_NET_INCOME_LINE_53 = AmountKind.declare(
    CATALOG, "schedule_p_spouse_net_income_line_53", non_negative=True
)
"""Schedule P Part C line 53, "Amount from line 275 of your spouse's return (spouse on December 31,
2025)", as the caller gives it; blank when the caller has none, and line 54 reads it as 0."""

SCHEDULE_P_FAMILY_INCOME_LINE_54 = AmountKind.declare(
    CATALOG, "schedule_p_family_income_line_54", non_negative=True
)
"""Schedule P Part C line 54, "Add lines 52 and 53", "Family income": the net income of line 52 plus
the spouse's of line 53 (blank, read as 0), rounded half-up to the cent."""

SCHEDULE_P_WORK_PREMIUM_SUPPLEMENT_AMOUNT_LINE_56 = AmountKind.declare(
    CATALOG, "schedule_p_work_premium_supplement_amount_line_56", non_negative=True
)
"""Schedule P Part D, line 56: the printed 200.00, the amount for each month of the supplement to
the work premium, claimed whole."""

SCHEDULE_P_RL5_MONTHS_LINE_57 = CountKind.declare(
    CATALOG, "schedule_p_rl5_months_line_57", non_negative=True
)
"""Schedule P Part D line 57, "Total number of months in box V of your RL-5 slip", as the caller
gives it; blank when the caller has none, and line 59 reads it as 0."""

SCHEDULE_P_SUPPLEMENT_MONTHS_LINE_58 = CountKind.declare(
    CATALOG, "schedule_p_supplement_months_line_58", non_negative=True
)
"""Schedule P Part D line 58, "Number of months in 2025 for which you meet the requirements for
claiming the supplement to the work premium (see the guide)", as the caller gives it; blank when the
caller has none, and line 59 reads it as 0."""

SCHEDULE_P_LESSER_MONTHS_LINE_59 = CountKind.declare(
    CATALOG, "schedule_p_lesser_months_line_59", non_negative=True
)
"""Schedule P Part D line 59, "Number from line 57 or line 58, whichever is less": the lesser of the
months of line 57 and of line 58, each blank read as 0."""

SCHEDULE_P_SUPPLEMENT_LINE_60 = AmountKind.declare(
    CATALOG, "schedule_p_supplement_line_60", non_negative=True
)
"""Schedule P Part D line 60, "Multiply line 56 by line 59": the supplement to the work premium, the
amount for each month times the months, rounded half-up to the cent. Carried to line 88 on
page 2."""

SCHEDULE_P_TAX_CREDITS_LINE_90 = AmountKind.declare(
    CATALOG, "schedule_p_tax_credits_line_90", non_negative=True
)
"""Schedule P Part F line 90, "Add lines 88 and 89" (the supplement of line 60 and the work premium
of line 87), "Tax credits respecting the work premium", rounded half-up to the cent. Carried to
line 456 of the TP-1."""

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

TP1_ADJUSTMENT_OF_DEDUCTIONS_LINE_276 = AmountKind.declare(
    CATALOG, "tp1_adjustment_of_deductions_line_276", non_negative=True
)
"""TP-1 line 276 "Adjustment of deductions. Specify": an input a salary-only caller does not give;
line 279 reads it as 0 when it is left out."""

TP1_BENEFIT_AND_DISABILITY_SAVINGS_INCOME_LINE_278 = AmountKind.declare(
    CATALOG, "tp1_benefit_and_disability_savings_income_line_278", non_negative=True
)
"""TP-1 line 278 "Universal Child Care Benefit and income from a registered disability savings
plan": an input a salary-only caller does not give; line 279 reads it as 0 when it is left out."""

TP1_LINE_279 = AmountKind.declare(CATALOG, "tp1_line_279", non_negative=True)
"""TP-1 line 279 "Add lines 275 through 278": net income plus lines 276 and 278, rounded half-up to
the cent."""

TP1_TOTAL_DEDUCTIONS_LINE_298 = AmountKind.declare(
    CATALOG, "tp1_total_deductions_line_298", non_negative=True
)
"""TP-1 line 298 "Add lines 287 through 297. Total deductions": the printed sum of lines 287 to 297,
one optional input a salary-only caller does not give; read as 0 (default "0")."""

TP1_TAXABLE_INCOME_LINE_299 = AmountKind.declare(
    CATALOG, "tp1_taxable_income_line_299", non_negative=True
)
"""Taxable income, TP-1 line 299 "Subtract line 298 from line 279. If the result is negative, enter
0": line 279 less line 298, not below zero, rounded half-up to the cent."""

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

AGE_AMOUNT_LINE_79 = AmountKind.declare(CATALOG, "age_amount_line_79", non_negative=True)
"""Age amount, 5005-R line 79 and line 30100: an optional input a salary-only caller does not give;
the credit sum that adds it reads a blank as 0 (`t1_tax_and_credits_line_30100_inputs.yaml`)."""

SPOUSE_AMOUNT_LINE_80 = AmountKind.declare(CATALOG, "spouse_amount_line_80", non_negative=True)
"""Spouse or common-law partner amount, 5005-R line 80 and line 30300: an optional input a salary-
only caller does not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_30300_inputs.yaml`)."""

ELIGIBLE_DEPENDANT_AMOUNT_LINE_81 = AmountKind.declare(
    CATALOG, "eligible_dependant_amount_line_81", non_negative=True
)
"""Amount for an eligible dependant, 5005-R line 81 and line 30400: an optional input a salary-only
caller does not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_30400_inputs.yaml`)."""

CAREGIVER_AMOUNT_SPOUSE_LINE_82 = AmountKind.declare(
    CATALOG, "caregiver_amount_spouse_line_82", non_negative=True
)
"""Canada caregiver amount for spouse or common-law partner, or eligible dependant age 18 or older,
5005-R line 82 and line 30425: an optional input a salary-only caller does not give; the credit
sum that adds it reads a blank as 0 (`t1_tax_and_credits_line_30425_inputs.yaml`)."""

CAREGIVER_AMOUNT_INFIRM_DEPENDANTS_LINE_83 = AmountKind.declare(
    CATALOG, "caregiver_amount_infirm_dependants_line_83", non_negative=True
)
"""Canada caregiver amount for other infirm dependants age 18 or older, 5005-R line 83 and line
30450: an optional input a salary-only caller does not give; the credit sum that adds it reads a
blank as 0 (`t1_tax_and_credits_line_30450_inputs.yaml`)."""

CAREGIVER_AMOUNT_INFIRM_CHILDREN_LINE_84 = AmountKind.declare(
    CATALOG, "caregiver_amount_infirm_children_line_84", non_negative=True
)
"""Canada caregiver amount for infirm children under 18 years of age, 5005-R line 84 and line
30500: an optional input a salary-only caller does not give; the credit sum that adds it reads a
blank as 0 (`t1_tax_and_credits_line_30500_inputs.yaml`)."""

QPP_BASE_SELF_EMPLOYMENT_LINE_88 = AmountKind.declare(
    CATALOG, "qpp_base_self_employment_line_88", non_negative=True
)
"""Base CPP or QPP contributions on self-employment income and other earnings, 5005-R line 88 and
line 31000: an optional input a salary-only caller does not give; the credit sum that adds it
reads a blank as 0 (`t1_tax_and_credits_line_31000_inputs.yaml`)."""

EI_PREMIUMS_SELF_EMPLOYMENT_LINE_90 = AmountKind.declare(
    CATALOG, "ei_premiums_self_employment_line_90", non_negative=True
)
"""Employment insurance premiums on self-employment and other eligible earnings, 5005-R line 90 and
line 31217: an optional input a salary-only caller does not give; the credit sum that adds it
reads a blank as 0 (`t1_tax_and_credits_line_31217_inputs.yaml`)."""

PPIP_PREMIUMS_PAYABLE_LINE_92 = AmountKind.declare(
    CATALOG, "ppip_premiums_payable_line_92", non_negative=True
)
"""PPIP premiums payable on employment income, 5005-R line 92 and line 31210: an optional input a
salary-only caller does not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_31210_inputs.yaml`)."""

PPIP_PREMIUMS_PAYABLE_SELF_EMPLOYMENT_LINE_93 = AmountKind.declare(
    CATALOG, "ppip_premiums_payable_self_employment_line_93", non_negative=True
)
"""PPIP premiums payable on self-employment income, 5005-R line 93 and line 31215: an optional
input a salary-only caller does not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_31215_inputs.yaml`)."""

VOLUNTEER_FIREFIGHTERS_AMOUNT_LINE_94 = AmountKind.declare(
    CATALOG, "volunteer_firefighters_amount_line_94", non_negative=True
)
"""Volunteer firefighters' amount (VFA), 5005-R line 94 and line 31220: an optional input a salary-
only caller does not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_31220_inputs.yaml`)."""

SEARCH_AND_RESCUE_AMOUNT_LINE_95 = AmountKind.declare(
    CATALOG, "search_and_rescue_amount_line_95", non_negative=True
)
"""Search and rescue volunteers' amount (SRVA), 5005-R line 95 and line 31240: an optional input a
salary-only caller does not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_31240_inputs.yaml`)."""

HOME_BUYERS_AMOUNT_LINE_97 = AmountKind.declare(
    CATALOG, "home_buyers_amount_line_97", non_negative=True
)
"""Home buyers' amount, 5005-R line 97 and line 31270: an optional input a salary-only caller does
not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_31270_inputs.yaml`)."""

HOME_ACCESSIBILITY_EXPENSES_LINE_98 = AmountKind.declare(
    CATALOG, "home_accessibility_expenses_line_98", non_negative=True
)
"""Home accessibility expenses, 5005-R line 98 and line 31285: an optional input a salary-only
caller does not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_31285_inputs.yaml`)."""

ADOPTION_EXPENSES_LINE_99 = AmountKind.declare(
    CATALOG, "adoption_expenses_line_99", non_negative=True
)
"""Adoption expenses, 5005-R line 99 and line 31300: an optional input a salary-only caller does
not give; the credit sum that adds it reads a blank as 0
(`t1_tax_and_credits_line_31300_inputs.yaml`)."""

CREDIT_AMOUNTS_LINE_85 = AmountKind.declare(CATALOG, "credit_amounts_line_85", non_negative=True)
"""Credit amounts through line 84, 5005-R line 85 "Line 85: Add lines 78 to 84. =": the basic
personal amount (line 78) plus the optional lines 79 to 84, each blank read as 0. Produced by
one core/sum (`t1_tax_and_credits_line_85.yaml`); line 86 is its copy, so it has no step."""

QPP_BASE_CONTRIBUTIONS_LINE_87 = AmountKind.declare(
    CATALOG, "qpp_base_contributions_line_87", non_negative=True
)
"""Base CPP or QPP contributions through employment income, 5005-R line 87 and line 30800 (maximum
$3,661.20): a copy of Schedule 8 line 25, read from the Schedule 8 export by one
core/record_total (`t1_tax_and_credits_line_30800.yaml`)."""

EI_PREMIUMS_LINE_89 = AmountKind.declare(CATALOG, "ei_premiums_line_89", non_negative=True)
"""Employment insurance premiums through employment, 5005-R line 89 and line 31200 (maximum
$860.67): a copy of T2204 line 16, read from the T2204 export by one core/record_total
(`t1_tax_and_credits_line_31200.yaml`)."""

PPIP_PREMIUMS_LINE_91 = AmountKind.declare(CATALOG, "ppip_premiums_line_91", non_negative=True)
"""Provincial parental insurance plan (PPIP) premiums paid, 5005-R line 91 and line 31205 (maximum
$484.12): a copy of the PPIP premium figure, read from the `ca-qc/ppip_premium` export by one
core/record_total (`t1_tax_and_credits_line_31205.yaml`)."""

CANADA_EMPLOYMENT_AMOUNT_INCOME = AmountKind.declare(
    CATALOG, "canada_employment_amount_income", non_negative=True
)
"""Line 1 plus line 2, 5005-R line 96 and line 31260 "Enter whichever is less: $1,471 or line 1
plus line 2.": the base the cap is applied to, from one core/sum
(`t1_tax_and_credits_line_31260.yaml`)."""

CANADA_EMPLOYMENT_AMOUNT = AmountKind.declare(
    CATALOG, "canada_employment_amount", non_negative=True
)
"""Canada employment amount, 5005-R line 96 and line 31260: the lesser of the printed $1,471 (the
dataset `ca/canada_employment_amount`) and line 1 plus line 2, from one core/capped_amount
(`t1_tax_and_credits_line_31260.yaml`)."""

CREDITS_LINE_100 = AmountKind.declare(CATALOG, "credits_line_100", non_negative=True)
"""Credits of lines 87 to 99, 5005-R line 100 "Line 100: Add lines 87 to 99. =": the base QPP, EI
and PPIP lines, the Canada employment amount and the optional lines 88, 90, 92 to 95 and 97 to
99, each blank read as 0. Produced by one core/sum (`t1_tax_and_credits_line_100.yaml`); line
102 reads it."""

PENSION_INCOME_AMOUNT_LINE_101 = AmountKind.declare(
    CATALOG, "pension_income_amount_line_101", non_negative=True
)
"""Pension income amount, 5005-R line 101 and line 31400: an optional input a salary-only caller
does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_31400_inputs.yaml`)."""

CREDITS_LINE_102 = AmountKind.declare(CATALOG, "credits_line_102", non_negative=True)
"""Credits of lines 86, 100 and 101, 5005-R line 102 "Line 102: Add lines 86, 100, and 101. =":
the credit amounts through line 84 plus the credits of lines 87 to 99 plus the pension income
amount, each blank read as 0, from one core/sum (`t1_tax_and_credits_line_102.yaml`); line 105
reads it."""

DISABILITY_AMOUNT_SELF_LINE_103 = AmountKind.declare(
    CATALOG, "disability_amount_self_line_103", non_negative=True
)
"""Disability amount for self, 5005-R line 103 and line 31600: an optional input a salary-only
caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_31600_inputs.yaml`)."""

DISABILITY_AMOUNT_TRANSFERRED_LINE_104 = AmountKind.declare(
    CATALOG, "disability_amount_transferred_line_104", non_negative=True
)
"""Disability amount transferred from a dependant, 5005-R line 104 and line 31800: an optional
input a salary-only caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_31800_inputs.yaml`)."""

CREDITS_LINE_105 = AmountKind.declare(CATALOG, "credits_line_105", non_negative=True)
"""Credits of lines 102 to 104, 5005-R line 105 "Line 105: Add lines 102 to 104. =": the credits
through line 102 plus the disability amount for self (line 103) and the disability amount
transferred from a dependant (line 104), each blank read as 0, from one core/sum
(`t1_tax_and_credits_line_105.yaml`); line 110 reads it."""

STUDENT_LOAN_INTEREST_LINE_106 = AmountKind.declare(
    CATALOG, "student_loan_interest_line_106", non_negative=True
)
"""Interest paid on your student loans, 5005-R line 106 and line 31900: an optional input a
salary-only caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_31900_inputs.yaml`)."""

FEDERAL_TUITION_AMOUNT_LINE_107 = AmountKind.declare(
    CATALOG, "federal_tuition_amount_line_107", non_negative=True
)
"""Your federal tuition amount, 5005-R line 107 and line 32300: an optional input a salary-only
caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_32300_inputs.yaml`)."""

TUITION_AMOUNT_TRANSFERRED_LINE_108 = AmountKind.declare(
    CATALOG, "tuition_amount_transferred_line_108", non_negative=True
)
"""Tuition amount transferred from a child or grandchild, 5005-R line 108 and line 32400: an
optional input a salary-only caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_32400_inputs.yaml`)."""

AMOUNTS_TRANSFERRED_FROM_SPOUSE_LINE_109 = AmountKind.declare(
    CATALOG, "amounts_transferred_from_spouse_line_109", non_negative=True
)
"""Amounts transferred from your spouse or common-law partner, 5005-R line 109 and line 32600: an
optional input a salary-only caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_32600_inputs.yaml`)."""

CREDITS_LINE_110 = AmountKind.declare(CATALOG, "credits_line_110", non_negative=True)
"""Credits of lines 105 to 109, 5005-R line 110 "Line 110: Add lines 105 to 109. =": the credits
through line 105 plus the student loan interest, the federal tuition amount, the tuition amount
transferred and the amounts transferred from a spouse (lines 106 to 109), each blank read as 0,
from one core/sum (`t1_tax_and_credits_line_110.yaml`); line 117 reads it."""

NET_INCOME_LINE_112 = AmountKind.declare(CATALOG, "net_income_line_112", non_negative=True)
"""Amount from line 23600, 5005-R line 112 "Line 112: Amount from line 23600 multiplied by 3% =":
a copy of net income, read from the net income export by one core/record_total
(`t1_tax_and_credits_line_112.yaml`); the 3% is applied to it by the next step."""

MEDICAL_NET_INCOME_SHARE_LINE_112 = AmountKind.declare(
    CATALOG, "medical_net_income_share_line_112", non_negative=True
)
"""Share of net income for medical expenses, 5005-R line 112 "Line 112: Amount from line 23600
multiplied by 3% =": net income times the printed 3% (the dataset `ca/medical_net_income_rate`),
from one core/apply_rate (`t1_tax_and_credits_line_112.yaml`); line 113 caps it."""

MEDICAL_THRESHOLD_LINE_113 = AmountKind.declare(
    CATALOG, "medical_threshold_line_113", non_negative=True
)
"""Medical expenses threshold, 5005-R line 113 "Line 113: Enter whichever is less: $2,834 or the
amount from line 112.": the lesser of the printed $2,834 (the dataset
`ca/medical_threshold_ceiling`) and line 112, from one core/capped_amount
(`t1_tax_and_credits_line_113.yaml`); line 114 takes it off line 111."""

MEDICAL_EXPENSES_LINE_111 = AmountKind.declare(
    CATALOG, "medical_expenses_line_111", non_negative=True
)
"""Medical expenses for self, spouse or common-law partner and your dependent children under 18
years of age, 5005-R line 111 and line 33099: an optional input a salary-only caller does not
give; the line that reads it takes a blank as 0 (`t1_tax_and_credits_line_33099_inputs.yaml`)."""

MEDICAL_EXPENSES_OVER_THRESHOLD_LINE_114 = AmountKind.declare(
    CATALOG, "medical_expenses_over_threshold_line_114", non_negative=True
)
"""Medical expenses over the threshold, 5005-R line 114 "Line 114: Line 111 minus line 113 (if
negative, enter "0") =": the medical expenses of line 111 (a blank read as 0) less the threshold
of line 113, not below zero, from one core/subtract_not_below_zero
(`t1_tax_and_credits_line_114.yaml`); line 116 adds line 115 to it."""

MEDICAL_EXPENSES_OTHER_DEPENDANTS_LINE_115 = AmountKind.declare(
    CATALOG, "medical_expenses_other_dependants_line_115", non_negative=True
)
"""Allowable amount of medical expenses for other dependants, 5005-R line 115 and line 33199: an
optional input a salary-only caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_33199_inputs.yaml`)."""

MEDICAL_EXPENSES_LINE_116 = AmountKind.declare(
    CATALOG, "medical_expenses_line_116", non_negative=True
)
"""Medical expenses for the credit, 5005-R line 116 and line 33200 "Line 114 plus line 115 =":
the medical expenses over the threshold plus the allowable medical expenses for other dependants
(line 115, a blank read as 0), from one core/sum (`t1_tax_and_credits_line_33200.yaml`); line 117
adds it to line 110."""

CREDIT_AMOUNTS_LINE_117 = AmountKind.declare(CATALOG, "credit_amounts_line_117", non_negative=True)
"""Total credit amounts, 5005-R line 117 and line 33500 "Line 110 plus line 116 =": the credits
of lines 85 to 110 plus the medical expenses of line 116, from one core/sum
(`t1_tax_and_credits_line_33500.yaml`); line 119 applies the federal credit rate to it."""

CREDITS_AT_CREDIT_RATE_LINE_119 = AmountKind.declare(
    CATALOG, "credits_at_credit_rate_line_119", non_negative=True
)
"""Federal non-refundable tax credits at the credit rate, 5005-R line 119 and line 33800 "Line
117 multiplied by the percentage from line 118 =": line 117 times the printed 14.5% (the dataset
`ca/credit_rate`), from one core/apply_rate (`t1_tax_and_credits_line_33800.yaml`); line 122 adds
the donations and the top-up to it."""

DONATIONS_AND_GIFTS_LINE_120 = AmountKind.declare(
    CATALOG, "donations_and_gifts_line_120", non_negative=True
)
"""Donations and gifts, 5005-R line 120 and line 34900: an optional input a salary-only caller
does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_34900_inputs.yaml`)."""

TOP_UP_TAX_CREDIT_LINE_121 = AmountKind.declare(
    CATALOG, "top_up_tax_credit_line_121", non_negative=True
)
"""Top-up tax credit, 5005-R line 121 and line 34990: an optional input a salary-only caller does
not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_34990_inputs.yaml`)."""

NON_REFUNDABLE_TAX_CREDITS_LINE_122 = AmountKind.declare(
    CATALOG, "non_refundable_tax_credits_line_122", non_negative=True
)
"""Total federal non-refundable tax credits, 5005-R line 122 and line 35000 "Add lines 119 to
121.": the credits at the credit rate plus the donations and gifts (line 120) and the top-up tax
credit (line 121), each blank read as 0, from one core/sum
(`t1_tax_and_credits_line_35000.yaml`); Part C line 126 copies it."""

FEDERAL_TAX_ON_SPLIT_INCOME_LINE_124 = AmountKind.declare(
    CATALOG, "federal_tax_on_split_income_line_124", non_negative=True
)
"""Federal tax on split income (TOSI), 5005-R line 124 and line 40424: an optional input a
salary-only caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_40424_inputs.yaml`)."""

FEDERAL_TAX_WITH_SPLIT_INCOME_LINE_125 = AmountKind.declare(
    CATALOG, "federal_tax_with_split_income_line_125", non_negative=True
)
"""Net federal tax before credits, 5005-R line 125 and line 40400 "Line 123 plus line 124 =": line
77 (line 123 copies it) plus the federal tax on split income (line 124), a blank read as 0 from
one core/sum (`t1_tax_and_credits_line_40400.yaml`)."""

FEDERAL_DIVIDEND_TAX_CREDIT_LINE_127 = AmountKind.declare(
    CATALOG, "federal_dividend_tax_credit_line_127", non_negative=True
)
"""Federal dividend tax credit, 5005-R line 127 and line 40425: an optional input a salary-only
caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_40425_inputs.yaml`)."""

MINIMUM_TAX_CARRYOVER_LINE_128 = AmountKind.declare(
    CATALOG, "minimum_tax_carryover_line_128", non_negative=True
)
"""Minimum tax carryover, 5005-R line 128 and line 40427: an optional input a salary-only caller
does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_40427_inputs.yaml`)."""

FEDERAL_CREDITS_AND_CARRYOVERS_LINE_129 = AmountKind.declare(
    CATALOG, "federal_credits_and_carryovers_line_129", non_negative=True
)
"""Credits and carryovers, 5005-R line 129 "Add lines 126 to 128. =": line 122 (line 126 copies it)
plus the federal dividend tax credit (line 127) and the minimum tax carryover (line 128), each
blank read as 0 from one core/sum (`t1_tax_and_credits_line_129.yaml`)."""

BASIC_FEDERAL_TAX_LINE_130 = AmountKind.declare(
    CATALOG, "basic_federal_tax_line_130", non_negative=True
)
"""Basic federal tax, 5005-R line 130 and line 42900 "Line 125 minus line 129 (if negative, enter
"0") Basic federal tax =": line 125 less line 129, not below zero from one
core/subtract_not_below_zero (`t1_tax_and_credits_line_42900.yaml`)."""

FEDERAL_SURTAX_OUTSIDE_CANADA_LINE_131 = AmountKind.declare(
    CATALOG, "federal_surtax_outside_canada_line_131", non_negative=True
)
"""Federal surtax on income earned outside Canada, 5005-R line 131: an optional input a salary-only
caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_131_inputs.yaml`)."""

FEDERAL_TAX_WITH_SURTAX_LINE_132 = AmountKind.declare(
    CATALOG, "federal_tax_with_surtax_line_132", non_negative=True
)
"""Federal tax with the surtax, 5005-R line 132 "Line 130 plus line 131 =": line 130 plus the
federal surtax on income earned outside Canada (line 131), a blank read as 0 from one core/sum
(`t1_tax_and_credits_line_132.yaml`)."""

FEDERAL_FOREIGN_TAX_CREDIT_LINE_133 = AmountKind.declare(
    CATALOG, "federal_foreign_tax_credit_line_133", non_negative=True
)
"""Federal foreign tax credit, 5005-R line 133 and line 40500: an optional input a salary-only
caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_40500_inputs.yaml`)."""

FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT_LINE_134 = AmountKind.declare(
    CATALOG, "federal_tax_less_foreign_tax_credit_line_134"
)
"""Federal tax less the foreign tax credit, 5005-R line 134 "Line 132 minus line 133 =": line 132
less the federal foreign tax credit (line 133), a blank read as 0; the form prints no floor, so
the figure is signed from one core/subtract (`t1_tax_and_credits_line_134.yaml`)."""

INVESTMENT_TAX_CREDIT_RECAPTURE_LINE_135 = AmountKind.declare(
    CATALOG, "investment_tax_credit_recapture_line_135", non_negative=True
)
"""Recapture of investment tax credit, 5005-R line 135: an optional input a salary-only caller does
not give; the line that reads it takes a blank as 0 (`t1_tax_and_credits_line_135_inputs.yaml`)."""

FEDERAL_TAX_WITH_ITC_RECAPTURE_LINE_136 = AmountKind.declare(
    CATALOG, "federal_tax_with_itc_recapture_line_136"
)
"""Federal tax with the investment tax credit recapture, 5005-R line 136 "Line 134 plus line 135
=": line 134 plus the recapture of investment tax credit (line 135), a blank read as 0; the
figure is signed from one core/sum (`t1_tax_and_credits_line_136.yaml`)."""

FEDERAL_LOGGING_TAX_CREDIT_LINE_137 = AmountKind.declare(
    CATALOG, "federal_logging_tax_credit_line_137", non_negative=True
)
"""Federal logging tax credit, 5005-R line 137: an optional input a salary-only caller does not
give; the line that reads it takes a blank as 0 (`t1_tax_and_credits_line_137_inputs.yaml`)."""

FEDERAL_TAX_LINE_138 = AmountKind.declare(CATALOG, "federal_tax_line_138", non_negative=True)
"""Federal tax, 5005-R line 138 and line 40600 "Line 136 minus line 137 (if negative, enter "0")
Federal tax =": line 136 less the federal logging tax credit (line 137), a blank read as 0, not
below zero; line 143 and the Quebec abatement read it from one core/subtract_not_below_zero
(`t1_tax_and_credits_line_40600.yaml`)."""

FEDERAL_CREDITS_LINE_142 = AmountKind.declare(
    CATALOG, "federal_credits_line_142", non_negative=True
)
"""Federal political contribution, investment tax and labour-sponsored funds credits (the sum of
lines 139 to 141), 5005-R line 142 and line 41600: an optional input a salary-only caller does not
give; the line that reads it takes a blank as 0 (`t1_tax_and_credits_line_41600_inputs.yaml`)."""

FEDERAL_TAX_LESS_CREDITS_LINE_143 = AmountKind.declare(
    CATALOG, "federal_tax_less_credits_line_143", non_negative=True
)
"""Federal tax less credits, 5005-R line 143 and line 41700 "Line 138 minus line 142 (if negative,
enter "0") =": line 138 less the credits of line 142, a blank read as 0, not below zero from one
core/subtract_not_below_zero (`t1_tax_and_credits_line_41700.yaml`)."""

ADVANCED_CANADA_WORKERS_BENEFIT_LINE_144 = AmountKind.declare(
    CATALOG, "advanced_canada_workers_benefit_line_144", non_negative=True
)
"""Advanced Canada workers benefit (ACWB), 5005-R line 144 and line 41500: an optional input a
salary-only caller does not give; the line that reads it takes a blank as 0
(`t1_tax_and_credits_line_41500_inputs.yaml`)."""

SPECIAL_TAXES_LINE_145 = AmountKind.declare(CATALOG, "special_taxes_line_145", non_negative=True)
"""Special taxes, 5005-R line 145 and line 41800: an optional input a salary-only caller does not
give; the line that reads it takes a blank as 0 (`t1_tax_and_credits_line_41800_inputs.yaml`)."""

NET_FEDERAL_TAX_LINE_146 = AmountKind.declare(
    CATALOG, "net_federal_tax_line_146", non_negative=True
)
"""Net federal tax, 5005-R line 146 and line 42000 "Add lines 143 to 145. Net federal tax =": line
143 plus the advanced Canada workers benefit (line 144) and the special taxes (line 145), each
blank read as 0, from one core/sum (`t1_tax_and_credits_line_42000.yaml`); line 147 copies it."""

EI_PREMIUMS_SELF_EMPLOYED_LINE_148 = AmountKind.declare(
    CATALOG, "ei_premiums_self_employed_line_148", non_negative=True
)
"""Employment insurance premiums payable on self-employment and other eligible earnings, 5005-R line
148 and line 42120: an optional input a salary-only caller does not give; the line that reads it
takes a blank as 0 (`t1_tax_and_credits_line_42120_inputs.yaml`)."""

SOCIAL_BENEFITS_REPAYMENT_LINE_149 = AmountKind.declare(
    CATALOG, "social_benefits_repayment_line_149", non_negative=True
)
"""Social benefits repayment, 5005-R line 149 and line 42200 "Social benefits repayment (amount from
line 23500)": a copy of line 56, read from the T1 taxable-income export by one core/record_total
(`t1_tax_and_credits_line_42200.yaml`)."""

PROVINCIAL_TAX_LINE_150 = AmountKind.declare(CATALOG, "provincial_tax_line_150", non_negative=True)
"""Provincial or territorial tax (from Form T2203, if applicable), 5005-R line 150 and line
42800: an optional input a salary-only caller does not give; the line that reads it takes a
blank as 0 (`t1_tax_and_credits_line_42800_inputs.yaml`)."""

TOTAL_PAYABLE_LINE_151 = AmountKind.declare(CATALOG, "total_payable_line_151", non_negative=True)
"""Total payable, 5005-R line 151 and line 43500 "Add lines 147 to 150. Total payable =": line
147 (a copy of line 146) plus the lines 148 and 150 (blank, read as 0), the social benefits
repayment (line 149) from one core/sum (`t1_tax_and_credits_line_43500.yaml`);
Step 6 line 152 reads it."""

INCOME_TAX_DEDUCTED_NET_LINE_155 = AmountKind.declare(
    CATALOG, "income_tax_deducted_net_line_155", non_negative=True
)
"""Total income tax deducted less the tax transfer for residents of Quebec, 5005-R line 155 and line
43850 "Line 153 minus line 154 =": lines 153 (43700) and 154 (43800) are left out of the take-home
(no T4 slip, so tax deducted is 0), so the difference is one optional input a salary-only caller
does not give; the sum on line 171 takes a blank as 0
(`t1_tax_and_credits_line_43850_inputs.yaml`)."""

REFUNDABLE_QUEBEC_ABATEMENT_LINE_156 = AmountKind.declare(
    CATALOG, "refundable_quebec_abatement_line_156", non_negative=True
)
"""Refundable Quebec abatement, 5005-R line 156 and line 44000 "Amount from Line 42900 multiplied by
16.5% =": line 130 (line 42900) at the printed 16.5% from one core/apply_rate
(`t1_tax_and_credits_line_44000.yaml`); the total credits of line 171 add it, and the Quebec return
summary reads it."""

EI_OVERPAYMENT_LINE_157 = AmountKind.declare(CATALOG, "ei_overpayment_line_157", non_negative=True)
"""Employment insurance (EI) overpayment, 5005-R line 157 and line 45000: the T2204 line 15 amount
(0 when line 15 is not more than $1), read from the T2204 export by one core/record_total
(`t1_tax_and_credits_line_45000.yaml`); line 159 reads it."""

NET_EI_OVERPAYMENT_LINE_159 = AmountKind.declare(
    CATALOG, "net_ei_overpayment_line_159", non_negative=True
)
"""Net EI overpayment, 5005-R line 159 and line 45100 "Line 157 minus line 158 (if negative, enter
"0") =": line 157 less line 158 (a copy of line 92, a blank read as 0), not below zero from one
core/subtract_not_below_zero (`t1_tax_and_credits_line_45100.yaml`); the total credits of line 171
add it."""

REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT_LINE_160 = AmountKind.declare(
    CATALOG, "refundable_medical_expense_supplement_line_160", non_negative=True
)
"""Refundable medical expense supplement, 5005-R line 160 and line 45200: an optional input a
salary-only caller does not give; the sum on line 171 takes a blank as 0
(`t1_tax_and_credits_line_45200_inputs.yaml`)."""

CANADA_TRAINING_CREDIT_LINE_162 = AmountKind.declare(
    CATALOG, "canada_training_credit_line_162", non_negative=True
)
"""Canada training credit (CTC), 5005-R line 162 and line 45350: an optional input a salary-only
caller does not give; the sum on line 171 takes a blank as 0
(`t1_tax_and_credits_line_45350_inputs.yaml`)."""

CWB_LINE_161 = AmountKind.declare(CATALOG, "cwb_line_161", non_negative=True)
"""Canada workers benefit (CWB), 5005-R line 161 and line 45300 "(complete Schedule 6)": Schedule 6
line 28, read from the Schedule 6 export by one core/record_total
(`t1_tax_and_credits_line_45300.yaml`); the total credits of line 171 add it, and the Quebec return
summary reads it."""

TAXABLE_INCOME = AmountKind.declare(CATALOG, "taxable_income", non_negative=True)
"""Taxable income, 5005-R line 70 and line 26000 "Line 58 minus line 69 (if negative, enter "0")
Taxable income =": net income (line 58, a copy of line 57) less the deductions from net income (line
69, an optional input read as 0), not below zero. Produced by one core/subtract_not_below_zero
(`t1_taxable_income_line_26000.yaml`); the federal bracket columns (line 71 onward) start from
it."""

TP1_SCHEDULE_F_LOWER_BOUND_LINE_77 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_lower_bound_line_77", non_negative=True
)
"""Schedule F line 77, the printed lower bound of the column that line 76 falls in (each column
prints 18,130.00 under "If $63,060 or less" and 63,060.00 under "If more than $63,060"); blank
when line 76 is $18,130 or less, because Part B is then not completed."""

TP1_SCHEDULE_F_INCOME_OVER_LOWER_BOUND_LINE_78 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_income_over_lower_bound_line_78", non_negative=True
)
"""Schedule F line 78, "Subtract line 77 from line 76. If the result is negative, enter 0": the
part of line 76 over the column's lower bound; blank when line 77 is blank."""

TP1_SCHEDULE_F_COLUMN_RATE = AmountKind.declare(
    CATALOG, "tp1_schedule_f_column_rate", non_negative=True
)
"""Schedule F, Part B, the row "x 1%" below line 78 (the form gives it no line number): the printed
rate of the column that line 76 falls in; blank for a line 76 of $18,130 or less."""

TP1_SCHEDULE_F_CONTRIBUTION_ON_EXCESS_LINE_80 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_contribution_on_excess_line_80", non_negative=True
)
"""Schedule F line 80, "Multiply line 78 by 1%": line 78 times the column's rate, rounded half-up to
the cent; blank when line 78 or the rate is blank."""

TP1_SCHEDULE_F_COLUMN_CONSTANT_LINE_81 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_column_constant_line_81", non_negative=True
)
"""Schedule F line 81, "+ 81 0 00 | 150 00": the printed constant of the column that line 76 falls
in (0.00 and 150.00); blank for a line 76 of $18,130 or less."""

TP1_SCHEDULE_F_CONTRIBUTION_BEFORE_MAXIMUM = AmountKind.declare(
    CATALOG, "tp1_schedule_f_contribution_before_maximum", non_negative=True
)
"""Schedule F line 82, "Add lines 80 and 81", before its maximum is applied: the sum of the two
lines, each read as 0 when blank. Not printed on its own, so it is engine-internal."""

TP1_SCHEDULE_F_COLUMN_MAXIMUM = AmountKind.declare(
    CATALOG, "tp1_schedule_f_column_maximum", non_negative=True
)
"""Schedule F line 82, "Maximum: $150 | Maximum: $1,000": the printed maximum of the column that
line 76 falls in; blank for a line 76 of $18,130 or less."""

TP1_SCHEDULE_F_CONTRIBUTION_LINE_82 = AmountKind.declare(
    CATALOG, "tp1_schedule_f_contribution_line_82", non_negative=True
)
"""Schedule F line 82, "Contribution to the health services fund", carried to TP-1 line 446: the
lesser of lines 80 plus 81 and the column's maximum; 0.00 when Part B is not completed."""

SCHEDULE_B_LINE_10 = AmountKind.declare(CATALOG, "schedule_b_line_10", non_negative=True)
"""Schedule B (TP-1.D.B-V) Part A line 10, "Amount from line 275 of your return": the net income of
the TP-1 net income form, read from its export. Produced by one core/record_total
(`schedule_b_line_10.yaml`)."""

SCHEDULE_B_LINE_12 = AmountKind.declare(CATALOG, "schedule_b_line_12", non_negative=True)
"""Schedule B Part A line 12, "Amount from line 275 of your spouse's return (spouse on December 31,
2025)": an optional input, a spouse line a salary-only caller does not give; line 14 reads it as 0
when it is left out."""

SCHEDULE_B_LINE_14 = AmountKind.declare(CATALOG, "schedule_b_line_14", non_negative=True)
"""Schedule B Part A line 14, "Add lines 10 and 12. Family income", rounded half-up to the cent.
Produced by one core/sum (`schedule_b_line_14.yaml`)."""

SCHEDULE_B_THRESHOLD_LINE_16 = AmountKind.declare(
    CATALOG, "schedule_b_threshold_line_16", non_negative=True
)
"""Schedule B Part A line 16, the printed 42,090.00 subtracted from the family income, claimed
whole (`schedule_b_line_16.yaml`)."""

SCHEDULE_B_LINE_18 = AmountKind.declare(CATALOG, "schedule_b_line_18", non_negative=True)
"""Schedule B Part A line 18, "Subtract line 16 from line 15. If the result is negative, enter 0":
the family income (line 15, a copy of line 14) less line 16, not below zero, rounded half-up to the
cent. Produced by one core/subtract_not_below_zero (`schedule_b_line_18.yaml`)."""

SCHEDULE_B_LIVED_ALONE_LINE_20 = CountKind.declare(
    CATALOG, "schedule_b_lived_alone_line_20", non_negative=True
)
"""Lived alone answer, Schedule B line 20 "If, throughout 2025, you maintained and ordinarily lived
in a dwelling in which you lived alone or only with ...": 1 for yes, 0 for no, read as 0 (not alone)
when the caller gives no answer."""

SCHEDULE_B_LIVED_ALONE_CHECKED_LINE_20 = CountKind.declare(
    CATALOG, "schedule_b_lived_alone_checked_line_20", non_negative=True
)
"""Lived alone answer, checked, Schedule B line 20: the answer, refused above 1 so that the
situation cannot be checked twice."""

SCHEDULE_B_LIVING_ALONE_AMOUNT_LINE_20 = AmountKind.declare(
    CATALOG, "schedule_b_living_alone_amount_line_20", non_negative=True
)
"""Schedule B line 20, the printed $2,128 for a person living alone, claimed whole."""

SCHEDULE_B_LINE_18_GATE_COUNT_LINE_20 = CountKind.declare(
    CATALOG, "schedule_b_line_18_gate_count_line_20", non_negative=True
)
"""Schedule B line 20's income gate: 0 when the amount on line 18 is more than $64,699 (not entitled
to the amount, no spouse), else 1."""

SCHEDULE_B_LIVING_ALONE_AMOUNT_IF_ALONE_LINE_20 = AmountKind.declare(
    CATALOG, "schedule_b_living_alone_amount_if_alone_line_20", non_negative=True
)
"""Schedule B line 20, fourth step: the printed $2,128 when the answer is yes, 0 when it is no,
rounded half-up to the cent."""

SCHEDULE_B_LINE_20 = AmountKind.declare(CATALOG, "schedule_b_line_20", non_negative=True)
"""Schedule B Part B line 20, the amount for a person living alone: $2,128 when the answer is yes
and the income gate does not apply, else 0, rounded half-up to the cent."""

SCHEDULE_B_LINE_30 = AmountKind.declare(CATALOG, "schedule_b_line_30", non_negative=True)
"""Schedule B Part B line 30, "Add lines 20 through 28": line 20 alone, the only amount the
take-home builds (lines 21, 22, 23, 27 and 28 are not built), rounded half-up to the cent. Produced
by one core/sum (`schedule_b_line_30.yaml`)."""

SCHEDULE_B_LINE_31 = AmountKind.declare(CATALOG, "schedule_b_line_31", non_negative=True)
"""Schedule B Part B line 31, "Amount from line 18 x 18.75%": line 18 at the printed rate, rounded
half-up to the cent. Produced by one core/apply_rate (`schedule_b_line_31.yaml`)."""

SCHEDULE_B_LINE_32 = AmountKind.declare(CATALOG, "schedule_b_line_32", non_negative=True)
"""Schedule B Part B line 32, "Subtract line 31 from line 30. If the result is negative, enter 0.
Amount to which you or, if applicable, your spouse is entitled", rounded half-up to the cent.
Produced by one core/subtract_not_below_zero (`schedule_b_line_32.yaml`)."""

SCHEDULE_B_LINE_33 = AmountKind.declare(CATALOG, "schedule_b_line_33", non_negative=True)
"""Schedule B Part B line 33, "Amount claimed on line 361 of your spouse's return (spouse on
December 31, 2025)": an optional input, a spouse line a salary-only caller does not give; line 34
reads it as 0 when it is left out."""

SCHEDULE_B_LINE_34 = AmountKind.declare(CATALOG, "schedule_b_line_34")
"""Schedule B Part B line 34, "Subtract line 33 from line 32. Carry the result to line 361 of your
return. Age amount, amount for a person living alone and amount for retirement income", rounded
half-up to the cent. The form prints no floor, so the figure is signed. Produced by one
core/subtract (`schedule_b_line_34.yaml`) and exported by the form for TP-1 line 361."""

FEDERAL_TAXABLE_INCOME_LINE_71 = AmountKind.declare(
    CATALOG, "federal_taxable_income_line_71", non_negative=True
)
"""5005-R Step 5 Part A line 71 "Amount from line 26000": taxable income read from the T1 taxable
income export (`ca-qc/taxable_income`, line 70 and line 26000) into Part A, Federal tax on
taxable income. Produced by one core/record_total (`t1_tax_and_credits_line_71.yaml`)."""

FEDERAL_BRACKET_LOWER_BOUND_LINE_72 = AmountKind.declare(
    CATALOG, "federal_bracket_lower_bound_line_72", non_negative=True
)
"""5005-R Step 5 Part A line 72 (0.00, 57,375.00, 114,750.00, 177,882.00 or 253,414.00): the
printed lower bound of the column that line 71 falls in. Produced by one
core/bracket_column_lower_bound (`t1_tax_and_credits_line_72.yaml`)."""

FEDERAL_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_73 = AmountKind.declare(
    CATALOG, "federal_taxable_income_over_lower_bound_line_73", non_negative=True
)
"""5005-R Step 5 Part A line 73 "Line 71 minus line 72 (cannot be negative) =": line 71 minus line
72, not below zero, rounded half-up to the cent. Produced by one core/subtract_not_below_zero
(`t1_tax_and_credits_line_73.yaml`)."""

FEDERAL_BRACKET_COLUMN_RATE_LINE_74 = AmountKind.declare(
    CATALOG, "federal_bracket_column_rate_line_74", non_negative=True
)
"""5005-R Step 5 Part A line 74 "Rate" (14.5%, 20.5%, 26%, 29% or 33%): the printed rate of the
column that line 71 falls in, a fraction (0.205 for 20.5%). Produced by one
core/bracket_column_rate (`t1_tax_and_credits_line_74.yaml`)."""

FEDERAL_EXCESS_TIMES_COLUMN_RATE_LINE_75 = AmountKind.declare(
    CATALOG, "federal_excess_times_column_rate_line_75", non_negative=True
)
"""5005-R Step 5 Part A line 75 "Line 73 multiplied by the percentage from line 74 =": line 73
times line 74, rounded half-up to the cent. Produced by one core/multiply_by_rate
(`t1_tax_and_credits_line_75.yaml`)."""

FEDERAL_TAX_AT_COLUMN_START_LINE_76 = AmountKind.declare(
    CATALOG, "federal_tax_at_column_start_line_76", non_negative=True
)
"""5005-R Step 5 Part A line 76 (0.00, 8,319.38, 20,081.25, 36,495.57 or 58,399.85): the printed
constant of the column that line 71 falls in, taken as printed. Produced by one
core/bracket_column_tax_at_start (`t1_tax_and_credits_line_76.yaml`)."""

FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_77 = AmountKind.declare(
    CATALOG, "federal_tax_on_taxable_income_line_77", non_negative=True
)
"""5005-R Step 5 Part A line 77 "Line 75 plus line 76 Federal tax on taxable income =": line 75
plus line 76, rounded half-up to the cent, which the form enters on line 123. Produced by one
core/sum (`t1_tax_and_credits_line_77.yaml`)."""

WORK_CHART_401_TAXABLE_INCOME_LINE_1 = AmountKind.declare(
    CATALOG, "work_chart_401_taxable_income_line_1", non_negative=True
)
"""Work Chart 401 line 1 "Taxable income (line 299 of your return)": TP-1 line 299, read from the
net income form's export. Produced by one core/record_total (`work_chart_401_line_1.yaml`); line 2
is a copy of it and has no step."""

WORK_CHART_401_LOWER_BOUND_LINE_3 = AmountKind.declare(
    CATALOG, "work_chart_401_lower_bound_line_3", non_negative=True
)
"""Work Chart 401 line 3 (0.00, 53,255.00, 106,495.00 or 129,590.00): the printed lower bound of the
column that line 1 falls in. Produced by one core/bracket_column_lower_bound
(`work_chart_401_line_3.yaml`)."""

WORK_CHART_401_INCOME_OVER_LOWER_BOUND_LINE_4 = AmountKind.declare(
    CATALOG, "work_chart_401_income_over_lower_bound_line_4", non_negative=True
)
"""Work Chart 401 line 4 "Subtract line 3 from line 2": line 1 (line 2 is a copy of it) less the
column's lower bound (line 3), rounded half-up to the cent. Produced by one
core/subtract_not_below_zero (`work_chart_401_line_4.yaml`)."""

WORK_CHART_401_COLUMN_RATE_LINE_5 = AmountKind.declare(
    CATALOG, "work_chart_401_column_rate_line_5", non_negative=True
)
"""Work Chart 401 line 5 "x 5" (14%, 19%, 24% or 25.75%): the printed rate of the column that line
1 falls in, a fraction (0.2575 for 25.75%). Produced by one core/bracket_column_rate
(`work_chart_401_line_5.yaml`)."""

WORK_CHART_401_TAX_ON_EXCESS_LINE_6 = AmountKind.declare(
    CATALOG, "work_chart_401_tax_on_excess_line_6", non_negative=True
)
"""Work Chart 401 line 6 "Multiply line 4 by line 5": the tax on the part of the taxable income over
the column's lower bound, rounded half-up to the cent. Produced by one core/multiply_by_rate
(`work_chart_401_line_6.yaml`)."""

WORK_CHART_401_TAX_AT_START_LINE_7 = AmountKind.declare(
    CATALOG, "work_chart_401_tax_at_start_line_7", non_negative=True
)
"""Work Chart 401 line 7 "+ 7" (0.00, 7,455.70, 17,571.30 or 23,114.10): the printed amount of the
column that line 1 falls in, taken as printed. Produced by one core/bracket_column_tax_at_start
(`work_chart_401_line_7.yaml`)."""

WORK_CHART_401_INCOME_TAX_LINE_8 = AmountKind.declare(
    CATALOG, "work_chart_401_income_tax_line_8", non_negative=True
)
"""Work Chart 401 line 8 "Add lines 6 and 7. Income tax on taxable income": line 6 plus line 7,
rounded half-up to the cent, which the chart carries to line 401 of the return. Produced by one
core/sum (`work_chart_401_line_8.yaml`); the chart exports it."""

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

TP1_BASIC_PERSONAL_AMOUNT_LINE_350 = AmountKind.declare(
    CATALOG, "tp1_basic_personal_amount_line_350", non_negative=True
)
"""TP-1 line 350 "Basic personal amount": the printed figure 18,571.00, claimed whole. Produced by
one core/credit_amount over the dataset of the same name (`tp1_credits_line_350.yaml`). It is its
own kind: `ca-qc/basic_personal_amount` is the federal basic personal amount of 5005-R line 78."""


TP1_INCOME_REPLACEMENT_ADJUSTMENT_LINE_358 = AmountKind.declare(
    CATALOG, "tp1_income_replacement_adjustment_line_358", non_negative=True
)
"""TP-1 line 358 "Adjustment for income replacement indemnities": one optional input a salary-only
caller does not give; line 359 reads a blank as 0 (`tp1_credits_line_358_input.yaml`)."""


TP1_LINE_359 = AmountKind.declare(CATALOG, "tp1_line_359")
"""TP-1 line 359 "Subtract line 358 from line 350": the basic personal amount less the adjustment,
rounded half-up to the cent. The form prints no floor, so the figure is signed. Produced by one
core/subtract (`tp1_credits_line_359.yaml`)."""


TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361 = AmountKind.declare(
    CATALOG, "tp1_age_living_alone_retirement_amount_line_361"
)
"""TP-1 line 361 "Age amount, amount for a person living alone and amount for retirement income.
Complete Schedule B": the figure Schedule B carries from its line 34, which is signed. Produced by
one core/record_total over the Schedule B export (`tp1_credits_line_361.yaml`)."""


TP1_LINE_377 = AmountKind.declare(CATALOG, "tp1_line_377")
"""TP-1 line 377 "Add lines 359 through 376": lines 359 and 361, rounded half-up to the cent (lines
367 and 376 are not built). Signed, as its parts are. Produced by one core/sum
(`tp1_credits_line_377.yaml`)."""


TP1_LINE_377_1 = AmountKind.declare(CATALOG, "tp1_line_377_1")
"""TP-1 line 377.1 "Multiply line 377 by 14%": line 377 at the printed 14%, rounded half-up to the
cent. Signed, as line 377 is. Produced by one core/apply_rate (`tp1_credits_line_377_1.yaml`)."""


TP1_LINE_388 = AmountKind.declare(CATALOG, "tp1_line_388", non_negative=True)
"""TP-1 line 388 "Add lines 378 through 385": the printed sum of lines 378 to 385, one optional
input a salary-only caller does not give; line 389 reads a blank as 0
(`tp1_credits_line_388_input.yaml`)."""


TP1_LINE_389 = AmountKind.declare(CATALOG, "tp1_line_389", non_negative=True)
"""TP-1 line 389 "Multiply line 388 by 20%": line 388 at the printed 20%, rounded half-up to the
cent. Produced by one core/apply_rate (`tp1_credits_line_389.yaml`)."""


TP1_UNION_DUES_LINE_397_1 = AmountKind.declare(
    CATALOG, "tp1_union_dues_line_397_1", non_negative=True
)
"""TP-1 line 397.1 "Union, professional or other dues": one optional input a salary-only caller does
not give; line 397 reads a blank as 0 (`tp1_credits_line_397_1_input.yaml`)."""


TP1_UNION_DUES_CREDIT_LINE_397 = AmountKind.declare(
    CATALOG, "tp1_union_dues_credit_line_397", non_negative=True
)
"""TP-1 line 397 "Multiply line 397.1 by 10%. Tax credit for union, professional or other dues":
line 397.1 at the printed 10%, rounded half-up to the cent. Produced by one core/apply_rate
(`tp1_credits_line_397.yaml`)."""


TP1_LINE_390 = AmountKind.declare(CATALOG, "tp1_line_390", non_negative=True)
"""TP-1 line 390, one of the lines that line 399 adds ("Add lines 377.1, 389 through 392, 395
through 397, 398 and 398.1"): one optional input a salary-only caller does not give; line 399 reads
a blank as 0 (`tp1_credits_line_399_inputs.yaml`)."""

TP1_LINE_391 = AmountKind.declare(CATALOG, "tp1_line_391", non_negative=True)
"""TP-1 line 391, one of the lines that line 399 adds: an optional input, read as 0 when blank
(`tp1_credits_line_399_inputs.yaml`)."""

TP1_LINE_392 = AmountKind.declare(CATALOG, "tp1_line_392", non_negative=True)
"""TP-1 line 392, one of the lines that line 399 adds: an optional input, read as 0 when blank
(`tp1_credits_line_399_inputs.yaml`)."""

TP1_LINE_395 = AmountKind.declare(CATALOG, "tp1_line_395", non_negative=True)
"""TP-1 line 395, one of the lines that line 399 adds: an optional input, read as 0 when blank
(`tp1_credits_line_399_inputs.yaml`)."""

TP1_LINE_396 = AmountKind.declare(CATALOG, "tp1_line_396", non_negative=True)
"""TP-1 line 396, one of the lines that line 399 adds: an optional input, read as 0 when blank
(`tp1_credits_line_399_inputs.yaml`)."""

TP1_LINE_398 = AmountKind.declare(CATALOG, "tp1_line_398", non_negative=True)
"""TP-1 line 398, one of the lines that line 399 adds: an optional input, read as 0 when blank
(`tp1_credits_line_399_inputs.yaml`)."""

TP1_LINE_398_1 = AmountKind.declare(CATALOG, "tp1_line_398_1", non_negative=True)
"""TP-1 line 398.1, one of the lines that line 399 adds: an optional input, read as 0 when blank
(`tp1_credits_line_399_inputs.yaml`)."""

TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_399 = AmountKind.declare(
    CATALOG, "tp1_non_refundable_tax_credits_line_399"
)
"""TP-1 line 399 "Add lines 377.1, 389 through 392, 395 through 397, 398 and 398.1. Non-refundable
tax credits": the sum, rounded half-up to the cent; the optional lines read as 0 when blank. Signed,
as line 377.1 is. Produced by one core/sum (`tp1_credits_line_399.yaml`) and exported by the form
for TP-1 line 406."""

SCHEDULE_K_COLUMN_LOWER_BOUND_LINE_78 = AmountKind.declare(
    CATALOG, "schedule_k_column_lower_bound_line_78", non_negative=True
)
"""Schedule K line 78, the printed lower bound of the column that line 77 (a copy of line 48) falls
in: 0.00 under column A ($5,000 or less) and 5,000.00 under column B (more than $5,000). One
core/bracket_column_lower_bound (`tp1_schedule_k_line_78.yaml`)."""

SCHEDULE_K_INCOME_OVER_LOWER_BOUND_LINE_79 = AmountKind.declare(
    CATALOG, "schedule_k_income_over_lower_bound_line_79", non_negative=True
)
"""Schedule K line 79, "Subtract line 78 from line 77": the part of line 48 over the column's lower
bound, rounded half-up to the cent. One core/subtract_not_below_zero
(`tp1_schedule_k_line_79.yaml`)."""

SCHEDULE_K_COLUMN_RATE_LINE_80 = AmountKind.declare(
    CATALOG, "schedule_k_column_rate_line_80", non_negative=True
)
"""Schedule K line 80, the row "x 80 | 7.84% | 11.76%": the printed rate of the column that line 48
falls in. One core/bracket_column_rate (`tp1_schedule_k_line_80.yaml`)."""

SCHEDULE_K_PREMIUM_ON_EXCESS_LINE_81 = AmountKind.declare(
    CATALOG, "schedule_k_premium_on_excess_line_81", non_negative=True
)
"""Schedule K line 81, "Multiply line 79 by line 80": line 79 times the column's rate, rounded
half-up to the cent. One core/multiply_by_rate (`tp1_schedule_k_line_81.yaml`)."""

SCHEDULE_K_COLUMN_CONSTANT_LINE_82 = AmountKind.declare(
    CATALOG, "schedule_k_column_constant_line_82", non_negative=True
)
"""Schedule K line 82, "+ 82 | 000 00 | 392 00": the printed constant of the column that line 48
falls in (0.00 and 392.00), taken as printed. One core/bracket_column_tax_at_start
(`tp1_schedule_k_line_82.yaml`)."""

SCHEDULE_K_COLUMN_PREMIUM_LINE_83 = AmountKind.declare(
    CATALOG, "schedule_k_column_premium_line_83", non_negative=True
)
"""Schedule K line 83, "Add lines 81 and 82 (maximum $766)": the two lines added, rounded half-up to
the cent. One core/sum (`tp1_schedule_k_line_83.yaml`); line 84 applies the printed maximum, so
this figure is above 766 for a line 48 over about $8,180."""

SCHEDULE_K_PREMIUM_LINE_84 = AmountKind.declare(
    CATALOG, "schedule_k_premium_line_84", non_negative=True
)
"""Premium, Schedule K line 84 "Amount from line 83 of column A or B, as applicable", with the
printed maximum of $766 ("is more than $14,669, enter $766 on line 84"): the lesser of line 83 and
`ca-qc/schedule_k_line_84_maximum`. One core/capped_amount (`tp1_schedule_k_line_84.yaml`). The
form exports it; the lines after it read it."""

TP1_INCOME_TAX_ON_TAXABLE_INCOME_LINE_401 = AmountKind.declare(
    CATALOG, "tp1_income_tax_on_taxable_income_line_401", non_negative=True
)
"""TP-1 line 401 "Income tax on taxable income. Complete Work Chart 401": the chart's line 8, which
it says to carry to line 401. Produced by one core/record_total over the chart's export
(`tp1_tax_line_401.yaml`)."""

TP1_NON_REFUNDABLE_TAX_CREDITS_LINE_406 = AmountKind.declare(
    CATALOG, "tp1_non_refundable_tax_credits_line_406"
)
"""TP-1 line 406 "Non-refundable tax credits (line 399)": the credits form's line 399, a copy.
Signed, as line 399 is. Produced by one core/record_total over the credits form's export
(`tp1_tax_line_406.yaml`)."""

TP1_LINE_413 = AmountKind.declare(CATALOG, "tp1_line_413")
"""TP-1 line 413 "Subtract line 406 from line 401": the income tax on taxable income less the
non-refundable tax credits, rounded half-up to the cent. The form prints no floor, so the figure is
signed (line 432 floors it). Produced by one core/subtract (`tp1_tax_line_413.yaml`) and exported by
the form for lines 425 and 430."""

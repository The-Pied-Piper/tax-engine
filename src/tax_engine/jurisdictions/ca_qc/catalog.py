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

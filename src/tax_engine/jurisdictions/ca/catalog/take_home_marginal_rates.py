"""The federal catalog: the federal part of the take-home marginal rate.

The form `ca/take_home_marginal_rates` runs once and works from the salary alone. No form prints
any of these figures, so none has a title or a line; each is a rate per further dollar of salary,
a fraction (0.2 for 20%), exact. A province's return reads the form's exports and adds its own
steps.
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca.catalog.base import CATALOG

MARGINAL_SALARY = AmountKind.declare(CATALOG, "marginal_salary", non_negative=True)
"""Salary, T1 line 10100: the T1 employment income form's export totalled into the marginal rate
form's own artifact, the base of the contribution rates."""

MARGINAL_CPP_LINE_2 = AmountKind.declare(CATALOG, "marginal_cpp_line_2", non_negative=True)
"""Part 3 line 2 "Line 2: Enter whichever is less: amount from line D of Part 2 or line 1.":
Schedule 8's export totalled into the marginal rate form's own artifact, the figure the signed line
4 is built from."""

MARGINAL_CPP_LINE_5 = AmountKind.declare(CATALOG, "marginal_cpp_line_5", non_negative=True)
"""Part 3 line 5 "Line 5: Line 2 minus line 4 (if negative, enter "0")": Schedule 8's export
totalled into the marginal rate form's own artifact, the figure the signed line 7 is built from."""

MARGINAL_CPP_BASIC_EXEMPTION = AmountKind.declare(
    CATALOG, "marginal_cpp_basic_exemption", non_negative=True
)
"""Part 2 line E, the maximum basic exemption: Schedule 8's export totalled into the marginal rate
form's own artifact, the figure taken off line 5 to build the signed line 7."""

MARGINAL_CPP_MAXIMUM_PENSIONABLE_EARNINGS = AmountKind.declare(
    CATALOG, "marginal_cpp_maximum_pensionable_earnings", non_negative=True
)
"""Part 2 line B, the maximum pensionable earnings: Schedule 8's export totalled into the marginal
rate form's own artifact, the figure taken off line 2 to build the signed line 4."""

MARGINAL_CPP_LINE_7_SIGNED = AmountKind.declare(
    CATALOG, "marginal_cpp_line_7_signed", non_negative=False
)
"""Line 5 less the maximum basic exemption, Schedule 8 Part 3 line 7 "Line 5 minus line 6" before
its floor at zero and its maximum: a signed figure, negative below the exemption. The base and first
additional rates read it, not line 7, because line 7 is 0 both below the exemption and at it, which
hides that a further dollar at the exemption is the first of the band, and stops at its maximum, the
tier's upper bound, so it would look inside the band for every higher salary."""

MARGINAL_CPP_LINE_4_SIGNED = AmountKind.declare(
    CATALOG, "marginal_cpp_line_4_signed", non_negative=False
)
"""Line 2 less the maximum pensionable earnings, Schedule 8 Part 3 line 4 "Line 2 minus line 3"
before its floor at zero: a signed figure, negative below the maximum pensionable earnings. The
second additional rate reads it, not line 4, because line 4 is 0 both below that maximum and at it,
which hides that a further dollar at it is the first of the band."""

MARGINAL_NET_INCOME = AmountKind.declare(CATALOG, "marginal_net_income", non_negative=True)
"""Net income, T1 line 23600 (the signed figure): the T1 taxable income form's export totalled into
the marginal rate form's own artifact, the base of the federal basic personal amount band."""

MARGINAL_FEDERAL_BRACKET_COLUMN_RATE = AmountKind.declare(
    CATALOG, "marginal_federal_bracket_column_rate", non_negative=True
)
"""Federal bracket rate, T1 line 73 "Line 73: Rate" (each column prints "Line 73: Rate" with
14.5%, 20.5%, 26%, 29% or 33%): the printed rate of the column that line 70 falls in, read from the
T1 form's export into the marginal rate form."""

MARGINAL_BASIC_FEDERAL_TAX = AmountKind.declare(
    CATALOG, "marginal_basic_federal_tax", non_negative=True
)
"""Basic federal tax, T1 line 42900 "Basic federal tax": the T1 form's export totalled into the
marginal rate form's own artifact, the base of the federal gate."""

MARGINAL_FEDERAL_GATE = AmountKind.declare(CATALOG, "marginal_federal_gate", non_negative=True)
"""Federal gate: 0 where the basic federal tax (T1 line 42900) is 0.00 and 1 where it is at least
one cent, from the `ca/marginal_rate_gate` dataset. A plain figure, not printed on the form."""

MARGINAL_CPP_BASE_RATE = AmountKind.declare(CATALOG, "marginal_cpp_base_rate", non_negative=True)
"""CPP base rate on a further dollar of salary, Schedule 8 Part 3 line 11 "multiplied by 4.95%":
4.95% from the maximum basic exemption (included) up to the maximum pensionable earnings
(excluded), 0 outside it, from the `ca/cpp_line_11_base_contribution` dataset the contribution
reads, applied to the signed line 7. Not printed on the form."""

MARGINAL_CPP_FIRST_ADDITIONAL_RATE = AmountKind.declare(
    CATALOG, "marginal_cpp_first_additional_rate", non_negative=True
)
"""CPP first additional rate on a further dollar of salary, Schedule 8 Part 3 line 12 "multiplied
by 1%": 1% over the same earnings as the base rate, 0 outside them, from the
`ca/cpp_line_12_first_additional_contribution` dataset the contribution reads. Not printed on
the form."""

MARGINAL_CPP_SECOND_ADDITIONAL_RATE = AmountKind.declare(
    CATALOG, "marginal_cpp_second_additional_rate", non_negative=True
)
"""CPP second additional rate on a further dollar of salary, Schedule 8 Part 3 line 22 "multiplied
by 4%": 4% from the maximum pensionable earnings (included) up to the additional maximum
pensionable earnings (excluded), 0 outside it, from the
`ca/cpp_line_22_second_additional_contribution` dataset the contribution reads, applied to the
signed line 4. Not printed on the form."""

MARGINAL_EI_LINE_1 = AmountKind.declare(CATALOG, "marginal_ei_line_1", non_negative=True)
"""Total EI insurable earnings, T2204 line 1: the form's export totalled into the marginal rate
form's own artifact, which the premium rate reads."""

MARGINAL_EI_LINE_7 = AmountKind.declare(CATALOG, "marginal_ei_line_7", non_negative=True)
"""T2204 line 7 "Amount from line 3 - $2,000 = (if negative, enter "0")": the form's export totalled
into the marginal rate form's own artifact."""

MARGINAL_EI_LINE_10 = AmountKind.declare(CATALOG, "marginal_ei_line_10", non_negative=True)
"""Required premiums, T2204 line 10: the form's export totalled into the marginal rate form's own
artifact. The take-home filer's premiums deducted (line 9) are the same figure, so line 16 is the
lesser of line 7 and this one."""

MARGINAL_EI_PREMIUM_RATE = AmountKind.declare(
    CATALOG, "marginal_ei_premium_rate", non_negative=True
)
"""Premium rate on a further dollar of insurable earnings, T2204 line 10 "Amount from line 1 x
1.64%": the rate of the `ca/ei_premium` dataset the premium reads, 0 outside its band. Not printed
on the form."""

MARGINAL_EI_LINE_7_RATE = AmountKind.declare(CATALOG, "marginal_ei_line_7_rate", non_negative=True)
"""Rate of a further dollar of T2204 line 7: 1 while the line is positive, 0 at zero, from the
`ca/marginal_rate_gate` dataset. Line 7 only decides line 16 where it is the lesser, far below its
own maximum. Not printed on the form."""

MARGINAL_EI_RATE = AmountKind.declare(CATALOG, "marginal_ei_rate", non_negative=True)
"""EI rate on a further dollar of salary, T2204 line 16 "Enter whichever amount is the least: line
7, line 9 or line 12": the rate of line 7 or of line 10, whichever of the two is the least. Not
printed on the form."""

MARGINAL_SALARY_GATE = AmountKind.declare(CATALOG, "marginal_salary_gate", non_negative=True)
"""Salary gate: 0 where the salary (T1 line 10100) is 0.00 and 1 where it is at least one cent,
from the `ca/marginal_rate_gate` dataset. The whole of a further dollar of salary, before the CPP
deductions. A plain figure, not printed on the form."""

MARGINAL_NET_INCOME_RATE_BEFORE_CPP2 = AmountKind.declare(
    CATALOG, "marginal_net_income_rate_before_cpp2", non_negative=True
)
"""Part of a further dollar of salary left in the net income after the CPP first additional
contribution, T1 line 22215 "Deduction for CPP or QPP enhanced contributions on employment
income": 1 less the CPP first additional rate. An exact difference, not printed on the form."""

MARGINAL_NET_INCOME_RATE = AmountKind.declare(
    CATALOG, "marginal_net_income_rate", non_negative=True
)
"""Net income rate: the part of a further dollar of salary left in the net income (T1 line 23600)
and the taxable income, 1 less the CPP first additional rate and the CPP second additional rate,
which T1 line 22215 takes off the income. An exact difference, not printed on the form. An
export of the form, read by a province's return."""

MARGINAL_CREDIT_CONTRIBUTION_RATE = AmountKind.declare(
    CATALOG, "marginal_credit_contribution_rate", non_negative=True
)
"""Credit-earning contribution rate on a further dollar of salary: the CPP base rate (T1 line
30800) plus the EI rate (T1 line 31200), the two contributions that earn a non-refundable credit,
which a province's return multiplies by its own credit rate. An exact sum, not printed on the form.
An export of the form."""

MARGINAL_FEDERAL_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_federal_credit_rate", non_negative=True
)
"""Federal non-refundable tax credit rate, T1 line 114: the `ca/credit_rate` dataset as it is, with
none of the cent rounding the credit box applies. A rate, not printed on the form."""

MARGINAL_FEDERAL_CONTRIBUTION_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_federal_contribution_credit_rate", non_negative=True
)
"""Federal credit rate on the CPP base and EI of a further dollar of salary: the credit-earning
contribution rate times the federal credit rate (T1 line 114 "Federal non-refundable tax credit
rate"), the federal tax the contributions take off. An exact product, not printed on the form."""

MARGINAL_FEDERAL_BRACKET_RATE = AmountKind.declare(
    CATALOG, "marginal_federal_bracket_rate", non_negative=True
)
"""Federal bracket rate on a further dollar of salary, T1 line 73 "Line 73: Rate" times the part
left in the net income. An exact product, not printed on the form."""

MARGINAL_PHASE_DOWN_NET_INCOME_RATE = AmountKind.declare(
    CATALOG, "marginal_phase_down_net_income_rate", non_negative=True
)
"""Fall of the federal basic personal amount on a further dollar of salary: its fall per dollar of
net income times the part of the dollar left in the net income. An exact product, not printed on
the form."""

MARGINAL_FEDERAL_BPA_REDUCTION_RATE = AmountKind.declare(
    CATALOG, "marginal_federal_bpa_reduction_rate", non_negative=True
)
"""Fall of the federal basic personal amount (T1 line 77) on a further dollar of net income: the
Federal Worksheet's supplement over its range, from the `ca/basic_personal_amount` dataset the
amount reads, where the net income (T1 line 23600) is inside the phase-down, 0 outside it. Rounded
as the `ca/marginal_rate_rounding` dataset says, not printed on the form."""

MARGINAL_FEDERAL_BPA_CREDIT_RATE = AmountKind.declare(
    CATALOG, "marginal_federal_bpa_credit_rate", non_negative=True
)
"""Federal tax a further dollar of salary adds through the basic personal amount: the fall of the
basic personal amount times the federal credit rate. An exact product, not printed on the form."""

MARGINAL_FEDERAL_RATE_BEFORE_CREDITS = AmountKind.declare(
    CATALOG, "marginal_federal_rate_before_credits", non_negative=True
)
"""Federal rate on a further dollar of salary before the CPP base and EI credits: the bracket rate
part plus the basic personal amount part. An exact sum, not printed on the form."""

MARGINAL_FEDERAL_RATE_AFTER_CREDITS = AmountKind.declare(
    CATALOG, "marginal_federal_rate_after_credits", non_negative=True
)
"""Federal rate on a further dollar of salary after the CPP base and EI credits, before the
federal gate. An exact difference, not printed on the form."""

MARGINAL_FEDERAL_RATE = AmountKind.declare(CATALOG, "marginal_federal_rate", non_negative=True)
"""Federal marginal rate on the take-home basis: the federal rate on a further dollar of salary
after the credits, where the basic federal tax (T1 line 42900) is above zero, and 0 where it is
not, a fraction (0.2 for 20%). Not printed on the form. An export of the form."""

MARGINAL_CONTRIBUTION_RATE = AmountKind.declare(
    CATALOG, "marginal_contribution_rate", non_negative=True
)
"""Contribution rate on a further dollar of salary: the CPP base, first additional and second
additional rates plus the EI rate of T2204 line 16. An exact sum, not printed on the form. An
export of the form."""

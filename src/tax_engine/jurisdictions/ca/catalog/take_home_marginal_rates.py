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
4.95% from the maximum basic exemption up to the maximum pensionable earnings, 0 outside it, from
the `ca/marginal_cpp_base_rate_rows` dataset. Not printed on the form."""

MARGINAL_CPP_FIRST_ADDITIONAL_RATE = AmountKind.declare(
    CATALOG, "marginal_cpp_first_additional_rate", non_negative=True
)
"""CPP first additional rate on a further dollar of salary, Schedule 8 Part 3 line 12 "multiplied
by 1%": 1% over the same earnings as the base rate, 0 outside them, from the
`ca/marginal_cpp_first_additional_rate_rows` dataset. Not printed on the form."""

MARGINAL_CPP_SECOND_ADDITIONAL_RATE = AmountKind.declare(
    CATALOG, "marginal_cpp_second_additional_rate", non_negative=True
)
"""CPP second additional rate on a further dollar of salary, Schedule 8 Part 3 line 22 "multiplied
by 4%": 4% from the maximum pensionable earnings up to the additional maximum pensionable
earnings, 0 outside it, from the `ca/marginal_cpp_second_additional_rate_rows` dataset. Not
printed on the form."""

MARGINAL_EI_RATE = AmountKind.declare(CATALOG, "marginal_ei_rate", non_negative=True)
"""EI rate on a further dollar of salary, T2204 line 16 "Enter whichever amount is the least: line
7, line 9 or line 12": 0 up to $2,000, 1 (a 100% band) up to the salary where line 12 is the
least, then the premium rate up to the maximum insurable earnings and 0 above, from the
`ca/marginal_ei_rate_rows` dataset. Not printed on the form."""

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

MARGINAL_FEDERAL_BPA_PHASE_DOWN_GATE = AmountKind.declare(
    CATALOG, "marginal_federal_bpa_phase_down_gate", non_negative=True
)
"""Federal basic personal amount gate: 1 where the net income (T1 line 23600) is in the band where
the basic personal amount falls with net income (T1 line 77), 0 outside it, from the
`ca/marginal_federal_bpa_rows` dataset. A plain figure, not printed on the form."""

MARGINAL_PHASE_DOWN_NET_INCOME_RATE = AmountKind.declare(
    CATALOG, "marginal_phase_down_net_income_rate", non_negative=True
)
"""Part of a further dollar of salary that lowers the basic personal amount: the part left in the
net income where the basic personal amount is phased down, 0 elsewhere. An exact product, not
printed on the form."""

MARGINAL_FEDERAL_BPA_REDUCTION_RATE = AmountKind.declare(
    CATALOG, "marginal_federal_bpa_reduction_rate", non_negative=True
)
"""Fall of the federal basic personal amount on a further dollar of salary: the net income part
over the phase-down times the Federal Worksheet's supplement over its range. Rounded as the
`ca/federal_bpa_phase_down_fraction` dataset says, not printed on the form."""

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

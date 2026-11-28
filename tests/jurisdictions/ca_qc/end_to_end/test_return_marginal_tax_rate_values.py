"""The Quebec marginal rate at a few salaries, worked by hand from the printed rates.

The marginal rate (`ca-qc/marginal_tax_rate`) is the extra take-home deductions on a further dollar
of salary: the federal tax (5005-R line 43500, less the refundable Quebec abatement of line 44000,
which is 16.5% of the basic federal tax), the Quebec tax (TP-1
line 450, with the prescription drug insurance premium), and the QPP, QPP2, EI and QPIP rates, for
a salary-only filer. The parts are the printed rates (5005-R "Line 74: Rate", Work Chart 401 line
5, Work Chart 201 line 9, TP-1 Schedule K line 80, Schedule 8 lines 11, 12 and 22, T2204 lines 10
and 16, Schedule 10 line 16), with the part of a salary dollar left in the net income
N = 1 - QPP first additional rate - QPP second additional rate (5005-R line 22215 and TP-1 line 248
take those contributions off the income) and T = N - 6% while the deduction for workers is under
its $1,420 maximum:

    federal  = (bracket rate x N + BPA phase-down - 14.5% x (QPP base + EI + QPIP)) x (1 - 16.5%),
               0 where no federal tax is paid
    Quebec   = Work Chart 401 rate x T, 0 where no Quebec tax is paid
    premium  = Schedule K line 80 rate x T, from a premium income of one cent to the $755 maximum
    marginal = federal + Quebec + premium + QPP base + QPP first additional + QPP2 + EI + QPIP

The engine rounds the marginal rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so each hand-derived exact sum below is stated rounded
half-up to four decimals in the test table (the exact sum stays in the worked lines).

The extra-run check over a sweep is in `test_return_marginal_tax_rate_extra_run.py`.

- 2025, $10,000: no income tax; QPP 5.4% + 1%, EI 1.31%, QPIP 0.494%: 0.08204.
- 2025, $22,000: federal 0.1331042 x 0.835 = 0.1111420; Quebec 14% x 0.93 = 0.1302; the premium
  row 7.84% x 0.93 = 0.072912; contributions 0.08204: 0.3962940.
- 2025, $40,000: federal 0.1111420; Quebec 14% x 0.99 (T = 0.99, the deduction for workers is at
  its maximum) = 0.1386; the premium is at its maximum, 0; contributions 0.08204: 0.3317820.
- 2025, $70,000 (over the EI maximum): federal (20.5% x 0.99 - 14.5% x (0.054 + 0.00494)) x 0.835 =
  0.1944037 x 0.835 = 0.1623271; Quebec 19% x 0.99 = 0.1881; contributions 0.054 + 0.01 +
  0.00494: 0.4193671.
- 2025, $75,000 (QPP2 band, no QPP base or EI): N = 0.96; federal (20.5% x 0.96 - 14.5% x 0.00494)
  x 0.835 = 0.1960837 x 0.835 = 0.1637299; Quebec 19% x 0.96; contributions 0.04 + 0.00494:
  0.3910699.
- 2025, $120,000: over the QPIP maximum, no contributions; federal 26% x 0.835 = 0.2171, Quebec
  24%: 0.4571.
- 2025, $200,000: the federal basic personal amount falls over $177,882 to $253,414: (29% + 14.5% x
  (1,591 / 75,532, which is 0.0210639 to seven places)) x 0.835 = 0.2447004, Quebec 25.75%:
  0.5022004.
- 2025, $300,000: federal 33% x 0.835 = 0.27555, Quebec 25.75%: 0.53305,
  which rounds half-up to 0.5331.
- 2026, $10,000, $70,000 and $200,000: the same parts with the 2026 datasets (provisional).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_qc.catalog import SCHEDULE_B_LINE_33
from tests.kinds import bundled_kinds

D = Decimal
QUEBEC = JurisdictionCode("CA-QC")


@pytest.mark.parametrize(
    ("year", "salary", "rate"),
    [
        (2025, "10000", "0.0820"),
        (2025, "22000", "0.3963"),
        (2025, "40000", "0.3318"),
        (2025, "70000", "0.4194"),
        (2025, "75000", "0.3911"),
        (2025, "120000", "0.4571"),
        (2025, "200000", "0.5022"),
        (2025, "300000", "0.5331"),
        (2026, "10000", "0.0803"),
        (2026, "70000", "0.4182"),
        (2026, "200000", "0.5021"),
    ],
)
def test_the_marginal_rate_is_the_sum_of_the_rates_that_apply_rounded_to_four_decimals(
    year: int, salary: str, rate: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(QUEBEC, year, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets["ca-qc/return"]

    assert summary.get(bundled_kinds().kind("ca-qc/marginal_tax_rate")).value == D(rate)


# The Quebec marginal rate of a filer 65 or over: the fall of the Schedule B age amount and of the
# career extension credit, worked by hand from the printed lines.
#
# Two TP-1 credits fall as net income (TP-1 line 275) rises, so a further dollar of salary costs
# more
# Quebec tax in their ranges. N is the part of a salary dollar left in the net income: 0.99 under
# the
# QPP maximum, 0.96 in the second additional contribution band and 1 over it (the first and second
# additional QPP rates, taken off by TP-1 line 248).
#
# Schedule B (TP-1.D.B-V, lines 18 to 34): line 18 is the net income over the threshold (line 10
# less
# line 16, 42,090 in 2025, 42,955 in 2026) and line 32 is line 30 (the age amount of line 22, 3,906
# in 2025 and 3,986 in 2026 for a filer 65 or over, plus the living-alone amount of line 20, 0 here)
# less line 31, the printed 18.75% of line 18. The amount falls by 18.75% of each dollar over the
# threshold while line 34 (line 32 less the spouse's line 33, 0 here) is still above 0 (the dollar
# that reaches 0.00 is not counted), and each
# dollar of that fall is Quebec tax at the TP-1 line 377.1 rate of 14%:
#
#     age term = 18.75% x N x 14% = 0.0259875 (N = 0.99)
#
# Career extension credit (TP-752.PC-V, lines 35 to 40): line 40 is line 35 (the credit before the
# reduction, 1,750 in 2025 and 1,785.70 in 2026) less line 39, 7% of line 38, the net income over
# the
# threshold of line 37 (56,500 in 2025, 57,660 in 2026). The credit reduces TP-1 line 399 dollar for
# dollar, so it falls by 7% of each dollar of net income over the threshold while line 40 is above
# 0:
#
#     career term = 7% x N = 0.0693 (N = 0.99), 0.0672 (N = 0.96), 0.07 (N = 1)
#
# Each term is counted only where the Quebec tax after credits (line 432) is above 0, like the
# bracket rate (Work Chart 401 line 5 x the part of the dollar left in the taxable income, N):
#
#     Quebec = (bracket rate x N + age term + career term) x gate
#
# The net income is 0.99 x salary - 1,385 in 2025 and 0.99 x salary - 1,415 in 2026 under the QPP
# maximum (the deduction for workers at its maximum of 1,420 and 1,450, and the first additional QPP
# rate of 1% over the 3,500 exemption). The salaries around a gate are worked back from the net
# income wanted, to the cent.
#
# The cases below are for a filer born in 1955: 2025, 14% bracket under 53,255 of taxable income,
# then 19%.
#
# - 2025, $43,914.14: net income 42,089.99 is under the threshold, no age term; Quebec 0.1386.
#   $43,914.15: net income 42,090.00 + 0.01 over it, age term 0.0259875; Quebec 0.1645875.
# - 2025, $50,000: age term only, Quebec 0.1386 + 0.0259875 = 0.1645875.
# - 2025, $58,469.70 and $58,469.71: net income reaches 56,500.01, the career term starts: Quebec
#   0.1881 + 0.0259875 = 0.2140875, then + 0.0693 = 0.2833875.
# - 2025, $64,956.54 and $64,956.55: line 34 reaches 0.00 (18.75% x 20,831.98 = 3,905.99 less than
# the
#   3,906 age amount), the age term stops: 0.2833875, then 0.1881 + 0.0693 = 0.2574.
# - 2025, $75,000 (N = 0.96): 0.19 x 0.96 + 0.07 x 0.96 = 0.2496.
# - 2025, $83,993.92 and $83,993.93 (N = 1): the credit is 0.00 at the second, so the career term
#   stops: 0.19 + 0.07 = 0.26, then 0.19.
# - 2026 follows the same lines with the 2026 figures (provisional): the age term from $44,818.19,
# the
#   career term from $59,671.73, the age term stops at $66,291.56 and the career term at $85,746.93.
#
# A filer born in 1980, or with no birth year, claims neither the age amount nor the career
# extension
# credit (the 65 or over flag is 0), so both terms are 0 at every salary above, whatever the net
# income.

THRESHOLD_GATE = "ca-qc/marginal_schedule_b_threshold_gate"
AMOUNT_GATE = "ca-qc/marginal_schedule_b_amount_gate"
CAREER_THRESHOLD_GATE = "ca-qc/marginal_career_extension_threshold_gate"
CAREER_AMOUNT_GATE = "ca-qc/marginal_career_extension_amount_gate"
AGE_TERM = "ca-qc/marginal_tp1_age_credit_rate"
CAREER_TERM = "ca-qc/marginal_tp1_career_extension_credit_rate"
BRACKET_TERM = "ca-qc/marginal_tp1_bracket_rate_on_taxable_income"
BEFORE_GATE = "ca-qc/marginal_tp1_rate_before_gate"
QUEBEC_RATE = "ca-qc/marginal_tp1_income_tax_rate"


def _summary(
    year: int, salary: str, birth_year: int | None, spouse_line_33: str | None = None
) -> Worksheet:
    given: tuple[Artifact[Decimal] | Artifact[int], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    if birth_year is not None:
        given = (*given, Artifact(BIRTH_YEAR, birth_year))
    if spouse_line_33 is not None:
        given = (*given, Artifact(SCHEDULE_B_LINE_33, D(spouse_line_33)))
    worksheets = build_tax_computation().compute(TaxCalculationRequest(QUEBEC, year, given))
    (summary,) = worksheets["ca-qc/return"]
    return summary


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


# Year, salary, bracket term, age term, career term and the Quebec rate (the bracket term and the
# two terms, summed) of a filer born in 1955, worked above.
BORN_1955 = [
    (2025, "43914.14", "0.1386", "0", "0", "0.1386"),
    (2025, "43914.15", "0.1386", "0.0259875", "0", "0.1645875"),
    (2025, "50000", "0.1386", "0.0259875", "0", "0.1645875"),
    (2025, "58469.70", "0.1881", "0.0259875", "0", "0.2140875"),
    (2025, "58469.71", "0.1881", "0.0259875", "0.0693", "0.2833875"),
    (2025, "64956.54", "0.1881", "0.0259875", "0.0693", "0.2833875"),
    (2025, "64956.55", "0.1881", "0", "0.0693", "0.2574"),
    (2025, "75000", "0.1824", "0", "0.0672", "0.2496"),
    (2025, "83993.92", "0.19", "0", "0.07", "0.26"),
    (2025, "83993.93", "0.19", "0", "0", "0.19"),
    (2026, "44818.18", "0.1386", "0", "0", "0.1386"),
    (2026, "44818.19", "0.1386", "0.0259875", "0", "0.1645875"),
    (2026, "50000", "0.1386", "0.0259875", "0", "0.1645875"),
    (2026, "59671.72", "0.1881", "0.0259875", "0", "0.2140875"),
    (2026, "59671.73", "0.1881", "0.0259875", "0.0693", "0.2833875"),
    (2026, "66291.55", "0.1881", "0.0259875", "0.0693", "0.2833875"),
    (2026, "66291.56", "0.1881", "0", "0.0693", "0.2574"),
    (2026, "80000", "0.1824", "0", "0.0672", "0.2496"),
    (2026, "85746.92", "0.19", "0", "0.07", "0.26"),
    (2026, "85746.93", "0.19", "0", "0", "0.19"),
]


@pytest.mark.parametrize(("year", "salary", "bracket", "age", "career", "rate"), BORN_1955)
def test_born_1955_the_quebec_rate_is_the_bracket_rate_plus_the_two_terms(
    year: int, salary: str, bracket: str, age: str, career: str, rate: str
) -> None:
    summary = _summary(year, salary, 1955)

    assert _value(summary, BRACKET_TERM) == D(bracket)
    assert _value(summary, AGE_TERM) == D(age)
    assert _value(summary, CAREER_TERM) == D(career)
    assert _value(summary, BEFORE_GATE) == D(rate)
    assert _value(summary, QUEBEC_RATE) == D(rate)


# Year, salary, the four gates in the order age threshold, age amount, career threshold, career
# amount, for a filer born in 1955: each opens or shuts on the cent worked above. At $0 of salary
# the career extension credit is 0 already (no work income), so its amount gate is shut.
GATES = [
    (2025, "0", "0", "1", "0", "0"),
    (2025, "43914.14", "0", "1", "0", "1"),
    (2025, "43914.15", "1", "1", "0", "1"),
    (2025, "58469.70", "1", "1", "0", "1"),
    (2025, "58469.71", "1", "1", "1", "1"),
    (2025, "64956.54", "1", "1", "1", "1"),
    (2025, "64956.55", "1", "0", "1", "1"),
    (2025, "83993.92", "1", "0", "1", "1"),
    (2025, "83993.93", "1", "0", "1", "0"),
    (2026, "0", "0", "1", "0", "0"),
    (2026, "44818.18", "0", "1", "0", "1"),
    (2026, "44818.19", "1", "1", "0", "1"),
    (2026, "59671.72", "1", "1", "0", "1"),
    (2026, "59671.73", "1", "1", "1", "1"),
    (2026, "66291.55", "1", "1", "1", "1"),
    (2026, "66291.56", "1", "0", "1", "1"),
    (2026, "85746.92", "1", "0", "1", "1"),
    (2026, "85746.93", "1", "0", "1", "0"),
]


@pytest.mark.parametrize(
    ("year", "salary", "age_over", "age_left", "career_over", "career_left"), GATES
)
def test_born_1955_the_gates_open_and_shut_on_the_cent_the_amounts_reach_their_limits(
    year: int, salary: str, age_over: str, age_left: str, career_over: str, career_left: str
) -> None:
    summary = _summary(year, salary, 1955)

    assert _value(summary, THRESHOLD_GATE) == D(age_over)
    assert _value(summary, AMOUNT_GATE) == D(age_left)
    assert _value(summary, CAREER_THRESHOLD_GATE) == D(career_over)
    assert _value(summary, CAREER_AMOUNT_GATE) == D(career_left)


@pytest.mark.parametrize(
    "salary", ["0", "43914.15", "50000", "60000", "75000", "83993.92", "90000"]
)
@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("birth_year", [1980, None])
def test_a_filer_born_in_1980_or_with_no_year_has_both_terms_at_0(
    birth_year: int | None, year: int, salary: str
) -> None:
    summary = _summary(year, salary, birth_year)

    assert _value(summary, AGE_TERM) == D("0")
    assert _value(summary, CAREER_TERM) == D("0")
    assert _value(summary, BEFORE_GATE) == _value(summary, BRACKET_TERM)


@pytest.mark.parametrize(
    ("spouse_line_33", "age_term"),
    [("0", "0.0259875"), ("2776.30", "0.0259875"), ("2776.31", "0"), ("5000", "0")],
)
def test_the_age_term_follows_line_34_so_the_spouses_line_33_can_shut_it_off(
    spouse_line_33: str, age_term: str
) -> None:
    # Born 1955, $50,000 in 2025: net income 48,115 less the 42,090 threshold is 6,025 over, so line
    # 31 is 18.75% x 6,025 = 1,129.69 and line 32 is 3,906 - 1,129.69 = 2,776.31. The spouse's line
    # 33 comes off line 32 to give line 34, which has no floor: the fall stops once line 34 is 0 or
    # less (the dollar that reaches 0.00 is not counted).
    summary = _summary(2025, "50000", 1955, spouse_line_33)

    assert _value(summary, AGE_TERM) == D(age_term)

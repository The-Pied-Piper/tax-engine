"""The fall of the age amount in the British Columbia marginal rate, worked by hand, both years.

A filer born in 1960 or earlier claims the age amount on BC428 line 17 (Worksheet BC428 "Line 58080
- Age amount") and on T1 line 30100. Worksheet line 4 is the net income over the threshold (BC:
43,169.00 in 2025 and 44,119.00 in 2026; federal: 45,522.00 and 46,432.00), line 5 the printed 15%,
line 6 line 4 times 15% and line 7 the maximum (BC: 5,799.00 and 5,927.00; federal: 9,028.00 and
9,209.00) less line 6, not below 0. Each further dollar of net income over a threshold takes 15
cents off that credit amount, and the credit is worth the credit rate (BC428 line 55: 5.06% in
2025, 5.60% in 2026; T1 line 114: 14.5% in 2025, 14% in 2026), so the rate on a further dollar of
salary is higher by

    15% x N x credit rate,   N = the part of a dollar left in the net income (1 less the CPP first
                             and second additional rates)

in British Columbia while line 4 is above 0 and an amount is still claimed, and in the federal part
from the federal threshold on (the federal amount reaches 0 only at a net income above 105,000, so
it is still falling where the British Columbia amount has run out).

The net income is the salary less the CPP enhanced contribution (T1 line 22215): 1% of the salary
over 3,500 up to the year's maximum pensionable earnings (71,300 in 2025), and the CPP2 contribution
of 4% of the salary over it, up to the second ceiling (81,200). A filer born in 1955 pays CPP in
2025 (turning 70 in the year) but not in 2026, so in 2026 her net income is her salary, N = 1 and
the contributions are the EI rate alone (1.63% up to 68,900); a filer born in 1980 pays CPP in
both years.

2025, born 1955 (N = 0.99 up to 71,300, 1 above 81,200):
- Salary 43,569.70: CPP enhanced 400.697 -> 400.70, net income 43,169.00 = the BC threshold, line 4
  = 0.00: no effect. Salary 43,570.71: CPP enhanced 400.71, net income 43,170.00, line 4 = 1.00,
  line 6 = 0.15, line 7 = 5,798.85: the full British Columbia rate applies at once (the federal
  threshold is further up).
- Salary 47,000: net income 47,000 - 435.00 = 46,565.00 (over both thresholds), line 4 = 3,396.00,
  line 6 = 509.40, line 7 = 5,289.60. Salary 60,000: net income 59,435.00, line 4 = 16,266.00,
  line 6 = 2,439.90, line 7 = 3,359.10.
- Salary 82,902.96: net income = salary - 678.00 - 396.00 = 81,828.96, line 4 = 38,659.96, line 6 =
  5,798.994 -> 5,798.99, line 7 = 0.01: the last cent of the British Columbia credit. Salary
  82,902.97: net income 81,828.97, line 6 = 5,798.9955 -> 5,799.00, line 7 = 0: the credit is gone.
2026, born 1955 (N = 1):
- Salary 44,119.00 = the threshold, line 4 = 0.00; 44,120.00: line 4 = 1.00, line 7 = 5,926.85.
- Salary 47,000: line 4 = 2,881.00, line 6 = 432.15, line 7 = 5,494.85 (over both thresholds).
  Salary 60,000: line 4 = 15,881.00, line 6 = 2,382.15, line 7 = 3,544.85.
- Salary 83,632.29: line 4 = 39,513.29, line 6 = 5,926.9935 -> 5,926.99, line 7 = 0.01. Salary
  83,632.30: line 4 = 39,513.30, line 6 = 5,926.995 -> 5,927.00 (half up), line 7 = 0.

Each total is the exact sum of the federal rate, the British Columbia rate and the contribution
rate, rounded half-up to 0.0001. Without an age amount (born 1980, or no year of birth):

- 2025, 43,569.70 and 43,570.71: federal 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945; British
  Columbia 5.06% x 0.99 - 5.06% x 0.0659 = 0.04675946; contributions 0.0759: 0.25665396.
- 2025, 47,000: the same. 2025, 60,000: federal 20.5% x 0.99 - 14.5% x 0.0659 = 0.1933945;
  British Columbia 7.7% x 0.99 - 5.06% x 0.0659 = 0.07289546; 0.0759: 0.34218996.
- 2025, 82,902.96 and .97 (no contributions): 20.5% + 7.7% = 0.282.
- 2026, 44,119 and 44,120 (net income under 44,952, where the British Columbia tax reduction of
  BC428 lines 73 to 79 is still falling: 3.56% x 0.99 more): federal 14% x 0.99 - 14% x 0.0658 =
  0.129388; British Columbia 5.6% x 0.99 - 5.6% x 0.0658 + 3.56% x 0.99 = 0.0517552 + 0.035244 =
  0.0869992; contributions 0.0758: 0.2921872.
- 2026, 47,000: the reduction has run out: 0.129388 + 0.0517552 + 0.0758 = 0.2569432.
- 2026, 60,000: federal 20.5% x 0.99 - 14% x 0.0658 = 0.193738; British Columbia 7.7% x 0.99 - 5.6%
  x 0.0658 = 0.0725452; 0.0758: 0.3420832.
- 2026, 83,632.29 and .30 (CPP2 band, N = 0.96): 20.5% x 0.96 + 7.7% x 0.96 + 4% = 0.31072.

With the age amount (born 1955):

- 2025, 43,570.71: British Columbia part + 0.15 x 0.99 x 0.0506 = 0.0075141: 0.26416806.
- 2025, 47,000: federal + 0.15 x 0.99 x 0.145 = 0.0215325, British Columbia + 0.0075141: 0.1339945 +
  0.0215325 + 0.04675946 + 0.0075141 + 0.0759 = 0.28570056.
- 2025, 60,000: 0.1933945 + 0.0215325 + 0.07289546 + 0.0075141 + 0.0759 = 0.37123656.
- 2025, 82,902.96: federal 20.5% + 0.15 x 0.145 = 0.02175; British Columbia 7.7% + 0.15 x 0.0506 =
  0.00759: 0.205 + 0.02175 + 0.077 + 0.00759 = 0.31134.
- 2025, 82,902.97: the British Columbia term is gone, the federal one stays: 0.30375 (rounded half
  up, 0.3038).
- 2026 (no CPP: N = 1, EI 1.63% to 68,900): federal 14% x 1 - 14% x 0.0163 = 0.137718 (20.5% -
  0.002282 = 0.202718 over 58,523); British Columbia 5.6% - 5.6% x 0.0163 = 0.0550872 (7.7% -
  0.0009128 = 0.0760872 over 50,363); the terms are 0.15 x 0.056 = 0.0084 (British Columbia) and
  0.15 x 0.14 = 0.021 (federal).
  - 44,119 (the tax reduction is still falling, 3.56% x 1 more): 0.137718 + 0.0550872 + 0.0356 +
    0.0163 = 0.2447052.
  - 44,120: + 0.0084: 0.2531052.
  - 47,000: 0.137718 + 0.021 + 0.0550872 + 0.0084 + 0.0163 = 0.2385052.
  - 60,000: 0.202718 + 0.021 + 0.0760872 + 0.0084 + 0.0163 = 0.3245052.
  - 83,632.29 (no EI above 68,900): 0.205 + 0.021 + 0.077 + 0.0084 = 0.3114.
  - 83,632.30: 0.205 + 0.021 + 0.077 = 0.303.

British Columbia's gate on BC428 line 80 stays on the age term, but a filer over the age threshold
always owes British Columbia tax, so the gate is open at every salary here.
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
from tests.kinds import bundled_kinds

D = Decimal
BRITISH_COLUMBIA = JurisdictionCode("CA-BC")
RETURN = "ca-bc/return"
BC428_FORM = "ca-bc/bc428"
MARGINAL = "ca-bc/marginal_tax_rate"
BC_RATE = "ca-bc/british_columbia_marginal_rate"
FEDERAL = "ca-bc/marginal_federal_rate"
AGE_CREDIT_RATE = "ca-bc/marginal_british_columbia_age_credit_rate"
AGE_REDUCTION_RATE = "ca-bc/marginal_british_columbia_age_reduction_rate"
THRESHOLD_GATE = "ca-bc/british_columbia_age_threshold_gate"
AMOUNT_GATE = "ca-bc/british_columbia_age_amount_gate"
LINE_4 = "ca-bc/worksheet_bc428_age_amount_line_4"
LINE_7 = "ca-bc/worksheet_bc428_age_amount_line_7"


def _sheets(year: int, salary: str, birth_year: int | None) -> dict[str, Worksheet]:
    given: tuple[Artifact[Decimal] | Artifact[int], ...] = (Artifact(EMPLOYMENT_INCOME, D(salary)),)
    if birth_year is not None:
        given = (*given, Artifact(BIRTH_YEAR, birth_year))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(BRITISH_COLUMBIA, year, given)
    )
    return {form: sheet for form, (sheet, *_) in worksheets.items()}


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


# (year, salary, line 4, line 7, British Columbia age credit rate, marginal rate born 1955,
# marginal rate born 1980 or with no year of birth), hand-worked in the module text.
RANGE = [
    (2025, "0", "0", "5799", "0", "0", "0"),
    (2025, "43569.70", "0", "5799", "0", "0.2567", "0.2567"),
    (2025, "43570.71", "1", "5798.85", "0.0075141", "0.2642", "0.2567"),
    (2025, "47000", "3396", "5289.6", "0.0075141", "0.2857", "0.2567"),
    (2025, "60000", "16266", "3359.1", "0.0075141", "0.3712", "0.3422"),
    (2025, "82902.96", "38659.96", "0.01", "0.00759", "0.3113", "0.282"),
    (2025, "82902.97", "38659.97", "0", "0", "0.3038", "0.282"),
    (2026, "0", "0", "5927", "0", "0", "0"),
    (2026, "44119", "0", "5927", "0", "0.2447", "0.2922"),
    (2026, "44120", "1", "5926.85", "0.0084", "0.2531", "0.2922"),
    (2026, "47000", "2881", "5494.85", "0.0084", "0.2385", "0.2569"),
    (2026, "60000", "15881", "3544.85", "0.0084", "0.3245", "0.3421"),
    (2026, "83632.29", "39513.29", "0.01", "0.0084", "0.3114", "0.3107"),
    (2026, "83632.30", "39513.30", "0", "0", "0.303", "0.3107"),
]


@pytest.mark.parametrize(
    ("year", "salary", "line_4", "line_7", "age_credit", "born_1955", "_born_1980"), RANGE
)
def test_a_filer_born_1955_pays_the_fall_of_the_age_amount_in_the_marginal_rate(
    year: int,
    salary: str,
    line_4: str,
    line_7: str,
    age_credit: str,
    born_1955: str,
    _born_1980: str,
) -> None:
    sheets = _sheets(year, salary, 1955)

    assert _value(sheets[BC428_FORM], LINE_4) == D(line_4)
    assert _value(sheets[BC428_FORM], LINE_7) == D(line_7)
    assert _value(sheets[RETURN], AGE_CREDIT_RATE) == D(age_credit)
    assert _value(sheets[RETURN], MARGINAL) == D(born_1955)


@pytest.mark.parametrize(
    ("year", "salary", "_line_4", "_line_7", "_age_credit", "_born_1955", "born_1980"), RANGE
)
@pytest.mark.parametrize("birth_year", [1980, None])
def test_a_filer_born_1980_or_with_no_birth_year_has_no_age_amount_in_the_marginal_rate(
    year: int,
    salary: str,
    _line_4: str,
    _line_7: str,
    _age_credit: str,
    _born_1955: str,
    born_1980: str,
    birth_year: int | None,
) -> None:
    sheets = _sheets(year, salary, birth_year)

    assert _value(sheets[RETURN], AGE_CREDIT_RATE) == D("0")
    assert _value(sheets[RETURN], MARGINAL) == D(born_1980)


@pytest.mark.parametrize(
    ("year", "salary", "threshold_gate", "amount_gate"),
    [
        (2025, "43569.70", "0", "1"),
        (2025, "43570.71", "1", "1"),
        (2025, "82902.96", "1", "1"),
        (2025, "82902.97", "1", "0"),
        (2026, "44119", "0", "1"),
        (2026, "44120", "1", "1"),
        (2026, "83632.29", "1", "1"),
        (2026, "83632.30", "1", "0"),
    ],
)
def test_the_two_gates_open_at_the_threshold_and_close_when_the_amount_is_gone(
    year: int, salary: str, threshold_gate: str, amount_gate: str
) -> None:
    # The threshold gate follows worksheet line 4 (0.00 up to the threshold), the amount gate the
    # amount still claimed (line 7 reaches 0.00 at the salaries below, to the cent).
    sheets = _sheets(year, salary, 1955)

    assert _value(sheets[RETURN], THRESHOLD_GATE) == D(threshold_gate)
    assert _value(sheets[RETURN], AMOUNT_GATE) == D(amount_gate)


@pytest.mark.parametrize(
    ("year", "last_born", "credit_rate", "federal_credit_rate"),
    [(2025, 1960, "0.0506", "0.145"), (2026, 1961, "0.056", "0.14")],
)
def test_the_age_term_is_the_printed_rate_times_the_net_income_rate_times_the_credit_rate(
    year: int, last_born: int, credit_rate: str, federal_credit_rate: str
) -> None:
    # The last year of birth that is 65 at the end of the year (1960 in 2025, 1961 in 2026) and the
    # year after it differ in the age amount alone, and both pay CPP: 15% x 0.99 x the credit rate
    # in each part, at a salary over both thresholds.
    claims = _sheets(year, "60000", last_born)
    does_not = _sheets(year, "60000", last_born + 1)
    net_income_rate = D("0.99")

    assert _value(claims[RETURN], AGE_REDUCTION_RATE) == D("0.15")
    assert _value(does_not[RETURN], AGE_CREDIT_RATE) == D("0")
    assert _value(claims[RETURN], AGE_CREDIT_RATE) == D("0.15") * net_income_rate * D(credit_rate)
    assert _value(claims[RETURN], BC_RATE) - _value(does_not[RETURN], BC_RATE) == (
        D("0.15") * net_income_rate * D(credit_rate)
    )
    assert _value(claims[RETURN], FEDERAL) - _value(does_not[RETURN], FEDERAL) == (
        D("0.15") * net_income_rate * D(federal_credit_rate)
    )

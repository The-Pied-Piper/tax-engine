"""The fall of the Nova Scotia age amount in the marginal rate, through the real engine, by hand.

A filer born in 1960 or earlier claims the age amount (NS428 line 10, Worksheet NS428 "Line 58080 -
Age amount"): the maximum (5,734 in 2025; 5,826 in 2026) less line 5 "Applicable rate 15%" of the
net income over the threshold of 30,828 (line 4), not below 0. Every dollar of that fall is tax at
the Nova Scotia credit rate (NS428 line 47, 8.79%), so a further dollar of salary adds

    15% x N x 8.79% = 0.01305315 (N = 0.99 in 2025 for a filer who pays CPP; 0.013185 where N = 1)

to the Nova Scotia part, while the net income is over the threshold and an age amount is still
claimed, and nothing otherwise (a filer under 65 or with no birth year claims none). N is the part
of a dollar left in the net income: T1 line 22215 takes the enhanced CPP (1%) off it, so N = 0.99.
In 2026 a filer born in 1955 is past 70 and pays no CPP, so N = 1, the contribution rate is the EI
rate of 1.63% alone, and the net income is the salary.

The rest of each figure is the one of `test_return_marginal_tax_rate_values.py`:

- 2025, 14.95% bracket (taxable income from 30,507 to 61,015), CPP 4.95% + 1% and EI 1.64%:
  14.95% x 0.99 - 8.79% x 0.0659 = 0.14221239, plus the age term 0.01305315: 0.15526554.
- 2025, 16.67% bracket, over the EI maximum (CPP base 4.95% only): 16.67% x 0.99 - 8.79% x 0.0495
  = 0.16068195, plus the age term: 0.1737351.
- 2026, 8.79% bracket (to 30,995): 8.79% - 8.79% x 0.0163 = 0.08646723.
- 2026, 14.95% bracket (to 61,991): 14.95% - 8.79% x 0.0163 = 0.14806723, plus 0.013185: 0.16125223.
- 2026, 16.67% bracket, over the EI maximum of 68,900 (no contribution): 0.1667, plus 0.013185:
  0.179885.

The salaries are worked back from the net income wanted: net income = salary less 1% of the salary
over 3,500 (the enhanced CPP, rounded to the cent). The zero point is where the cent-rounded
line 6 (15% of line 4) reaches the maximum: 2025 5,734 at line 4 = 38,226.64 (5,733.996, rounded to
5,734.00), so line 4 = 38,226.63 (5,733.9945, rounded to 5,733.99) is the last cent with 0.01 left,
net income 69,054.63; 2026 5,826 at line 4 = 38,839.97 (5,825.9955), so line 4 = 38,839.96
(5,825.994) is the last, net income 69,667.96.
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
NOVA_SCOTIA = JurisdictionCode("CA-NS")

OVER_THRESHOLD = "ca-ns/marginal_age_income_over_threshold"
CLAIMED = "ca-ns/marginal_age_amount_claimed"
THRESHOLD_GATE = "ca-ns/marginal_age_threshold_gate"
AMOUNT_GATE = "ca-ns/marginal_age_amount_gate"
AGE_RATE = "ca-ns/marginal_age_rate"
AGE_CREDIT_RATE = "ca-ns/marginal_nova_scotia_age_credit_rate"
TAX_GATE = "ca-ns/nova_scotia_rate_gate"
PROVINCIAL = "ca-ns/nova_scotia_marginal_rate"
MARGINAL = "ca-ns/marginal_tax_rate"

# Year, salary, over the threshold (worksheet line 4), age amount claimed (before the printed
# maximum check), the two gates, the age term, and the Nova Scotia marginal rate, all for a filer
# born in 1955.
BORN_1955 = [
    # 2025: net income = salary less 1% of the salary over 3,500.
    # $0: nothing yet; the threshold gate is shut and no tax.
    (2025, "0", "0.00", "5734.00", "0", "1", "0", "0"),
    # Net income 30,828.00 = the threshold: line 4 is 0.00, no effect.
    (2025, "31104.04", "0.00", "5734.00", "0", "1", "0", "0.14221239"),
    # Net income 30,828.01: one cent over; the whole 15% starts at once.
    (2025, "31104.05", "0.01", "5734.00", "1", "1", "0.01305315", "0.15526554"),
    # Net income 30,829.00: $1 over; line 6 is 0.15, line 7 is 5,733.85.
    (2025, "31105.05", "1.00", "5733.85", "1", "1", "0.01305315", "0.15526554"),
    # Net income 39,635.00: 8,807 over; line 6 is 1,321.05, line 7 is 4,412.95.
    (2025, "40000", "8807.00", "4412.95", "1", "1", "0.01305315", "0.15526554"),
    # Net income 69,054.63: line 4 is 38,226.63, line 7 is 0.01, the last cent with an amount left.
    (2025, "69716.80", "38226.63", "0.01", "1", "1", "0.01305315", "0.1737351"),
    # Net income 69,054.64: line 6 rounds to 5,734.00, nothing is left, the term is off again.
    (2025, "69716.81", "38226.64", "0.00", "1", "0", "0", "0.16068195"),
    # 2026: no CPP, so net income = salary.
    (2026, "0", "0.00", "5826.00", "0", "1", "0", "0"),
    (2026, "30828", "0.00", "5826.00", "0", "1", "0", "0.08646723"),
    (2026, "30828.01", "0.01", "5826.00", "1", "1", "0.013185", "0.09965223"),
    (2026, "30829", "1.00", "5825.85", "1", "1", "0.013185", "0.09965223"),
    (2026, "40000", "9172.00", "4450.20", "1", "1", "0.013185", "0.16125223"),
    (2026, "60000", "29172.00", "1450.20", "1", "1", "0.013185", "0.16125223"),
    (2026, "69667.96", "38839.96", "0.01", "1", "1", "0.013185", "0.179885"),
    (2026, "69667.97", "38839.97", "0.00", "1", "0", "0", "0.1667"),
]


def _summary(year: int, salary: str, born: int | None) -> Worksheet:
    extra = () if born is None else (Artifact(BIRTH_YEAR, born),)
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NOVA_SCOTIA, year, (Artifact(EMPLOYMENT_INCOME, D(salary)), *extra))
    )
    (summary,) = worksheets["ca-ns/return"]
    return summary


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("year", "salary", "over", "claimed", "threshold_gate", "amount_gate", "term", "provincial"),
    BORN_1955,
)
def test_born_1955_the_age_amount_falls_only_over_the_threshold_and_while_some_is_left(
    year: int,
    salary: str,
    over: str,
    claimed: str,
    threshold_gate: str,
    amount_gate: str,
    term: str,
    provincial: str,
) -> None:
    summary = _summary(year, salary, 1955)

    assert _value(summary, OVER_THRESHOLD) == D(over)
    assert _value(summary, CLAIMED) == D(claimed)
    assert _value(summary, THRESHOLD_GATE) == D(threshold_gate)
    assert _value(summary, AMOUNT_GATE) == D(amount_gate)
    assert _value(summary, AGE_RATE) == D("0.15")
    assert _value(summary, AGE_CREDIT_RATE) == D(term)
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("year", "salary", "provincial"),
    [
        (2025, "0", "0"),
        (2025, "31104.04", "0.14221239"),
        (2025, "31104.05", "0.14221239"),
        (2025, "31105.05", "0.14221239"),
        (2025, "40000", "0.14221239"),
        (2025, "69716.80", "0.16068195"),
        (2025, "69716.81", "0.16068195"),
        (2026, "0", "0"),
        # 14.95% x 0.99 - 8.79% x 0.0658 = 0.148005 - 0.00578382.
        (2026, "40000", "0.14222118"),
    ],
)
@pytest.mark.parametrize("born", [1980, None])
def test_born_1980_or_with_no_birth_year_the_age_amount_never_changes_the_rate(
    born: int | None, year: int, salary: str, provincial: str
) -> None:
    # A filer under 65 (or with no birth year) claims no age amount: the amount gate is shut
    # although the net income is over the threshold, and the Nova Scotia part is the bracket rate
    # after the CPP and EI credits alone.
    summary = _summary(year, salary, born)

    assert _value(summary, CLAIMED) == D("0")
    assert _value(summary, AMOUNT_GATE) == D("0")
    assert _value(summary, AGE_CREDIT_RATE) == D("0")
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("year", "salary", "born", "marginal"),
    [
        # Below the federal age threshold the federal part is the bracket rate alone: 2025,
        # 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945 with contributions of 0.0759.
        (2025, "31104.04", 1955, "0.3521"),  # 0.1339945 + 0.14221239 + 0.0759
        (2025, "31104.04", 1980, "0.3521"),
        (2025, "31104.05", 1955, "0.3652"),  # 0.1339945 + 0.15526554 + 0.0759
        (2025, "31104.05", 1980, "0.3521"),
        (2025, "40000", 1955, "0.3652"),
        (2025, "40000", 1980, "0.3521"),
        # 2026, born 1955: no CPP, federal 14% - 14% x 0.0163 = 0.137718, EI 0.0163.
        (2026, "30828", 1955, "0.2405"),  # 0.137718 + 0.08646723 + 0.0163
        (2026, "30828.01", 1955, "0.2537"),  # 0.137718 + 0.09965223 + 0.0163
        (2026, "40000", 1955, "0.3153"),  # 0.137718 + 0.16125223 + 0.0163
        # 2026, born 1980: federal 14% x 0.99 - 14% x 0.0658 = 0.129388, contributions 0.0758.
        (2026, "40000", 1980, "0.3474"),  # 0.129388 + 0.14222118 + 0.0758
    ],
)
def test_the_total_marginal_rate_below_the_federal_age_threshold(
    year: int, salary: str, born: int, marginal: str
) -> None:
    assert _value(_summary(year, salary, born), MARGINAL) == D(marginal)


@pytest.mark.parametrize("salary", ["31104.05", "40000", "69716.80", "69716.81"])
def test_the_line_99_gate_still_governs_the_age_term(salary: str) -> None:
    # The age term is inside the provincial part, which is the line 99 gate times the rate.
    summary = _summary(2025, salary, 1955)

    assert _value(summary, TAX_GATE) == D("1")
    assert _value(summary, PROVINCIAL) == _value(summary, TAX_GATE) * _value(
        summary, "ca-ns/marginal_nova_scotia_rate_with_reduction"
    )

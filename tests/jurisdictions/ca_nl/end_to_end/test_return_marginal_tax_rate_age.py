"""The fall of the age amount in the Newfoundland and Labrador marginal rate, 2025 and 2026.

For a filer born in 1960 or earlier the age amount (NL428 line 17, Worksheet NL428 "Line 58080 -
Age amount") falls by 15% (worksheet line 5 "Applicable rate 15%") of the net income over the
threshold (worksheet line 3 "Income threshold": 38,712 in 2025, 39,138 in 2026) until it is 0. Each
dollar of that fall is taxed at the NL428 credit rate (line 57, 8.7%), so a further dollar of salary
adds 15% x (the part left in the net income) x 8.7% to the provincial rate while line 4 is above 0
and an age amount is still claimed, and the federal rate adds its own term the same way (15% x the
part left x the federal credit rate: 14.5% in 2025, 14% in 2026). Each figure is worked by hand
from the printed rates; the boundaries are found cent by cent from the engine and checked against
the worksheet's arithmetic.

2025, born 1955 (CPP still applies, so the net income is the salary less 1% of the salary over
3,500, N = 0.99 below the CPP ceiling):

- net income = threshold at a salary of 39,067.68 (39,067.68 less 1% of 35,567.68 = 355.68 is
  38,712.00): line 4 is 0.00 and nothing is added; at 39,067.69 line 4 is 0.01 and the term is
  0.15 x 0.99 x 0.087 = 0.0129195 (federal 0.15 x 0.99 x 0.145 = 0.0215325 once the net income
  passes the federal threshold of 45,522, as at 46,000);
- 40,000: net income 39,635, line 4 923.00, line 6 138.45, line 7 6,925.55; the provincial rate is
  0.0803967 + 0.0129195 = 0.0933162 and the total 0.1339945 + 0.0933162 + 0.0759 = 0.3032107;
- 46,000: net income 45,575, line 4 6,863.00, line 6 1,029.45, line 7 6,034.55; federal 0.1339945 +
  0.0215325 = 0.155527, provincial 0.1378167 + 0.0129195 = 0.1507362, total 0.3821632;
- 60,000: net income 59,435, line 4 20,723.00, line 6 3,108.45, line 7 3,955.55; federal 0.1933945 +
  0.0215325 = 0.214927, provincial 0.1507362, total 0.4415632;
- the amount reaches 0 where 15% of line 4 rounds up to 7,064.00, that is at line 4 of 47,093.30
  (15% is 7,063.995, a half, rounded up): at line 4 of 47,093.29 the amount is 0.01. With the CPP
  and CPP2 ceilings reached (net income = salary less 678.00 and 396.00) that is a salary of
  86,879.29 (claimed 0.01, N = 1, the bracket rate 14.5%: provincial 0.145 + 0.15 x 0.087 = 0.15805,
  federal 0.205 + 0.15 x 0.145 = 0.22675, total 0.3848) and 86,879.30 (provincial 0.145, federal
  0.22675, total 0.37175 rounded half-up to 0.3718).

2026, born 1955 (71 in 2026, so no CPP; EI 1.63% only, N = 1, net income = salary): the net income
is the threshold of 39,138 at a salary of 39,138.00 (line 4 0.00) and passes it at 39,138.01. The
provincial rate at 40,000 is 8.7% - 8.7% x 0.0163 + 0.15 x 0.087 = 0.0986319 and the total 0.14 -
0.14 x 0.0163 = 0.137718 federal + 0.0986319 + 0.0163 = 0.2526499. The amount reaches 0 at line 4
of 47,613.30 (15% is 7,141.995, rounded up to 7,142.00), so a salary of 86,751.29 still claims 0.01
and 86,751.30 does not.

A filer born in 1980, or with no birth year, claims no age amount: the age gate is 0 and the rate is
the one without the term (the figures of `test_return_marginal_tax_rate_values.py`).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

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
NEWFOUNDLAND = JurisdictionCode("CA-NL")
RETURN = "ca-nl/return"

LINE_4 = "ca-nl/age_income_over_threshold_return"
CLAIMED = "ca-nl/age_amount_claimed_return"
THRESHOLD_GATE = "ca-nl/age_income_over_threshold_gate"
AMOUNT_GATE = "ca-nl/age_amount_gate"
AGE_TERM = "ca-nl/marginal_newfoundland_and_labrador_age_credit_rate"
PROVINCIAL = "ca-nl/newfoundland_and_labrador_marginal_rate"
MARGINAL = "ca-nl/marginal_tax_rate"

# (tax year, salary, born): line 4, the age amount claimed, the threshold gate, the amount gate,
# the age term, the provincial rate and the marginal tax rate, worked by hand as the docstring says.
AGE_CASES = [
    # Born 1955, 2025.
    (2025, "0", 1955, "0.00", "7064.00", "0", "1", "0", "0", "0"),
    (2025, "39067.68", 1955, "0.00", "7064.00", "0", "1", "0", "0.0803967", "0.2903"),
    (2025, "39067.69", 1955, "0.01", "7064.00", "1", "1", "0.0129195", "0.0933162", "0.3032"),
    (2025, "40000", 1955, "923.00", "6925.55", "1", "1", "0.0129195", "0.0933162", "0.3032"),
    (2025, "46000", 1955, "6863.00", "6034.55", "1", "1", "0.0129195", "0.1507362", "0.3822"),
    (2025, "60000", 1955, "20723.00", "3955.55", "1", "1", "0.0129195", "0.1507362", "0.4416"),
    (2025, "86879.29", 1955, "47093.29", "0.01", "1", "1", "0.01305", "0.15805", "0.3848"),
    (2025, "86879.30", 1955, "47093.30", "0.00", "1", "0", "0", "0.145", "0.3718"),
    (2025, "90000", 1955, "50214.00", "0.00", "1", "0", "0", "0.158", "0.3848"),
    # Born 1980 and no birth year, 2025: no age amount, the figures without the term.
    (2025, "0", 1980, "0.00", "0.00", "0", "0", "0", "0", "0"),
    (2025, "40000", 1980, "923.00", "0.00", "1", "0", "0", "0.0803967", "0.2903"),
    (2025, "46000", 1980, "6863.00", "0.00", "1", "0", "0", "0.1378167", "0.3477"),
    (2025, "60000", 1980, "20723.00", "0.00", "1", "0", "0", "0.1378167", "0.4071"),
    (2025, "86879.29", 1980, "47093.29", "0.00", "1", "0", "0", "0.145", "0.35"),
    (2025, "40000", None, "923.00", "0.00", "1", "0", "0", "0.0803967", "0.2903"),
    (2025, "60000", None, "20723.00", "0.00", "1", "0", "0", "0.1378167", "0.4071"),
    # Born 1955, 2026 (no CPP at 71).
    (2026, "0", 1955, "0.00", "7142.00", "0", "1", "0", "0", "0"),
    (2026, "39138.00", 1955, "0.00", "7142.00", "0", "1", "0", "0.0855819", "0.2396"),
    (2026, "39138.01", 1955, "0.01", "7142.00", "1", "1", "0.01305", "0.0986319", "0.2526"),
    (2026, "40000", 1955, "862.00", "7012.70", "1", "1", "0.01305", "0.0986319", "0.2526"),
    (2026, "60000", 1955, "20862.00", "4012.70", "1", "1", "0.01305", "0.1566319", "0.3966"),
    (2026, "86751.29", 1955, "47613.29", "0.01", "1", "1", "0.01305", "0.15805", "0.3841"),
    (2026, "86751.30", 1955, "47613.30", "0.00", "1", "0", "0", "0.145", "0.371"),
    # Born 1980 and no birth year, 2026.
    (2026, "40000", 1980, "497.00", "0.00", "1", "0", "0", "0.0804054", "0.2856"),
    (2026, "40000", None, "497.00", "0.00", "1", "0", "0", "0.0804054", "0.2856"),
    (2026, "60000", 1980, "20297.00", "0.00", "1", "0", "0", "0.1378254", "0.4074"),
]


def _summary(year: int, salary: str, born: int | None) -> Worksheet:
    artifacts: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if born is not None:
        artifacts.append(Artifact(BIRTH_YEAR, born))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, year, tuple(artifacts))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    (
        "year",
        "salary",
        "born",
        "line_4",
        "claimed",
        "threshold_gate",
        "amount_gate",
        "term",
        "provincial",
        "marginal",
    ),
    AGE_CASES,
)
def test_the_age_amount_fall_and_its_gates_in_the_marginal_rate(
    year: int,
    salary: str,
    born: int | None,
    line_4: str,
    claimed: str,
    threshold_gate: str,
    amount_gate: str,
    term: str,
    provincial: str,
    marginal: str,
) -> None:
    summary = _summary(year, salary, born)

    assert _value(summary, LINE_4) == D(line_4)
    assert _value(summary, CLAIMED) == D(claimed)
    assert _value(summary, THRESHOLD_GATE) == D(threshold_gate)
    assert _value(summary, AMOUNT_GATE) == D(amount_gate)
    assert _value(summary, AGE_TERM) == D(term)
    assert _value(summary, PROVINCIAL) == D(provincial)
    assert _value(summary, MARGINAL) == D(marginal)


@pytest.mark.parametrize("year", (2025, 2026))
def test_a_salary_of_0_has_no_marginal_rate_for_any_birth_year(year: int) -> None:
    for born in (None, 1955, 1980):
        assert _value(_summary(year, "0", born), MARGINAL) == D("0")

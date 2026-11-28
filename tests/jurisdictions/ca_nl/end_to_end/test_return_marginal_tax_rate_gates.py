"""The gated Newfoundland and Labrador marginal tax rate, 2025, through the real engine.

The salary-only case, 2025. Newfoundland and Labrador's low-income tax reduction absorbs the
provincial tax at low salaries, so the provincial part opens late and is steepest while the
reduction is phased out.

The provincial part is counted only while NL428 line 105 "Line 94 minus line 104 (if negative,
enter "0")" is above zero, and the low-income tax reduction slope (16%, NL428 line 102) only while
NL428 line 101 and line 104 are both above zero. Each boundary below is found cent by cent from the
engine, and each rate is the hand-worked figure of `test_return_marginal_tax_rate_values.py`; each
other salary pins the structure: the gates are 0 or 1 and open with the amounts they read, the
provincial part is its gate times its rate, and the total is the exact sum of the three parts.

- line 105 is 0.00 at a salary of 24,140.18 and 0.01 at 24,140.19 (the reduction absorbs the tax);
- line 101 is 0.00 at 24,134.34 and 0.01 at 24,134.35 (the net income passes the low-income
  threshold of 23,928); line 104 is 0.01 at 30,428.50 and 0.00 at 30,428.51 (the reduction is used
  up); in between the provincial part is 8.7% x 0.99 - 8.7% x 0.0659 + 16% x 0.99 = 0.2387967, and
  after it 0.0803967.

The age amount (NL428 line 17, Worksheet NL428 "Line 58080 - Age amount") of a filer born in 1960 or
earlier falls by 15% (worksheet line 5 "Applicable rate 15%") of the net income over the threshold
(worksheet line 3 "Income threshold") until it is 0, and each dollar of that fall is taxed at the
NL428 credit rate (line 57, 8.7%). The term is counted while worksheet line 4 is above 0 and an age
amount is still claimed: a further dollar of salary adds 15% x (the part left in the net income) x
8.7% to the provincial rate, and the federal rate adds its own term the same way (15% x the part
left x the federal credit rate). Each figure is worked by hand from the printed rates; the
boundaries are found cent by cent from the engine and checked against the worksheet's arithmetic.

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

A filer born in 1980, or with no birth year, claims no age amount: the age gate is 0 and the rate is
the one without the term (the figures of `test_return_marginal_tax_rate_values.py`).

The engine rounds the marginal tax rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the marginal column of PARTS is the exact sum of the
parts, kept in the comments, rounded half-up to four places (e.g. 0.2098945 is 0.2099); the parts
themselves stay exact.
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
YEAR = 2025
RETURN = "ca-nl/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_105 = "ca-nl/newfoundland_and_labrador_tax_return"
TAX_GATE = "ca-nl/newfoundland_and_labrador_rate_gate"
REDUCTION_RATE = "ca-nl/marginal_newfoundland_and_labrador_rate_with_reduction"
INCOME_GATE = "ca-nl/income_over_low_income_threshold_gate"
REDUCTION_GATE = "ca-nl/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-nl/low_income_reduction_phase_out_gate"
AGE_LINE_4 = "ca-nl/marginal_age_income_over_threshold"
AGE_CLAIMED = "ca-nl/marginal_age_amount_claimed"
AGE_THRESHOLD_GATE = "ca-nl/marginal_age_threshold_gate"
AGE_AMOUNT_GATE = "ca-nl/marginal_age_amount_gate"
AGE_TERM = "ca-nl/marginal_newfoundland_and_labrador_age_credit_rate"
FEDERAL = "ca-nl/marginal_federal_rate"
PROVINCIAL = "ca-nl/newfoundland_and_labrador_marginal_rate"
CONTRIBUTION = "ca-nl/marginal_contribution_rate"
MARGINAL = "ca-nl/marginal_tax_rate"

# Salary, then the federal marginal rate, the Newfoundland and Labrador marginal rate, the
# contribution rate and the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 8.7%.
    ("100", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "1", "1"),
    # Contributions only: CPP 4.95% + 1% and EI 1.64%, no basic federal tax yet.
    ("18820.26", "0", "0", "0.0759", "0.0759"),
    # Basic federal tax is first positive: 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945.
    ("18820.27", "0.1339945", "0", "0.0759", "0.2099"),
    ("24140.18", "0.1339945", "0", "0.0759", "0.2099"),
    # NL428 line 105 is first positive: 8.7% x 0.99 - 8.7% x 0.0659 + 16% x 0.99 = 0.2387967.
    ("24140.19", "0.1339945", "0.2387967", "0.0759", "0.4487"),
    # The reduction is used up (NL428 line 104 is 0.00): 8.7% x 0.99 - 8.7% x 0.0659 = 0.0803967.
    ("30428.51", "0.1339945", "0.0803967", "0.0759", "0.2903"),
    # Above the EI maximum of 65,700: CPP 4.95% + 1% only; 14.5% x 0.99 - 14.5% x 0.0495 (the
    # Newfoundland and Labrador rate is the same 14.5%).
    ("70000", "0.1957725", "0.1392435", "0.0595", "0.3945"),
    # Above the CPP ceilings: the net income rate is 1 and no contribution is left.
    ("153824", "0.26", "0.158", "0", "0.4180"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Newfoundland and Labrador manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (federal,) = worksheets[FEDERAL_FORM]
    return federal


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(name)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("salary", "gate", "provincial"),
    [
        ("24140.18", "0", "0"),
        ("24140.19", "1", "0.2387967"),
        ("30428.50", "1", "0.2387967"),
        ("30428.51", "1", "0.0803967"),
    ],
)
def test_2025_the_provincial_part_follows_line_105_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("salary", "income_gate", "reduction_gate"),
    [
        ("24134.34", "0", "1"),
        ("24134.35", "1", "1"),
        ("30428.50", "1", "1"),
        ("30428.51", "1", "0"),
    ],
)
def test_2025_the_phase_out_gates_open_where_lines_101_and_104_turn_positive_or_zero(
    salary: str, income_gate: str, reduction_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, INCOME_GATE) == D(income_gate)
    assert _value(summary, REDUCTION_GATE) == D(reduction_gate)


@pytest.mark.parametrize(("salary", "federal", "provincial", "contribution", "marginal"), PARTS)
def test_each_part_and_the_total_of_the_marginal_tax_rate(
    salary: str, federal: str, provincial: str, contribution: str, marginal: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, FEDERAL) == D(federal)
    assert _value(summary, PROVINCIAL) == D(provincial)
    assert _value(summary, CONTRIBUTION) == D(contribution)
    assert _value(summary, MARGINAL) == D(marginal)


@pytest.mark.parametrize(
    ("salary", "basic_federal_tax", "federal_gate"),
    [
        ("18820.26", "0.00", "0"),
        ("18820.27", "0.01", "1"),
    ],
)
def test_the_federal_gate_opens_where_the_basic_federal_tax_is_first_above_zero(
    salary: str, basic_federal_tax: str, federal_gate: str
) -> None:
    federal = _federal(salary)

    assert _value(federal, BASIC_FEDERAL_TAX) == D(basic_federal_tax)
    assert _value(federal, FEDERAL_GATE) == D(federal_gate)


@pytest.mark.parametrize(
    ("salary", "line_105", "provincial_gate"),
    [
        ("24140.18", "0.00", "0"),
        ("24140.19", "0.01", "1"),
    ],
)
def test_the_provincial_gate_opens_where_line_105_is_first_above_zero(
    salary: str, line_105: str, provincial_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_105) == D(line_105)
    assert _value(summary, TAX_GATE) == D(provincial_gate)


# Salary, year of birth, then NL428 worksheet line 4, the age amount claimed, the age threshold
# gate, the age amount gate, the age term and the provincial marginal rate, worked by hand as the
# docstring says (the marginal tax rate of each is in `test_return_marginal_tax_rate_values.py`).
AGE_CASES = [
    ("0", 1955, "0.00", "7064.00", "0", "1", "0", "0"),
    ("39067.68", 1955, "0.00", "7064.00", "0", "1", "0", "0.0803967"),
    ("39067.69", 1955, "0.01", "7064.00", "1", "1", "0.0129195", "0.0933162"),
    ("40000", 1955, "923.00", "6925.55", "1", "1", "0.0129195", "0.0933162"),
    ("46000", 1955, "6863.00", "6034.55", "1", "1", "0.0129195", "0.1507362"),
    ("60000", 1955, "20723.00", "3955.55", "1", "1", "0.0129195", "0.1507362"),
    ("86879.29", 1955, "47093.29", "0.01", "1", "1", "0.01305", "0.15805"),
    ("86879.30", 1955, "47093.30", "0.00", "1", "0", "0", "0.145"),
    ("90000", 1955, "50214.00", "0.00", "1", "0", "0", "0.158"),
    ("0", 1980, "0.00", "0.00", "0", "0", "0", "0"),
    ("40000", 1980, "923.00", "0.00", "1", "0", "0", "0.0803967"),
    ("46000", 1980, "6863.00", "0.00", "1", "0", "0", "0.1378167"),
    ("60000", 1980, "20723.00", "0.00", "1", "0", "0", "0.1378167"),
    ("86879.29", 1980, "47093.29", "0.00", "1", "0", "0", "0.145"),
    ("40000", None, "923.00", "0.00", "1", "0", "0", "0.0803967"),
    ("60000", None, "20723.00", "0.00", "1", "0", "0", "0.1378167"),
]


@pytest.mark.parametrize(
    ("salary", "born", "line_4", "claimed", "threshold_gate", "amount_gate", "term", "provincial"),
    AGE_CASES,
)
def test_2025_the_age_amount_fall_and_its_gates_in_the_marginal_rate(
    salary: str,
    born: int | None,
    line_4: str,
    claimed: str,
    threshold_gate: str,
    amount_gate: str,
    term: str,
    provincial: str,
) -> None:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if born is not None:
        given.append(Artifact(BIRTH_YEAR, born))
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(NEWFOUNDLAND, 2025, tuple(given))
    )
    (summary,) = worksheets[RETURN]

    assert _value(summary, AGE_LINE_4) == D(line_4)
    assert _value(summary, AGE_CLAIMED) == D(claimed)
    assert _value(summary, AGE_THRESHOLD_GATE) == D(threshold_gate)
    assert _value(summary, AGE_AMOUNT_GATE) == D(amount_gate)
    assert _value(summary, AGE_TERM) == D(term)
    assert _value(summary, PROVINCIAL) == D(provincial)

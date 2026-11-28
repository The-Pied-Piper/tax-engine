"""The gated Prince Edward Island marginal tax rate, 2025, through the real engine.

The salary-only case, 2025. Prince Edward Island's low-income tax reduction (PE428 lines 66 to 88)
absorbs the provincial tax at low salaries, so the provincial part opens late and is steepest while
the reduction is phased out.

The provincial part is counted only while PE428 line 97 "Line 93 minus line 96 (if negative,
enter "0")" is above zero, and the low-income tax reduction slope (5%, PE428 line 85) only while
PE428 line 84 and line 87 are both above zero. Each boundary below is found cent by cent from the
engine, and each rate is the hand-worked figure of `test_return_marginal_tax_rate_values.py`; each
other salary pins the structure: the gates are 0 or 1 and open with the amounts they read, the
provincial part is its gate times its rate, and the total is the exact sum of the three parts.

- line 97 is 0.00 at a salary of 19,614.78 and 0.01 at 19,614.79 (the reduction absorbs the tax);
- line 84 is 0.00 at 22,843.43 and 0.01 at 22,843.44 (the net income passes the base amount of
  22,650); line 87 is 0.01 at 29,914.03 and 0.00 at 29,914.04 (the reduction is used up); between
  line 97 opening and line 84 opening, and again after line 87 is used up, the provincial part is
  9.5% x 0.99 - 9.5% x 0.0659 = 0.0877895; in between it is that plus 5% x 0.99 = 0.1372895.

The engine rounds the marginal tax rate half-up to 0.0001 like the average rate
(`ca/take_home_average_rate_rounding`), so the marginal column of PARTS is the exact sum of the
parts, kept in the comments, rounded half-up to four places (e.g. 0.297684 is 0.2977); the parts
themselves stay exact.
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
PRINCE_EDWARD_ISLAND = JurisdictionCode("CA-PE")
YEAR = 2025
RETURN = "ca-pe/return"
FEDERAL_FORM = "ca/take_home_marginal_rates"

BASIC_FEDERAL_TAX = "ca/marginal_basic_federal_tax"
FEDERAL_GATE = "ca/marginal_federal_gate"
LINE_97 = "ca-pe/prince_edward_island_tax_return"
TAX_GATE = "ca-pe/prince_edward_island_rate_gate"
REDUCTION_RATE = "ca-pe/marginal_prince_edward_island_rate_with_reduction"
INCOME_GATE = "ca-pe/income_over_base_amount_gate"
REDUCTION_GATE = "ca-pe/low_income_tax_reduction_gate"
PHASE_OUT_GATE = "ca-pe/low_income_reduction_phase_out_gate"
FEDERAL = "ca-pe/marginal_federal_rate"
PROVINCIAL = "ca-pe/prince_edward_island_marginal_rate"
CONTRIBUTION = "ca-pe/marginal_contribution_rate"
MARGINAL = "ca-pe/marginal_tax_rate"

# Salary, then the federal marginal rate, the Prince Edward Island marginal rate, the
# contribution rate and the marginal tax rate, worked by hand from the printed rates and the gates.
PARTS = [
    # No tax and no contribution: every part is 0 although the bracket rates are 14.5% and 9.5%.
    ("100", "0", "0", "0", "0"),
    # T2204 line 16 rises 1 for 1 between 2,000 and 2,033: the EI rate is 1.
    ("2001", "0", "0", "1", "1"),
    # Contributions only: CPP 4.95% + 1% and EI 1.64%, no basic federal tax yet.
    ("18820.26", "0", "0", "0.0759", "0.0759"),
    # Basic federal tax is first positive: 14.5% x 0.99 - 14.5% x 0.0659 = 0.1339945.
    ("18820.27", "0.1339945", "0", "0.0759", "0.2099"),
    ("19614.78", "0.1339945", "0", "0.0759", "0.2099"),
    # PE428 line 97 is first positive: 9.5% x 0.99 - 9.5% x 0.0659 = 0.0877895.
    ("19614.79", "0.1339945", "0.0877895", "0.0759", "0.2977"),
    ("22843.43", "0.1339945", "0.0877895", "0.0759", "0.2977"),
    # PE428 line 84 is first positive: the reduction slope 5% x 0.99 is added, 0.1372895.
    ("22843.44", "0.1339945", "0.1372895", "0.0759", "0.3472"),
    ("29914.03", "0.1339945", "0.1372895", "0.0759", "0.3472"),
    # The reduction is used up (PE428 line 87 is 0.00): back to 0.0877895.
    ("29914.04", "0.1339945", "0.0877895", "0.0759", "0.2977"),
    # Above the EI maximum of 65,700: CPP 4.95% + 1% only; 14.5% x 0.99 - 14.5% x 0.0495 federal
    # (20.5% x 0.99 - 14.5% x 0.0495) and 16.6% x 0.99 - 9.5% x 0.0495 for Prince Edward Island.
    ("70000", "0.1957725", "0.1596375", "0.0595", "0.4149"),
    # Above the CPP ceilings: the net income rate is 1 and no contribution is left.
    ("153824", "0.26", "0.19", "0", "0.4500"),
]


def _summary(salary: str) -> Worksheet:
    # No fixture: the bundled Prince Edward Island manifest, as the calculator loads it,
    # salary the only input.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (summary,) = worksheets[RETURN]
    return summary


def _federal(salary: str) -> Worksheet:
    # The federal form's sheet, which holds the federal gate.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
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
        ("19614.78", "0", "0"),
        ("19614.79", "1", "0.0877895"),
        ("22843.43", "1", "0.0877895"),
        ("22843.44", "1", "0.1372895"),
        ("29914.03", "1", "0.1372895"),
        ("29914.04", "1", "0.0877895"),
    ],
)
def test_2025_the_provincial_part_follows_line_97_and_the_reduction_phase_out(
    salary: str, gate: str, provincial: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, TAX_GATE) == D(gate)
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("salary", "income_gate", "reduction_gate"),
    [
        ("22843.43", "0", "1"),
        ("22843.44", "1", "1"),
        ("29914.03", "1", "1"),
        ("29914.04", "1", "0"),
    ],
)
def test_2025_the_phase_out_gates_open_where_lines_84_and_87_turn_positive_or_zero(
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
    ("salary", "line_97", "provincial_gate"),
    [
        ("19614.78", "0.00", "0"),
        ("19614.79", "0.01", "1"),
    ],
)
def test_the_provincial_gate_opens_where_line_97_is_first_above_zero(
    salary: str, line_97: str, provincial_gate: str
) -> None:
    summary = _summary(salary)

    assert _value(summary, LINE_97) == D(line_97)
    assert _value(summary, TAX_GATE) == D(provincial_gate)


@pytest.mark.parametrize(
    ("salary", "net_income", "reduction", "provincial"),
    [
        # Net income exactly at the base amount of PE428 line 83 (22,650): line 84 is 0.00, so a
        # further dollar does not yet take anything off the reduction of 350.
        ("22843.43", "22650.00", "350.00", "0.0877895"),
        # Inside the fade: net income 25,050, the reduction left is 230 (350 - 5% x 2,400) and a
        # further dollar of income takes 5% off it: 0.0877895 + 5% x 0.99 = 0.1372895.
        ("25267.68", "25050.00", "230.00", "0.1372895"),
        # The reduction is used up (line 87 is 0.00) at net income 29,649.90, a dollar short of
        # 29,650 (350 / 5% = 7,000 over the base amount, less the cent rounding of line 86).
        ("29914.03", "29649.89", "0.01", "0.1372895"),
        ("29914.04", "29649.90", "0.00", "0.0877895"),
    ],
)
def test_the_reduction_slope_follows_the_net_income_in_the_fade_from_22650_to_29650(
    salary: str, net_income: str, reduction: str, provincial: str
) -> None:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, YEAR, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (pe428,) = worksheets["ca-pe/pe428"]
    (summary,) = worksheets[RETURN]

    assert _value(pe428, "ca-pe/pe428_adjusted_family_income_line_72") == D(net_income)
    assert _value(pe428, "ca-pe/pe428_low_income_tax_reduction_line_87") == D(reduction)
    assert _value(summary, PROVINCIAL) == D(provincial)


@pytest.mark.parametrize(
    ("salary", "line_4", "threshold_gate", "claimed", "amount_gate"),
    [
        ("36934.34", "0.00", "0", "6510.00", "1"),
        ("36935.35", "1.00", "1", "6509.85", "1"),
        ("81067.71", "43399.00", "1", "0.15", "1"),
        ("81068.75", "43400.00", "1", "0.00", "0"),
    ],
)
def test_2025_the_age_gates_open_where_line_4_and_the_amount_claimed_are_first_above_zero(
    salary: str, line_4: str, threshold_gate: str, claimed: str, amount_gate: str
) -> None:
    # A filer born in 1955 claims the age amount; the two gates read worksheet line 4 (net income
    # over 36,600.00) and the amount claimed.
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            PRINCE_EDWARD_ISLAND,
            YEAR,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), Artifact(BIRTH_YEAR, 1955)),
        )
    )
    (summary,) = worksheets[RETURN]

    assert _value(summary, "ca-pe/marginal_age_income_over_threshold") == D(line_4)
    assert _value(summary, "ca-pe/marginal_age_threshold_gate") == D(threshold_gate)
    assert _value(summary, "ca-pe/marginal_age_amount_claimed") == D(claimed)
    assert _value(summary, "ca-pe/marginal_age_amount_gate") == D(amount_gate)

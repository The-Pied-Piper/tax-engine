"""The 2025 per-slip maximum of CPP pensionable earnings, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 3 line 1: "Total CPP pensionable earnings from box 26
of all of your T4 slips (if box 26 is blank, enter the amount from box 14) (maximum $81,200 per
slip)". The dataset holds that printed figure as an amount; the capped_amount capability caps
the earnings at it, so earnings above it are produced as $81,200.00 rather than refused.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.core.capabilities.capped_amount import CappedAmount

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/cpp_pensionable_earnings_per_slip_maximum"

# Made up for this test and not registered: the salary line 1 reads, and line 1 itself.
SALARY = AmountKind("ex/salary")
LINE_1 = AmountKind("ex/line_1")


def test_2025_per_slip_maximum_is_81200_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("81200"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_per_slip_maximum_cites_the_schedule_8_text() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt",
    )


@pytest.mark.parametrize(
    ("salary", "line_1"),
    [
        # The ticket's $70,000 salary is under the maximum, so it is line 1 unchanged.
        ("70000", "70000.00"),
        # $90,000 is above the maximum, so line 1 is the printed $81,200.
        ("90000", "81200.00"),
        # At the maximum, and a cent either side of it.
        ("81200", "81200.00"),
        ("81200.01", "81200.00"),
        ("81199.99", "81199.99"),
        ("0", "0.00"),
    ],
)
def test_line_1_caps_the_salary_at_the_per_slip_maximum(salary: str, line_1: str) -> None:
    wired = CappedAmount(SOURCE.get(FAMILY, 2025, AMOUNT), SALARY, LINE_1)

    (output,) = wired.compute((Artifact(SALARY, D(salary)),)).outputs

    assert output.value == D(line_1)
    assert output.value.as_tuple().exponent == -2

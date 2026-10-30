"""The 2025 figures of the multigenerational home renovation credit, checked against CRA's forms.

Schedule 12 (form 5000-S12), "Step 1", line 4 "Maximum amount per qualifying renovation
50,000.00": the most each qualifying renovation can claim, a yearly `amount` dataset that the
caps of lines 3 and 6 read. "How much you can claim": "The MHRTC is 14.5% of whichever amount is
less: $50,000, your total qualifying expenditures". Line 9 "Applicable rate 14.5%" is the yearly
`rate` dataset, and line 10 "Line 8 multiplied by the percentage from line 9 Enter this amount on
line 45355 of your return." rounds half-up to the cent, the owner's decision, as the form states
no rounding rule. The worked figures are those of Return CY: 50,000 gives 7,250.00, 100,000 gives
14,500.00, 25,000 gives 3,625.00, 75,000 gives 10,875.00 and nothing gives 0.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
MAXIMUM = "ca/home_renovation_maximum"
RATE_DATASET = "ca/home_renovation_rate"

# Made up for this test and not registered: line 8 (the total of line 7) and the credit (line 10).
LINE_8 = ArtifactKind("ex/home_renovation_line_8", Decimal)
CREDIT = ArtifactKind("ex/multigenerational_home_renovation_credit", Decimal)


def test_2025_maximum_per_qualifying_renovation_is_50000() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("50000"))


def test_2025_applicable_rate_is_14_5_percent_rounded_half_up_to_the_cent() -> None:
    data = SOURCE.get(RATE_DATASET, 2025, RATE)

    assert data.values == Rate(D("0.145"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


@pytest.mark.parametrize(
    ("line_8", "credit"),
    [
        ("50000", "7250.00"),
        ("100000", "14500.00"),
        ("25000", "3625.00"),
        ("75000", "10875.00"),
        ("0", "0"),
    ],
    ids=[
        "one_at_the_maximum",
        "two_at_the_maximum",
        "one_partly_reimbursed",
        "two_renovations",
        "none",
    ],
)
def test_the_credit_is_the_applicable_rate_times_line_8_to_the_cent(
    line_8: str, credit: str
) -> None:
    capability = ApplyRate(SOURCE.get(RATE_DATASET, 2025, RATE), LINE_8, CREDIT)

    (output,) = capability.compute((Artifact(LINE_8, D(line_8)),)).outputs

    assert output == Artifact(CREDIT, D(credit))

"""The 2025 restricted farm loss datasets of the T2042 net farm loss, checked against the guide.

Guide T4002 (docs/cra-forms-2025/t4002-25e.pdf, "Restricted farm losses (partly deductible)", pages
95 and 96; confirmed from the PDF, no .txt published): "For tax years that end after March 20,
2013, the annual maximum deduction used in the calculation for restricted farm losses is $17,500.
When your net farm loss is $32,500 or more, you can deduct $17,500 from your other income. The
rest of your net farm loss is your restricted farm loss. When your net farm loss is less than
$32,500, the amount you can deduct from your other income is the lesser of: A) your net farm loss
for the year B) $2,500 plus 50% × (your net farm loss minus $2,500) The amount remaining is your
restricted farm loss." The $2,500, the $32,500, the $17,500 and the 50% are the figures the guide
prints, each a dataset; the 50% is the caller's way of a percentage, as the guide prints it (50 for
50%). The guide states no rounding rule for the 50% of an amount in dollars and cents, so it rounds
half-up to the cent, the owner's decision, the repo convention. The datasets are the restricted
farm loss's own, `farm_restricted_loss_*`, none of the T2042's other `farm_*` ones.

Each dataset is tested with the capability that reads it, on made-up kinds; the lines together,
from the net farm loss to line 14100, are in `returns/2025_return_iq.yaml` and
`end_to_end/test_return_iq.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_calculator.jurisdictions.ca.capabilities.apply_percentage import ApplyPercentage

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASE_AMOUNT = "ca/farm_restricted_loss_base_amount"
FULL_THRESHOLD = "ca/farm_restricted_loss_full_threshold"
ANNUAL_MAXIMUM = "ca/farm_restricted_loss_annual_maximum"
PERCENTAGE = "ca/farm_restricted_loss_percentage"
ROUNDING = "ca/farm_restricted_loss_rounding"
T4002_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4002/t4002-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the figure a credit dataset gives, the amount the
# percentage is taken of and the result.
FIGURE = ArtifactKind("ex/printed_figure", Decimal)
EXCESS = ArtifactKind("ex/excess", Decimal)
HALF = ArtifactKind("ex/half", Decimal)
FIGURES = [
    (BASE_AMOUNT, "2500"),
    (FULL_THRESHOLD, "32500"),
    (ANNUAL_MAXIMUM, "17500"),
    (PERCENTAGE, "50"),
]


@pytest.mark.parametrize(("family", "figure"), FIGURES)
def test_2025_figure_is_the_one_the_guide_prints(family: str, figure: str) -> None:
    # "$2,500 plus 50% × (your net farm loss minus $2,500)", "When your net farm loss is $32,500
    # or more" and "the annual maximum deduction ... is $17,500": each as printed, the percentage
    # as 50 for 50%.
    data = SOURCE.get(family, 2025, CREDIT)

    assert data.values == Credit(amount=D(figure))
    assert data.rounding == CENT


@pytest.mark.parametrize(("family", "_figure"), FIGURES)
def test_2025_figures_cite_the_guide_they_are_printed_in(family: str, _figure: str) -> None:
    assert SOURCE.get(family, 2025, CREDIT).sources == (T4002_PDF,)


def test_2025_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY)

    assert data.rounding == CENT
    assert data.sources == (T4002_PDF,)


@pytest.mark.parametrize(("family", "figure"), FIGURES)
def test_the_credit_amount_capability_gives_the_printed_figure(family: str, figure: str) -> None:
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), FIGURE)

    (output,) = capability.compute(()).outputs

    assert output.kind == FIGURE
    assert output.value == D(figure)


@pytest.mark.parametrize(
    ("excess", "result"),
    [
        # Sharon: 50% x (9,200 - 2,500) = 50% x 6,700 = 3,350.00.
        ("6700", "3350.00"),
        # 50% x 29,999 = 14,999.50, the 32,499 loss's.
        ("29999", "14999.50"),
        # 50% x 1 = 0.50.
        ("1", "0.50"),
        # 50% x 0.01 = 0.005, rounded half-up to the cent, 0.01.
        ("0.01", "0.01"),
        # Below the base amount the excess is negative: 50% x -1,500 = -750.00.
        ("-1500", "-750.00"),
        ("0", "0.00"),
    ],
)
def test_half_of_the_excess_is_the_percentage_as_printed_rounded_once_to_the_cent(
    excess: str, result: str
) -> None:
    capability = ApplyPercentage(SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY), EXCESS, FIGURE, HALF)

    (output,) = capability.compute((Artifact(EXCESS, D(excess)), Artifact(FIGURE, D("50")))).outputs

    assert output.value == D(result)
    assert output.value.as_tuple().exponent == -2


def test_the_restricted_farm_loss_datasets_are_none_of_the_other_farm_ones() -> None:
    others = {
        "ca/farm_immediate_expensing_cap",
        "ca/farm_epop_percentage_maximum",
        "ca/farm_immediate_expensing_rounding",
    }
    assert {BASE_AMOUNT, FULL_THRESHOLD, ANNUAL_MAXIMUM, PERCENTAGE, ROUNDING}.isdisjoint(others)
    assert SOURCE.get(BASE_AMOUNT, 2025, CREDIT).sources != (
        SOURCE.get("ca/farm_immediate_expensing_cap", 2025, CREDIT).sources
    )

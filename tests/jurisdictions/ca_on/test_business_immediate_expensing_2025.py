"""The 2025 immediate expensing limit datasets of Form T2125, checked against CRA's form.

2025 Form T2125 (Statement of Business or Professional Activities; confirmed from the PDF,
docs/cra-forms-2025/t2125-25e.pdf; no .txt published), Area A endnote 5: "The immediate expensing
applies to DIEPs included in column 8. The total immediate expensing amount for the tax year (total
of column 9) is limited to the lesser of: the immediate expensing limit, which is equal to one of
the following, whichever is applicable: $1.5 million, if you are not associated with any other
eligible person or partnership (EPOP) in the tax year; amount iii of Area G, if you are associated
with one or more EPOPs in the tax year; zero, if you are associated with one or more EPOPs and an
agreement that assigns a percentage to one or more of the associated EPOPs was not filed with the
minister in a prescribed form; any amount allocated by the minister under subsection 1104(3.4) of
the Regulations". Area G: "The total of all percentages assigned under the agreement should not be
more than 100%. If the total is more than 100%, then the associated group has an immediate
expensing limit of zero."; "Immediate expensing limit allocated to your business: Multiply $1.5
million by the percentage assigned to your business in column 3**" (amount iii); "** If the total of
column 3 is more than 100%, enter "0."". The $1.5 million and the 100% are the figures the form
prints, each a dataset; amount iii is a dollars-and-cents box and the form states no rounding rule,
so the product rounds half-up to the cent, the owner's decision, the repo convention. The
percentage is the caller's, as the form prints it (40 for 40%). The datasets are the T2125's own,
`business_*`, and are not the T776's `rental_*` ones.

Each dataset is tested with the capability that reads it, on made-up kinds; the lines together,
from the Area G answers to line i, are in `returns/2025_return_bt.yaml` and
`end_to_end/test_return_bt.py`.
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
CAP = "ca/business_immediate_expensing_cap"
PERCENTAGE_MAXIMUM = "ca/business_epop_percentage_maximum"
ROUNDING = "ca/business_immediate_expensing_rounding"
T2125_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2125/t2125-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the figure a credit dataset gives, the percentage
# assigned to your business and amount iii.
FIGURE = ArtifactKind("ex/printed_figure", Decimal)
LIMIT = ArtifactKind("ex/limit", Decimal)
PERCENTAGE = ArtifactKind("ex/percentage_assigned", Decimal)
ALLOCATED = ArtifactKind("ex/allocated", Decimal)


def test_2025_immediate_expensing_cap_is_1_5_million() -> None:
    data = SOURCE.get(CAP, 2025, CREDIT)

    # Endnote 5 "$1.5 million, if you are not associated with any other eligible person or
    # partnership (EPOP) in the tax year" and Area G "Multiply $1.5 million by the percentage
    # assigned to your business in column 3".
    assert data.values == Credit(amount=D("1500000"))
    assert data.rounding == CENT


def test_2025_percentage_maximum_is_100() -> None:
    data = SOURCE.get(PERCENTAGE_MAXIMUM, 2025, CREDIT)

    # Area G "should not be more than 100%" and "** If the total of column 3 is more than 100%,
    # enter "0."": the percentage as the form prints it, 100 for 100%.
    assert data.values == Credit(amount=D("100"))
    assert data.rounding == CENT


def test_2025_immediate_expensing_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY)

    assert data.rounding == CENT


@pytest.mark.parametrize("family", [CAP, PERCENTAGE_MAXIMUM])
def test_2025_figures_cite_the_form_they_are_printed_on(family: str) -> None:
    assert SOURCE.get(family, 2025, CREDIT).sources == (T2125_PDF,)


def test_2025_immediate_expensing_rounding_cites_the_form_it_is_printed_on() -> None:
    assert SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY).sources == (T2125_PDF,)


@pytest.mark.parametrize("family", [CAP, PERCENTAGE_MAXIMUM])
def test_the_credit_amount_capability_gives_the_printed_figure(family: str) -> None:
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), FIGURE)

    (output,) = capability.compute(()).outputs

    assert output.kind == FIGURE
    assert output.value == SOURCE.get(family, 2025, CREDIT).values.amount


@pytest.mark.parametrize(
    ("percentage", "result"),
    [
        # Area G amount iii: $1.5 million times 40% = 600,000.00.
        ("40", "600000.00"),
        # 100% of the limit, the whole $1.5 million.
        ("100", "1500000.00"),
        # No percentage assigned: 0.00.
        ("0", "0.00"),
        # 1500000 x 0.0000005 / 100 = 0.0075, rounded half-up to the cent, 0.01.
        ("0.0000005", "0.01"),
        # 1500000 x 0.0000003 / 100 = 0.0045, rounded half-up to the cent, 0.00.
        ("0.0000003", "0.00"),
    ],
)
def test_amount_iii_is_the_cap_times_the_percentage_as_printed_rounded_once_to_the_cent(
    percentage: str, result: str
) -> None:
    capability = ApplyPercentage(
        SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY), LIMIT, PERCENTAGE, ALLOCATED
    )

    (output,) = capability.compute(
        (Artifact(LIMIT, D("1500000")), Artifact(PERCENTAGE, D(percentage)))
    ).outputs

    assert output.value == D(result)
    assert output.value.as_tuple().exponent == -2


def test_the_business_datasets_are_not_the_rental_ones() -> None:
    # Each form has its own printed figure: the T2125 reads the `business_*` datasets, the T776
    # the `rental_*` ones, as the vehicle charts' datasets are the T2125's alone.
    assert {CAP, PERCENTAGE_MAXIMUM, ROUNDING}.isdisjoint(
        {
            "ca/rental_immediate_expensing_cap",
            "ca/rental_epop_percentage_maximum",
            "ca/rental_immediate_expensing_rounding",
        }
    )
    assert (
        SOURCE.get(CAP, 2025, CREDIT).sources
        != SOURCE.get("ca/rental_immediate_expensing_cap", 2025, CREDIT).sources
    )

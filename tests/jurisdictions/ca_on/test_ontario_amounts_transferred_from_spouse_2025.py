"""The 2025 Schedule ON(S2) dataset (Ontario amounts from a spouse), checked against CRA.

Form 5006-S2 (Schedule ON(S2), 2025), "Spouse's or common-law partner's taxable income": line 5
"Enter the amount from line 26000 of their return on line 5 if it is $52,886 or less. If it is more
than $52,886, enter the result of the following calculation: Amount from line 8 of their Form
ON428" "divided by 5.05% =".

One dataset, the `threshold_rate` kind: $52,886 and 5.05%. They are Schedule ON(S11) line 2's
figures again, but a dataset of its own because it is another form's line, rounded by its own rule:
line 5 is a dollars-and-cents box and states no rounding rule, so it rounds half-up to the cent, as
every dollars-and-cents line does.

The maximums of the spouse's amounts the Schedule takes from their Form ON428 (pension income
$1,762, disability $16,305; the age amount and the basic personal amount reuse their datasets)
and the refusal of an amount above one: the tests follow the dataset ones.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.capabilities.amount_or_divided_by_rate import (
    AmountOrDividedByRate,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import compute

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
INCOME_LIMIT = "ca-on/spouse_transfer_income_limit"
S2_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-s2/5006-s2-25e.txt"

# Made up for these tests and not registered.
INCOME = ArtifactKind("ex/income", Decimal)
TAX = ArtifactKind("ex/tax", Decimal)
OUTPUT = ArtifactKind("ex/out", Decimal)


def test_2025_line_5_threshold_is_52886_and_rate_5_05_percent_to_the_cent() -> None:
    data = SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE)

    assert data.values == ThresholdRate(Rate(D("0.0505")), D("52886"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_5_cites_only_schedule_on_s2() -> None:
    data = SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE)

    assert data.sources == (S2_TEXT,)


@pytest.mark.parametrize(
    ("income", "tax", "line_5"),
    [
        # Return AT's example: their taxable income 20,000 is at or below $52,886.
        ("20000", "1010.00", "20000"),
        # At the threshold, the amount passes through ("or less").
        ("52886", "2670.74", "52886"),
        # A cent over, their tax is divided by 5.05%: 2670.74 x 2000 / 101 = 52885.9406, half-up
        # to 52885.94.
        ("52886.01", "2670.74", "52885.94"),
        # 3269.97 x 2000 / 101 = 64751.8812, half-up to 64751.88; their taxable income is unused.
        ("59435", "3269.97", "64751.88"),
    ],
)
def test_line_5_is_their_taxable_income_or_their_ontario_tax_divided_by_5_05_percent(
    income: str, tax: str, line_5: str
) -> None:
    capability = AmountOrDividedByRate(
        SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE), INCOME, TAX, OUTPUT
    )

    result = capability.compute((Artifact(INCOME, D(income)), Artifact(TAX, D(tax))))

    assert result.outputs == (Artifact(OUTPUT, D(line_5)),)


CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
D_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"
PENSION_MAXIMUM = "ca-on/spouse_return_ontario_pension_income_amount_maximum"
DISABILITY_MAXIMUM = "ca-on/spouse_return_ontario_disability_amount_maximum"

# The form lines each dataset header quotes, lowercased as the header is compared.
HEADER_QUOTES = {
    PENSION_MAXIMUM: (
        "line 2 and line 59050",
        "enter the amount from line 58360 of their form on428",
        "(maximum $1,762)",
    ),
    DISABILITY_MAXIMUM: (
        "line 7: line 1 plus line 6",
        "enter this amount on line 58440 of your form on428",
        "(maximum $16,305)",
    ),
}


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    name = family.removeprefix("ca-on/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_spouse_pension_income_amount_maximum_is_1762() -> None:
    data = SOURCE.get(PENSION_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("1762.00"))
    # Schedule ON(S2) line 2, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_spouse_disability_amount_maximum_is_16305() -> None:
    data = SOURCE.get(DISABILITY_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("16305.00"))
    # Worksheet ON428 line 7, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_spouse_maximums_cite_the_form_text_they_are_printed_on() -> None:
    assert S2_TEXT in SOURCE.get(PENSION_MAXIMUM, 2025, CREDIT).sources
    assert D_TEXT in SOURCE.get(DISABILITY_MAXIMUM, 2025, CREDIT).sources


@pytest.mark.parametrize(("family", "quotes"), HEADER_QUOTES.items())
def test_the_dataset_header_quotes_the_form_line_it_is_printed_on(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family).lower()

    for quoted in quotes:
        assert quoted in header, quoted


@pytest.mark.parametrize("family", HEADER_QUOTES)
def test_the_dataset_header_states_the_half_up_cent_rule(family: str) -> None:
    assert "half-up to the cent" in dataset_header(family)


@pytest.mark.parametrize(
    ("family", "amount"),
    [(PENSION_MAXIMUM, "1762.00"), (DISABILITY_MAXIMUM, "16305.00")],
)
def test_the_credit_amount_capability_gives_each_spouse_maximum_as_an_artifact(
    family: str, amount: str
) -> None:
    figure = ArtifactKind("ex/spouse_maximum_artifact", Decimal)
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), figure)

    (output,) = capability.compute(()).outputs

    assert output.kind == figure
    assert output.value == D(amount)


# The return of the example: every input the return needs, the rest at their defaults.
EXAMPLE: dict[str, Any] = {
    "employment_income": "60000",
    "share_dispositions": (),
    "unused_rrsp_contributions": "0",
    "rrsp_contributions": "0",
    "rrsp_deduction_limit": "0",
    "rrsp_amount_deducted": "0",
    "union_dues": "0",
    "spouse_not_separated_90_days": 1,
    "spouse_return_taxable_income": "0",
}

# (the input, an amount above its maximum, the bound and its maximum as the error prints it).
REFUSED = [
    (
        "spouse_return_ontario_age_amount",
        "20000",
        "ca-on/age_maximum",
        "6223.00",
    ),
    (
        "spouse_return_ontario_pension_income_amount",
        "5000",
        "ca-on/spouse_return_ontario_pension_income_amount_maximum",
        "1762.00",
    ),
    (
        "spouse_return_ontario_disability_amount",
        "50000",
        "ca-on/spouse_return_ontario_disability_amount_maximum",
        "16305.00",
    ),
    (
        "spouse_return_ontario_basic_personal_amount",
        "12748",
        "ca-on/basic_personal_amount",
        "12747.00",
    ),
]

# (the input, its amount at the maximum, the checked artifact's name in the catalog, the value it
# checks to). The names are looked up when the test runs, so a missing name fails that test alone.
ACCEPTED = [
    (
        "spouse_return_ontario_age_amount",
        "6223",
        "SPOUSE_RETURN_ONTARIO_AGE_AMOUNT_CHECKED",
        "6223.00",
    ),
    (
        "spouse_return_ontario_pension_income_amount",
        "1762",
        "SPOUSE_RETURN_ONTARIO_PENSION_INCOME_AMOUNT_CHECKED",
        "1762.00",
    ),
    (
        "spouse_return_ontario_disability_amount",
        "16305",
        "SPOUSE_RETURN_ONTARIO_DISABILITY_AMOUNT_CHECKED",
        "16305.00",
    ),
    (
        "spouse_return_ontario_basic_personal_amount",
        "12747",
        "SPOUSE_RETURN_ONTARIO_BASIC_PERSONAL_AMOUNT_CHECKED",
        "12747.00",
    ),
]


@pytest.mark.parametrize(("field", "value", "bound", "maximum"), REFUSED)
def test_an_amount_above_its_maximum_is_an_input_error_naming_the_maximum(
    field: str, value: str, bound: str, maximum: str
) -> None:
    with pytest.raises(InputAboveBoundError) as raised:
        compute(**{**EXAMPLE, field: value})

    assert str(raised.value) == (
        f"ca-on/return, instance 1: ca-on/{field} {value} is above {bound} {maximum}"
    )


@pytest.mark.parametrize(("field", "value", "checked_name", "expected"), ACCEPTED)
def test_an_amount_at_its_maximum_is_accepted_and_checks_to_the_maximum(
    field: str, value: str, checked_name: str, expected: str
) -> None:
    worksheet: Worksheet = compute(**{**EXAMPLE, field: value})

    assert worksheet.get(getattr(ontario, checked_name)).value == D(expected)

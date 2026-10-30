"""The 2025 Schedule 2 dataset (federal amounts transferred from a spouse), checked against CRA.

Form 5000-S2 (T1-2025), "Spouse's or common-law partner's taxable income": line 7 "Enter the
amount from line 26000 of their return on line 7 if it is $57,375 or less. If it is more than
$57,375, enter the result of the following calculation: amount from line 76 of their return
divided by 14.5% =".

One dataset, the `threshold_rate` kind: $57,375 and 14.5%. It is Schedule 11 line 11's figures
again, but a dataset of its own because it is another form's line, rounded by its own rule:
Schedule 2 line 7 is a dollars-and-cents box and states no rounding rule, so it rounds half-up to
the cent, the owner's decision.

Two more datasets, the `credit` kind, are the maxima of Schedule 2 line 1 and line 3: the T1
lines they copy print them, "Age amount (if you were born in 1960 or earlier) (use Federal
Worksheet) (maximum $9,028)" (T1 line 78 and line 30100) and "Pension income amount (use Federal
Worksheet) (maximum $2,000)" (T1 line 97 and line 31400). Each is a claimed amount, taken whole
by `core/credit_amount`, and rounds half-up to the cent as the T1 states no rounding rule.
The third is the maximum of Schedule 2 line 8, the basic personal amount, printed on T1 line
30000 as "(maximum $16,129)". The fourth is the maximum of Schedule 2 line 5, the tuition amount
designated by a spouse, printed in Note 2 of Schedule 2 as "$5,000 minus the current year amounts
they use", so $5,000 as printed, claimed whole. The fifth is the maximum of Schedule 2 line 4,
the disability amount of a spouse, printed on Federal Worksheet 5000-D1 line 7 as "Enter this
amount on line 31600 of your return. (maximum $16,052)", claimed whole.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.capabilities.amount_or_divided_by_rate import (
    AmountOrDividedByRate,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
INCOME_LIMIT = "ca/spouse_transfer_income_limit"
AGE_MAXIMUM = "ca/spouse_return_age_amount_maximum"
PENSION_MAXIMUM = "ca/spouse_return_pension_income_amount_maximum"
BASIC_MAXIMUM = "ca/spouse_return_basic_personal_amount_maximum"
DESIGNATED_MAXIMUM = "ca/spouse_designated_tuition_maximum"
DISABILITY_MAXIMUM = "ca/spouse_return_disability_amount_maximum"
SCHEDULE_2_SOURCE = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s2/5000-s2-25e.txt"
)
T1_SOURCE = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-r/5006-r-25e.txt"
D1_SOURCE = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for these tests and not registered.
INCOME = ArtifactKind("ex/income", Decimal)
TAX = ArtifactKind("ex/tax", Decimal)
OUTPUT = ArtifactKind("ex/out", Decimal)
CLAIMED = ArtifactKind("ex/spouse_maximum_claimed", Decimal)


def test_2025_line_7_threshold_is_57375_and_rate_14_5_percent_to_the_cent() -> None:
    data = SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE)

    assert data.values == ThresholdRate(Rate(D("0.145")), D("57375"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_line_7_cites_schedule_2() -> None:
    data = SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE)

    assert (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s2/5000-s2-25e.txt"
        in data.sources
    )


@pytest.mark.parametrize(
    ("income", "tax", "line_7"),
    [
        # Schedule 2 worked example: their taxable income 20,000 is at or below $57,375.
        ("20000", "2900", "20000"),
        ("57375", "8319.38", "57375"),
        # Over it: their line 76 divided by 14.5%, half-up to the cent: 11000 / 0.145 =
        # 75862.0689..., 75862.07.
        ("70000", "11000", "75862.07"),
    ],
)
def test_line_7_is_their_taxable_income_or_their_tax_divided_by_14_5_percent(
    income: str, tax: str, line_7: str
) -> None:
    capability = AmountOrDividedByRate(
        SOURCE.get(INCOME_LIMIT, 2025, THRESHOLD_RATE), INCOME, TAX, OUTPUT
    )

    result = capability.compute((Artifact(INCOME, D(income)), Artifact(TAX, D(tax))))

    assert result.outputs == (Artifact(OUTPUT, D(line_7)),)


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, whitespace squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (
        (root / "parameters" / family.removeprefix("ca/") / "2025.yaml").read_text().splitlines()
    )
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return " ".join(" ".join(lines[:first_key]).split())


# --- the maxima of Schedule 2 line 1 and line 3: a claimed amount, printed on the T1 -------------


def test_2025_spouse_age_maximum_is_9028() -> None:
    data = SOURCE.get(AGE_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("9028.00"))
    assert data.rounding == CENT


def test_2025_spouse_pension_maximum_is_2000() -> None:
    data = SOURCE.get(PENSION_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("2000.00"))
    assert data.rounding == CENT


def test_2025_spouse_basic_personal_maximum_is_16129() -> None:
    data = SOURCE.get(BASIC_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("16129.00"))
    assert data.rounding == CENT


def test_2025_spouse_designated_tuition_maximum_is_5000() -> None:
    data = SOURCE.get(DESIGNATED_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("5000.00"))
    assert data.rounding == CENT


def test_2025_spouse_designated_tuition_maximum_cites_schedule_2() -> None:
    assert SOURCE.get(DESIGNATED_MAXIMUM, 2025, CREDIT).sources == (SCHEDULE_2_SOURCE,)


def test_2025_spouse_disability_maximum_is_16052() -> None:
    data = SOURCE.get(DISABILITY_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("16052.00"))
    assert data.rounding == CENT


def test_2025_spouse_disability_maximum_cites_the_federal_worksheet() -> None:
    assert SOURCE.get(DISABILITY_MAXIMUM, 2025, CREDIT).sources == (D1_SOURCE,)


def test_2025_spouse_maxima_cite_the_t1_form_they_are_printed_on() -> None:
    assert SOURCE.get(AGE_MAXIMUM, 2025, CREDIT).sources == (T1_SOURCE,)
    assert SOURCE.get(PENSION_MAXIMUM, 2025, CREDIT).sources == (T1_SOURCE,)
    assert SOURCE.get(BASIC_MAXIMUM, 2025, CREDIT).sources == (T1_SOURCE,)


def test_2025_spouse_maxima_quote_the_t1_lines_as_printed() -> None:
    assert "(maximum $9,028)" in dataset_header(AGE_MAXIMUM)
    assert "(maximum $2,000)" in dataset_header(PENSION_MAXIMUM)
    assert "(maximum $16,129)" in dataset_header(BASIC_MAXIMUM)
    # Schedule 2 Note 2, the maximum tuition amount a spouse can transfer.
    assert "is $5,000 minus the current year amounts they use" in dataset_header(DESIGNATED_MAXIMUM)
    # Federal Worksheet 5000-D1 line 7, the maximum of Schedule 2 line 4.
    assert "(maximum $16,052)" in dataset_header(DISABILITY_MAXIMUM)


@pytest.mark.parametrize(
    ("family", "amount"),
    [
        (AGE_MAXIMUM, "9028.00"),
        (PENSION_MAXIMUM, "2000.00"),
        (BASIC_MAXIMUM, "16129.00"),
        (DESIGNATED_MAXIMUM, "5000.00"),
        (DISABILITY_MAXIMUM, "16052.00"),
    ],
)
def test_a_spouse_maximum_is_claimed_whole_by_the_credit_amount_capability(
    family: str, amount: str
) -> None:
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), CLAIMED)

    (output,) = capability.compute(()).outputs

    assert output.kind == CLAIMED
    assert output.value == D(amount)

"""The 2025 additional tax on RESP accumulated income payments, checked against CRA's Form T1172.

2025 Form T1172, Additional Tax on Accumulated Income Payments from RESPs, Part A: "Maximum
lifetime RRSP contribution limit that can be used to reduce or eliminate the amount of AIPs
subject to the additional tax $ 50,000.00 4" (a printed amount taken whole, the `credit` kind read
by `core/credit_amount`); "Rate of the additional tax on AIPs × 20% 9" and Part B "Rate of the
additional tax on AIPs × 20% 12", the same printed figure twice but on two lines of two parts, so
one dataset each (the `rate` kind). Each is rounded half-up to the cent, as every dollars-and-cents
box on the forms is. The form is a PDF with no published .txt, so the datasets cite the PDF.

The datasets are tested with the capabilities that read them, on made-up kinds; Part A and Part B
together, from the AIPs of lines 1 and 11 to line 41800, are in the `end_to_end` tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
LIFETIME_LIMIT = "ca/resp_aips_lifetime_limit"
PART_A_RATE = "ca/resp_aips_part_a_rate"
PART_B_RATE = "ca/resp_aips_part_b_rate"
T1172_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1172/t1172-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the amount a credit dataset gives, the AIPs the tax is
# on, the tax of each part, the count that says Part A applies (0 or 1) and the tax chosen.
CLAIMED = ArtifactKind("ex/claimed_amount", Decimal)
AIPS = ArtifactKind("ex/aips", Decimal)
PART_A_TAX = ArtifactKind("ex/part_a_tax", Decimal)
PART_B_TAX = ArtifactKind("ex/part_b_tax", Decimal)
PART_A_APPLIES = ArtifactKind("ex/part_a_applies", int)
TAX = ArtifactKind("ex/tax", Decimal)


def test_2025_lifetime_limit_is_50000() -> None:
    data = SOURCE.get(LIFETIME_LIMIT, 2025, CREDIT)

    # Line 4 "Maximum lifetime RRSP contribution limit ... $ 50,000.00".
    assert data.values == Credit(amount=D("50000.00"))
    assert data.rounding == CENT


def test_2025_part_a_rate_is_20_percent() -> None:
    data = SOURCE.get(PART_A_RATE, 2025, RATE)

    # Line 9 "Rate of the additional tax on AIPs × 20%".
    assert data.values == Rate(D("0.20"))
    assert data.rounding == CENT


def test_2025_part_b_rate_is_20_percent() -> None:
    data = SOURCE.get(PART_B_RATE, 2025, RATE)

    # Line 12 "Rate of the additional tax on AIPs × 20%".
    assert data.values == Rate(D("0.20"))
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_t1172_pdf() -> None:
    assert SOURCE.get(LIFETIME_LIMIT, 2025, CREDIT).sources == (T1172_PDF,)
    assert SOURCE.get(PART_A_RATE, 2025, RATE).sources == (T1172_PDF,)
    assert SOURCE.get(PART_B_RATE, 2025, RATE).sources == (T1172_PDF,)


def test_the_lifetime_limit_is_claimed_whole() -> None:
    capability = CreditAmount(SOURCE.get(LIFETIME_LIMIT, 2025, CREDIT), CLAIMED)

    result = capability.compute(())

    assert result.outputs == (Artifact(CLAIMED, D("50000.00")),)


@pytest.mark.parametrize(
    ("aips", "tax"),
    [
        # Part A line 10: line 8 x 20%.
        ("10000", "2000.00"),
        ("0", "0.00"),
        # 0.02 x 20% = 0.004, rounded half-up to 0.00; 0.03 x 20% = 0.006, up to 0.01.
        ("0.02", "0.00"),
        ("0.03", "0.01"),
    ],
)
def test_part_a_line_10_is_20_percent_of_line_8(aips: str, tax: str) -> None:
    capability = ApplyRate(SOURCE.get(PART_A_RATE, 2025, RATE), AIPS, PART_A_TAX)

    result = capability.compute((Artifact(AIPS, D(aips)),))

    assert result.outputs == (Artifact(PART_A_TAX, D(tax)),)


@pytest.mark.parametrize(
    ("aips", "tax"),
    [
        # Part B line 13: line 11 x 20%, the acceptance criteria's 10,000 of AIPs.
        ("10000", "2000.00"),
        ("0", "0.00"),
        ("0.02", "0.00"),
        ("0.03", "0.01"),
    ],
)
def test_part_b_line_13_is_20_percent_of_line_11(aips: str, tax: str) -> None:
    capability = ApplyRate(SOURCE.get(PART_B_RATE, 2025, RATE), AIPS, PART_B_TAX)

    result = capability.compute((Artifact(AIPS, D(aips)),))

    assert result.outputs == (Artifact(PART_B_TAX, D(tax)),)


@pytest.mark.parametrize(
    ("part_a_applies", "tax"),
    [
        # Part B is "Fill out this part only if Part A does not apply to you": a count of 0.
        (0, "2000.00"),
        (1, "1000.00"),
    ],
)
def test_the_count_chooses_part_a_when_it_applies_and_part_b_when_it_does_not(
    part_a_applies: int, tax: str
) -> None:
    capability = ChooseByCount(PART_A_APPLIES, PART_B_TAX, PART_A_TAX, TAX)

    result = capability.compute(
        (
            Artifact(PART_A_APPLIES, part_a_applies),
            Artifact(PART_B_TAX, D("2000.00")),
            Artifact(PART_A_TAX, D("1000.00")),
        )
    )

    assert result.outputs == (Artifact(TAX, D(tax)),)

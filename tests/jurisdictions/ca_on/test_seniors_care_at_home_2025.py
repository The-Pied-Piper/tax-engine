"""The 2025 Ontario seniors care at home tax credit figures, checked against CRA's ON479.

2025 Form ON479 (form 5006-TC), "Ontario seniors care at home tax credit": "Line 3: Medical
expenses from line 58769 of your Form ON428"; "Line 4: Allowable percentage 25%"; "Line 5: Line 3
multiplied by the percentage from line 4 (maximum $1,500) ="; "Line 6: Your net income from line
23600 of your return"; "Line 7: Your spouse's or common-law partner's net income from line 23600 of
their return (if applicable)"; "Line 8: Line 6 plus line 7 Family net income ="; "Line 9: Base
amount 35,000.00"; "Line 10: Line 8 minus line 9 (if negative, enter "0") ="; "Line 11: Applicable
rate 5%"; "Line 12: Line 10 multiplied by the percentage from line 11 ="; "Line 13 and line 63095:
Line 5 minus line 12 (if negative, enter "0") =". The form prints the maximum after the percentage
of line 5, so it caps the result. Each percentage is a rate (the `rate` kind), the maximum a plain
cap (the `amount` kind) and the base amount a printed constant of the form (the `credit` kind, as
the co-operative education credit's are). Every figure sits in a dollars-and-cents box, so each
dataset carries the half-up cent rule.

The form's first printed rule says that a family net income of $35,000 or less enters line 5 on line
13, and its second that more than $65,000 enters "0": both follow from lines 9 to 13 (line 10 is 0
up to $35,000; at $65,000 line 12 is 5% of $30,000, $1,500.00, the most line 5 can be), so the
tests pin the edges at $35,000 and $65,000 instead of a gate. The datasets are tested with the
capabilities that read them, on made-up kinds; the lines together, from the expenses paid to line
167, are in the `end_to_end` tests and `returns/2025_return_ag.yaml`.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
RATE_FAMILY = "ca-on/seniors_care_rate"
MAXIMUM_FAMILY = "ca-on/seniors_care_maximum"
BASE_FAMILY = "ca-on/seniors_care_base_amount"
REDUCTION_RATE_FAMILY = "ca-on/seniors_care_reduction_rate"
ON479_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-tc/5006-tc-25e.txt"
ON479_FILE = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025" / "5006-tc-25e.txt"

# Made up for this test and not registered: the medical expenses (line 3), the lines that follow
# from them, the two net incomes (lines 6 and 7) and the lines that follow from those.
MEDICAL = ArtifactKind("ex/medical", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/before_maximum", Decimal)
LINE_5 = ArtifactKind("ex/line_5", Decimal)
OWN_INCOME = ArtifactKind("ex/own_income", Decimal)
SPOUSE_INCOME = ArtifactKind("ex/spouse_income", Decimal)
FAMILY_INCOME = ArtifactKind("ex/family_income", Decimal)
BASE = ArtifactKind("ex/base", Decimal)
OVER_BASE = ArtifactKind("ex/over_base", Decimal)
LINE_12 = ArtifactKind("ex/line_12", Decimal)
LINE_13 = ArtifactKind("ex/line_13", Decimal)
CLAIMS = ArtifactKind("ex/claims", int)
CLAIMED = ArtifactKind("ex/claimed", Decimal)


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


def test_2025_allowable_percentage_is_25_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.25"))
    # Line 5, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_maximum_is_1500() -> None:
    data = SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1500"))
    # Line 5, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_base_amount_is_35000() -> None:
    data = SOURCE.get(BASE_FAMILY, 2025, CREDIT)

    assert data.values == Credit(D("35000.00"))
    # Line 9, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_applicable_rate_is_5_percent() -> None:
    data = SOURCE.get(REDUCTION_RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.05"))
    # Line 12, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_on479_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (ON479_TEXT,)
    assert SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT).sources == (ON479_TEXT,)
    assert SOURCE.get(BASE_FAMILY, 2025, CREDIT).sources == (ON479_TEXT,)
    assert SOURCE.get(REDUCTION_RATE_FAMILY, 2025, RATE).sources == (ON479_TEXT,)


@pytest.mark.parametrize(
    ("family", "quotes"),
    [
        (
            RATE_FAMILY,
            (
                "ontario seniors care at home tax credit",
                "line 4",
                "allowable percentage 25%",
                "line 5",
                "line 3 multiplied by the percentage from line 4",
            ),
        ),
        (
            MAXIMUM_FAMILY,
            (
                "ontario seniors care at home tax credit",
                "line 5",
                "line 3 multiplied by the percentage from line 4 (maximum $1,500)",
            ),
        ),
        (
            BASE_FAMILY,
            ("ontario seniors care at home tax credit", "line 9", "base amount 35,000.00"),
        ),
        (
            REDUCTION_RATE_FAMILY,
            (
                "ontario seniors care at home tax credit",
                "line 11",
                "applicable rate 5%",
                "line 12",
                "line 10 multiplied by the percentage from line 11",
            ),
        ),
    ],
)
def test_each_dataset_header_quotes_on479_as_the_form_prints_it(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family).lower()
    form = squashed(ON479_FILE.read_text(encoding="utf-8-sig")).lower()

    for quoted in quotes:
        assert quoted in header, quoted
        assert quoted in form, quoted


def test_each_dataset_header_states_the_half_up_cent_rule() -> None:
    for family in (RATE_FAMILY, MAXIMUM_FAMILY, BASE_FAMILY, REDUCTION_RATE_FAMILY):
        header = dataset_header(family).lower()

        assert "dollars-and-cents box" in header, family
        assert "half-up" in header, family


def test_the_form_text_in_the_repository_is_the_text_the_figures_are_checked_against() -> None:
    form = squashed(ON479_FILE.read_text(encoding="utf-8-sig"))

    for printed in (
        "Line 3: Medical expenses from line 58769 of your Form ON428",
        "Line 4: Allowable percentage 25%",
        "Line 5: Line 3 multiplied by the percentage from line 4 (maximum $1,500) =",
        "Line 6: Your net income from line 23600 of your return",
        "Line 7: Your spouse's or common-law partner's net income from line 23600 of their return"
        " (if applicable)",
        "Line 8: Line 6 plus line 7 Family net income =",
        "Line 9: Base amount 35,000.00",
        'Line 10: Line 8 minus line 9 (if negative, enter "0") =',
        "Line 11: Applicable rate 5%",
        "Line 12: Line 10 multiplied by the percentage from line 11 =",
        'Line 13 and line 63095: Line 5 minus line 12 (if negative, enter "0") =',
    ):
        assert printed in form, printed


# --- line 5, from the medical expenses ---------------------------------------------------------


@pytest.mark.parametrize(
    ("medical", "before_maximum"),
    [
        # The worked example: 25% of 4000.00.
        ("4000.00", "1000.00"),
        ("0", "0"),
        # 25% of 8000 is 2000, before the maximum.
        ("8000", "2000.00"),
        # 0.02 x 25% = 0.005, a tie, rounded half-up to 0.01; 0.01 x 25% = 0.0025, down to 0.00.
        ("0.02", "0.01"),
        ("0.01", "0.00"),
    ],
)
def test_25_percent_of_the_medical_expenses(medical: str, before_maximum: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), MEDICAL, BEFORE_MAXIMUM)

    result = capability.compute((Artifact(MEDICAL, D(medical)),))

    assert result.outputs == (Artifact(BEFORE_MAXIMUM, D(before_maximum)),)


@pytest.mark.parametrize(
    ("before_maximum", "line_5"),
    [
        # Below the maximum, the product itself.
        ("1000.00", "1000.00"),
        ("0", "0"),
        # At the maximum, and a cent over it (25% of 6000.04 is 1500.01).
        ("1500", "1500"),
        ("1500.01", "1500"),
        # The worked example for the most: 8000 gives 2000.00, which counts as 1500.
        ("2000.00", "1500"),
    ],
)
def test_line_5_is_at_most_1500(before_maximum: str, line_5: str) -> None:
    capability = CappedAmount(SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT), BEFORE_MAXIMUM, LINE_5)

    result = capability.compute((Artifact(BEFORE_MAXIMUM, D(before_maximum)),))

    assert result.outputs == (Artifact(LINE_5, D(line_5)),)


def test_medical_expenses_of_8000_give_line_5_of_1500_through_the_rate_then_the_cap() -> None:
    rate = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), MEDICAL, BEFORE_MAXIMUM)
    cap = CappedAmount(SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT), BEFORE_MAXIMUM, LINE_5)

    result = cap.compute(rate.compute((Artifact(MEDICAL, D("8000")),)).outputs)

    assert result.outputs == (Artifact(LINE_5, D("1500.00")),)


# --- lines 8 to 12, from the two net incomes ----------------------------------------------------


def line_12_for(own: str, spouse: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Lines 8, 9, 10 and 12 for a net income and a spouse's, through the capabilities."""
    start = [Artifact(OWN_INCOME, D(own)), Artifact(SPOUSE_INCOME, D(spouse))]
    (line_8,) = Sum((OWN_INCOME, SPOUSE_INCOME), FAMILY_INCOME).compute(tuple(start)).outputs
    (line_9,) = CreditAmount(SOURCE.get(BASE_FAMILY, 2025, CREDIT), BASE).compute(()).outputs
    (line_10,) = (
        SubtractNotBelowZero(FAMILY_INCOME, BASE, OVER_BASE).compute((line_8, line_9)).outputs
    )
    (line_12,) = (
        ApplyRate(SOURCE.get(REDUCTION_RATE_FAMILY, 2025, RATE), OVER_BASE, LINE_12)
        .compute((line_10,))
        .outputs
    )
    return line_8.value, line_9.value, line_10.value, line_12.value


@pytest.mark.parametrize(
    ("own", "spouse", "line_8", "line_10", "line_12"),
    [
        # The worked example: 30000 + 10000 = 40000, 5000 over 35000, 5% of it is 250.00.
        ("30000", "10000", "40000", "5000", "250.00"),
        # No spouse: line 7 is 0, "if applicable".
        ("30000", "0", "30000", "0", "0"),
        # At 35000, line 10 is 0; a cent under it, line 8 minus line 9 is negative, so 0.
        ("35000", "0", "35000", "0", "0"),
        ("34999.99", "0", "34999.99", "0", "0"),
        # A cent over: 0.01 x 5% = 0.0005, down to 0.00. Ten cents over: 0.005, a tie, up to 0.01.
        ("35000.01", "0", "35000.01", "0.01", "0.00"),
        ("35000.10", "0", "35000.10", "0.10", "0.01"),
        # The two incomes together count: 20000 + 20000.
        ("20000", "20000", "40000", "5000", "250.00"),
        # At 65000, line 12 is 5% of 30000, 1500.00, the most line 5 can be.
        ("65000", "0", "65000", "30000", "1500.00"),
        # A cent over: 30000.01 x 5% = 1500.0005, down to 1500.00.
        ("65000.01", "0", "65000.01", "30000.01", "1500.00"),
    ],
)
def test_the_family_net_income_gives_lines_8_to_12(
    own: str, spouse: str, line_8: str, line_10: str, line_12: str
) -> None:
    assert line_12_for(own, spouse) == (D(line_8), D("35000.00"), D(line_10), D(line_12))


# --- line 13 and the claim ----------------------------------------------------------------------


def credit_for(medical: str, own: str, spouse: str, claims: int = 1) -> Decimal:
    """Line 13 for the medical expenses (line 3) and the two net incomes, as claimed or not."""
    rate = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), MEDICAL, BEFORE_MAXIMUM)
    cap = CappedAmount(SOURCE.get(MAXIMUM_FAMILY, 2025, AMOUNT), BEFORE_MAXIMUM, LINE_5)
    (line_5,) = cap.compute(rate.compute((Artifact(MEDICAL, D(medical)),)).outputs).outputs
    *_, line_12 = line_12_for(own, spouse)
    (line_13,) = (
        SubtractNotBelowZero(LINE_5, LINE_12, LINE_13)
        .compute((line_5, Artifact(LINE_12, line_12)))
        .outputs
    )
    (claimed,) = (
        TimesCount(LINE_13, CLAIMS, CLAIMED).compute((line_13, Artifact(CLAIMS, claims))).outputs
    )
    return D(claimed.value)


@pytest.mark.parametrize(
    ("medical", "own", "spouse", "line_13"),
    [
        # The worked examples: 750.00 (family net income 40000), 1000.00 (30000), 0 (70000).
        ("4000.00", "30000", "10000", "750.00"),
        ("4000.00", "30000", "0", "1000.00"),
        ("4000.00", "40000", "30000", "0"),
        # Line 58769 of 8000 gives line 5 of 1500, the maximum.
        ("8000", "30000", "0", "1500.00"),
        # Family net income of 65000 and 65000.01: line 12 is 1500.00 at least line 5.
        ("8000", "65000", "0", "0"),
        ("8000", "65000.01", "0", "0"),
        ("4000.00", "65000", "0", "0"),
        # A cent under the 65000 where line 12 first reaches 1500.00 (1499.9995 rounds up to it).
        ("8000", "64999.99", "0", "0"),
        # At 35000 nothing comes off; ten cents over takes off 0.01.
        ("4000.00", "35000", "0", "1000.00"),
        ("4000.00", "35000.10", "0", "999.99"),
        # No medical expenses: no credit, however low the income.
        ("0", "20000", "0", "0"),
        # Line 12 is the same 250.00 at 40000 whatever line 5 is; line 5 of 1500 less it: 1250.00.
        ("8000", "30000", "10000", "1250.00"),
        # Line 12 above line 5 is not carried below zero: 1000.00 - 1500.00 is 0.
        ("4000.00", "64000", "1000", "0"),
    ],
)
def test_line_13_is_line_5_less_line_12_not_below_zero(
    medical: str, own: str, spouse: str, line_13: str
) -> None:
    assert credit_for(medical, own, spouse) == D(line_13)


@pytest.mark.parametrize(
    ("medical", "own", "spouse"),
    [("4000.00", "30000", "10000"), ("8000", "30000", "0")],
)
def test_a_filer_who_does_not_claim_has_no_credit(medical: str, own: str, spouse: str) -> None:
    assert credit_for(medical, own, spouse, claims=0) == D("0")

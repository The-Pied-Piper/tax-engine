"""The 2025 net capital loss of 2000 figures of Form T1436, checked against CRA's form.

Form T1436 (Capital Gains Worksheet, 2025; CRA publishes no .txt, so the quotes are from the text
extracted from the PDF), "Line 25300 - Net capital loss of other years (if you have pre-1986
capital loss balance)", "Chart A - Adjustment calculation for carry-forward losses", row "In 2000":
column (B) "1/(IR × 2)" and column (F) "2 × IR", where IR is the inclusion rate for 2000. The
chart's footnote: "When you complete this table, replace “IR” with your inclusion rate for 2000.
This rate is from line 16 in Part 4 of Schedule 3 for 2000, or from your notice of assessment or
latest notice of reassessment for 2000." The IR is the filer's figure that Form T657 Chart 2 also
reads, so this row reads the same input.

Column (B) is 1 over column (F), so column (C) is column (A) divided by column (F): one division,
rounded half-up to the cent once, 0 when IR is 0. Column (G) is column (E) multiplied by column
(F), rounded once. The 2 of "2 × IR" is the fraction 2/1 applied to IR, exact and not rounded; the
printed 1 of "1/(IR × 2)" is a credit of 1. Columns (D) and (E) are the manifest's, from existing
capabilities: this module builds them from the same datasets with made-up kinds and pins the chain,
the way the form prints it, with the row left after the 1990 to 1999 row as the input for column
(D) and oldest first. Guide T4037 (2025): "You have to apply net capital losses of earlier years
before you apply net capital losses of later years."
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.apply_ratio import ApplyRatio
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capability import CapabilityResult
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.fraction import FRACTION, Fraction
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.registry import Namespace
from tax_calculator.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FORM = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1436/t1436-25e.pdf"

TWICE_IR = "ca/net_capital_loss_twice_ir_fraction_2000"
NUMERATOR_ONE = "ca/net_capital_loss_numerator_one_2000"
COLUMN_C_ROUNDING = "ca/adjusted_gross_capital_losses_2000_rounding"
COLUMN_G_ROUNDING = "ca/net_capital_loss_balance_2000_rounding"

# The form lines each dataset header quotes, lowercased as the header is compared. CRA publishes
# no .txt of T1436, so the quotes are checked against the form lines as copied from the PDF.
HEADER_QUOTES = {
    TWICE_IR: ("in 2000", "2 × ir"),
    NUMERATOR_ONE: ("1/(ir × 2)",),
    COLUMN_C_ROUNDING: ("adjusted gross capital losses (column a multiplied by column b)",),
    COLUMN_G_ROUNDING: (
        "net capital loss balance available to carry forward (column e multiplied by column f)",
    ),
}


# Made up for this test and not registered: the inputs and the columns of the row "In 2000", and
# the line 13 left after the row "After 1989 and before 2000".
def kind(name: str) -> ArtifactKind[Decimal]:
    return ArtifactKind(f"ex/{name}", Decimal)


UNAPPLIED = kind("unapplied_2000")
RATE = kind("inclusion_rate")
TWICE = kind("twice_ir")
NUMERATOR = kind("numerator_one")
COLUMN_C = kind("column_c")
LEFT_BEFORE = kind("left_before_2000")
COLUMN_D = kind("column_d")
LEFT_AFTER = kind("left_after_2000")
COLUMN_E = kind("column_e")
COLUMN_G = kind("column_g")


def only(result: CapabilityResult) -> Artifact[Decimal]:
    (output,) = result.outputs
    return cast(Artifact[Decimal], output)


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    text = "\n".join(lines[:first_key]).replace("#", " ")
    return " ".join(text.split())


def chart_2000(loss: str, ir: str, left: str) -> dict[str, Decimal]:
    """The row "In 2000" of Chart A from the real datasets: columns C, D, E and G, the 2 × IR, and
    the line 13 left for the rows after it.

    `loss` is column A, `ir` the 2000 inclusion rate and `left` what is left of line 13 after the
    row "After 1989 and before 2000".
    """
    column_a = Artifact(UNAPPLIED, D(loss))
    rate = Artifact(RATE, D(ir))
    left_before = Artifact(LEFT_BEFORE, D(left))
    twice_ir = only(
        ApplyFraction(SOURCE.get(TWICE_IR, 2025, FRACTION), RATE, TWICE).compute((rate,))
    )
    numerator = only(CreditAmount(SOURCE.get(NUMERATOR_ONE, 2025, CREDIT), NUMERATOR).compute(()))
    column_c = only(
        ApplyRatioOrZero(
            SOURCE.get(COLUMN_C_ROUNDING, 2025, ROUNDING_ONLY),
            UNAPPLIED,
            NUMERATOR,
            TWICE,
            COLUMN_C,
        ).compute((column_a, numerator, twice_ir))
    )
    applied = only(LesserOf((COLUMN_C, LEFT_BEFORE), COLUMN_D).compute((column_c, left_before)))
    left_after = only(Subtract(LEFT_BEFORE, COLUMN_D, LEFT_AFTER).compute((left_before, applied)))
    column_e = only(Subtract(COLUMN_C, COLUMN_D, COLUMN_E).compute((column_c, applied)))
    column_g = only(
        ApplyRatio(
            SOURCE.get(COLUMN_G_ROUNDING, 2025, ROUNDING_ONLY),
            COLUMN_E,
            TWICE,
            NUMERATOR,
            COLUMN_G,
        ).compute((column_e, twice_ir, numerator))
    )
    return {
        "twice_ir": twice_ir.value,
        "c": column_c.value,
        "d": applied.value,
        "left_after": left_after.value,
        "e": column_e.value,
        "g": column_g.value,
    }


def test_2025_the_2_of_2_x_ir_is_an_exact_fraction_of_2_over_1_with_no_rounding() -> None:
    data = SOURCE.get(TWICE_IR, 2025, FRACTION)

    assert data.values == Fraction(2, 1)
    assert data.rounding == NO_ROUNDING
    assert FORM in data.sources


def test_2025_the_printed_1_of_1_over_2_x_ir_is_a_credit_of_1_rounded_to_the_cent() -> None:
    data = SOURCE.get(NUMERATOR_ONE, 2025, CREDIT)

    assert data.values == Credit(amount=D("1"))
    assert data.rounding == CENT
    assert FORM in data.sources


@pytest.mark.parametrize("family", [COLUMN_C_ROUNDING, COLUMN_G_ROUNDING])
def test_2025_columns_c_and_g_round_half_up_to_the_cent_with_no_values(family: str) -> None:
    data = SOURCE.get(family, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT
    assert FORM in data.sources


def test_the_printed_1_is_an_artifact_of_the_same_name() -> None:
    result = CreditAmount(SOURCE.get(NUMERATOR_ONE, 2025, CREDIT), NUMERATOR).compute(())

    assert result.outputs == (Artifact(NUMERATOR, D("1.00")),)


@pytest.mark.parametrize(("family", "quotes"), HEADER_QUOTES.items())
def test_the_dataset_header_quotes_t1436_as_the_form_prints_it(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family).lower()

    for quoted in quotes:
        assert quoted in header, quoted


@pytest.mark.parametrize("family", [NUMERATOR_ONE, COLUMN_C_ROUNDING, COLUMN_G_ROUNDING])
def test_the_dataset_header_states_the_half_up_cent_rule(family: str) -> None:
    assert "half-up to the cent" in dataset_header(family)


@pytest.mark.parametrize(
    ("ir", "twice_ir"),
    [
        ("0.6", "1.2"),
        ("0.6667", "1.3334"),
        ("0.75", "1.5"),
        ("1", "2"),
        ("0", "0"),
    ],
)
def test_twice_ir_is_2_times_the_inclusion_rate_exactly(ir: str, twice_ir: str) -> None:
    capability = ApplyFraction(SOURCE.get(TWICE_IR, 2025, FRACTION), RATE, TWICE)

    result = capability.compute((Artifact(RATE, D(ir)),))

    assert result.outputs == (Artifact(TWICE, D(twice_ir)),)


@pytest.mark.parametrize(
    ("loss", "ir", "column_c"),
    [
        # 1000 divided by 1.20 is 833.33...
        ("1000", "0.6", "833.33"),
        # 2000 divided by 1.3334 is 1499.925..., up to 1499.93 (half-up, not down).
        ("2000", "0.6667", "1499.93"),
        # 3000 divided by 1.5 is exactly 2000.
        ("3000", "0.75", "2000.00"),
        # Twice IR is 1 at IR 0.5, so column C is column A.
        ("1234.56", "0.5", "1234.56"),
        # A tie rounds up: 0.01 divided by 2 is 0.005.
        ("0.01", "1", "0.01"),
        # IR not entered (0): column F is 0 and column C is 0.
        ("1000", "0", "0.00"),
    ],
)
def test_column_c_is_column_a_over_twice_ir_rounded_half_up_once(
    loss: str, ir: str, column_c: str
) -> None:
    chart = chart_2000(loss, ir, left="1000000")

    assert chart["c"] == D(column_c)


def test_the_row_in_2000_at_ir_06_gives_1_20_then_833_33_and_leaves_19166_67() -> None:
    # Chart A row "In 2000" with 1000 at IR 0.6, the line 13 left after 1990 to 1999 being 20000:
    # column F is 1.20, column C is 833.33, column D is 833.33, columns E and G are 0.00, and
    # 19166.67 is left for the row "After 2000 and before 2025".
    chart = chart_2000("1000", "0.6", left="20000")

    assert chart["twice_ir"] == D("1.2")
    assert chart["c"] == D("833.33")
    assert chart["d"] == D("833.33")
    assert chart["left_after"] == D("19166.67")
    assert chart["e"] == D("0.00")
    assert chart["g"] == D("0.00")


def test_column_d_is_the_lesser_of_column_c_and_what_1990_to_1999_leaves_of_line_13() -> None:
    # Column C is 1499.93 and 500 is left: column D is 500.00, and nothing is left for the rows
    # after: 0.00. Column E is 999.93.
    chart = chart_2000("2000", "0.6667", left="500")

    assert chart["d"] == D("500.00")
    assert chart["left_after"] == D("0.00")
    assert chart["e"] == D("999.93")


def test_column_d_takes_all_of_column_c_when_more_is_left_and_column_e_is_0() -> None:
    chart = chart_2000("1000", "0.6", left="20000")

    assert chart["d"] == D("833.33")
    assert chart["e"] == D("0.00")


def test_column_g_is_column_e_times_twice_ir_rounded_half_up_once() -> None:
    # Column E 999.93 times 1.3334 is 1333.306662, up to 1333.31, rounded once.
    chart = chart_2000("2000", "0.6667", left="500")

    assert chart["e"] == D("999.93")
    assert chart["g"] == D("1333.31")


def test_column_g_rounds_a_tie_half_up_to_the_cent() -> None:
    # 0.01 times 1.5 is 0.015, a tie, up to 0.02.
    capability = ApplyRatio(
        SOURCE.get(COLUMN_G_ROUNDING, 2025, ROUNDING_ONLY),
        COLUMN_E,
        TWICE,
        NUMERATOR,
        COLUMN_G,
    )

    result = capability.compute(
        (
            Artifact(COLUMN_E, D("0.01")),
            Artifact(TWICE, D("1.5")),
            Artifact(NUMERATOR, D("1")),
        )
    )

    assert result.outputs == (Artifact(COLUMN_G, D("0.02")),)

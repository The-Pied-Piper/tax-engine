"""The 2025 federal political contribution tax credit figures, checked against CRA's forms.

2025 Federal Worksheet (form 5000-D1), "Line 41000 - Federal political contribution tax credit":
"If your total federal political contributions from line 40900 of your return were" "$1,275 or
more, enter $650 on line 41000 of your return. If not, use the amount from line 40900 of your
return to decide which column to complete."; three alternative columns, "Column 1: Line 40900 is
$400 or less", "Column 2: Line 40900 is more than $400 but not more than $750" and "Column 3: Line
40900 is more than more than $750", each with line 1 "Total federal political contributions from
line 40900 of your return"; line 2 a printed constant (0.00, 400.00, 750.00); line 3 "Line 1 minus
line 2 (if negative, enter "0") ="; line 4 "Rate" (75%, 50%, 33.33%); line 5 "Line 3 multiplied by
the percentage from line 4 ="; line 6 a printed constant (0.00, 300.00, 475.00); line 7 "Line 5
plus line 6 Enter this amount on line 41000 of your return. =". 2025 T1 for Ontario (form 5006-R),
"Line 135 and line 41000: Total federal political contributions (attach receipts) Line 40900"
"(maximum $650)".

Every printed figure is a dataset as printed, none derived: each line 2 and line 6 a constant (the
`credit` kind, claimed whole), each line 4 a rate (33.33% is `0.3333`, a plain decimal), the
shortcut's $1,275 and $650 two more constants and the return's maximum a plain cap (the `amount`
kind). The form states no rounding rule; lines 5 and 41000 are dollars-and-cents boxes, so each is
rounded half-up to the cent, the owner's decision. The column that applies is picked by the
contributions (line 1): column 1 when they are at most the column 2 line 2 constant, column 2 when
they are over that but at most the column 3 line 2 constant, column 3 otherwise; the shortcut
then chooses the printed $650 when the contributions are at least the printed $1,275 (the same
chooser, which needs six different artifacts: its middle range is column 3's line 2 and line 7,
never reached as $1,275 is over $750), and the maximum caps the result.
"""

from __future__ import annotations

from decimal import Decimal
from typing import cast

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capability import CapabilityResult
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca_on.capabilities.choose_by_range import ChooseByRange

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"
RETURN_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-r/5006-r-25e.txt"
MAXIMUM = "ca/political_credit_maximum"
THRESHOLD = "ca/political_credit_shortcut_threshold"
SHORTCUT = "ca/political_credit_shortcut_amount"


def family(column: int, line: int) -> str:
    return f"ca/political_credit_column_{column}_line_{line}"


# Made up for this test and not registered: the contributions (line 1), each column's lines 2, 3,
# 5, 6 and 7, the shortcut's two constants, the chosen column, the pick (before the maximum) and
# line 41000.
CONTRIBUTIONS = ArtifactKind("ex/contributions", Decimal)
THRESHOLD_KIND = ArtifactKind("ex/shortcut_threshold", Decimal)
SHORTCUT_KIND = ArtifactKind("ex/shortcut_amount", Decimal)
CHOSEN_COLUMN = ArtifactKind("ex/chosen_column", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/credit_before_maximum", Decimal)
LINE_41000 = ArtifactKind("ex/credit", Decimal)


def line(column: int, number: int) -> ArtifactKind[Decimal]:
    return ArtifactKind(f"ex/column_{column}_line_{number}", Decimal)


def only(result: CapabilityResult) -> Artifact[Decimal]:
    (output,) = result.outputs
    return cast(Artifact[Decimal], output)


def constant(name: str, kind: ArtifactKind[Decimal]) -> Artifact[Decimal]:
    return only(CreditAmount(SOURCE.get(name, 2025, CREDIT), kind).compute(()))


def column_line_7(column: int, contributions: str) -> Decimal:
    """The column's line 7 from the real datasets: lines 2 to 6 as the form prints them."""
    line_2 = constant(family(column, 2), line(column, 2))
    line_6 = constant(family(column, 6), line(column, 6))
    line_3 = only(
        SubtractNotBelowZero(CONTRIBUTIONS, line(column, 2), line(column, 3)).compute(
            (Artifact(CONTRIBUTIONS, D(contributions)), line_2)
        )
    )
    line_5 = only(
        ApplyRate(
            SOURCE.get(family(column, 4), 2025, RATE), line(column, 3), line(column, 5)
        ).compute((line_3,))
    )
    return only(
        Sum((line(column, 5), line(column, 6)), line(column, 7)).compute((line_5, line_6))
    ).value


def line_41000(contributions: str) -> Decimal:
    """Line 41000: the column that applies, the shortcut over it, capped by the maximum."""
    contributed = Artifact(CONTRIBUTIONS, D(contributions))
    columns = tuple(Artifact(line(c, 7), column_line_7(c, contributions)) for c in (1, 2, 3))
    limits = tuple(constant(family(c, 2), line(c, 2)) for c in (2, 3))
    chosen = only(
        ChooseByRange(
            CONTRIBUTIONS,
            line(2, 2),
            line(3, 2),
            line(1, 7),
            line(2, 7),
            line(3, 7),
            CHOSEN_COLUMN,
        ).compute((contributed, *limits, *columns))
    )
    picked = only(
        ChooseByRange(
            THRESHOLD_KIND,
            CONTRIBUTIONS,
            line(3, 2),
            SHORTCUT_KIND,
            line(3, 7),
            CHOSEN_COLUMN,
            BEFORE_MAXIMUM,
        ).compute(
            (
                constant(THRESHOLD, THRESHOLD_KIND),
                contributed,
                limits[1],
                constant(SHORTCUT, SHORTCUT_KIND),
                columns[2],
                chosen,
            )
        )
    )
    return only(
        CappedAmount(SOURCE.get(MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, LINE_41000).compute(
            (picked,)
        )
    ).value


@pytest.mark.parametrize(
    ("column", "constant_"),
    [(1, "0.00"), (2, "400.00"), (3, "750.00")],
)
def test_2025_line_2_is_the_printed_constant(column: int, constant_: str) -> None:
    data = SOURCE.get(family(column, 2), 2025, CREDIT)

    assert data.values == Credit(amount=D(constant_))
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


@pytest.mark.parametrize(
    ("column", "rate"),
    [(1, "0.75"), (2, "0.5"), (3, "0.3333")],
)
def test_2025_line_4_is_the_printed_rate(column: int, rate: str) -> None:
    data = SOURCE.get(family(column, 4), 2025, RATE)

    assert data.values == Rate(D(rate))
    # Line 5, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


@pytest.mark.parametrize(
    ("column", "constant_"),
    [(1, "0.00"), (2, "300.00"), (3, "475.00")],
)
def test_2025_line_6_is_the_printed_constant(column: int, constant_: str) -> None:
    data = SOURCE.get(family(column, 6), 2025, CREDIT)

    assert data.values == Credit(amount=D(constant_))
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_shortcut_threshold_is_1275() -> None:
    data = SOURCE.get(THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("1275"))
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_shortcut_amount_is_650() -> None:
    data = SOURCE.get(SHORTCUT, 2025, CREDIT)

    assert data.values == Credit(amount=D("650"))
    assert data.rounding == CENT
    assert data.sources == (WORKSHEET_TEXT,)


def test_2025_maximum_is_650() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("650"))
    # T1 line 135 and line 41000, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (RETURN_TEXT,)


@pytest.mark.parametrize(
    ("contributions", "column_1", "column_2", "column_3"),
    [
        # Column 1: 75% of the contributions; columns 2 and 3 on 0 over their line 2: only line 6.
        ("300", "225.00", "300.00", "475.00"),
        # 1,000: column 2 line 3 = 600, line 5 = 300, line 7 = 600.00; column 3 line 3 = 250, line 5
        # = 83.325, up to 83.33, line 7 = 558.33.
        ("1000", "750.00", "600.00", "558.33"),
        ("0", "0.00", "300.00", "475.00"),
    ],
)
def test_each_column_is_built_as_the_form_prints_it(
    contributions: str, column_1: str, column_2: str, column_3: str
) -> None:
    assert column_line_7(1, contributions) == D(column_1)
    assert column_line_7(2, contributions) == D(column_2)
    assert column_line_7(3, contributions) == D(column_3)


@pytest.mark.parametrize(
    ("contributions", "credit"),
    [
        # The acceptance figures.
        ("0", "0.00"),
        ("400", "300.00"),
        ("750", "475.00"),
        ("1000", "558.33"),
        ("1275", "650"),
        ("5000", "650"),
        ("300", "225.00"),
        # A cent over column 1's limit: column 2 line 3 = 0.01, line 5 = 0.005, up to 0.01, line 7
        # = 300.01.
        ("400.01", "300.01"),
        # A cent over column 2's limit: column 3 line 3 = 0.01, line 5 = 0.003333, down to 0.00.
        ("750.01", "475.00"),
        # A cent under the $1,275 the form names: column 3 line 3 = 524.99, line 5 = 174.9792, down
        # to 174.98, line 7 = 649.98, two cents under the maximum.
        ("1274.99", "649.98"),
        # At the $1,275 the shortcut chooses the printed $650 (acceptance figures above), where
        # the worksheet would give line 5 = 33.33% x 525 = 174.9825, down to 174.98, and line 7 =
        # 649.98; a cent over, the shortcut still applies.
        ("1275.01", "650"),
    ],
)
def test_line_41000_is_the_applicable_column_or_the_shortcut_capped_at_the_maximum(
    contributions: str, credit: str
) -> None:
    assert line_41000(contributions) == D(credit)

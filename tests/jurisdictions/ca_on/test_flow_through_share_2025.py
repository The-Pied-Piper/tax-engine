"""The 2025 Ontario focused flow-through share credit rate, checked against CRA's ON479.

2025 Form ON479 (form 5006-TC), "Ontario focused flow-through share tax credit": "Line 17 and line
63220: Enter your total expenses from your Form T1221. multiplied by 5% ="; "Line 18: Add lines 1,
2, 13, 14, 16, and 17. =". The 5% is a rate (the `rate` kind), and line 17 is a dollars-and-cents
box, so the product rounds half-up to the cent. The expenses are Form T1221 line 4, the total of
its slip lines, which a capability adds from the record list of slips. Line 17 is one of the
lines line 18 adds.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
RATE_FAMILY = "ca-on/flow_through_share_rate"
ON479_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-tc/5006-tc-25e.txt"
FORM_TEXT = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025" / "5006-tc-25e.txt"

# Made up for this test and not registered: the total expenses (T1221 line 4) and the credit
# (ON479 line 17).
EXPENSES = ArtifactKind("ex/expenses", Decimal)
CREDIT = ArtifactKind("ex/credit", Decimal)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header() -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (root / "parameters" / "flow_through_share_rate" / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_rate_is_5_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.05"))
    # ON479 line 17, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_cites_only_the_on479_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (ON479_TEXT,)


def test_the_dataset_header_quotes_on479_line_17_as_the_form_prints_it() -> None:
    header = dataset_header().lower()
    form = squashed(FORM_TEXT.read_text(encoding="utf-8-sig")).lower()

    for quoted in (
        "line 17 and line 63220",
        "enter your total expenses from your form t1221.",
        "multiplied by 5%",
        "ontario focused flow-through share tax credit",
    ):
        assert quoted in header, quoted
        assert quoted in form, quoted


@pytest.mark.parametrize(
    ("expenses", "credit"),
    [
        # Return M: T1221 line 4 of 6,000 + 4,000, x 5%.
        ("10000", "500.00"),
        ("6000", "300.00"),
        ("0", "0"),
        # 1234.56 x 5% = 61.728, rounded half-up to 61.73.
        ("1234.56", "61.73"),
        # 0.10 x 5% = 0.005, a tie, up to 0.01; 0.09 x 5% = 0.0045, down to 0.00.
        ("0.10", "0.01"),
        ("0.09", "0.00"),
        # 10000.30 x 5% = 500.015, a tie, up to 500.02.
        ("10000.30", "500.02"),
    ],
)
def test_5_percent_of_the_total_expenses(expenses: str, credit: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), EXPENSES, CREDIT)

    result = capability.compute((Artifact(EXPENSES, D(expenses)),))

    assert result.outputs == (Artifact(CREDIT, D(credit)),)

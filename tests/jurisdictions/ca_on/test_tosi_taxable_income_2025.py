"""The 2025 TOSI-adjusted taxable income rate (Form T1206 Part 2 line 8A), checked against CRA.

Form T1206 2025 (docs/cra-forms-2025/t1206-25e.pdf, confirmed 2026-10-19 from the PDF; no .txt
published), Part 2 - Federal tax on split income: "TOSI-adjusted taxable income Amount from line 8
÷ 14.5% = 8A", and the page 5 note "If you are completing a federal Schedule 11, calculate line 8A
and add it to the amount on line 11 of Schedule 11".

The printed 14.5% is a `rate` dataset of its own, `ca/tosi_taxable_income_rate`, beside the T1206
rates of line 8 and line 14 and the Schedule 11 rate of line 11 (the same percentage on other
forms). Line 8A is a dollars-and-cents box, so the quotient rounds half-up to the cent, the owner's
decision, as the form states no rounding rule.

The dataset is tested with the capability that reads it, on made-up kinds for the form's lines.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.divided_by_rate import DividedByRate

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T1206_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1206/t1206-25e.pdf"
TOSI_TAXABLE_INCOME_RATE = "ca/tosi_taxable_income_rate"

# Made up for this test and not registered: the form's lines, by number.
LINE_8 = ArtifactKind("ex/line_8", Decimal)
LINE_8A = ArtifactKind("ex/line_8a", Decimal)


def line_8a(amount: str) -> Decimal:
    """Line 8A from line 8 `amount`, as the capability the manifest selects does."""
    capability = DividedByRate(SOURCE.get(TOSI_TAXABLE_INCOME_RATE, 2025, RATE), LINE_8, LINE_8A)
    (output,) = capability.compute((Artifact(LINE_8, D(amount)),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def test_2025_line_8a_rate_is_the_printed_14_5_percent() -> None:
    data = SOURCE.get(TOSI_TAXABLE_INCOME_RATE, 2025, RATE)

    assert data.values == Rate(D("0.145"))
    # Line 8A, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


@pytest.mark.parametrize(
    ("line_8", "result"),
    [
        # The worked example: 3,795 / 14.5% = 26,172.4137..., down to 26,172.41.
        ("3795.00", "26172.41"),
        ("0.00", "0.00"),
        ("145", "1000.00"),
        # Half-up to the cent: 0.000725 / 14.5% is exactly 0.005, a tie, up to 0.01; 0.00072 / 14.5%
        # is 0.00496..., down to 0.00.
        ("0.000725", "0.01"),
        ("0.00072", "0.00"),
    ],
)
def test_line_8a_is_line_8_divided_by_14_5_percent_to_the_cent(line_8: str, result: str) -> None:
    assert line_8a(line_8) == D(result)

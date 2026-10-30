"""The 2025 Ontario TOSI-adjusted taxable income rate (Form T1206 line 33B), checked against CRA.

Form T1206 2025 (docs/cra-forms-2025/t1206-25e.pdf, confirmed 2026-10-19 from the PDF; no .txt
published), Part 3 "TOSI-adjusted taxable income": "Amount from line 33 ... 33A", "Tax rate that
applies to your province or territory from column 3 in Chart C on page 5 ÷ % 33B", "Amount from
line 33A divided by the tax rate you entered on line 33B = 33C", and Chart C, Ontario's row: "ON
20.53% 5.05% 10% 2.9863% Not applicable" (column 3, 5.05%).

The printed 5.05% is a `rate` dataset of its own, `ca-on/tosi_taxable_income_rate`, beside the
Ontario rates of line 33 and line 37 (the same percentage on other lines). Line 33C is a
dollars-and-cents box, so the quotient rounds half-up to the cent, the owner's decision, as the form
states no rounding rule.

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
TOSI_TAXABLE_INCOME_RATE = "ca-on/tosi_taxable_income_rate"

# Made up for this test and not registered: the form's lines, by number.
LINE_33A = ArtifactKind("ex/line_33a", Decimal)
LINE_33C = ArtifactKind("ex/line_33c", Decimal)


def line_33c(amount: str) -> Decimal:
    """Line 33C from line 33A `amount`, as the capability the manifest selects does."""
    capability = DividedByRate(SOURCE.get(TOSI_TAXABLE_INCOME_RATE, 2025, RATE), LINE_33A, LINE_33C)
    (output,) = capability.compute((Artifact(LINE_33A, D(amount)),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def test_2025_line_33b_rate_is_the_printed_5_05_percent() -> None:
    data = SOURCE.get(TOSI_TAXABLE_INCOME_RATE, 2025, RATE)

    assert data.values == Rate(D("0.0505"))
    # Line 33C, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT
    assert data.sources == (T1206_PDF,)


@pytest.mark.parametrize(
    ("line_33a", "result"),
    [
        # The worked example: 2,360.95 / 5.05% = 46,751.4851..., up to 46,751.49.
        ("2360.95", "46751.49"),
        ("0.00", "0.00"),
        ("5.05", "100.00"),
        # Half-up to the cent: 0.000252500 / 5.05% is exactly 0.005, a tie, up to 0.01;
        # 0.00025 / 5.05% is 0.00495..., down to 0.00.
        ("0.0002525", "0.01"),
        ("0.00025", "0.00"),
    ],
)
def test_line_33c_is_line_33a_divided_by_5_05_percent_to_the_cent(
    line_33a: str, result: str
) -> None:
    assert line_33c(line_33a) == D(result)

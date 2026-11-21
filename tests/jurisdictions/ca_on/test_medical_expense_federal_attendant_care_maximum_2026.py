"""The 2026 `ca-on/medical_expense_federal_attendant_care_maximum` dataset, from CRA 5006-PC
"Ontario
tax information for 2025", section "Line 58689" (5006-pc-25e.txt): "If the amount you claimed for
medical expenses on your return includes an amount for attendant care expenses that was limited to
$10,000 ($20,000 in the year of death), the maximum Ontario claim for attendant care expenses is
$17,627 ($35,253 in the year of death)"

The figure is the federal limit the text names ("limited to $10,000 ($20,000 in the year of
death)"). It is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice,
as the text states no rounding rule.

Provisional: the 2026 CRA Ontario tax information is not published, so the 2025 printed figure is
carried forward.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)


def test_2026_medical_expense_federal_attendant_care_maximum_is_10000() -> None:
    data = SOURCE.get("ca-on/medical_expense_federal_attendant_care_maximum", 2026, AMOUNT)

    assert data.values == Amount(D("10000"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_medical_expense_federal_attendant_care_maximum_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (
        (root / "parameters" / "medical_expense_federal_attendant_care_maximum" / "2026.yaml")
        .read_text()
        .splitlines()
    )

    assert lines[0] == (
        "# Provisional: taken from the 2025 form text named in sources; to be confirmed against "
        "the 2026 form text when CRA publishes it."
    )
    assert lines[1] == (
        "# Derivation: carried forward unchanged from the 2025 file; the 2026 form is not yet "
        "published."
    )

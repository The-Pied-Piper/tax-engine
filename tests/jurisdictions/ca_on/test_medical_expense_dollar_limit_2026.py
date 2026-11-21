"""The 2026 `ca-on/medical_expense_dollar_limit` dataset, from Form ON428 (5006-c-25e.txt) line 40:
"Enter whichever is less: $2,885 or the amount on line 39."

The figure is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice, as
the form states no rounding rule.

Provisional: the 2026 Form ON428 is not published, so the 2025 printed figure is carried forward.
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


def test_2026_medical_expense_dollar_limit_is_2885() -> None:
    data = SOURCE.get("ca-on/medical_expense_dollar_limit", 2026, AMOUNT)

    assert data.values == Amount(D("2885"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_medical_expense_dollar_limit_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (
        (root / "parameters" / "medical_expense_dollar_limit" / "2026.yaml")
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

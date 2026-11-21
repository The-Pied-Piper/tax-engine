"""The 2026 `ca-on/medical_expense_patient_move_maximum` dataset, from CRA 5006-PC "Ontario tax
information for 2025", section "Line 58689" (5006-pc-25e.txt): "The maximum Ontario claim for moving
expenses for a patient's move to a more accessible dwelling is $3,525"

The figure is a printed maximum on an unprinted working step, so the dataset carries no rounding
(exact), the project's rule that only a printed line rounds.

Provisional: the 2026 CRA Ontario tax information is not published, so the 2025 printed figure is
carried forward.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)


def test_2026_medical_expense_patient_move_maximum_is_3525() -> None:
    data = SOURCE.get("ca-on/medical_expense_patient_move_maximum", 2026, AMOUNT)

    assert data.values == Amount(D("3525"))
    assert data.rounding == NO_ROUNDING


def test_2026_medical_expense_patient_move_maximum_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    lines = (
        (root / "parameters" / "medical_expense_patient_move_maximum" / "2026.yaml")
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

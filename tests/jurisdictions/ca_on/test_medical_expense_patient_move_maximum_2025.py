"""The 2025 `ca-on/medical_expense_patient_move_maximum` dataset, from CRA 5006-PC "Ontario tax
information for 2025", section "Line 58689" (5006-pc-25e.txt): "The maximum Ontario claim for moving
expenses for a patient's move to a more accessible dwelling is $3,525"

The figure is a printed maximum on an unprinted working step, so the dataset carries no rounding
(exact), the project's rule that only a printed line rounds.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import NO_ROUNDING

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)


def test_2025_medical_expense_patient_move_maximum_is_3525() -> None:
    data = SOURCE.get("ca-on/medical_expense_patient_move_maximum", 2025, AMOUNT)

    assert data.values == Amount(D("3525"))
    assert data.rounding == NO_ROUNDING

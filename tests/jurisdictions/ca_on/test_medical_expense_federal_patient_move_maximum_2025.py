"""The 2025 `ca-on/medical_expense_federal_patient_move_maximum` dataset, from CRA Guide RC4065
"Medical Expenses" (PDF page 22, confirmed 2026-11-21 from the PDF; no .txt published):
"to a limit of $2,000 (for residents of Ontario, the provincial limit is $3,525)"

The figure is the federal limit that the Ontario maximum replaces on ON428 line 36. It feeds an
unprinted working step, so the dataset carries no rounding (exact), the project's rule that only a
printed line rounds.
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


def test_2025_medical_expense_federal_patient_move_maximum_is_2000() -> None:
    data = SOURCE.get("ca-on/medical_expense_federal_patient_move_maximum", 2025, AMOUNT)

    assert data.values == Amount(D("2000"))
    assert data.rounding == NO_ROUNDING

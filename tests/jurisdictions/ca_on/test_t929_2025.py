"""The 2025 amounts of Form T929, the disability supports deduction, checked against the form.

Form T929 (2024 edition, the latest CRA publishes; `docs/cra-forms-2025/t929-24e.pdf`), Step 2:
line 9 "Line 8 multiplied by $375" and line 10 "Enter the amount from line 7 or line 9, whichever
is less. (maximum $15,000)". The 2024 figures are used for 2025 as printed, to be confirmed when a
2025 edition is published. Line 9 and line 10 are dollars-and-cents boxes, so each is rounded
half-up to the cent; the form states no other rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
WEEKLY_AMOUNT = "ca/t929_weekly_amount"
MAXIMUM = "ca/t929_maximum"


def test_2025_weekly_amount_is_375_per_week_of_attendance() -> None:
    data = SOURCE.get(WEEKLY_AMOUNT, 2025, AMOUNT)

    # Line 9: "Line 8 multiplied by $375", the number of weeks the filer attended.
    assert data.values == Amount(D("375"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_for_the_school_attendance_part_is_15000() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    # Line 10: "Enter the amount from line 7 or line 9, whichever is less. (maximum $15,000)".
    assert data.values == Amount(D("15000"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)

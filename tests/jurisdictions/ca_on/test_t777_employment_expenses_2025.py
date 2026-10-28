"""The 2025 Form T777 datasets of the employment expenses lines and the labour mobility deduction.

Form T777 (2025), Statement of Employment Expenses, read from the PDF
(https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t777/t777-25e.pdf; `docs/cra-forms-2025/
t777-25e.pdf`, pages 1 to 3; no .txt is published). Five datasets, one for each figure the
form prints:
- `ca/t777_meals_rate`: line 4 "Food, beverages, and entertainment expenses × 50% = 8523", a rate
  of 0.5 on the amount entered (the product rounds half-up to the cent, the owner's decision, as the
  form states no rounding rule);
- `ca/t777_tradespersons_tools_maximum`: line 9 "Tradesperson's tools expenses (maximum
  $1,000)", the amount of $1,000;
- `ca/t777_vehicle_rounding`: line 30 "Line 20 multiplied by line 29. Employment-use portion", a
  dollars-and-cents box, rounded half-up to the cent once (the quotient of line 18 over line 19 is
  not rounded on its own);
- `ca/t777_relocation_income_rate`: line 38 "Employment income earned as an eligible tradesperson in
  the year at the temporary work location × 50%", a rate of 0.5;
- `ca/t777_relocation_maximum`: line 39 "(maximum $4,000)", the amount of $4,000 for each copy;
- `ca/t777_line_11_maximum`: line 11 and line 41 "Total labour mobility deduction for the year
  (maximum $4,000)", the claimed amount of $4,000 for the year (the `credit` kind).
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T777_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t777/t777-25e.pdf"
MEALS_RATE = "ca/t777_meals_rate"
TOOLS_MAXIMUM = "ca/t777_tradespersons_tools_maximum"
VEHICLE_ROUNDING = "ca/t777_vehicle_rounding"
RELOCATION_INCOME_RATE = "ca/t777_relocation_income_rate"
RELOCATION_MAXIMUM = "ca/t777_relocation_maximum"
LINE_11_MAXIMUM = "ca/t777_line_11_maximum"

# Made up for this test and not registered: the base and the figure a rate produces.
BASE = ArtifactKind("ex/base", Decimal)
OUTPUT = ArtifactKind("ex/output", Decimal)


def test_2025_meals_rate_is_fifty_percent_rounded_to_the_cent() -> None:
    data = SOURCE.get(MEALS_RATE, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    assert data.rounding == CENT
    assert T777_PDF in data.sources


def test_line_4_is_fifty_percent_of_the_food_entered_so_400_is_200() -> None:
    # Acceptance: food of 400 gives line 4 of 200.00.
    capability = ApplyRate(SOURCE.get(MEALS_RATE, 2025, RATE), BASE, OUTPUT)

    result = capability.compute((Artifact(BASE, D("400")),))

    assert result.outputs == (Artifact(OUTPUT, D("200.00")),)


def test_2025_tradespersons_tools_maximum_is_1000_rounded_to_the_cent() -> None:
    data = SOURCE.get(TOOLS_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("1000"))
    assert data.rounding == CENT
    assert T777_PDF in data.sources


def test_2025_vehicle_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(VEHICLE_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.rounding == CENT
    assert T777_PDF in data.sources


def test_2025_relocation_income_rate_is_fifty_percent_rounded_to_the_cent() -> None:
    data = SOURCE.get(RELOCATION_INCOME_RATE, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    assert data.rounding == CENT
    assert T777_PDF in data.sources


def test_line_38_is_fifty_percent_of_the_tradesperson_income_so_6000_is_3000() -> None:
    # Acceptance: employment income of 6,000 from an eligible tradesperson gives line 38 of
    # 3,000.00.
    capability = ApplyRate(SOURCE.get(RELOCATION_INCOME_RATE, 2025, RATE), BASE, OUTPUT)

    result = capability.compute((Artifact(BASE, D("6000")),))

    assert result.outputs == (Artifact(OUTPUT, D("3000.00")),)


def test_2025_relocation_maximum_is_4000_rounded_to_the_cent() -> None:
    data = SOURCE.get(RELOCATION_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("4000"))
    assert data.rounding == CENT
    assert T777_PDF in data.sources


def test_2025_line_11_maximum_is_4000_rounded_to_the_cent() -> None:
    data = SOURCE.get(LINE_11_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(D("4000"))
    assert data.rounding == CENT
    assert T777_PDF in data.sources


def test_the_two_fifty_percent_rates_are_the_same_printed_rate_in_their_own_datasets() -> None:
    # Each rate is its own dataset of this form (line 4 and line 38), both at the printed 50%.
    assert SOURCE.get(MEALS_RATE, 2025, RATE).values == Rate(D("0.5"))
    assert SOURCE.get(RELOCATION_INCOME_RATE, 2025, RATE).values == Rate(D("0.5"))
    assert MEALS_RATE != RELOCATION_INCOME_RATE

"""The 2025 Ontario disability amount for self, checked against CRA's forms.

Ontario: Form ON428 (form 5006-C) line 29 and line 58440 "Disability amount for self (claim $10,298
or, if you were under 18 years of age, use Worksheet ON428)". Worksheet ON428 (form 5006-D),
"Line 58440 - Disability amount for self": "Complete the following calculation if you were under
18 years of age on December 31, 2025": line 1 "Base amount 10,298.00"; line 2 "Maximum amount
6,007.00"; line 4 "Threshold for child and attendant care expenses 3,518.00"; line 7 "Line 1 plus
line 6 Enter this amount on line 58440 of your Form ON428. (maximum $16,305) =". The three figures
are kind `credit`, as core/credit_amount reads them, and the worksheet's lines are
dollars-and-cents boxes, so each is rounded half-up to the cent, the owner's decision, as the form
states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASE = "ca-on/disability_self_base_amount"
SUPPLEMENT_MAXIMUM = "ca-on/disability_self_supplement_maximum"
CARE_THRESHOLD = "ca-on/disability_self_care_threshold"
D5006D_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_base_amount_is_10298() -> None:
    data = SOURCE.get(BASE, 2025, CREDIT)

    assert data.values == Credit(amount=D("10298.00"))
    # Worksheet ON428 line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_maximum_amount_is_6007() -> None:
    data = SOURCE.get(SUPPLEMENT_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("6007.00"))
    # Worksheet ON428 line 2, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_care_threshold_is_3518() -> None:
    data = SOURCE.get(CARE_THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("3518.00"))
    # Worksheet ON428 line 4, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(BASE, 2025, CREDIT).sources == (D5006D_TEXT,)
    assert SOURCE.get(SUPPLEMENT_MAXIMUM, 2025, CREDIT).sources == (D5006D_TEXT,)
    assert SOURCE.get(CARE_THRESHOLD, 2025, CREDIT).sources == (D5006D_TEXT,)

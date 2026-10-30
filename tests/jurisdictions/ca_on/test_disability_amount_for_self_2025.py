"""The 2025 disability amount for self, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 99 (line 31600) "Disability amount for self (if you were under
18 years of age, use Federal Worksheet; if not, claim $10,138)". Federal Worksheet (form 5000-D1),
"Line 31600 - Disability amount for self": "If you qualify for the disability amount and, on
December 31, 2025, you were: 18 years of age or older, enter $10,138 on line 31600 of your return;
under 18 years of age, complete the calculation below". Line 1 "Base amount 10,138.00"; line 2
"Maximum supplement 5,914.00"; line 4 "Threshold for child care and attendant care expenses
3,464.00"; line 7 "Line 1 plus line 6 Enter this amount on line 31600 of your return. (maximum
$16,052)". The three figures are kind `credit`, as core/credit_amount reads them (the dataset
kind of the age amount's maximum), and the worksheet's lines are dollars-and-cents boxes, so each
is rounded half-up to the cent, the owner's decision, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
BASE = "ca/disability_self_base_amount"
SUPPLEMENT_MAXIMUM = "ca/disability_self_supplement_maximum"
CARE_THRESHOLD = "ca/disability_self_care_threshold"
D1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_base_amount_is_10138() -> None:
    data = SOURCE.get(BASE, 2025, CREDIT)

    assert data.values == Credit(amount=D("10138.00"))
    # Federal Worksheet line 1, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_maximum_supplement_is_5914() -> None:
    data = SOURCE.get(SUPPLEMENT_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("5914.00"))
    # Federal Worksheet line 2, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_care_threshold_is_3464() -> None:
    data = SOURCE.get(CARE_THRESHOLD, 2025, CREDIT)

    assert data.values == Credit(amount=D("3464.00"))
    # Federal Worksheet line 4, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(BASE, 2025, CREDIT).sources == (D1_TEXT,)
    assert SOURCE.get(SUPPLEMENT_MAXIMUM, 2025, CREDIT).sources == (D1_TEXT,)
    assert SOURCE.get(CARE_THRESHOLD, 2025, CREDIT).sources == (D1_TEXT,)

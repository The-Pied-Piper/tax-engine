"""The 2025 Ontario disability amount transferred from a dependant, checked against CRA's forms.

Ontario: 2025 ON428 (form 5006-C) line 30 and line 58480 "Disability amount transferred from a
dependant (use Worksheet ON428)". Worksheet ON428 (form 5006-D), "Line 58480 - Disability amount
transferred from a dependant": "Complete this calculation for each dependant."; line 1 "Base amount
10,298.00"; line 2 "Maximum amount 6,007.00"; line 4 "Threshold for child and attendant care
expenses 3,518.00"; line 7 "Line 1 plus line 6 (maximum $16,305) ="; line 8 "Enter the amount from
line 28 of the dependant's Form ON428."; line 12 "Enter whichever is less: amount from line 7 or
line 11. Allowable amount for this dependant"; "Enter the total of allowable amounts claimed for
all dependants on line 58480 of your Form ON428.". The four figures are plain amounts (the `amount`
kind: none is a claimed credit, each is combined with the dependant's own figures), and the
worksheet's lines are dollars-and-cents boxes, so each is rounded half-up to the cent, line 12 once
with the maximum's rule.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.catalog import (
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
)
from tax_calculator.jurisdictions.ca_on.capabilities.disability_transfer_amount import (
    OntarioDisabilityTransferAmount,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    DEPENDANT_ON428_LINE_28,
    DISABILITY_DEPENDANTS,
    DISABILITY_TRANSFERRED_AMOUNT,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASE = "ca-on/disability_transfer_base_amount"
SUPPLEMENT = "ca-on/disability_transfer_supplement_maximum"
THRESHOLD = "ca-on/disability_transfer_care_threshold"
MAXIMUM = "ca-on/disability_transfer_maximum"
WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_base_amount_is_10298() -> None:
    data = SOURCE.get(BASE, 2025, AMOUNT)

    assert data.values == Amount(D("10298.00"))
    # Worksheet ON428 line 1 is printed "Base amount 10,298.00"; line 12 is a dollars-and-cents
    # box.
    assert data.rounding == CENT


def test_2025_maximum_amount_is_6007() -> None:
    data = SOURCE.get(SUPPLEMENT, 2025, AMOUNT)

    assert data.values == Amount(D("6007.00"))
    # Worksheet ON428 line 2 is printed "Maximum amount 6,007.00".
    assert data.rounding == CENT


def test_2025_care_expenses_threshold_is_3518() -> None:
    data = SOURCE.get(THRESHOLD, 2025, AMOUNT)

    assert data.values == Amount(D("3518.00"))
    # Worksheet ON428 line 4 is printed "Threshold for child and attendant care expenses
    # 3,518.00".
    assert data.rounding == CENT


def test_2025_maximum_is_16305() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("16305"))
    # Worksheet ON428 line 7 "Line 1 plus line 6 (maximum $16,305)", a dollars-and-cents box:
    # half-up to the cent.
    assert data.rounding == CENT


def test_2025_base_plus_the_maximum_amount_is_the_maximum() -> None:
    base = SOURCE.get(BASE, 2025, AMOUNT).values.value
    supplement = SOURCE.get(SUPPLEMENT, 2025, AMOUNT).values.value
    maximum = SOURCE.get(MAXIMUM, 2025, AMOUNT).values.value

    assert base + supplement == maximum


@pytest.mark.parametrize("family", [BASE, SUPPLEMENT, THRESHOLD, MAXIMUM])
def test_2025_datasets_cite_only_their_form_text(family: str) -> None:
    assert SOURCE.get(family, 2025, AMOUNT).sources == (WORKSHEET_TEXT,)


def transferred(*dependants: tuple[int, str, str, str]) -> Decimal:
    """Line 58480 for dependants of these figures (under 18, line 3, line 8, line 10), from the
    registered 2025 datasets."""
    capability = OntarioDisabilityTransferAmount(
        SOURCE.get(BASE, 2025, AMOUNT),
        SOURCE.get(SUPPLEMENT, 2025, AMOUNT),
        SOURCE.get(THRESHOLD, 2025, AMOUNT),
        SOURCE.get(MAXIMUM, 2025, AMOUNT),
        DISABILITY_DEPENDANTS,
        DISABILITY_TRANSFERRED_AMOUNT,
    )
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            DEPENDANT_UNDER_18: under_18,
            DEPENDANT_CARE_EXPENSES: D(care),
            DEPENDANT_ON428_LINE_28: D(line_28),
            DEPENDANT_TAXABLE_INCOME: D(taxable),
        }
        for under_18, care, line_28, taxable in dependants
    ]
    given = Artifact(DISABILITY_DEPENDANTS, RecordList(DISABILITY_DEPENDANTS.fields, records))

    (output,) = capability.compute((given,)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("dependant", "allowable"),
    [
        # Aged 20, line 28 of their ON428 15,000 (a chosen figure), taxable income 20,000: line 9
        # = 10,298.00 + 15,000 = 25,298.00; line 11 = 25,298.00 - 20,000 = 5,298.00, under line 7.
        ((0, "0", "15000", "20000"), "5298.00"),
        # Aged 18 or older ignores the care expenses (line 6 is "0"): line 7 is 10,298.00.
        ((0, "5000", "0", "0"), "10298.00"),
        # Under 18 with no care expenses: line 7 = 10,298.00 + 6,007.00 = 16,305.00, the maximum.
        ((1, "0", "0", "0"), "16305.00"),
        # Care expenses at the threshold, 3,518.00: line 5 is 0, the whole line 2 amount.
        ((1, "3518", "0", "0"), "16305.00"),
        # Care expenses of 5,000: line 5 = 1,482.00; line 6 = 4,525.00; line 7 = 14,823.00.
        ((1, "5000", "0", "0"), "14823.00"),
        # Care expenses of 9,525 use up line 2: line 6 is 0, line 7 is the base.
        ((1, "9525", "0", "0"), "10298.00"),
        # Care expenses above that: line 6 is "0", never negative.
        ((1, "20000", "0", "0"), "10298.00"),
        # Taxable income above line 9: line 11 is "0".
        ((0, "0", "0", "20000"), "0"),
        # Line 11 above line 7: line 12 is line 7.
        ((0, "0", "15000", "0"), "10298.00"),
        # Cents count: line 11 = 10,298.00 + 0 - 10,297.99 = 0.01.
        ((0, "0", "0", "10297.99"), "0.01"),
        # A sub-cent taxable income rounds half-up at line 12: 5,297.995 -> 5,298.00.
        ((0, "0", "15000", "20000.005"), "5298.00"),
    ],
)
def test_the_allowable_amount_for_one_dependant(
    dependant: tuple[int, str, str, str], allowable: str
) -> None:
    assert transferred(dependant) == D(allowable)


def test_the_total_is_the_sum_of_the_allowable_amounts() -> None:
    # 5,298.00 (aged 20) + 14,823.00 (under 18 with care expenses of 5,000).
    assert transferred((0, "0", "15000", "20000"), (1, "5000", "0", "0")) == D("20121.00")


def test_no_dependants_give_zero() -> None:
    assert transferred() == D("0")

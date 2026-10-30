"""The 2025 disability amount transferred from a dependant, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 100 (line 31800) "Disability amount transferred from a
dependant (use Federal Worksheet)". Federal Worksheet (form 5000-D1), "Line 31800 - Disability
amount transferred from a dependant", completed for each dependant who is eligible for the
disability tax credit: line 1 "Base amount 10,138.00"; line 2 "Maximum supplement 5,914.00"; line 4
"Threshold for child care and attendant care expenses 3,464.00"; line 8 "Line 1 plus line 7
(maximum $16,052)"; line 13 "Enter whichever is less: amount from line 8 or line 12. Allowable
amount for this dependant"; "Enter the total of allowable amounts claimed for all dependants who
qualify for the disability tax credit on line 31800 of your return.". The four figures are plain
amounts (the `amount` kind: none is a claimed credit, each is combined with the dependant's own
figures), and the worksheet's lines are dollars-and-cents boxes, so each is rounded half-up to the
cent, line 13 once with the maximum's rule.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.disability_transfer_amount import (
    DisabilityTransferAmount,
)
from tax_engine.jurisdictions.ca.catalog import (
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_CREDIT_AMOUNTS,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
    DISABILITY_DEPENDANTS,
    DISABILITY_TRANSFERRED_AMOUNT,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
BASE = "ca/disability_transfer_base_amount"
SUPPLEMENT = "ca/disability_transfer_supplement_maximum"
THRESHOLD = "ca/disability_transfer_care_threshold"
MAXIMUM = "ca/disability_transfer_maximum"
D1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_base_amount_is_10138() -> None:
    data = SOURCE.get(BASE, 2025, AMOUNT)

    assert data.values == Amount(D("10138.00"))
    # Worksheet line 1 is printed "Base amount 10,138.00"; line 13 is a dollars-and-cents box.
    assert data.rounding == CENT


def test_2025_maximum_supplement_is_5914() -> None:
    data = SOURCE.get(SUPPLEMENT, 2025, AMOUNT)

    assert data.values == Amount(D("5914.00"))
    # Worksheet line 2 is printed "Maximum supplement 5,914.00".
    assert data.rounding == CENT


def test_2025_care_expenses_threshold_is_3464() -> None:
    data = SOURCE.get(THRESHOLD, 2025, AMOUNT)

    assert data.values == Amount(D("3464.00"))
    # Worksheet line 4 is printed "Threshold for child care and attendant care expenses 3,464.00".
    assert data.rounding == CENT


def test_2025_maximum_is_16052() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("16052"))
    # Worksheet line 8 "Line 1 plus line 7 (maximum $16,052)", a dollars-and-cents box: half-up
    # to the cent.
    assert data.rounding == CENT


def test_2025_base_plus_the_maximum_supplement_is_the_maximum() -> None:
    base = SOURCE.get(BASE, 2025, AMOUNT).values.value
    supplement = SOURCE.get(SUPPLEMENT, 2025, AMOUNT).values.value
    maximum = SOURCE.get(MAXIMUM, 2025, AMOUNT).values.value

    assert base + supplement == maximum


@pytest.mark.parametrize("family", [BASE, SUPPLEMENT, THRESHOLD, MAXIMUM])
def test_2025_datasets_cite_only_their_form_text(family: str) -> None:
    assert SOURCE.get(family, 2025, AMOUNT).sources == (D1_TEXT,)


def transferred(*dependants: tuple[int, str, str, str]) -> Decimal:
    """Line 31800 for dependants of these figures (under 18, line 3, line 9, line 11), from the
    registered 2025 datasets."""
    capability = DisabilityTransferAmount(
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
            DEPENDANT_CREDIT_AMOUNTS: D(credits),
            DEPENDANT_TAXABLE_INCOME: D(taxable),
        }
        for under_18, care, credits, taxable in dependants
    ]
    given = Artifact(DISABILITY_DEPENDANTS, RecordList(DISABILITY_DEPENDANTS.fields, records))

    (output,) = capability.compute((given,)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("dependant", "allowable"),
    [
        # The ticket's worked example: aged 20, line 98 of their return 16,129, taxable income
        # 20,000: line 12 = 10,138.00 + 16,129 - 20,000 = 6,267.00, under line 8.
        ((0, "0", "16129", "20000"), "6267.00"),
        # Aged 18 or older ignores the care expenses (line 7 is "0"): line 8 is 10,138.00.
        ((0, "5000", "0", "0"), "10138.00"),
        # Under 18 with no care expenses: line 8 = 10,138.00 + 5,914.00 = 16,052.00, the maximum.
        ((1, "0", "0", "0"), "16052.00"),
        # Care expenses at the threshold, 3,464.00: line 5 is 0, the whole supplement.
        ((1, "3464", "0", "0"), "16052.00"),
        # Care expenses of 5,000: line 5 = 1,536.00; line 6 = 4,378.00; line 8 = 14,516.00.
        ((1, "5000", "0", "0"), "14516.00"),
        # Care expenses of 9,378 use up the supplement: line 6 is 0, line 8 is the base.
        ((1, "9378", "0", "0"), "10138.00"),
        # Care expenses above that: line 6 is "0", never negative.
        ((1, "20000", "0", "0"), "10138.00"),
        # Taxable income above line 10: line 12 is "0".
        ((0, "0", "0", "20000"), "0"),
        # Line 12 above line 8: line 13 is line 8.
        ((0, "0", "16129", "0"), "10138.00"),
        # Cents count: line 12 = 10,138.00 + 0 - 10,137.99 = 0.01.
        ((0, "0", "0", "10137.99"), "0.01"),
        # A sub-cent taxable income rounds half-up at line 13: 6,266.995 -> 6,267.00.
        ((0, "0", "16129", "20000.005"), "6267.00"),
    ],
)
def test_the_allowable_amount_for_one_dependant(
    dependant: tuple[int, str, str, str], allowable: str
) -> None:
    assert transferred(dependant) == D(allowable)


def test_the_total_is_the_sum_of_the_allowable_amounts() -> None:
    # 6,267.00 (aged 20) + 14,516.00 (under 18 with care expenses of 5,000).
    assert transferred((0, "0", "16129", "20000"), (1, "5000", "0", "0")) == D("20783.00")


def test_no_dependants_give_zero() -> None:
    assert transferred() == D("0")

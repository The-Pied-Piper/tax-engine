"""The 2025 Canada caregiver amount for other infirm dependants, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 82 (line 30450) "Canada caregiver amount for other infirm
dependants age 18 or older (complete Schedule 5)". Schedule 5 (form 5000-S5), "Line 30450 -
Canada caregiver amount for other infirm dependants age 18 or older": "Complete the chart below
for each dependant who meets the conditions above."; line 1 "Base amount 28,798.00"; line 2
"Infirm dependant's net income from line 23600 of their return"; "Allowable amount for this
dependant:" line 3 "Line 1 minus line 2 (if negative, enter "0") (maximum $8,601) ="; "Enter on
line 30450 of your return the total of allowable amounts claimed for all dependants.". The base
and the maximum are both plain amounts (the `amount` kind: the base is not a claimed credit, it is
reduced by the dependant's net income), and line 3 is a dollars-and-cents box, so each is rounded
half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.caregiver_amount import CaregiverAmount
from tax_calculator.jurisdictions.ca.catalog import (
    CAREGIVER_AMOUNT,
    DEPENDANT_NET_INCOME,
    INFIRM_DEPENDANTS,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASE = "ca/caregiver_base_amount"
MAXIMUM = "ca/caregiver_maximum_amount"
S5_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s5/5000-s5-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_base_amount_is_28798() -> None:
    data = SOURCE.get(BASE, 2025, AMOUNT)

    assert data.values == Amount(D("28798.00"))
    # Schedule 5 line 1 is printed "Base amount 28,798.00"; line 3 is a dollars-and-cents box.
    assert data.rounding == CENT


def test_2025_maximum_amount_is_8601() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("8601"))
    # Schedule 5 line 3 "(maximum $8,601)", a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(BASE, 2025, AMOUNT).sources == (S5_TEXT,)
    assert SOURCE.get(MAXIMUM, 2025, AMOUNT).sources == (S5_TEXT,)


def claimed(*net_incomes: str) -> Decimal:
    """Line 30450 for dependants of these net incomes, from the registered 2025 datasets."""
    capability = CaregiverAmount(
        SOURCE.get(BASE, 2025, AMOUNT),
        SOURCE.get(MAXIMUM, 2025, AMOUNT),
        INFIRM_DEPENDANTS,
        CAREGIVER_AMOUNT,
    )
    dependants = RecordList(
        INFIRM_DEPENDANTS.fields, [{DEPENDANT_NET_INCOME: D(income)} for income in net_incomes]
    )

    (output,) = capability.compute((Artifact(INFIRM_DEPENDANTS, dependants),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("net_income", "allowable"),
    [
        # No income: the maximum, not the 28,798.00 base.
        ("0", "8601"),
        # 28,798.00 - 20,197 = 8,601.00: just reaches the maximum.
        ("20197", "8601"),
        # A dollar more income, a dollar less: 28,798.00 - 20,198 = 8,600.00.
        ("20198", "8600"),
        # Return Q's two dependants: 28,798.00 - 25,000 = 3,798.00.
        ("5000", "8601"),
        ("25000", "3798"),
        # Cents count: 28,798.00 - 28,797.99 = 0.01.
        ("28797.99", "0.01"),
        # At the base and above it: "less than $28,798" fails, line 3 is "0".
        ("28798", "0"),
        ("28798.01", "0"),
        ("90000", "0"),
    ],
)
def test_the_allowable_amount_for_one_dependant(net_income: str, allowable: str) -> None:
    assert claimed(net_income) == D(allowable)


def test_the_total_is_the_sum_of_the_allowable_amounts_not_the_pooled_figure() -> None:
    # 8,601 + 3,798.00 = 12,399.00; pooled, 28,798.00 - 30,000 is negative and gives 0.
    assert claimed("5000", "25000") == D("12399.00")

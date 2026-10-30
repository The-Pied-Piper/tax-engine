"""The 2025 Ontario caregiver amount, checked against CRA's forms.

Ontario: 2025 ON428 (form 5006-C) line 17 and line 58185 "Ontario caregiver amount (use Worksheet
ON428)". Worksheet ON428 (form 5006-D), "Line 58185 - Ontario caregiver amount": "Complete one
column for each dependant."; line 1 "Base amount" "26,562.00"; line 2 "Dependant's net income from
line 23600 of their return"; line 3 "Line 1 minus line 2 (if negative, enter "0") (maximum $6,008
per dependant)"; line 4 "Amount claimed for this dependant on line 58160 of your Form ON428, if
any"; line 5 "Allowable amount for this dependant: line 3 minus line 4 (if negative, enter "0")";
line 6 "Add the amounts from line 5 of columns 1, 2, and 3 (and others, if any). Enter this amount
on line 58185 of your Form ON428.". The base and the maximum are both plain amounts (the `amount`
kind: the base is not a claimed credit, it is reduced by the dependant's net income), and line 3 is
a dollars-and-cents box, so each is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.catalog import (
    DEPENDANT_NET_INCOME,
    ELIGIBLE_DEPENDANTS_CHECKED,
)
from tax_engine.jurisdictions.ca_on.capabilities.caregiver_amount import OntarioCaregiverAmount
from tax_engine.jurisdictions.ca_on.catalog import (
    CAREGIVER_AMOUNT,
    CAREGIVER_DEPENDANTS,
    CLAIMED_AS_ELIGIBLE_DEPENDANT,
    ELIGIBLE_DEPENDANT_AMOUNT,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
BASE = "ca-on/caregiver_base_amount"
MAXIMUM = "ca-on/caregiver_maximum_amount"
WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_base_amount_is_26562() -> None:
    data = SOURCE.get(BASE, 2025, AMOUNT)

    assert data.values == Amount(D("26562.00"))
    # Worksheet ON428 line 1 is printed "26,562.00"; line 3 is a dollars-and-cents box.
    assert data.rounding == CENT


def test_2025_maximum_amount_is_6008() -> None:
    data = SOURCE.get(MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("6008"))
    # Worksheet ON428 line 3 "(maximum $6,008 per dependant)", a dollars-and-cents box: half-up
    # to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(BASE, 2025, AMOUNT).sources == (WORKSHEET_TEXT,)
    assert SOURCE.get(MAXIMUM, 2025, AMOUNT).sources == (WORKSHEET_TEXT,)


def claimed(
    *dependants: tuple[str, int], eligible_dependant_amount: str = "0", eligible: int = 1
) -> Decimal:
    """Line 58185 for dependants of (net income, flag), from the registered 2025 datasets."""
    capability = OntarioCaregiverAmount(
        SOURCE.get(BASE, 2025, AMOUNT),
        SOURCE.get(MAXIMUM, 2025, AMOUNT),
        CAREGIVER_DEPENDANTS,
        ELIGIBLE_DEPENDANT_AMOUNT,
        ELIGIBLE_DEPENDANTS_CHECKED,
        CAREGIVER_AMOUNT,
    )
    records = RecordList(
        CAREGIVER_DEPENDANTS.fields,
        [
            {DEPENDANT_NET_INCOME: D(income), CLAIMED_AS_ELIGIBLE_DEPENDANT: flag}
            for income, flag in dependants
        ],
    )

    (output,) = capability.compute(
        (
            Artifact(CAREGIVER_DEPENDANTS, records),
            Artifact(ELIGIBLE_DEPENDANT_AMOUNT, D(eligible_dependant_amount)),
            Artifact(ELIGIBLE_DEPENDANTS_CHECKED, eligible),
        )
    ).outputs
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("net_income", "allowable"),
    [
        # No income: the maximum, not the 26,562.00 base.
        ("0", "6008"),
        # 26,562.00 - 20,554 = 6,008.00: just reaches the maximum.
        ("20554", "6008"),
        # A dollar more income, a dollar less: 26,562.00 - 20,555 = 6,007.00.
        ("20555", "6007"),
        # Return V's two dependants: 26,562.00 - 5,000 is over the maximum; 26,562.00 - 25,000 =
        # 1,562.00.
        ("5000", "6008"),
        ("25000", "1562"),
        # Cents count: 26,562.00 - 26,561.99 = 0.01.
        ("26561.99", "0.01"),
        # At the base and above it: "less than $26,562" fails, line 3 is "0".
        ("26562", "0"),
        ("26562.01", "0"),
        ("90000", "0"),
    ],
)
def test_the_allowable_amount_for_one_dependant(net_income: str, allowable: str) -> None:
    assert claimed((net_income, 0)) == D(allowable)


def test_the_total_is_the_sum_of_the_allowable_amounts_not_the_pooled_figure() -> None:
    # 6,008 + 1,562.00 = 7,570.00; pooled, 26,562.00 - 30,000 is negative and gives 0.
    assert claimed(("5000", 0), ("25000", 0)) == D("7570.00")


def test_the_claimed_dependant_takes_line_58160_off_line_3() -> None:
    # Line 3 is 6,008 for net income 5,000; line 4 is the 2,500.00 claimed on line 58160 for
    # this dependant; line 5 is 6,008 - 2,500.00 = 3,508.00. The other dependant takes line 4 of
    # 0 whatever line 58160 is: 1,562.00.
    assert claimed(("5000", 1), ("25000", 0), eligible_dependant_amount="2500.00") == D("5070.00")
    assert claimed(("5000", 0), ("25000", 1), eligible_dependant_amount="2500.00") == D("6008")

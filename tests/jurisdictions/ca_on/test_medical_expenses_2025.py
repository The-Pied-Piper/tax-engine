"""The 2025 medical expenses figures (T1 lines 108, 109 and 33199), checked against CRA's forms.

2025 T1, Ontario edition (form 5006-R), Step 5 Part B: "Line 107 and line 33099: Medical expenses
for self, spouse or common-law partner and your dependent children under 18 years of age"; "Line
108: Amount from line 23600" "multiplied by 3% ="; "Line 109: Enter whichever is less: $2,834 or
the amount from line 108."; "Line 110: Line 107 minus line 109 (if negative, enter "0") =". The
3% is a rate (the `rate` kind) and the $2,834 a plain cap (the `amount` kind). Line 108 is a
dollars-and-cents box, so each is rounded half-up to the cent.

Federal Worksheet (form 5000-D1), "Line 33199 - Allowable amount of medical expenses for other
dependants": "Complete one column for each dependant."; "Line 1: Medical expenses for other
dependant"; "Line 2: For provinces and territories other than Quebec: amount from line 109 of the
dependant's return."; "Line 3: Line 1 minus line 2 (if negative, enter "0")"; "Line 4: Add the
amounts from line 3 of columns 1, 2, and 3 (and others, if any). Enter this amount on line 33199
of your return." The dependant's line 109 is the lesser of $2,834 and 3% of that person's line
23600, so one `claim_reduction` dataset (rate 3%, ceiling 2,834, no maximum, the federal worksheet
printing none) gives line 2 from the dependant's net income.

The datasets are tested with the capabilities that read them, on made-up kinds for the T1 lines
and with the registered kinds for line 33199; the lines together, from the expenses paid to line
48200, are in the `end_to_end` tests and `returns/2025_return_x.yaml`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.claim_reduction import CLAIM_REDUCTION, ClaimReduction
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.other_dependants_medical import (
    OtherDependantsMedical,
)
from tax_engine.jurisdictions.ca.catalog import (
    DEPENDANT_NET_INCOME,
    OTHER_DEPENDANT_MEDICAL_EXPENSES,
    OTHER_DEPENDANTS,
    OTHER_DEPENDANTS_MEDICAL,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
RATE_FAMILY = "ca/medical_net_income_rate"
CEILING_FAMILY = "ca/medical_threshold_ceiling"
REDUCTION_FAMILY = "ca/other_dependants_medical_reduction"
T1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-r/5006-r-25e.txt"
D1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"

# Made up for this test and not registered: the net income (line 23600), the share of it on
# line 108 and the threshold of line 109.
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
SHARE = ArtifactKind("ex/share", Decimal)
THRESHOLD = ArtifactKind("ex/threshold", Decimal)
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_is_3_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.03"))
    # Line 108, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ceiling_is_2834() -> None:
    data = SOURCE.get(CEILING_FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("2834"))
    # Line 109, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_other_dependants_reduction_is_3_percent_at_most_2834_with_no_maximum() -> None:
    data = SOURCE.get(REDUCTION_FAMILY, 2025, CLAIM_REDUCTION)

    assert data.values == ClaimReduction(Rate(D("0.03")), D("2834"))
    assert data.values.maximum is None
    # Line 3 of the worksheet's column, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (T1_TEXT,)
    assert SOURCE.get(CEILING_FAMILY, 2025, AMOUNT).sources == (T1_TEXT,)
    assert SOURCE.get(REDUCTION_FAMILY, 2025, CLAIM_REDUCTION).sources == (D1_TEXT, T1_TEXT)


@pytest.mark.parametrize(
    ("net_income", "share"),
    [
        # Return X: 3% of 47555.00 = 1426.65.
        ("47555.00", "1426.65"),
        ("0", "0"),
        # 3% of 115000 = 3450.00.
        ("115000", "3450.00"),
        # 0.15 x 3% = 0.0045, rounded half-up to 0.00; 0.50 x 3% = 0.015, a tie, up to 0.02.
        ("0.15", "0.00"),
        ("0.50", "0.02"),
    ],
)
def test_line_108_is_3_percent_of_the_net_income(net_income: str, share: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), NET_INCOME, SHARE)

    result = capability.compute((Artifact(NET_INCOME, D(net_income)),))

    assert result.outputs == (Artifact(SHARE, D(share)),)


@pytest.mark.parametrize(
    ("share", "threshold"),
    [
        # Below the ceiling, the share itself.
        ("1426.65", "1426.65"),
        ("0", "0"),
        # At the ceiling, and a cent above it.
        ("2834", "2834"),
        ("2834.01", "2834"),
        # 3% of 115000.
        ("3450.00", "2834"),
    ],
)
def test_line_109_is_the_lesser_of_2834_and_line_108(share: str, threshold: str) -> None:
    capability = CappedAmount(SOURCE.get(CEILING_FAMILY, 2025, AMOUNT), SHARE, THRESHOLD)

    result = capability.compute((Artifact(SHARE, D(share)),))

    assert result.outputs == (Artifact(THRESHOLD, D(threshold)),)


def claimed(*dependants: tuple[str, str]) -> Decimal:
    """Line 33199 for dependants of these (expenses, net income), from the registered dataset."""
    capability = OtherDependantsMedical(
        SOURCE.get(REDUCTION_FAMILY, 2025, CLAIM_REDUCTION),
        OTHER_DEPENDANTS,
        OTHER_DEPENDANTS_MEDICAL,
    )
    records = RecordList(
        OTHER_DEPENDANTS.fields,
        [
            {OTHER_DEPENDANT_MEDICAL_EXPENSES: D(expenses), DEPENDANT_NET_INCOME: D(income)}
            for expenses, income in dependants
        ],
    )

    (output,) = capability.compute((Artifact(OTHER_DEPENDANTS, records),)).outputs
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("expenses", "net_income", "allowable"),
    [
        # Two dependants: 3000 - lesser(300.00, 2834) = 2700.00, and 1000 -
        # lesser(1200.00, 2834) is negative, so line 3 is "0".
        ("3000", "10000", "2700.00"),
        ("1000", "40000", "0"),
        # 3% of 94466.67 is 2834.0001, above the ceiling; 3% of 94466.66 is 2833.9998, rounded
        # half-up to 2834.00: either way 2834, so 5000 - 2834 = 2166.
        ("5000", "94466.67", "2166.00"),
        ("5000", "94466.66", "2166.00"),
        ("5000", "100000", "2166.00"),
        # No net income: the whole expenses.
        ("1000", "0", "1000"),
        # Cents count: 3% of 33333.33 is 999.9999, rounded half-up to 1000.00.
        ("1000.50", "33333.33", "0.50"),
        # Expenses equal to the reduction: nothing is left.
        ("300", "10000", "0"),
    ],
)
def test_line_3_of_one_dependants_column(expenses: str, net_income: str, allowable: str) -> None:
    assert claimed((expenses, net_income)) == D(allowable)


def test_line_4_is_the_sum_of_the_columns_not_the_pooled_figure() -> None:
    # 2700.00 + 0; pooled, 4000 - lesser(1500.00, 2834) = 2500.00.
    assert claimed(("3000", "10000"), ("1000", "40000")) == D("2700.00")
    assert claimed(("4000", "50000")) == D("2500.00")


def test_no_dependants_give_0_on_line_33199() -> None:
    assert claimed() == D("0")

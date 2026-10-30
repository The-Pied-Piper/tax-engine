"""The 2025 Ontario medical figures (ON428 lines 38, 40 and 58729), checked against CRA's forms.

2025 ON428 (form 5006-C): "Line 36 and line 58689: See line 58689 at canada.ca/on-tax-info for
maximum allowable amounts for attendant care, an adapted van, and moving expenses."; "Line 37:
Amount from line 23600 of your return"; "Line 38: Applicable rate 3%"; "Line 39: Line 37
multiplied by the percentage from line 38 ="; "Line 40: Enter whichever is less: $2,885 or the
amount on line 39."; "Line 41: Line 36 minus line 40 (if negative, enter "0") ="; "Line 42 and
line 58729: Allowable amount of medical expenses for other dependants (use Worksheet ON428)";
"Line 43 and line 58769: Line 41 plus line 42 =". The 3% is a rate (the `rate` kind) and the
$2,885 a plain cap (the `amount` kind). Line 39 is a dollars-and-cents box, so each is rounded
half-up to the cent.

Worksheet ON428 (form 5006-D), "Line 58729 - Allowable amount of medical expenses for other
dependants": "Complete one column for each dependant."; "Line 1: Medical expenses for other
dependant"; "Line 2: Enter the amount from line 40 of the dependant's Form ON428."; "Line 3: Line 1
minus line 2 (if negative, enter "0") (maximum $15,551 per dependant)"; "Line 4: Add the amounts
from line 3 of columns 1, 2, and 3 (and others, if any). Enter this amount on line 58729 of your
Form ON428." The dependant's line 40 is the lesser of $2,885 and 3% of that person's line 23600,
so one `claim_reduction` dataset (rate 3%, ceiling 2,885, maximum 15,551) gives line 2 from the
dependant's net income and line 3 its per-dependant maximum, which the federal dataset does not
have.

The datasets are tested with the capabilities that read them, on made-up kinds for the ON428
lines and with the registered kinds for line 58729; the lines together, from the expenses paid to
line 167, are in the `end_to_end` tests and `returns/2025_return_x.yaml`.
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
)
from tax_engine.jurisdictions.ca_on.catalog import OTHER_DEPENDANTS_MEDICAL

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
RATE_FAMILY = "ca-on/medical_net_income_rate"
CEILING_FAMILY = "ca-on/medical_threshold_ceiling"
REDUCTION_FAMILY = "ca-on/other_dependants_medical_reduction"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"
WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-d/5006-d-25e.txt"

# Made up for this test and not registered: the net income (line 37), the share of it on line 39
# and the threshold of line 40.
NET_INCOME = ArtifactKind("ex/net_income", Decimal)
SHARE = ArtifactKind("ex/share", Decimal)
THRESHOLD = ArtifactKind("ex/threshold", Decimal)
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_rate_is_3_percent() -> None:
    data = SOURCE.get(RATE_FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.03"))
    # Line 39, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_ceiling_is_2885() -> None:
    data = SOURCE.get(CEILING_FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("2885"))
    # Line 40, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_other_dependants_reduction_is_3_percent_at_most_2885_with_a_maximum_of_15551() -> (
    None
):
    data = SOURCE.get(REDUCTION_FAMILY, 2025, CLAIM_REDUCTION)

    assert data.values == ClaimReduction(Rate(D("0.03")), D("2885"), D("15551"))
    # Line 3 of the worksheet's column, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_the_ontario_reduction_has_a_maximum_the_federal_one_does_not() -> None:
    federal = SOURCE.get("ca/other_dependants_medical_reduction", 2025, CLAIM_REDUCTION)
    ontario = SOURCE.get(REDUCTION_FAMILY, 2025, CLAIM_REDUCTION)

    assert federal.values.maximum is None
    assert ontario.values.maximum == D("15551")


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(RATE_FAMILY, 2025, RATE).sources == (ON428_TEXT,)
    assert SOURCE.get(CEILING_FAMILY, 2025, AMOUNT).sources == (ON428_TEXT,)
    assert SOURCE.get(REDUCTION_FAMILY, 2025, CLAIM_REDUCTION).sources == (
        WORKSHEET_TEXT,
        ON428_TEXT,
    )


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
def test_line_39_is_3_percent_of_the_net_income(net_income: str, share: str) -> None:
    capability = ApplyRate(SOURCE.get(RATE_FAMILY, 2025, RATE), NET_INCOME, SHARE)

    result = capability.compute((Artifact(NET_INCOME, D(net_income)),))

    assert result.outputs == (Artifact(SHARE, D(share)),)


@pytest.mark.parametrize(
    ("share", "threshold"),
    [
        # Below the ceiling, the share itself.
        ("1426.65", "1426.65"),
        ("0", "0"),
        # Between the federal ceiling of 2834 and Ontario's 2885: the share itself.
        ("2850.00", "2850"),
        # At the ceiling, and a cent above it.
        ("2885", "2885"),
        ("2885.01", "2885"),
        # 3% of 115000.
        ("3450.00", "2885"),
    ],
)
def test_line_40_is_the_lesser_of_2885_and_line_39(share: str, threshold: str) -> None:
    capability = CappedAmount(SOURCE.get(CEILING_FAMILY, 2025, AMOUNT), SHARE, THRESHOLD)

    result = capability.compute((Artifact(SHARE, D(share)),))

    assert result.outputs == (Artifact(THRESHOLD, D(threshold)),)


def claimed(*dependants: tuple[str, str]) -> Decimal:
    """Line 58729 for dependants of these (expenses, net income), from the registered dataset."""
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
        # Return X's two dependants: 3000 - lesser(300.00, 2885) = 2700.00, and 1000 -
        # lesser(1200.00, 2885) is negative, so line 3 is "0".
        ("3000", "10000", "2700.00"),
        ("1000", "40000", "0"),
        # 3% of 96166.67 is 2885.0001, above the ceiling; 3% of 96166.66 is 2884.9998, rounded
        # half-up to 2885.00: either way 2885, so 5000 - 2885 = 2115.
        ("5000", "96166.67", "2115.00"),
        ("5000", "96166.66", "2115.00"),
        ("5000", "100000", "2115.00"),
        # No net income: the whole expenses.
        ("1000", "0", "1000"),
        # Cents count: 3% of 33333.33 is 999.9999, rounded half-up to 1000.00.
        ("1000.50", "33333.33", "0.50"),
        # Expenses equal to the reduction: nothing is left.
        ("300", "10000", "0"),
        # The maximum of 15551 per dependant: up to it the claim is whole, at it, the maximum,
        # above it, capped (the reduction is 300.00 at a net income of 10000).
        ("15851", "10000", "15551.00"),
        ("15850.99", "10000", "15550.99"),
        ("15851.01", "10000", "15551.00"),
        ("20000", "10000", "15551.00"),
        ("16000", "0", "15551.00"),
        ("15551", "0", "15551.00"),
        ("15551.01", "0", "15551.00"),
    ],
)
def test_line_3_of_one_dependants_column(expenses: str, net_income: str, allowable: str) -> None:
    assert claimed((expenses, net_income)) == D(allowable)


def test_the_maximum_is_for_each_dependant_not_for_the_total() -> None:
    # Two dependants at the maximum: 15551 + 15551, not capped at 15551 together.
    assert claimed(("20000", "0"), ("30000", "0")) == D("31102.00")
    # One at the maximum and one below it.
    assert claimed(("20000", "0"), ("1000", "0")) == D("16551.00")


def test_line_4_is_the_sum_of_the_columns_not_the_pooled_figure() -> None:
    # 2700.00 + 0; pooled, 4000 - lesser(1500.00, 2885) = 2500.00.
    assert claimed(("3000", "10000"), ("1000", "40000")) == D("2700.00")
    assert claimed(("4000", "50000")) == D("2500.00")


def test_no_dependants_give_0_on_line_58729() -> None:
    assert claimed() == D("0")

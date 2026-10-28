"""The 2025 FHSA datasets, checked against CRA's Schedule 15, FHSA Contributions, Transfers and
Activities.

Schedule 15 (form 5000-S15) Step 2: line 14 "8,000.00" and line 30 "8,000.00", the same printed
figure twice, so one dataset read by two steps; "If your maximum participation period (MPP) ended
in a prior year, do not complete this step. Your 2025 annual FHSA limit is "0". Enter "0" on line 40
and continue at Step 3.", the printed "0", a dataset of its own. Step 3: line 46 "Lifetime FHSA
limit 40,000.00". Each is a printed figure claimed whole (the `credit` kind, read by
`core/credit_amount`), rounded half-up to the cent, as every dollars-and-cents box on the forms is.

Each dataset is tested with the capability that reads it, on made-up kinds; the lines together,
from the T4FHSA slip boxes and the participation room statement to line 20805, are in
the `end_to_end` tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.choose_by_count import ChooseByCount
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
ANNUAL_AMOUNT = "ca/fhsa_annual_amount"
LIFETIME_LIMIT = "ca/fhsa_lifetime_limit"
ANNUAL_LIMIT_AFTER_MPP = "ca/fhsa_annual_limit_after_maximum_participation_period"
S15_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s15/5000-s15-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the amount a credit dataset gives, the count of
# maximum participation periods ended in a prior year (0 or 1) and the two annual limits it chooses
# between (Schedule 15 line 40).
CLAIMED = ArtifactKind("ex/claimed_amount", Decimal)
ENDED = ArtifactKind("ex/participation_period_ended", int)
COMPUTED_LIMIT = ArtifactKind("ex/computed_limit", Decimal)
ZERO_LIMIT = ArtifactKind("ex/zero_limit", Decimal)
CHOSEN_LIMIT = ArtifactKind("ex/chosen_limit", Decimal)


def test_2025_annual_amount_is_8000() -> None:
    data = SOURCE.get(ANNUAL_AMOUNT, 2025, CREDIT)

    # Schedule 15 line 14 "8,000.00" and line 30 "8,000.00": one dataset, read by two steps.
    assert data.values == Credit(amount=D("8000.00"))
    assert data.rounding == CENT


def test_2025_lifetime_limit_is_40000() -> None:
    data = SOURCE.get(LIFETIME_LIMIT, 2025, CREDIT)

    # Schedule 15 line 46 "Lifetime FHSA limit 40,000.00".
    assert data.values == Credit(amount=D("40000.00"))
    assert data.rounding == CENT


def test_2025_annual_limit_after_the_maximum_participation_period_is_0() -> None:
    data = SOURCE.get(ANNUAL_LIMIT_AFTER_MPP, 2025, CREDIT)

    # Step 2: "Your 2025 annual FHSA limit is "0". Enter "0" on line 40".
    assert data.values == Credit(amount=D("0"))
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_schedule_15_text() -> None:
    assert SOURCE.get(ANNUAL_AMOUNT, 2025, CREDIT).sources == (S15_TEXT,)
    assert SOURCE.get(LIFETIME_LIMIT, 2025, CREDIT).sources == (S15_TEXT,)
    assert SOURCE.get(ANNUAL_LIMIT_AFTER_MPP, 2025, CREDIT).sources == (S15_TEXT,)


@pytest.mark.parametrize(
    ("family", "amount"),
    [(ANNUAL_AMOUNT, "8000.00"), (LIFETIME_LIMIT, "40000.00"), (ANNUAL_LIMIT_AFTER_MPP, "0.00")],
)
def test_a_credit_dataset_is_claimed_whole(family: str, amount: str) -> None:
    capability = CreditAmount(SOURCE.get(family, 2025, CREDIT), CLAIMED)

    result = capability.compute(())

    assert result.outputs == (Artifact(CLAIMED, D(amount)),)


@pytest.mark.parametrize(
    ("ended", "annual_limit"),
    [
        # The maximum participation period has not ended: line 40 is Step 2's result.
        (0, "5500.00"),
        # It ended in a prior year: line 40 is the printed "0", whatever Step 2 would give.
        (1, "0.00"),
    ],
)
def test_the_printed_0_is_line_40_once_the_maximum_participation_period_has_ended(
    ended: int, annual_limit: str
) -> None:
    capability = ChooseByCount(ENDED, COMPUTED_LIMIT, ZERO_LIMIT, CHOSEN_LIMIT)
    zero = CreditAmount(SOURCE.get(ANNUAL_LIMIT_AFTER_MPP, 2025, CREDIT), ZERO_LIMIT).compute(())

    result = capability.compute(
        (Artifact(ENDED, ended), Artifact(COMPUTED_LIMIT, D("5500.00")), *zero.outputs)
    )

    assert result.outputs == (Artifact(CHOSEN_LIMIT, D(annual_limit)),)

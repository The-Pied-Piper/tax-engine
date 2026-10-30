"""The 2025 amounts for an eligible dependant and for infirm children, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 80 (line 30400) "Amount for an eligible dependant (complete
Schedule 5)" and line 83 (line 30500) "Canada caregiver amount for infirm children under 18
years of age (see Schedule 5) Number of children you are claiming this amount for Line 30499"
"multiplied by $2,687". Schedule 5 (form 5000-S5), "Line 30400 - Amount for an eligible
dependant": line 1 "Basic personal amount from line 30000 of your return"; line 2 "If you are
eligible for the Canada caregiver amount for your dependant (other than your infirm child under 18
years of age), enter $2,687"; line 3 "Line 1 plus line 2"; line 4 (51106) "Dependant's net
income from line 23600 of their return"; line 5 "Line 3 minus line 4 (if negative, enter "0")
Enter this amount on line 30400 of your return.". Line 30400 has no dataset of its own: it is the
filer's line 30000 amount plus line 2's $2,687 for an infirm eligible dependant 18 or older (a
dataset of its own, `ca/dependant_infirmity_amount`, as line 51100 prints the same figure), less
the dependant's net income, for each eligible dependant ("Each household is allowed only one claim
for this amount"). The $2,687 of line 30500 is a per-unit amount (the `amount` kind).

Ontario: 2025 ON428 (form 5006-C) line 14 "Base amount 11,905.00"; line 15 "Your eligible
dependant's net income from line 23600 of their return"; line 16 (line 58160) "Line 14 minus line
15 (if negative, enter "0") (maximum $10,823)". The base is a claimed amount (the `credit` kind,
as the basic reduction), the maximum a plain cap (the `amount` kind). Lines 30500, 14 and 16 are
dollars-and-cents boxes, so each is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
INFIRM_CHILD = "ca/infirm_child_amount"
ONTARIO_BASE = "ca-on/eligible_dependant_base"
ONTARIO_MAXIMUM = "ca-on/eligible_dependant_maximum"
DEPENDANT_INFIRMITY = "ca/dependant_infirmity_amount"
T1_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-r/5000-r-25e.txt"
S5_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s5/5000-s5-25e.txt"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the number of infirm children and their amount (line
# 30500), the Ontario base as an artifact (line 14), and the Ontario amount before its maximum
# and after it (line 16).
DEPENDANT_ELIGIBLE = ArtifactKind("ex/dependant_caregiver_eligible", int)
DEPENDANT_SUPPLEMENT = ArtifactKind("ex/dependant_infirmity_supplement", Decimal)
INFIRM_CHILDREN = ArtifactKind("ex/infirm_children", int)
INFIRM_AMOUNT = ArtifactKind("ex/infirm_children_amount", Decimal)
BASE = ArtifactKind("ex/base", Decimal)
BEFORE_MAXIMUM = ArtifactKind("ex/before_maximum", Decimal)
BEFORE_COUNT = ArtifactKind("ex/before_count", Decimal)


def test_2025_amount_per_infirm_child_is_2687() -> None:
    data = SOURCE.get(INFIRM_CHILD, 2025, AMOUNT)

    assert data.values == Amount(D("2687"))
    # T1 line 30500, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_for_an_infirm_dependant_18_or_older_is_2687() -> None:
    data = SOURCE.get(DEPENDANT_INFIRMITY, 2025, AMOUNT)

    assert data.values == Amount(D("2687"))
    # Schedule 5 line 2 (line 51100), a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_ontario_base_is_11905() -> None:
    data = SOURCE.get(ONTARIO_BASE, 2025, CREDIT)

    assert data.values == Credit(amount=D("11905.00"))
    # ON428 line 14, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_ontario_maximum_is_10823() -> None:
    data = SOURCE.get(ONTARIO_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("10823"))
    # ON428 line 16, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_datasets_cite_only_their_form_text() -> None:
    assert SOURCE.get(INFIRM_CHILD, 2025, AMOUNT).sources == (T1_TEXT,)
    assert SOURCE.get(DEPENDANT_INFIRMITY, 2025, AMOUNT).sources == (S5_TEXT,)
    assert SOURCE.get(ONTARIO_BASE, 2025, CREDIT).sources == (ON428_TEXT,)
    assert SOURCE.get(ONTARIO_MAXIMUM, 2025, AMOUNT).sources == (ON428_TEXT,)


@pytest.mark.parametrize(("eligible", "supplement"), [(0, "0"), (1, "2687.00")])
def test_the_dependant_supplement_is_2687_once_for_an_infirm_dependant_18_or_older(
    eligible: int, supplement: str
) -> None:
    capability = PerUnitAmount(
        SOURCE.get(DEPENDANT_INFIRMITY, 2025, AMOUNT), DEPENDANT_ELIGIBLE, DEPENDANT_SUPPLEMENT
    )

    result = capability.compute((Artifact(DEPENDANT_ELIGIBLE, eligible),))

    assert result.outputs == (Artifact(DEPENDANT_SUPPLEMENT, D(supplement)),)


@pytest.mark.parametrize(
    ("count", "amount"),
    [
        # Returns A to F: no infirm children.
        (0, "0"),
        (1, "2687"),
        (2, "5374"),
        (3, "8061"),
    ],
)
def test_2687_for_each_infirm_child(count: int, amount: str) -> None:
    capability = PerUnitAmount(
        SOURCE.get(INFIRM_CHILD, 2025, AMOUNT), INFIRM_CHILDREN, INFIRM_AMOUNT
    )

    result = capability.compute((Artifact(INFIRM_CHILDREN, count),))

    assert result.outputs == (Artifact(INFIRM_AMOUNT, D(amount)),)


def test_the_ontario_base_is_claimed_whole() -> None:
    capability = CreditAmount(SOURCE.get(ONTARIO_BASE, 2025, CREDIT), BASE)

    result = capability.compute(())

    assert result.outputs == (Artifact(BASE, D("11905.00")),)


@pytest.mark.parametrize(
    ("amount", "capped"),
    [
        # Return F: 11905.00 is above the maximum.
        ("11905.00", "10823"),
        # At the maximum, and a cent above it.
        ("10823", "10823"),
        ("10823.01", "10823"),
        # Below it, the amount itself, as for a dependant with 1500 of net income.
        ("10405.00", "10405.00"),
        # An amount past the cent is rounded half-up to it.
        ("10405.005", "10405.01"),
        ("0", "0"),
    ],
)
def test_the_ontario_amount_is_at_most_10823(amount: str, capped: str) -> None:
    capability = CappedAmount(
        SOURCE.get(ONTARIO_MAXIMUM, 2025, AMOUNT), BEFORE_MAXIMUM, BEFORE_COUNT
    )

    result = capability.compute((Artifact(BEFORE_MAXIMUM, D(amount)),))

    assert result.outputs == (Artifact(BEFORE_COUNT, D(capped)),)

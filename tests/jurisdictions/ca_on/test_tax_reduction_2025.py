"""The 2025 Ontario tax reduction amounts and factor, checked against CRA's ON428.

2025 ON428 (form 5006-C), Ontario tax reduction: line 74 "Basic reduction 294.00"; line 75 (line
60969) "Number of dependent children multiplied by $544"; line 76 (line 60970) "Number of
dependants multiplied by $544"; line 77 "Add lines 74 to 76."; line 78 "Amount from line 77 above
multiplied by 2"; line 79 "Amount from line 73 above"; line 80 "Line 78 minus line 79 (if negative,
enter "0") Ontario tax reduction". The basic reduction is a claimed amount (the `credit` kind, as
the basic personal amount), the $544 a per-unit amount (the `amount` kind) for both lines 75 and
76, and the 2 a factor (the `factor` kind), since a `rate` is at most 1. Lines 74, 75, 76 and 80
are dollars-and-cents boxes, so each is rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.capabilities.multiple_over import MultipleOver
from tax_calculator.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.factor import FACTOR, Factor
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
BASIC = "ca-on/tax_reduction_basic"
PER_DEPENDANT = "ca-on/tax_reduction_per_dependant"
FACTOR_FAMILY = "ca-on/tax_reduction_factor"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the basic reduction as an artifact, a count and its
# per-unit amount, the reduction amounts (line 77), the tax they are set against (line 73) and the
# reduction (line 80).
BASIC_REDUCTION = ArtifactKind("ex/basic_reduction", Decimal)
COUNT = ArtifactKind("ex/count", int)
COUNT_AMOUNT = ArtifactKind("ex/count_amount", Decimal)
AMOUNTS = ArtifactKind("ex/reduction_amounts", Decimal)
TAX = ArtifactKind("ex/tax", Decimal)
REDUCTION = ArtifactKind("ex/reduction", Decimal)


def test_2025_basic_reduction_is_294() -> None:
    data = SOURCE.get(BASIC, 2025, CREDIT)

    assert data.values == Credit(amount=D("294.00"))
    # ON428 line 74, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_per_dependant_is_544() -> None:
    data = SOURCE.get(PER_DEPENDANT, 2025, AMOUNT)

    assert data.values == Amount(D("544"))
    # ON428 lines 75 and 76, dollars-and-cents boxes: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_factor_is_2() -> None:
    data = SOURCE.get(FACTOR_FAMILY, 2025, FACTOR)

    assert data.values == Factor(D("2"))
    # ON428 line 80, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_datasets_cite_only_the_on428_text() -> None:
    assert SOURCE.get(BASIC, 2025, CREDIT).sources == (ON428_TEXT,)
    assert SOURCE.get(PER_DEPENDANT, 2025, AMOUNT).sources == (ON428_TEXT,)
    assert SOURCE.get(FACTOR_FAMILY, 2025, FACTOR).sources == (ON428_TEXT,)


def test_the_basic_reduction_is_claimed_whole() -> None:
    capability = CreditAmount(SOURCE.get(BASIC, 2025, CREDIT), BASIC_REDUCTION)

    result = capability.compute(())

    assert result.outputs == (Artifact(BASIC_REDUCTION, D("294.00")),)


@pytest.mark.parametrize(
    ("count", "amount"),
    [
        # Returns A, C, D and E: no dependent children and no dependants.
        (0, "0"),
        (1, "544"),
        (2, "1088"),
        (3, "1632"),
        (5, "2720"),
    ],
)
def test_544_for_each_dependent_child_or_dependant(count: int, amount: str) -> None:
    capability = PerUnitAmount(SOURCE.get(PER_DEPENDANT, 2025, AMOUNT), COUNT, COUNT_AMOUNT)

    result = capability.compute((Artifact(COUNT, count),))

    assert result.outputs == (Artifact(COUNT_AMOUNT, D(amount)),)


@pytest.mark.parametrize(
    ("amounts", "tax", "reduction"),
    [
        # Returns A, C, D and E: line 77 is the basic reduction alone, 294.00, so line 78 is
        # 588.00; each line 73 exceeds it, so line 80 is 0.
        ("294.00", "8195.77", "0"),
        ("294.00", "1700.15", "0"),
        ("294.00", "3750.97", "0"),
        ("294.00", "23570.20", "0"),
        # A tax below 588.00: the reduction is the difference.
        ("294.00", "486.80", "101.20"),
        # A tax past the cent: the difference is rounded half-up to the cent, 101.197675 to
        # 101.20, and 100.985, a tie, up to 100.99.
        ("294.00", "486.802325", "101.20"),
        ("294.00", "487.015", "100.99"),
        # At 588.00 nothing is left; with no tax the whole 588.00.
        ("294.00", "588.00", "0"),
        ("294.00", "0", "588.00"),
        # Five dependent children and three dependants: 294.00 + 2720 + 1632 = 4646.00, so line
        # 78 is 9292.00, above Return A's line 73.
        ("4646.00", "8195.77", "1096.23"),
    ],
)
def test_twice_the_reduction_amounts_over_the_tax(amounts: str, tax: str, reduction: str) -> None:
    capability = MultipleOver(SOURCE.get(FACTOR_FAMILY, 2025, FACTOR), AMOUNTS, TAX, REDUCTION)

    result = capability.compute((Artifact(AMOUNTS, D(amounts)), Artifact(TAX, D(tax))))

    assert result.outputs == (Artifact(REDUCTION, D(reduction)),)

"""A whole-cents amount kind: a value with a fraction of a cent is refused, not rounded."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactCatalog
from tax_engine.domain.errors import SubCentAmountError
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace

D = Decimal


def test_a_whole_cents_kind_refuses_a_fraction_of_a_cent_naming_the_kind_and_value() -> None:
    kind = AmountKind("ex/salary", whole_cents=True)

    with pytest.raises(SubCentAmountError, match=r"ex/salary.*70000\.004"):
        Artifact(kind, D("70000.004"))


@pytest.mark.parametrize("value", ["0.001", "1999.995", "-0.005", "1" + "0" * 40 + ".001"])
def test_a_whole_cents_kind_refuses_any_fraction_of_a_cent(value: str) -> None:
    with pytest.raises(SubCentAmountError):
        Artifact(AmountKind("ex/salary", whole_cents=True), D(value))


@pytest.mark.parametrize(
    "value",
    ["0", "70000", "1000.5", "1999.99", "70000.00", "1.230E+2", "1" + "0" * 40 + ".00", "0.0000"],
)
def test_a_whole_cents_kind_accepts_a_value_to_the_cent(value: str) -> None:
    assert Artifact(AmountKind("ex/salary", whole_cents=True), D(value)).value == D(value)


def test_a_kind_is_not_whole_cents_unless_declared() -> None:
    assert Artifact(AmountKind("ex/salary"), D("70000.004")).value == D("70000.004")


def test_a_catalog_declares_a_whole_cents_kind() -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = AmountKind.declare(catalog, "salary", whole_cents=True)

    assert kind.whole_cents is True
    with pytest.raises(SubCentAmountError):
        Artifact(kind, D("1.005"))

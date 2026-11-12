"""Unit tests for `Capability.MAY_BE_BLANK`: the produced slots whose output `compute` may return
blank (made-up `ex/` capabilities).

It names produced slots, defaults to none, is frozen at class definition and inherited unless
overridden. `run` accepts a blank output in such a slot and still raises CapabilityContractError
for a blank output in any other.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind, Money
from tax_engine.domain.blank import BLANK
from tax_engine.domain.capability import Capability, CapabilityResult
from tax_engine.domain.errors import CapabilityContractError, InvalidCapabilityError
from tax_engine.domain.kinds import AmountKind

D = Decimal

SOURCE = AmountKind("ex/source")
FIRST = AmountKind("ex/first_figure")
SECOND = AmountKind("ex/second_figure")


class TwoFigures(Capability):
    """Produces `first` and `second`, each the source; blank where `blank` names the slot."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"source": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"first": Decimal, "second": Decimal}
    blank: ClassVar[frozenset[str]] = frozenset()

    def __init__(self, source: Money, first: Money, second: Money) -> None:
        super().__init__(source=source, first=first, second=second)
        self._source, self._first, self._second = source, first, second

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self._source).value
        kinds: dict[str, ArtifactKind[Any]] = {"first": self._first, "second": self._second}
        outputs = tuple(
            Artifact(kind, BLANK if slot in self.blank else value) for slot, kind in kinds.items()
        )
        return CapabilityResult(outputs=outputs, trace=())


class FirstMayBeBlank(TwoFigures):
    MAY_BE_BLANK: ClassVar[frozenset[str]] = frozenset({"first"})
    blank = frozenset({"first"})


class BothBlankFirstAllowed(FirstMayBeBlank):
    blank = frozenset({"first", "second"})


class SecondBlank(TwoFigures):
    blank = frozenset({"second"})


def run(cls: type[TwoFigures]) -> CapabilityResult:
    return cls(SOURCE, FIRST, SECOND).run((Artifact(SOURCE, D(7)),))


# --- declaring it ------------------------------------------------------------------------------


def test_may_be_blank_is_empty_by_default() -> None:
    assert Capability.MAY_BE_BLANK == frozenset()
    assert TwoFigures.MAY_BE_BLANK == frozenset()


def test_a_subclass_inherits_its_parents_may_be_blank() -> None:
    class Child(FirstMayBeBlank):
        pass

    assert Child.MAY_BE_BLANK == frozenset({"first"})


def test_a_subclass_may_override_may_be_blank_and_a_plain_set_is_frozen() -> None:
    class Narrower(FirstMayBeBlank):
        MAY_BE_BLANK: ClassVar[frozenset[str]] = {"second"}  # type: ignore[assignment]

    assert Narrower.MAY_BE_BLANK == frozenset({"second"})
    assert isinstance(Narrower.MAY_BE_BLANK, frozenset)


@pytest.mark.parametrize("slot", ["source", "nowhere"])
def test_a_may_be_blank_slot_that_is_not_produced_is_refused(slot: str) -> None:
    with pytest.raises(InvalidCapabilityError, match=f"MAY_BE_BLANK slot '{slot}'"):

        class Bad(TwoFigures):
            MAY_BE_BLANK: ClassVar[frozenset[str]] = frozenset({slot})


def test_a_may_be_blank_that_is_not_a_set_is_refused() -> None:
    with pytest.raises(InvalidCapabilityError, match="MAY_BE_BLANK must be a set"):

        class Bad(TwoFigures):
            MAY_BE_BLANK: ClassVar[frozenset[str]] = 5  # type: ignore[assignment]


# --- run ---------------------------------------------------------------------------------------


def test_run_accepts_a_blank_output_in_a_may_be_blank_slot() -> None:
    result = run(FirstMayBeBlank)

    assert result.outputs == (Artifact(FIRST, BLANK), Artifact(SECOND, D(7)))
    assert result.outputs[0].is_blank


def test_run_still_refuses_a_blank_output_in_any_other_slot() -> None:
    with pytest.raises(CapabilityContractError, match="returned 'second_figure' blank"):
        run(SecondBlank)


def test_run_refuses_a_blank_output_in_a_slot_not_listed_even_when_another_is() -> None:
    class SecondOnlyBlank(FirstMayBeBlank):
        blank = frozenset({"second"})

    with pytest.raises(CapabilityContractError, match="returned 'second_figure' blank"):
        run(SecondOnlyBlank)


def test_run_names_only_the_slots_not_allowed_when_several_are_blank() -> None:
    with pytest.raises(CapabilityContractError) as raised:
        run(BothBlankFirstAllowed)

    assert "second_figure" in str(raised.value)
    assert "first_figure" not in str(raised.value)

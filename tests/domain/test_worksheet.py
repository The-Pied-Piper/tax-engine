"""Unit tests for the Worksheet: one filled-in copy of a form (design.md §3, §6).

The worksheet holds each capability to its contract when applying it: consumed
inputs must be present, outputs must match `produces`, and no artifact is overwritten.
"""

from __future__ import annotations

import decimal
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, assert_type, cast

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import Capability, CapabilityResult
from tax_calculator.domain.errors import (
    CapabilityContractError,
    DomainError,
    DuplicateArtifactError,
    MissingArtifactError,
)
from tax_calculator.domain.trace import TraceLine
from tax_calculator.domain.worksheet import Worksheet

D = Decimal
A = ArtifactKind("ex/a", Decimal)
B = ArtifactKind("ex/b", Decimal)
C = ArtifactKind("ex/c", Decimal)
SUM = ArtifactKind("ex/sum", Decimal)


@dataclass(frozen=True)
class DoubledLine(TraceLine):
    """A made-up trace line: the doubled value."""

    doubled: Decimal

    @property
    def amount(self) -> Decimal:
        return self.doubled


class Double(Capability):
    """Produces `out` = 2 × `inp`; `extra`, `skip` and `peek` let a test break the contract.

    Its slots are `inp` and `out`, passed to the base; the test hooks are not slots.
    """

    CONSUMES = {"inp": Decimal}
    PRODUCES = {"out": Decimal}

    def __init__(
        self,
        inp: Money,
        out: Money,
        extra: Money | None = None,
        skip: bool = False,
        peek: Money | None = None,
    ) -> None:
        super().__init__(inp=inp, out=out)
        self._inp, self._out, self._extra, self._skip, self._peek = inp, out, extra, skip, peek
        self.received: tuple[Artifact[Any], ...] = ()

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        self.received = inputs
        if self._peek is not None:
            self._input(inputs, self._peek)
        value = self._input(inputs, self._inp).value * 2
        outputs: tuple[Artifact[Any], ...] = () if self._skip else (Artifact(self._out, value),)
        if self._extra is not None:
            outputs += (Artifact(self._extra, value),)
        return CapabilityResult(outputs=outputs, trace=(DoubledLine(value),))


def test_holds_its_starting_artifacts() -> None:
    found = Worksheet(Artifact(A, D("2.5"))).get(A)

    assert_type(found, Artifact[Decimal])
    assert found == Artifact(A, D("2.5"))


def test_get_matches_by_kind_equality_not_identity() -> None:
    worksheet = Worksheet(Artifact(ArtifactKind("ex/a", Decimal), D(1)))

    assert worksheet.get(A) == Artifact(A, D(1))


def test_get_rejects_a_kind_it_holds_no_artifact_of() -> None:
    with pytest.raises(MissingArtifactError, match="'b'"):
        Worksheet(Artifact(A, D(1))).get(B)


def test_rejects_a_starting_value_that_is_not_an_artifact() -> None:
    with pytest.raises(TypeError, match="must be an Artifact, got Decimal"):
        Worksheet(cast(Any, D(1)))


def test_rejects_an_artifact_kind_given_as_a_starting_artifact() -> None:
    with pytest.raises(TypeError, match="must be an Artifact, got ArtifactKind"):
        Worksheet(cast(Any, A))


def test_rejects_two_starting_artifacts_of_one_kind() -> None:
    with pytest.raises(DuplicateArtifactError, match="'a'"):
        Worksheet(Artifact(A, D(1)), Artifact(A, D(2)))


def test_apply_records_the_outputs() -> None:
    worksheet = Worksheet(Artifact(A, D("2.5")))

    worksheet.apply(Double(A, B))

    assert worksheet.get(B) == Artifact(B, D("5.0"))


def test_apply_feeds_one_capability_into_the_next() -> None:
    worksheet = Worksheet(Artifact(A, D(1)))

    worksheet.apply(Double(A, B))
    worksheet.apply(Double(B, C))

    assert worksheet.get(C) == Artifact(C, D(4))


def test_apply_passes_only_what_the_capability_consumes() -> None:
    capability = Double(A, B)

    Worksheet(Artifact(A, D(1)), Artifact(C, D(9))).apply(capability)

    assert capability.received == (Artifact(A, D(1)),)


def test_apply_collects_the_trace_in_order() -> None:
    worksheet = Worksheet(Artifact(A, D(1)))

    worksheet.apply(Double(A, B))
    worksheet.apply(Double(B, C))

    assert worksheet.trace == (DoubledLine(D(2)), DoubledLine(D(4)))


def test_a_new_worksheet_has_no_trace() -> None:
    assert Worksheet(Artifact(A, D(1))).trace == ()


def test_records_the_producer_of_each_artifact() -> None:
    worksheet = Worksheet(Artifact(A, D(1)))
    capability = Double(A, B)

    worksheet.apply(capability)

    assert worksheet.producer_of(B) is capability


def test_starting_artifacts_have_no_producer() -> None:
    assert Worksheet(Artifact(A, D(1))).producer_of(A) is None


def test_producer_of_rejects_a_kind_it_holds_no_artifact_of() -> None:
    with pytest.raises(MissingArtifactError, match="'b'"):
        Worksheet(Artifact(A, D(1))).producer_of(B)


def test_apply_rejects_missing_input() -> None:
    with pytest.raises(MissingArtifactError, match="Double needs 'a'"):
        Worksheet(Artifact(C, D(1))).apply(Double(A, B))


class Add(Capability):
    """Produces `out` = `left` + `right`: a capability that consumes two kinds."""

    CONSUMES = {"left": Decimal, "right": Decimal}
    PRODUCES = {"out": Decimal}

    def __init__(self, left: Money, right: Money, out: Money) -> None:
        super().__init__(left=left, right=right, out=out)
        self._left, self._right, self._out = left, right, out

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self._left).value + self._input(inputs, self._right).value
        return CapabilityResult(outputs=(Artifact(self._out, value),), trace=(DoubledLine(value),))


def test_apply_names_every_missing_input_in_label_order() -> None:
    with pytest.raises(MissingArtifactError, match="Add needs 'a', 'b'"):
        Worksheet(Artifact(C, D(1))).apply(Add(B, A, SUM))


def test_apply_names_only_the_missing_inputs_among_present_ones() -> None:
    with pytest.raises(MissingArtifactError, match="Add needs 'b'$"):
        Worksheet(Artifact(A, D(1)), Artifact(C, D(1))).apply(Add(A, B, SUM))


def test_apply_with_every_input_present_records_the_output_and_trace() -> None:
    worksheet = Worksheet(Artifact(A, D(1)), Artifact(B, D(2)), Artifact(C, D(9)))

    worksheet.apply(Add(A, B, SUM))

    assert worksheet.get(SUM) == Artifact(SUM, D(3))
    assert worksheet.trace == (DoubledLine(D(3)),)


def test_apply_rejects_outputs_beyond_the_contract() -> None:
    with pytest.raises(CapabilityContractError, match="'c'"):
        Worksheet(Artifact(A, D(1))).apply(Double(A, B, extra=C))


def test_apply_rejects_outputs_short_of_the_contract() -> None:
    with pytest.raises(CapabilityContractError, match="'b'"):
        Worksheet(Artifact(A, D(1))).apply(Double(A, B, skip=True))


def test_apply_rejects_two_outputs_of_one_kind() -> None:
    with pytest.raises(DuplicateArtifactError, match="Double produced 'b' more than once"):
        Worksheet(Artifact(A, D(1))).apply(Double(A, B, extra=B))


def test_apply_records_nothing_when_the_contract_is_broken() -> None:
    worksheet = Worksheet(Artifact(A, D(1)))

    with pytest.raises(CapabilityContractError):
        worksheet.apply(Double(A, B, extra=C))

    with pytest.raises(MissingArtifactError):
        worksheet.get(B)
    assert worksheet.trace == ()


def test_apply_refuses_to_overwrite_an_artifact() -> None:
    worksheet = Worksheet(Artifact(A, D(1)), Artifact(B, D(7)))

    with pytest.raises(DuplicateArtifactError, match="'b'"):
        worksheet.apply(Double(A, B))

    assert worksheet.get(B) == Artifact(B, D(7))
    assert worksheet.producer_of(B) is None


def test_apply_rejects_an_output_that_is_not_an_artifact() -> None:
    class Plain(Double):
        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            return CapabilityResult(outputs=cast(Any, (D(2),)), trace=())

    with pytest.raises(TypeError, match="must be an Artifact, got Decimal"):
        Worksheet(Artifact(A, D(1))).apply(Plain(A, B))


def test_a_capability_cannot_read_what_it_does_not_consume() -> None:
    worksheet = Worksheet(Artifact(A, D(1)), Artifact(C, D(9)))

    with pytest.raises(CapabilityContractError, match="Double does not consume 'c'"):
        worksheet.apply(Double(A, B, peek=C))


def test_errors_are_domain_errors() -> None:
    assert issubclass(MissingArtifactError, DomainError)
    assert issubclass(CapabilityContractError, DomainError)
    assert issubclass(DuplicateArtifactError, DomainError)


# --- the Inexact trap -------------------------------------------------------------------------
#
# The worksheet applies every capability, whether through a composition or directly, so it runs
# each capability's compute under a decimal context that traps `decimal.Inexact`: arithmetic that
# would lose digits raises instead of being rounded to the context's 28 significant digits. The
# error is a `CapabilityContractError` naming the capability, chained from the `decimal.Inexact`.


class Multiply(Capability):
    """Produces `out` = `inp` × `factor`: a made-up capability whose product can need many digits"""

    CONSUMES = {"inp": Decimal}
    PRODUCES = {"out": Decimal}

    def __init__(self, inp: Money, out: Money, factor: Decimal) -> None:
        super().__init__(inp=inp, out=out)
        self._inp, self._out, self._factor = inp, out, factor

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self._inp).value * self._factor
        return CapabilityResult(outputs=(Artifact(self._out, value),), trace=(DoubledLine(value),))


# 15 digits × 15 digits is 29 digits, and 15 × 18 is 30 or more: a 28-digit context cannot hold it.
FIFTEEN_DIGITS = D("123456789012345")
EIGHTEEN_DIGITS = D("123456789012345678")


def test_apply_raises_when_a_capability_needs_more_digits_than_the_context_holds() -> None:
    worksheet = Worksheet(Artifact(A, FIFTEEN_DIGITS))

    with pytest.raises(CapabilityContractError):
        worksheet.apply(Multiply(A, B, EIGHTEEN_DIGITS))


def test_an_inexact_result_names_the_capability_and_says_it_was_inexact() -> None:
    worksheet = Worksheet(Artifact(A, FIFTEEN_DIGITS))

    with pytest.raises(CapabilityContractError, match=r"^Multiply .*inexact") as raised:
        worksheet.apply(Multiply(A, B, EIGHTEEN_DIGITS))

    assert isinstance(raised.value, DomainError)


def test_an_inexact_result_is_chained_from_decimal_inexact() -> None:
    worksheet = Worksheet(Artifact(A, FIFTEEN_DIGITS))

    with pytest.raises(CapabilityContractError) as raised:
        worksheet.apply(Multiply(A, B, EIGHTEEN_DIGITS))

    assert isinstance(raised.value.__cause__, decimal.Inexact)


def test_an_inexact_result_is_not_a_bare_decimal_inexact() -> None:
    worksheet = Worksheet(Artifact(A, FIFTEEN_DIGITS))

    with pytest.raises(CapabilityContractError) as raised:
        worksheet.apply(Multiply(A, B, EIGHTEEN_DIGITS))

    assert not isinstance(raised.value, decimal.Inexact)


def test_an_inexact_division_raises_too() -> None:
    class Third(Multiply):
        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            value = self._input(inputs, self._inp).value / 3
            return CapabilityResult(
                outputs=(Artifact(self._out, value),), trace=(DoubledLine(value),)
            )

    with pytest.raises(CapabilityContractError, match=r"^Third .*inexact"):
        Worksheet(Artifact(A, D(1))).apply(Third(A, B, D(1)))


def test_an_inexact_result_records_nothing() -> None:
    worksheet = Worksheet(Artifact(A, FIFTEEN_DIGITS))

    with pytest.raises(CapabilityContractError):
        worksheet.apply(Multiply(A, B, EIGHTEEN_DIGITS))

    with pytest.raises(MissingArtifactError):
        worksheet.get(B)
    assert worksheet.trace == ()


def test_apply_accepts_a_product_of_exactly_28_digits() -> None:
    worksheet = Worksheet(Artifact(A, D("99999999999999")))

    worksheet.apply(Multiply(A, B, D("99999999999999")))

    assert worksheet.get(B) == Artifact(B, D("9999999999999800000000000001"))


def test_apply_accepts_an_exact_product_with_a_short_expansion() -> None:
    worksheet = Worksheet(Artifact(A, D("2.5")))

    worksheet.apply(Multiply(A, B, D("0.5")))

    assert worksheet.get(B) == Artifact(B, D("1.25"))


def test_apply_leaves_the_callers_decimal_context_as_it_found_it() -> None:
    before = decimal.getcontext().copy()

    Worksheet(Artifact(A, D(1))).apply(Multiply(A, B, D(2)))
    with pytest.raises(CapabilityContractError):
        Worksheet(Artifact(A, FIFTEEN_DIGITS)).apply(Multiply(A, B, EIGHTEEN_DIGITS))

    after = decimal.getcontext()
    assert after.prec == before.prec
    assert after.rounding == before.rounding
    assert after.traps == before.traps
    assert not after.traps[decimal.Inexact]


def test_the_trap_is_off_again_after_apply_so_other_code_is_not_trapped() -> None:
    Worksheet(Artifact(A, D(1))).apply(Multiply(A, B, D(2)))

    assert D(1) / D(3) == D("0.3333333333333333333333333333")


def test_a_capability_that_rounds_through_a_rounding_rule_is_not_trapped() -> None:
    from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

    class Rounded(Multiply):
        def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
            value = RoundTo(D("0.01"), RoundingMode.HALF_UP).apply(
                self._input(inputs, self._inp).value
            )
            return CapabilityResult(
                outputs=(Artifact(self._out, value),), trace=(DoubledLine(value),)
            )

    worksheet = Worksheet(Artifact(A, D("0.1234567890123456789012345678901234")))

    worksheet.apply(Rounded(A, B, D(1)))

    assert worksheet.get(B) == Artifact(B, D("0.12"))

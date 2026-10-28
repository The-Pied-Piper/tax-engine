"""Unit tests for the Quotient capability (`ca-on/quotient`), with made-up kinds and values.

Worksheet ON479 line 8 is "Line 6 divided by line 7 =". The capability consumes a `dividend` and a
`divisor` money artifact and produces their exact quotient as `output`. It has no dataset and so
never rounds: the division is done as an exact fraction and written out with `NO_ROUNDING`, which
raises `decimal.Inexact` when the quotient has no finite decimal expansion. A zero divisor is
refused with a domain error naming both kinds. It records one `QuotientLine`.
"""

from __future__ import annotations

import decimal
from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType

import pytest

import tax_calculator.jurisdictions.ca_on
import tax_calculator.jurisdictions.ca_on.capabilities
import tax_calculator.registrations
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import DomainError, InvalidCapabilityError, MissingArtifactError
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.domain.trace import QuotientLine
from tax_calculator.jurisdictions.ca_on.capabilities.quotient import Quotient

D = Decimal

DIVIDEND = ArtifactKind("ex/dividend_amount", Decimal)
DIVISOR = ArtifactKind("ex/divisor_amount", Decimal)
OUTPUT = ArtifactKind("ex/quotient_amount", Decimal)


def capability() -> Quotient:
    return Quotient(dividend=DIVIDEND, divisor=DIVISOR, output=OUTPUT)


def inputs(dividend: str, divisor: str) -> tuple[Artifact[Decimal], Artifact[Decimal]]:
    return (Artifact(DIVIDEND, D(dividend)), Artifact(DIVISOR, D(divisor)))


def quotient_of(dividend: str, divisor: str) -> Decimal:
    (artifact,) = capability().compute(inputs(dividend, divisor)).outputs
    assert artifact.kind == OUTPUT
    value = artifact.value
    assert isinstance(value, Decimal)
    return value


def test_is_registered_as_ca_on_quotient() -> None:
    assert (
        tax_calculator.registrations.CORE_PACKAGES
    )  # importing registrations imports the packages

    assert CapabilityRegistry.shared().get("ca-on/quotient") is Quotient


def test_its_package_declares_the_ca_on_namespace_and_exports_the_module() -> None:
    package = tax_calculator.jurisdictions.ca_on.capabilities

    assert package.NAMESPACE == tax_calculator.jurisdictions.ca_on.NAMESPACE == "ca-on"
    assert "quotient" in package.__all__
    assert package.quotient.Quotient is Quotient


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({DIVIDEND, DIVISOR})
    assert capability().produces == frozenset({OUTPUT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(Quotient)
    assert "produces" not in vars(Quotient)


def test_declares_its_slots() -> None:
    assert Quotient.PARAMETERS == {}
    assert Quotient.CONSUMES == {"dividend": Decimal, "divisor": Decimal}
    assert Quotient.PRODUCES == {"output": Decimal}
    assert not Quotient.is_list_slot("dividend")
    assert not Quotient.is_list_slot("divisor")


def test_its_slots_are_read_only() -> None:
    for slots in (Quotient.PARAMETERS, Quotient.CONSUMES, Quotient.PRODUCES):
        assert isinstance(slots, MappingProxyType)
        assert isinstance(slots, Mapping)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        Quotient(DIVIDEND, DIVISOR, OUTPUT, object())  # type: ignore[call-arg]


def test_rejects_a_record_list_kind_for_its_dividend() -> None:
    other = RecordListKind("ex/not_money", fields=(DIVISOR,))

    with pytest.raises(InvalidCapabilityError, match="Quotient.*'dividend'"):
        Quotient(dividend=other, divisor=DIVISOR, output=OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_count_kind_for_its_divisor() -> None:
    other = ArtifactKind("ex/a_count", int)

    with pytest.raises(InvalidCapabilityError, match="Quotient.*'divisor'"):
        Quotient(dividend=DIVIDEND, divisor=other, output=OUTPUT)  # type: ignore[arg-type]


def test_rejects_a_count_kind_for_its_output() -> None:
    other = ArtifactKind("ex/a_count", int)

    with pytest.raises(InvalidCapabilityError, match="Quotient.*'output'"):
        Quotient(dividend=DIVIDEND, divisor=DIVISOR, output=other)  # type: ignore[arg-type]


def test_rejects_one_kind_for_both_the_dividend_and_the_divisor() -> None:
    with pytest.raises(InvalidCapabilityError, match="Quotient.*'dividend' and 'divisor'"):
        Quotient(dividend=DIVIDEND, divisor=DIVIDEND, output=OUTPUT)


# --- computing --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("dividend", "divisor", "quotient"),
    [
        # Worksheet ON479 line 8 for payroll of 500,000: (500,000 - 400,000) / 200,000.
        ("100000.00", "200000.00", "0.5"),
        ("0", "200000.00", "0"),
        ("200000.00", "200000.00", "1"),
        ("300000.00", "200000.00", "1.5"),
        ("1", "4", "0.25"),
        ("1", "8", "0.125"),
        ("3", "8", "0.375"),
        # More places than a cent: nothing is rounded to the cent.
        ("1", "1024", "0.0009765625"),
        ("123.45", "10", "12.345"),
        ("0.01", "0.04", "0.25"),
        ("7", "1", "7"),
        # A divisor and dividend with trailing zeros give the same value.
        ("1.50", "0.50", "3"),
    ],
)
def test_divides_exactly(dividend: str, divisor: str, quotient: str) -> None:
    assert quotient_of(dividend, divisor) == D(quotient)


def test_the_quotient_is_a_decimal() -> None:
    assert type(quotient_of("1", "4")) is Decimal


def test_the_quotient_is_never_rounded_to_the_cent() -> None:
    assert quotient_of("1", "8") == D("0.125")
    assert quotient_of("1", "8") != D("0.13")
    assert quotient_of("1", "8") != D("0.12")


def test_the_quotient_is_exact_beyond_a_binary_float() -> None:
    assert quotient_of("0.3", "0.1") == D("3")
    assert quotient_of("0.1", "0.4") == D("0.25")


def test_a_big_dividend_over_a_small_divisor_stays_exact() -> None:
    assert quotient_of("123456789012345.67", "0.01") == D("12345678901234567")


@pytest.mark.parametrize(
    ("dividend", "divisor"), [("1", "3"), ("1", "7"), ("2", "3"), ("100", "6")]
)
def test_a_quotient_with_no_finite_expansion_raises_inexact(dividend: str, divisor: str) -> None:
    with pytest.raises(decimal.Inexact):
        capability().compute(inputs(dividend, divisor))


def test_a_quotient_with_no_finite_expansion_is_not_rounded_instead() -> None:
    # 1/3 would round to 0.33 at the cent and to 0.3333333333333333333333333333 at 28 places; it
    # does neither.
    with pytest.raises(decimal.Inexact):
        quotient_of("1", "3")


@pytest.mark.parametrize(("dividend", "divisor"), [("1", "0"), ("0", "0"), ("100000.00", "0.00")])
def test_a_zero_divisor_is_refused_naming_both_kinds(dividend: str, divisor: str) -> None:
    # Both kinds are named, in either order.
    with pytest.raises(DomainError, match=r"(?s)(?=.*dividend_amount)(?=.*divisor_amount)"):
        capability().compute(inputs(dividend, divisor))


def test_a_zero_divisor_is_not_a_zero_division_error() -> None:
    with pytest.raises(DomainError) as raised:
        capability().compute(inputs("1", "0"))

    assert not isinstance(raised.value, ZeroDivisionError)


def test_a_zero_dividend_over_a_divisor_is_zero() -> None:
    assert quotient_of("0", "200000.00") == D("0")


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute(inputs("100000.00", "200000.00"))

    assert result.outputs == (Artifact(OUTPUT, D("0.5")),)


def test_records_one_trace_line_with_the_dividend_the_divisor_and_the_quotient() -> None:
    result = capability().compute(inputs("100000.00", "200000.00"))

    assert result.trace == (
        QuotientLine(
            output=OUTPUT,
            dividend=DIVIDEND,
            dividend_amount=D("100000.00"),
            divisor=DIVISOR,
            divisor_amount=D("200000.00"),
            result=D("0.5"),
        ),
    )


def test_its_trace_reads_as_a_division_in_english() -> None:
    result = capability().compute(inputs("100000.00", "200000.00"))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "quotient_amount: dividend_amount 100000 divided by divisor_amount 200000 = 0.5",
    )


def test_its_trace_for_a_zero_dividend_reads_zero_in_english() -> None:
    result = capability().compute(inputs("0", "200000.00"))

    assert EnglishTraceRenderer().render_all(result.trace) == (
        "quotient_amount: dividend_amount 0 divided by divisor_amount 200000 = 0",
    )


def test_needs_its_dividend() -> None:
    with pytest.raises(MissingArtifactError, match="Quotient.*dividend_amount"):
        capability().compute((Artifact(DIVISOR, D("200000.00")),))


def test_needs_its_divisor() -> None:
    with pytest.raises(MissingArtifactError, match="Quotient.*divisor_amount"):
        capability().compute((Artifact(DIVIDEND, D("100000.00")),))


def test_does_not_consume_anything_else() -> None:
    other = Artifact(ArtifactKind("ex/other", Decimal), D("9"))

    result = capability().compute((other, *inputs("1", "4")))

    assert result.outputs == (Artifact(OUTPUT, D("0.25")),)

"""Unit tests for the Divide capability (`core/divide`), made-up kinds and values.

Its slots: one parameter slot `rounding` (a `rounding_only` dataset, which carries only its
rounding rule), two consumed `Decimal` slots, `dividend` and `divisor`, and one produced slot
`output`. The output is `rounding.apply(Fraction(dividend) / Fraction(divisor))`: the quotient is
formed once as an exact `fractions.Fraction` and rounded once by the dataset's rule. Under
`rounding: none` a quotient with no finite decimal expansion raises `decimal.Inexact` instead of
being carried to 28 digits. A zero divisor is not an error: the output is 0. It records one
`QuotientLine`.

In the worked example (a made-up share of a total: 14,000 / 100,000) the quotient is 0.14, and
1,000 / 3 is the inexact one. The artifact kinds and the dataset family are made up.
"""

from __future__ import annotations

import decimal
from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCapabilityError, MissingArtifactError
from tax_engine.domain.kinds import AmountKind, RateKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import QuotientLine
from tax_engine.jurisdictions.core.capabilities.divide import Divide
from tests.capabilities import bundled_capabilities

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
TEN_THOUSANDTH = RoundTo(D("0.0001"), RoundingMode.HALF_UP)

TOTAL_TAX = AmountKind("ex/total_tax")
TOTAL_PAY = AmountKind("ex/total_pay")
TAX_SHARE = AmountKind("ex/tax_share")


def rounding(rule: RoundingRule = NO_ROUNDING) -> ParameterDataset[RoundingOnly]:
    """By default no rounding."""
    return ParameterDataset(
        "ex/tax_share_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> Divide:
    """By default the made-up total tax / total pay, exact."""
    return Divide(rounding_data or rounding(), TOTAL_TAX, TOTAL_PAY, TAX_SHARE)


def inputs(dividend: str, divisor: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(TOTAL_TAX, D(dividend)), Artifact(TOTAL_PAY, D(divisor)))


def compute(wired: Divide, dividend: str, divisor: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(dividend, divisor)).outputs
    return output


def test_is_registered_as_core_divide() -> None:
    assert bundled_capabilities().get("core/divide") is Divide


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({TOTAL_TAX, TOTAL_PAY})
    assert capability().produces == frozenset({TAX_SHARE})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(Divide)
    assert "produces" not in vars(Divide)


def test_declares_its_slots() -> None:
    assert Divide.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert Divide.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert Divide.CONSUMES == {"dividend": Decimal, "divisor": Decimal}
    assert Divide.PRODUCES == {"output": Decimal}
    assert not Divide.is_list_slot("dividend")
    assert not Divide.is_list_slot("divisor")


def test_its_slots_are_read_only() -> None:
    for slots in (Divide.PARAMETERS, Divide.CONSUMES, Divide.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(Divide.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(Divide.CONSUMES, Mapping[str, type])
    assert_type(Divide.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (Divide.PARAMETERS, Divide.CONSUMES, Divide.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = Divide(rounding=rounding(), dividend=TOTAL_TAX, divisor=TOTAL_PAY, output=TAX_SHARE)

    assert compute(wired, "14000", "100000") == Artifact(TAX_SHARE, D("0.14"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        Divide(rounding(), TOTAL_TAX, TOTAL_PAY, TAX_SHARE, NO_ROUNDING)  # type: ignore[call-arg]


def test_rejects_one_kind_as_both_dividend_and_divisor() -> None:
    with pytest.raises(InvalidCapabilityError, match="Divide") as raised:
        Divide(rounding(), TOTAL_TAX, TOTAL_TAX, TAX_SHARE)

    message = str(raised.value)
    assert "'dividend'" in message
    assert "'divisor'" in message


def test_rejects_one_kind_as_both_dividend_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="Divide") as raised:
        Divide(rounding(), TOTAL_TAX, TOTAL_PAY, TOTAL_TAX)

    message = str(raised.value)
    assert "'dividend'" in message
    assert "'output'" in message


def test_rejects_a_rate_kind_for_its_dividend() -> None:
    rate = RateKind("ex/rate_as_dividend")

    with pytest.raises(InvalidCapabilityError, match="Divide.*'dividend'"):
        Divide(rounding(), rate, TOTAL_PAY, TAX_SHARE)  # type: ignore[arg-type]


def test_rejects_a_rate_kind_for_its_divisor() -> None:
    rate = RateKind("ex/rate_as_divisor")

    with pytest.raises(InvalidCapabilityError, match="Divide.*'divisor'"):
        Divide(rounding(), TOTAL_TAX, rate, TAX_SHARE)  # type: ignore[arg-type]


def test_rejects_a_list_of_kinds_for_its_dividend() -> None:
    with pytest.raises(InvalidCapabilityError, match="Divide.*'dividend'"):
        Divide(rounding(), (TOTAL_TAX,), TOTAL_PAY, TAX_SHARE)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[RoundingOnly]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        Divide(rate, TOTAL_TAX, TOTAL_PAY, TAX_SHARE)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(Divide, "__type_params__", ())
    assert not getattr(Divide, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_an_exact_quotient_is_kept_exact() -> None:
    # 14,000 / 100,000 = 0.14 exactly.
    output = compute(capability(), "14000", "100000")

    assert output == Artifact(TAX_SHARE, D("0.14"))
    assert type(output.value) is Decimal


def test_a_whole_quotient_needs_no_rounding_rule() -> None:
    assert compute(capability(), "300", "3") == Artifact(TAX_SHARE, D("100"))


def test_an_inexact_quotient_without_a_rounding_rule_raises_inexact() -> None:
    # 1000 / 3 = 333.333... has no finite expansion; under `rounding: none` it is refused, not
    # carried to 28 digits.
    with pytest.raises(decimal.Inexact):
        compute(capability(), "1000", "3")


def test_an_inexact_quotient_is_inexact_whatever_the_scale() -> None:
    with pytest.raises(decimal.Inexact):
        compute(capability(), "1000.00", "3.00")
    with pytest.raises(decimal.Inexact):
        compute(capability(), "1", "7")


def test_rounds_an_inexact_quotient_once_half_up() -> None:
    wired = capability(rounding(CENT))

    # 1000 / 3 = 333.333... half-up to 333.33; 2000 / 3 = 666.666... to 666.67.
    assert compute(wired, "1000", "3") == Artifact(TAX_SHARE, D("333.33"))
    assert compute(wired, "2000", "3") == Artifact(TAX_SHARE, D("666.67"))


def test_the_worked_rate_rounds_to_ten_thousandths() -> None:
    # 11,497.09 / 70,000 = 0.164244..., half-up to 0.1642.
    output = compute(capability(rounding(TEN_THOUSANDTH)), "11497.09", "70000")

    assert output == Artifact(TAX_SHARE, D("0.1642"))
    assert str(output.value) == "0.1642"


def test_a_quotient_exactly_on_a_half_is_rounded_by_the_rule_alone() -> None:
    # 1.005 / 1 sits on the tie: half-up to 1.01, half-even to 1.00.
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert compute(capability(rounding(CENT)), "1.005", "1") == Artifact(TAX_SHARE, D("1.01"))
    assert compute(capability(rounding(half_even)), "1.005", "1") == Artifact(TAX_SHARE, D("1.00"))


def test_rounds_once_on_the_exact_fraction() -> None:
    # 0.015 / 3 is exactly 0.005, half-up to 0.01; 1 / 3 is 0.3333 and 2 / 3 is 0.6667 at 0.0001.
    assert compute(capability(rounding(CENT)), "0.015", "3") == Artifact(TAX_SHARE, D("0.01"))
    wired = capability(rounding(TEN_THOUSANDTH))
    assert compute(wired, "1", "3") == Artifact(TAX_SHARE, D("0.3333"))
    assert compute(wired, "2", "3") == Artifact(TAX_SHARE, D("0.6667"))


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(rounding(RoundTo(D("1"), RoundingMode.CEILING)))

    assert compute(wired, "1000", "3") == Artifact(TAX_SHARE, D("334"))


def test_a_rounded_output_carries_the_increments_scale() -> None:
    assert str(compute(capability(rounding(CENT)), "14000", "100000").value) == "0.14"
    assert str(compute(capability(rounding(TEN_THOUSANDTH)), "1", "4").value) == "0.2500"


def test_the_quotient_is_exact_under_a_context_that_traps_inexact() -> None:
    # The engine runs capabilities under a context trapping Inexact; only the rule may round.
    with decimal.localcontext() as context:
        context.traps[decimal.Inexact] = True
        output = compute(capability(rounding(TEN_THOUSANDTH)), "11497.09", "70000")

    assert output.value == D("0.1642")


def test_the_quotient_keeps_every_digit_of_a_long_dividend() -> None:
    dividend = "12345678901234567890123456789"

    assert str(compute(capability(), dividend, "1").value) == dividend


def test_a_quotient_above_one_is_not_capped() -> None:
    assert compute(capability(), "150000", "100000") == Artifact(TAX_SHARE, D("1.5"))


def test_a_zero_dividend_gives_zero() -> None:
    output = compute(capability(), "0", "100000")

    assert output == Artifact(TAX_SHARE, D("0"))
    assert type(output.value) is Decimal


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = AmountKind("ex/other")

    result = capability().compute((Artifact(other, D("9")), *inputs("14000", "100000")))

    assert result.outputs == (Artifact(TAX_SHARE, D("0.14")),)


def test_a_missing_dividend_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="total_tax"):
        capability().compute(inputs("14000", "100000")[1:])


def test_a_missing_divisor_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="total_pay"):
        capability().compute(inputs("14000", "100000")[:1])


# --- a zero divisor ---------------------------------------------------------------------------


def test_a_zero_divisor_gives_zero_not_an_error() -> None:
    output = compute(capability(), "14000", "0")

    assert output == Artifact(TAX_SHARE, D("0"))
    assert type(output.value) is Decimal


def test_a_zero_divisor_gives_zero_whatever_its_scale_or_sign() -> None:
    assert compute(capability(), "14000", "0.00").value == D("0")
    assert compute(capability(), "14000", "-0").value == D("0")


def test_a_zero_divisor_gives_zero_with_a_zero_dividend_too() -> None:
    assert compute(capability(), "0", "0").value == D("0")


def test_a_zero_divisor_gives_zero_under_a_rounding_rule() -> None:
    assert compute(capability(rounding(TEN_THOUSANDTH)), "14000", "0").value == D("0")


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_quotient_line() -> None:
    trace = capability().compute(inputs("14000", "100000")).trace

    assert trace == (
        QuotientLine(
            output=TAX_SHARE,
            dividend=TOTAL_TAX,
            dividend_amount=D("14000"),
            divisor=TOTAL_PAY,
            divisor_amount=D("100000"),
            rounding=NO_ROUNDING,
            result=D("0.14"),
        ),
    )


def test_traces_the_datasets_rounding_rule_and_the_rounded_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("1000", "3")).trace

    assert trace == (
        QuotientLine(TAX_SHARE, TOTAL_TAX, D("1000"), TOTAL_PAY, D("3"), CENT, D("333.33")),
    )


def test_traces_a_zero_divisor_with_its_zero_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("1000", "0")).trace

    (line,) = trace
    assert isinstance(line, QuotientLine)
    assert line.divisor_amount == D("0")
    assert line.result == D("0")
    assert line.rounding == CENT


def test_trace_amount_is_the_result() -> None:
    trace = capability(rounding(CENT)).compute(inputs("1000", "3")).trace

    assert [line.amount for line in trace] == [D("333.33")]


def test_trace_result_is_the_output() -> None:
    result = capability(rounding(CENT)).compute(inputs("4321", "91"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, QuotientLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("14000", "100000")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))

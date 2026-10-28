"""Unit tests for the ApplyChosenRate capability (`ca/apply_chosen_rate`).

Schedule ON479-A (2025, 5006-TCA), line 8: "Line 6 multiplied by the percentage from line 7".
Unlike `core/apply_rate`, whose rate is a `rate` dataset's, the rate here is an artifact (line
7's, chosen by `ca-on/rate_by_income_band`). Its slots: one parameter slot `rounding` (a
`rounding_only` dataset, which carries only its rounding rule), two consumed slots, `base` (a
`Decimal` kind) and `rate` (a kind whose values are `Rate`s), and one produced slot `output`. The
output is `rounding.apply(base × rate)`, the product computed exactly and rounded once by the
dataset's rule (half up to the cent in the wiring). It records one `ChosenRateAppliedLine`.

The artifact kinds and dataset families are made up; the wiring comes later. In the worked
example, family adjusted income 50,000 is in the form's row "more than $45,000 but not more than
$50,000: 55%", and 55% of a 5,000 child care deduction is 2,750.
"""

from __future__ import annotations

import decimal
import importlib.util
from collections.abc import Mapping
from dataclasses import fields
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_calculator.jurisdictions.ca.capabilities as ca_capabilities
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.composition import Composition
from tax_calculator.domain.errors import (
    InvalidCapabilityError,
    MissingArtifactError,
    UnknownRegistrationError,
)
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import (
    NO_ROUNDING,
    RoundingMode,
    RoundingRule,
    RoundTo,
)
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.trace import ChosenRateAppliedLine, RateAppliedLine, RateByIncomeBandLine
from tax_calculator.jurisdictions.ca.capabilities.apply_chosen_rate import ApplyChosenRate
from tax_calculator.jurisdictions.ca_on.capabilities.rate_by_income_band import RateByIncomeBand
from tests.jurisdictions.ca_on.capabilities.on479a_table import (
    FAMILY_INCOME,
    form_row,
)
from tests.jurisdictions.ca_on.capabilities.on479a_table import (
    table as on479a_table_data,
)

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

CARE_DEDUCTION = ArtifactKind("ex/child_care_deduction", Decimal)
CARE_RATE = ArtifactKind("ex/care_rate", Rate)
CARE_CREDIT = ArtifactKind("ex/care_credit", Decimal)


def rounding(rule: RoundingRule = CENT) -> ParameterDataset[RoundingOnly]:
    return ParameterDataset(
        "ex/care_credit_rounding",
        2025,
        ROUNDING_ONLY,
        RoundingOnly(),
        rule,
        ("https://example.org/rounding",),
    )


def capability(rounding_data: ParameterDataset[RoundingOnly] | None = None) -> ApplyChosenRate:
    """By default the made-up deduction × the made-up rate, half up to the cent."""
    return ApplyChosenRate(rounding_data or rounding(), CARE_DEDUCTION, CARE_RATE, CARE_CREDIT)


def inputs(base: str, rate: str) -> tuple[Artifact[Any], ...]:
    return (Artifact(CARE_DEDUCTION, D(base)), Artifact(CARE_RATE, Rate(D(rate))))


def compute(wired: ApplyChosenRate, base: str, rate: str) -> Artifact[Any]:
    (output,) = wired.compute(inputs(base, rate)).outputs
    return output


def test_is_registered_as_ca_apply_chosen_rate() -> None:
    assert CapabilityRegistry.shared().get("ca/apply_chosen_rate") is ApplyChosenRate


def test_is_exported_from_the_federal_capabilities_package() -> None:
    assert "apply_chosen_rate" in ca_capabilities.__all__
    assert ca_capabilities.apply_chosen_rate.ApplyChosenRate is ApplyChosenRate


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({CARE_DEDUCTION, CARE_RATE})
    assert capability().produces == frozenset({CARE_CREDIT})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(ApplyChosenRate)
    assert "produces" not in vars(ApplyChosenRate)


def test_declares_its_slots() -> None:
    assert ApplyChosenRate.PARAMETERS == {"rounding": ROUNDING_ONLY}
    assert ApplyChosenRate.PARAMETERS["rounding"] is ROUNDING_ONLY
    assert ApplyChosenRate.CONSUMES == {"base": Decimal, "rate": Rate}
    assert ApplyChosenRate.PRODUCES == {"output": Decimal}
    assert not ApplyChosenRate.is_list_slot("base")
    assert not ApplyChosenRate.is_list_slot("rate")


def test_its_slots_are_read_only() -> None:
    for slots in (ApplyChosenRate.PARAMETERS, ApplyChosenRate.CONSUMES, ApplyChosenRate.PRODUCES):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(ApplyChosenRate.PARAMETERS, Mapping[str, ParameterKind[RoundingOnly]])
    assert_type(ApplyChosenRate.CONSUMES, Mapping[str, type])
    assert_type(ApplyChosenRate.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (ApplyChosenRate.PARAMETERS, ApplyChosenRate.CONSUMES, ApplyChosenRate.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = ApplyChosenRate(
        rounding=rounding(), base=CARE_DEDUCTION, rate=CARE_RATE, output=CARE_CREDIT
    )

    assert compute(wired, "5000", "0.55") == Artifact(CARE_CREDIT, D("2750.00"))


def test_takes_no_separate_rounding_argument() -> None:
    with pytest.raises(TypeError):
        ApplyChosenRate(
            rounding(),
            CARE_DEDUCTION,
            CARE_RATE,
            CARE_CREDIT,
            NO_ROUNDING,  # type: ignore[call-arg]
        )


def test_rejects_one_kind_as_both_base_and_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="ApplyChosenRate") as raised:
        ApplyChosenRate(rounding(), CARE_DEDUCTION, CARE_RATE, CARE_DEDUCTION)

    message = str(raised.value)
    assert "'base'" in message
    assert "'output'" in message


def test_rejects_a_money_kind_as_its_rate() -> None:
    money = ArtifactKind("ex/rate_as_money", Decimal)

    with pytest.raises(InvalidCapabilityError, match="ApplyChosenRate.*'rate'"):
        ApplyChosenRate(rounding(), CARE_DEDUCTION, money, CARE_CREDIT)  # type: ignore[arg-type]


def test_rejects_a_rate_kind_as_its_base() -> None:
    other_rate = ArtifactKind("ex/other_rate", Rate)

    with pytest.raises(InvalidCapabilityError, match="ApplyChosenRate.*'base'"):
        ApplyChosenRate(rounding(), other_rate, CARE_RATE, CARE_CREDIT)  # type: ignore[arg-type]


def test_mypy_rejects_a_dataset_of_another_parameter_kind() -> None:
    def wire() -> None:  # type-checked, never run
        # A rate dataset is not a ParameterDataset[RoundingOnly]; the ignore fails under mypy
        # (warn_unused_ignores) if it is ever accepted.
        rate = ParameterDataset(
            "ex/some_rate", 2025, RATE, Rate(D("0.5")), NO_ROUNDING, ("https://example.org/r",)
        )
        ApplyChosenRate(rate, CARE_DEDUCTION, CARE_RATE, CARE_CREDIT)  # type: ignore[arg-type]

    assert callable(wire)


def test_is_not_generic_over_artifacts() -> None:
    assert not getattr(ApplyChosenRate, "__type_params__", ())
    assert not getattr(ApplyChosenRate, "__parameters__", ())


# --- computing --------------------------------------------------------------------------------


def test_the_worked_example_gives_2750() -> None:
    # 55% × 5,000 = 2,750.
    output = compute(capability(), "5000", "0.55")

    assert output == Artifact(CARE_CREDIT, D("2750"))
    assert str(output.value) == "2750.00"
    assert type(output.value) is Decimal


def test_keeps_the_product_exact_without_rounding() -> None:
    # 5000.01 × 0.55 = 2750.0055, not rounded.
    output = compute(capability(rounding(NO_ROUNDING)), "5000.01", "0.55")

    assert output == Artifact(CARE_CREDIT, D("2750.0055"))


def test_rounds_with_the_datasets_rule() -> None:
    # 2750.0055 half up to the cent.
    assert compute(capability(), "5000.01", "0.55") == Artifact(CARE_CREDIT, D("2750.01"))


def test_a_tie_rounds_by_the_datasets_mode() -> None:
    # 0.01 × 0.5 = 0.005: half up gives 0.01, half even gives 0.00.
    half_even = RoundTo(D("0.01"), RoundingMode.HALF_EVEN)

    assert compute(capability(), "0.01", "0.5") == Artifact(CARE_CREDIT, D("0.01"))
    assert compute(capability(rounding(half_even)), "0.01", "0.5") == Artifact(
        CARE_CREDIT, D("0.00")
    )


def test_rounds_with_another_rule_of_the_dataset() -> None:
    wired = capability(rounding(RoundTo(D("1"), RoundingMode.FLOOR)))

    # 5000.01 × 0.55 = 2750.0055, floored to 2750.
    assert str(compute(wired, "5000.01", "0.55").value) == "2750"


def test_a_zero_rate_gives_zero() -> None:
    output = compute(capability(), "5000", "0")

    assert output == Artifact(CARE_CREDIT, D("0"))
    assert str(output.value) == "0.00"


def test_a_whole_rate_gives_the_base() -> None:
    assert compute(capability(), "5000.25", "1") == Artifact(CARE_CREDIT, D("5000.25"))


def test_a_zero_base_gives_zero() -> None:
    assert compute(capability(), "0", "0.75") == Artifact(CARE_CREDIT, D("0"))


def test_the_product_is_exact_so_a_long_base_keeps_every_digit() -> None:
    # 29 digits × 0.55 = 6790123395679012339567901233.95, 30 digits: more than a 28-digit
    # context holds, so a plain Decimal product would be rounded before the rule.
    output = compute(capability(), "12345678901234567890123456789", "0.55")

    assert str(output.value) == "6790123395679012339567901233.95"


def test_the_product_is_exact_under_a_context_that_traps_inexact() -> None:
    # The engine runs capabilities under a context trapping Inexact; only the rule may round.
    with decimal.localcontext() as context:
        context.traps[decimal.Inexact] = True
        output = compute(capability(rounding(NO_ROUNDING)), "12345678901234567890123456789", "0.55")

    assert str(output.value) == "6790123395679012339567901233.95"


def test_ignores_artifacts_it_does_not_consume() -> None:
    other = ArtifactKind("ex/other", Decimal)

    result = capability().compute((Artifact(other, D("9")), *inputs("5000", "0.55")))

    assert result.outputs == (Artifact(CARE_CREDIT, D("2750.00")),)


def test_a_missing_rate_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="care_rate"):
        capability().compute((Artifact(CARE_DEDUCTION, D("5000")),))


def test_a_missing_base_is_a_missing_artifact() -> None:
    with pytest.raises(MissingArtifactError, match="child_care_deduction"):
        capability().compute((Artifact(CARE_RATE, Rate(D("0.55"))),))


# --- trace ------------------------------------------------------------------------------------


def test_traces_one_chosen_rate_applied_line() -> None:
    trace = capability().compute(inputs("5000.01", "0.55")).trace

    assert trace == (
        ChosenRateAppliedLine(
            output=CARE_CREDIT,
            base=CARE_DEDUCTION,
            base_amount=D("5000.01"),
            rate_kind=CARE_RATE,
            rate=Rate(D("0.55")),
            rounding=CENT,
            result=D("2750.01"),
        ),
    )


def test_traces_its_own_line_not_a_rate_applied_line() -> None:
    (line,) = capability().compute(inputs("5000", "0.55")).trace

    assert not isinstance(line, RateAppliedLine)


def test_trace_amount_is_the_result() -> None:
    trace = capability().compute(inputs("5000.01", "0.55")).trace

    assert [line.amount for line in trace] == [D("2750.01")]


def test_trace_result_is_the_output() -> None:
    result = capability().compute(inputs("4321", "0.37"))

    (line,) = result.trace
    (output,) = result.outputs
    assert isinstance(line, ChosenRateAppliedLine)
    assert line.result == output.value


def test_trace_holds_no_text() -> None:
    trace = capability().compute(inputs("5000", "0.55")).trace

    for line in trace:
        assert not any(isinstance(getattr(line, f.name), str) for f in fields(line))


# --- lines 7 and 8 together -------------------------------------------------------------------
#
# The two capabilities composed: line 7's rate artifact feeds line 8, through a worksheet that
# traps inexact arithmetic.


def lines_7_and_8() -> Composition:
    return Composition(
        (
            capability(),  # listed out of order on purpose
            RateByIncomeBand(on479a_table_data(), FAMILY_INCOME, CARE_RATE),
        ),
        inputs=frozenset({FAMILY_INCOME, CARE_DEDUCTION}),
        outputs=frozenset({CARE_CREDIT}),
    )


def test_line_7_runs_before_line_8() -> None:
    order = lines_7_and_8().order

    assert [type(step) for step in order] == [RateByIncomeBand, ApplyChosenRate]


def test_computes_the_worked_example_through_both_lines() -> None:
    worksheet = lines_7_and_8().compute(
        Artifact(FAMILY_INCOME, D("50000")), Artifact(CARE_DEDUCTION, D("5000"))
    )

    assert worksheet.get(CARE_RATE).value == Rate(D("0.55"))
    assert worksheet.get(CARE_CREDIT).value == D("2750")
    assert str(worksheet.get(CARE_CREDIT).value) == "2750.00"
    assert worksheet.trace == (
        RateByIncomeBandLine(
            CARE_RATE,
            FAMILY_INCOME,
            D("50000"),
            form_row("45000", "50000", "0.55"),
            Rate(D("0.55")),
        ),
        ChosenRateAppliedLine(
            CARE_CREDIT, CARE_DEDUCTION, D("5000"), CARE_RATE, Rate(D("0.55")), CENT, D("2750.00")
        ),
    )


def test_renders_the_worked_example_in_english() -> None:
    worksheet = lines_7_and_8().compute(
        Artifact(FAMILY_INCOME, D("50000")), Artifact(CARE_DEDUCTION, D("5000"))
    )

    assert EnglishTraceRenderer().render_all(worksheet.trace) == (
        "care_rate: family_adjusted_income 50000, more than 45000 but not more than 50000: 55%",
        "care_credit: care_rate 55% of child_care_deduction 5000 (half-up to 0.01)",
    )


def test_a_zero_family_income_takes_75_percent_through_both_lines() -> None:
    worksheet = lines_7_and_8().compute(
        Artifact(FAMILY_INCOME, D("0")), Artifact(CARE_DEDUCTION, D("1234.56"))
    )

    # 75% × 1234.56 = 925.92.
    assert worksheet.get(CARE_CREDIT).value == D("925.92")


def test_a_family_income_above_the_last_bound_gives_no_credit_through_both_lines() -> None:
    worksheet = lines_7_and_8().compute(
        Artifact(FAMILY_INCOME, D("150001")), Artifact(CARE_DEDUCTION, D("5000"))
    )

    assert worksheet.get(CARE_CREDIT).value == D("0")


def test_is_no_longer_registered_under_the_ontario_namespace() -> None:
    with pytest.raises(UnknownRegistrationError):
        CapabilityRegistry.shared().get("ca-on/apply_chosen_rate")


def test_the_ontario_package_holds_no_module_for_it() -> None:
    assert (
        importlib.util.find_spec(
            "tax_calculator.jurisdictions.ca_on.capabilities.apply_chosen_rate"
        )
        is None
    )

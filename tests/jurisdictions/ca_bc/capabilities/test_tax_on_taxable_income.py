"""Unit tests for the TaxOnTaxableIncome capability (`ca-bc/tax_on_taxable_income`), with made-up
kinds.

BC428 line 61: "Line 61: British Columbia tax on taxable income from line 8 or 15". Under the lines
2 to 8 table the form says "enter the amount from line 8 on line 61 and continue on line 16", and
under the lines 9 to 15 table "enter the amount from line 15 on line 61 and continue on line 16"
(CRA 5010-C, read 2026-11-14). A taxable income is in exactly one of the two tables, so the other
table's line 8 or line 15 is left blank.

Unlike Alberta's, whose lines 8 and 15 are on another form and are read as record lists, BC428 keeps
lines 8, 15 and 61 on one form, so the capability consumes two plain amounts. Its slots: no
parameter slot, two consumed slots `line_8` and `line_15` (each a plain amount that may be blank:
the manifest gives each the `compute` blank rule, so a blank reaches `compute`) and one produced
slot `output`. The output is the figure that is not blank, as it is: it is not rounded (it has no
dataset). A form that leaves both lines blank, or gives both a figure, cannot be the form's own, so
it is refused with a `ValidationError` that names line 8 and line 15 and says which case it is. It
records one `TaxOnTaxableIncomeLine`: the line used, its amount and the line left blank.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca_bc.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK, COMPUTE
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
    ValidationError,
)
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.jurisdictions.ca_bc.capabilities.tax_on_taxable_income import (
    TaxOnTaxableIncome,
)
from tax_engine.jurisdictions.ca_bc.trace import TaxOnTaxableIncomeLine
from tests.jurisdictions.ca_bc.support import british_columbia_capabilities

D = Decimal

LINE_8 = AmountKind("ex/tax_on_taxable_income_line_8", non_negative=True)
LINE_15 = AmountKind("ex/tax_on_taxable_income_line_15", non_negative=True)
LINE_61 = AmountKind("ex/tax_on_taxable_income_line_61", non_negative=True)


def capability() -> TaxOnTaxableIncome:
    return TaxOnTaxableIncome(LINE_8, LINE_15, LINE_61)


def amount(kind: AmountKind, figure: str | None) -> Artifact[Any]:
    """One plain amount; `None` is a blank."""
    return Artifact(kind, BLANK if figure is None else D(figure))


def inputs(eight: str | None, fifteen: str | None) -> tuple[Artifact[Any], ...]:
    return (amount(LINE_8, eight), amount(LINE_15, fifteen))


def compute(eight: str | None, fifteen: str | None) -> Artifact[Any]:
    (output,) = capability().compute(inputs(eight, fifteen)).outputs
    return output


def trace_of(eight: str | None, fifteen: str | None) -> tuple[Any, ...]:
    return capability().compute(inputs(eight, fifteen)).trace


# --- the class ---------------------------------------------------------------------------------


def test_is_registered_as_ca_bc_tax_on_taxable_income() -> None:
    assert british_columbia_capabilities().get("ca-bc/tax_on_taxable_income") is TaxOnTaxableIncome


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({LINE_8, LINE_15})
    assert capability().produces == frozenset({LINE_61})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TaxOnTaxableIncome)
    assert "produces" not in vars(TaxOnTaxableIncome)


def test_declares_its_slots() -> None:
    assert TaxOnTaxableIncome.PARAMETERS == {}
    assert TaxOnTaxableIncome.CONSUMES == {"line_8": Decimal, "line_15": Decimal}
    assert TaxOnTaxableIncome.PRODUCES == {"output": Decimal}
    assert not TaxOnTaxableIncome.is_list_slot("line_8")
    assert not TaxOnTaxableIncome.is_list_slot("line_15")


def test_its_two_amount_slots_may_be_blank_and_its_output_is_never_blank() -> None:
    assert TaxOnTaxableIncome.BLANK_ALLOWED == frozenset({"line_8", "line_15"})
    assert TaxOnTaxableIncome.BLANK_RECORD_FIELDS == frozenset()
    assert TaxOnTaxableIncome.MAY_BE_BLANK == frozenset()


def test_its_slots_are_read_only() -> None:
    for slots in (
        TaxOnTaxableIncome.PARAMETERS,
        TaxOnTaxableIncome.CONSUMES,
        TaxOnTaxableIncome.PRODUCES,
    ):
        assert isinstance(slots, MappingProxyType)


def test_its_slots_are_typed_as_read_only_mappings() -> None:
    assert_type(TaxOnTaxableIncome.CONSUMES, Mapping[str, type])
    assert_type(TaxOnTaxableIncome.PRODUCES, Mapping[str, type])


def test_its_slots_cannot_be_changed() -> None:
    for slots in (TaxOnTaxableIncome.CONSUMES, TaxOnTaxableIncome.PRODUCES):
        with pytest.raises(TypeError):
            cast(Any, slots)["extra"] = Decimal


def test_is_built_from_its_slot_names_as_keywords() -> None:
    wired = TaxOnTaxableIncome(line_8=LINE_8, line_15=LINE_15, output=LINE_61)

    assert wired.compute(inputs("1586.80", None)).outputs == (Artifact(LINE_61, D("1586.80")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        TaxOnTaxableIncome(LINE_8, LINE_15, LINE_61, object())  # type: ignore[call-arg]


def test_rejects_a_count_kind_for_line_8() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome.*'line_8'"):
        TaxOnTaxableIncome(CountKind("ex/count"), LINE_15, LINE_61)  # type: ignore[arg-type]


def test_rejects_a_count_kind_for_line_15() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome.*'line_15'"):
        TaxOnTaxableIncome(LINE_8, CountKind("ex/count"), LINE_61)  # type: ignore[arg-type]


def test_rejects_a_count_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome.*'output'"):
        TaxOnTaxableIncome(LINE_8, LINE_15, CountKind("ex/count"))  # type: ignore[arg-type]


def test_rejects_one_kind_as_both_lines() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome") as raised:
        TaxOnTaxableIncome(LINE_8, LINE_8, LINE_61)

    message = str(raised.value)
    assert "'line_8'" in message
    assert "'line_15'" in message


# --- computing ---------------------------------------------------------------------------------


def test_line_8_alone_gives_line_8() -> None:
    # A taxable income of 19,835.00 is in the table of lines 2 to 8: 5.06% of it is 1,003.65.
    assert compute("1003.65", None) == Artifact(LINE_61, D("1003.65"))


def test_line_15_alone_gives_line_15() -> None:
    # A taxable income of 198,926.00 is in the table of lines 9 to 15, column 2:
    # 12,620.00 x 16.8% = 2,120.16, plus 17,989.30 is 20,109.46.
    assert compute(None, "20109.46") == Artifact(LINE_61, D("20109.46"))


def test_a_line_8_of_zero_is_a_figure_so_line_15_blank_gives_zero() -> None:
    # Zero is not blank: the line was completed and came to 0.00.
    assert compute("0.00", None) == Artifact(LINE_61, D("0.00"))


def test_a_line_15_of_zero_is_a_figure_so_line_8_blank_gives_zero() -> None:
    assert compute(None, "0.00") == Artifact(LINE_61, D("0.00"))


def test_the_figure_is_given_as_it_is_and_never_rounded() -> None:
    assert str(compute("4037.834", None).value) == "4037.834"


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute(inputs("4037.83", None))

    assert result.outputs == (Artifact(LINE_61, D("4037.83")),)


def test_the_order_of_the_inputs_does_not_matter() -> None:
    (output,) = capability().compute((amount(LINE_15, None), amount(LINE_8, "4037.83"))).outputs

    assert output == Artifact(LINE_61, D("4037.83"))


def test_a_missing_line_8_artifact_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute((amount(LINE_15, "20109.46"),))


def test_a_missing_line_15_artifact_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute((amount(LINE_8, "1003.65"),))


# --- both blank, both present ------------------------------------------------------------------


def test_both_lines_blank_is_refused_naming_both_lines() -> None:
    with pytest.raises(ValidationError) as raised:
        compute(None, None)

    message = str(raised.value)
    assert "TaxOnTaxableIncome" in message
    assert "line 8" in message
    assert "line 15" in message
    assert "blank" in message


def test_both_lines_with_a_figure_is_refused_naming_both_lines() -> None:
    with pytest.raises(ValidationError) as raised:
        compute("1003.65", "20109.46")

    message = str(raised.value)
    assert "TaxOnTaxableIncome" in message
    assert "line 8" in message
    assert "line 15" in message
    assert "both" in message


def test_both_lines_zero_is_refused_as_both_having_a_figure() -> None:
    with pytest.raises(ValidationError, match="both"):
        compute("0.00", "0.00")


def test_a_refusal_is_a_validation_error_and_not_a_missing_or_blank_error() -> None:
    for eight, fifteen in ((None, None), ("1.00", "2.00")):
        with pytest.raises(ValidationError) as raised:
            compute(eight, fifteen)
        assert not isinstance(raised.value, MissingArtifactError | BlankNotAllowedError)


# --- blank rules (what the manifest wires) ------------------------------------------------------


def test_with_the_compute_rule_for_each_line_a_blank_line_reaches_the_capability() -> None:
    wired = capability().with_blank_rules({"line_8": COMPUTE, "line_15": COMPUTE})

    result = wired.run(inputs(None, "20109.46"))

    assert result.outputs == (Artifact(LINE_61, D("20109.46")),)


def test_without_a_rule_for_its_slot_a_blank_line_is_refused_by_the_base() -> None:
    with pytest.raises(BlankNotAllowedError):
        capability().run(inputs(None, "20109.46"))


# --- trace -------------------------------------------------------------------------------------


def test_records_one_trace_line_naming_line_8_when_it_is_the_one_used() -> None:
    assert trace_of("1003.65", None) == (
        TaxOnTaxableIncomeLine(
            output=LINE_61,
            used=LINE_8,
            used_amount=D("1003.65"),
            left_blank=LINE_15,
        ),
    )


def test_records_one_trace_line_naming_line_15_when_it_is_the_one_used() -> None:
    assert trace_of(None, "20109.46") == (
        TaxOnTaxableIncomeLine(
            output=LINE_61,
            used=LINE_15,
            used_amount=D("20109.46"),
            left_blank=LINE_8,
        ),
    )


def test_the_trace_line_is_about_the_output_and_holds_the_figure() -> None:
    (line,) = trace_of("4037.83", None)

    assert line.label == LINE_61.label
    assert line.amount == D("4037.83")


def test_the_english_sentence_when_line_8_is_the_figure() -> None:
    assert EnglishTraceRenderer().render_all(trace_of("1003.65", None)) == (
        "Tax on taxable income line 8 (1003.65), with tax on taxable income line 15 left blank, "
        "gives 1003.65.",
    )


def test_the_english_sentence_when_line_15_is_the_figure() -> None:
    assert EnglishTraceRenderer().render_all(trace_of(None, "20109.46")) == (
        "Tax on taxable income line 15 (20109.46), with tax on taxable income line 8 left blank, "
        "gives 20109.46.",
    )


def test_the_english_sentence_shows_cents_for_a_whole_figure() -> None:
    assert EnglishTraceRenderer().render_all(trace_of("4037", None)) == (
        "Tax on taxable income line 8 (4037.00), with tax on taxable income line 15 left blank, "
        "gives 4037.00.",
    )

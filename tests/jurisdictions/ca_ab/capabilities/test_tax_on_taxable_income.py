"""Unit tests for the TaxOnTaxableIncome capability (`ca-ab/tax_on_taxable_income`), with made-up
kinds.

AB428 line 59 (cra-docs, docs/cra-forms-2025/5009-c-25e.txt): "Line 59: Alberta tax on taxable
income from line 8 or line 15". The form prints two tables (lines 2 to 8 and lines 9 to 15), and a
taxable income is in exactly one of them: the other table's line 8 or line 15 is left blank (#660).
The capability reads both lines as record lists, because another form reads an export only as a
record list, and gives the one that has a figure.

Its slots: no parameter slot, two consumed slots `line_8` and `line_15` (each a record list of one
amount field; a blank field is handed to `compute` by the `compute` rule) and one produced slot
`output`. The output is that figure as it is: it is not rounded (it has no dataset). A form that
leaves both lines blank, or gives both a figure, cannot be the form's own, so it is refused with a
`ValidationError` that names line 8 and line 15 and says which case it is. It records one
`TaxOnTaxableIncomeLine`: the line used, its amount and the line left blank.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any, assert_type, cast

import pytest

import tax_engine.jurisdictions.ca_ab.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK, COMPUTE
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    InvalidCapabilityError,
    MissingArtifactError,
    ValidationError,
)
from tax_engine.domain.kinds import AmountKind, CountKind, RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca_ab.capabilities.tax_on_taxable_income import (
    TaxOnTaxableIncome,
)
from tax_engine.jurisdictions.ca_ab.trace import TaxOnTaxableIncomeLine
from tests.jurisdictions.ca_ab.support import alberta_capabilities

D = Decimal

LINE_8 = AmountKind("ex/tax_on_taxable_income_line_8", non_negative=True)
LINE_15 = AmountKind("ex/tax_on_taxable_income_line_15", non_negative=True)
LINE_8_LIST = RecordListKind("ex/credits.tax_on_taxable_income_line_8", fields=(LINE_8,))
LINE_15_LIST = RecordListKind("ex/credits.tax_on_taxable_income_line_15", fields=(LINE_15,))
LINE_59 = AmountKind("ex/tax_on_taxable_income_line_59", non_negative=True)


def capability() -> TaxOnTaxableIncome:
    return TaxOnTaxableIncome(LINE_8_LIST, LINE_15_LIST, LINE_59)


def line_8(*amounts: str | None) -> Artifact[Any]:
    """The line 8 export as one record per form instance; `None` is a blank."""
    records: list[dict[Any, Any]] = [{LINE_8: BLANK if a is None else D(a)} for a in amounts]
    return Artifact(LINE_8_LIST, RecordList(LINE_8_LIST.fields, records))


def line_15(*amounts: str | None) -> Artifact[Any]:
    records: list[dict[Any, Any]] = [{LINE_15: BLANK if a is None else D(a)} for a in amounts]
    return Artifact(LINE_15_LIST, RecordList(LINE_15_LIST.fields, records))


def inputs(eight: str | None, fifteen: str | None) -> tuple[Artifact[Any], ...]:
    return (line_8(eight), line_15(fifteen))


def compute(eight: str | None, fifteen: str | None) -> Artifact[Any]:
    (output,) = capability().compute(inputs(eight, fifteen)).outputs
    return output


def trace_of(eight: str | None, fifteen: str | None) -> tuple[Any, ...]:
    return capability().compute(inputs(eight, fifteen)).trace


# --- the class ---------------------------------------------------------------------------------


def test_is_registered_as_ca_ab_tax_on_taxable_income() -> None:
    assert alberta_capabilities().get("ca-ab/tax_on_taxable_income") is TaxOnTaxableIncome


def test_declares_its_contract() -> None:
    assert capability().consumes == frozenset({LINE_8_LIST, LINE_15_LIST})
    assert capability().produces == frozenset({LINE_59})


def test_leaves_its_contract_to_the_base() -> None:
    assert "consumes" not in vars(TaxOnTaxableIncome)
    assert "produces" not in vars(TaxOnTaxableIncome)


def test_declares_its_slots() -> None:
    assert TaxOnTaxableIncome.PARAMETERS == {}
    assert TaxOnTaxableIncome.CONSUMES == {"line_8": RecordList, "line_15": RecordList}
    assert TaxOnTaxableIncome.PRODUCES == {"output": Decimal}
    assert not TaxOnTaxableIncome.is_list_slot("line_8")
    assert not TaxOnTaxableIncome.is_list_slot("line_15")


def test_its_record_slots_may_hold_a_blank_field() -> None:
    assert TaxOnTaxableIncome.BLANK_RECORD_FIELDS == frozenset({"line_8", "line_15"})
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
    wired = TaxOnTaxableIncome(line_8=LINE_8_LIST, line_15=LINE_15_LIST, output=LINE_59)

    assert wired.compute(inputs("1586.80", None)).outputs == (Artifact(LINE_59, D("1586.80")),)


def test_takes_no_parameter_dataset() -> None:
    with pytest.raises(TypeError):
        TaxOnTaxableIncome(LINE_8_LIST, LINE_15_LIST, LINE_59, object())  # type: ignore[call-arg]


def test_rejects_an_amount_kind_for_line_8() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome.*'line_8'"):
        TaxOnTaxableIncome(LINE_8, LINE_15_LIST, LINE_59)  # type: ignore[arg-type]


def test_rejects_a_count_kind_for_line_15() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome.*'line_15'"):
        TaxOnTaxableIncome(LINE_8_LIST, CountKind("ex/count"), LINE_59)  # type: ignore[arg-type]


def test_rejects_a_record_list_kind_for_its_output() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome.*'output'"):
        TaxOnTaxableIncome(LINE_8_LIST, LINE_15_LIST, LINE_8_LIST)  # type: ignore[arg-type]


def test_rejects_one_list_kind_as_both_lines() -> None:
    with pytest.raises(InvalidCapabilityError, match="TaxOnTaxableIncome") as raised:
        TaxOnTaxableIncome(LINE_8_LIST, LINE_8_LIST, LINE_59)

    message = str(raised.value)
    assert "'line_8'" in message
    assert "'line_15'" in message


# --- computing ---------------------------------------------------------------------------------


def test_line_8_alone_gives_line_8() -> None:
    # A taxable income of 19,835.00 is in the table of lines 2 to 8: 8% of it is 1,586.80.
    assert compute("1586.80", None) == Artifact(LINE_59, D("1586.80"))


def test_line_15_alone_gives_line_15() -> None:
    # A taxable income of 198,926.00 is in the table of lines 9 to 15:
    # 17,553.04 + 17,445.00 x 13% = 17,553.04 + 2,267.85 = 19,820.89.
    assert compute(None, "19820.89") == Artifact(LINE_59, D("19820.89"))


def test_a_line_8_of_zero_is_a_figure_so_line_15_blank_gives_zero() -> None:
    # Zero is not blank: the line was completed and came to 0.00.
    assert compute("0.00", None) == Artifact(LINE_59, D("0.00"))


def test_a_line_15_of_zero_is_a_figure_so_line_8_blank_gives_zero() -> None:
    assert compute(None, "0.00") == Artifact(LINE_59, D("0.00"))


def test_the_figure_is_given_as_it_is_and_never_rounded() -> None:
    assert str(compute("5733.504", None).value) == "5733.504"


def test_produces_one_artifact_of_the_output_kind() -> None:
    result = capability().compute(inputs("5733.50", None))

    assert result.outputs == (Artifact(LINE_59, D("5733.50")),)


def test_the_order_of_the_inputs_does_not_matter() -> None:
    (output,) = capability().compute((line_15(None), line_8("5733.50"))).outputs

    assert output == Artifact(LINE_59, D("5733.50"))


def test_a_missing_line_8_artifact_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute((line_15("19820.89"),))


def test_a_missing_line_15_artifact_is_refused() -> None:
    with pytest.raises(MissingArtifactError):
        capability().compute((line_8("1586.80"),))


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
        compute("1586.80", "19820.89")

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


def test_with_the_compute_rule_for_each_field_a_blank_line_reaches_the_capability() -> None:
    wired = capability().with_blank_rules(
        {}, per_field={"line_8": {LINE_8: COMPUTE}, "line_15": {LINE_15: COMPUTE}}
    )

    result = wired.run(inputs(None, "19820.89"))

    assert result.outputs == (Artifact(LINE_59, D("19820.89")),)


def test_without_a_rule_for_its_field_a_blank_line_is_refused_by_the_base() -> None:
    with pytest.raises(BlankNotAllowedError):
        capability().run(inputs(None, "19820.89"))


# --- trace -------------------------------------------------------------------------------------


def test_records_one_trace_line_naming_line_8_when_it_is_the_one_used() -> None:
    assert trace_of("1586.80", None) == (
        TaxOnTaxableIncomeLine(
            output=LINE_59,
            used=LINE_8,
            used_amount=D("1586.80"),
            left_blank=LINE_15,
        ),
    )


def test_records_one_trace_line_naming_line_15_when_it_is_the_one_used() -> None:
    assert trace_of(None, "19820.89") == (
        TaxOnTaxableIncomeLine(
            output=LINE_59,
            used=LINE_15,
            used_amount=D("19820.89"),
            left_blank=LINE_8,
        ),
    )


def test_the_trace_line_is_about_the_output_and_holds_the_figure() -> None:
    (line,) = trace_of("5733.50", None)

    assert line.label == LINE_59.label
    assert line.amount == D("5733.50")


def test_the_english_sentence_when_line_8_is_the_figure() -> None:
    assert EnglishTraceRenderer().render_all(trace_of("1586.80", None)) == (
        "Tax on taxable income line 8 (1586.80), with tax on taxable income line 15 left blank, "
        "gives 1586.80.",
    )


def test_the_english_sentence_when_line_15_is_the_figure() -> None:
    assert EnglishTraceRenderer().render_all(trace_of(None, "19820.89")) == (
        "Tax on taxable income line 15 (19820.89), with tax on taxable income line 8 left blank, "
        "gives 19820.89.",
    )


def test_the_english_sentence_shows_cents_for_a_whole_figure() -> None:
    assert EnglishTraceRenderer().render_all(trace_of("5733", None)) == (
        "Tax on taxable income line 8 (5733.00), with tax on taxable income line 15 left blank, "
        "gives 5733.00.",
    )

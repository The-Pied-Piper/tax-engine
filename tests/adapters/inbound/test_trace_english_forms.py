"""Unit tests for the English text of the trace line of a form instance, made-up values.

A `FormInstanceLine` reads as its instance's lines, each inner sentence (rendered by the line's
own renderer) prefixed with "<form>, instance N: " where N is the position from 1, one sentence
per inner line, in order, separated by a newline. The form is named as the manifest names it.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.adapters.inbound.trace_english.forms as english_forms
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.form import FormSet
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import FormInstanceLine, RecordTotalLine, SubtractedLine
from tax_engine.jurisdictions.core.capabilities.subtract import Subtract
from tests.forms import composition

D = Decimal
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
CENT_ROUNDING = ParameterDataset(
    "ex/net_rounding",
    2025,
    ROUNDING_ONLY,
    RoundingOnly(),
    CENT,
    ("https://example.org/rounding",),
)

NET_INCOME = AmountKind("ex/net_income")
GROSS_RENT = AmountKind("ex/gross_rent")
EXPENSES = AmountKind("ex/expenses")
UNIT_AMOUNT = AmountKind("ex/unit_amount")
UNIT_TOTAL = AmountKind("ex/unit_total")

SUBTRACTED = SubtractedLine(
    NET_INCOME, GROSS_RENT, D("12000.00"), EXPENSES, D("2000"), CENT, D("10000.00")
)
TOTAL = RecordTotalLine(UNIT_TOTAL, UNIT_AMOUNT, (D("100"), D("250.50")), D("350.50"))


def render(line: FormInstanceLine) -> str:
    return EnglishTraceRenderer().render(line)


def test_the_forms_renderer_module_registers_the_line() -> None:
    assert english_forms.__name__ == "tax_engine.adapters.inbound.trace_english.forms"
    registry = EnglishRendererRegistry.shared()

    assert registry.for_line_class(FormInstanceLine).line_class is FormInstanceLine


def test_every_inner_sentence_is_prefixed_with_the_form_and_the_instance_position() -> None:
    inner = EnglishTraceRenderer().render_all((SUBTRACTED, TOTAL))

    assert inner == (
        "net_income: gross_rent 12000.00 less expenses 2000 = 10000.00 (half-up to 0.01)",
        "unit_total: item 1 unit_amount 100 + item 2 unit_amount 250.50 = 350.50",
    )
    assert render(FormInstanceLine("ex/rental", 2, (SUBTRACTED, TOTAL))) == (
        "ex/rental, instance 2: net_income: gross_rent 12000.00 less expenses 2000 = 10000.00 "
        "(half-up to 0.01)\n"
        "ex/rental, instance 2: unit_total: item 1 unit_amount 100 + item 2 unit_amount 250.50 "
        "= 350.50"
    )


def test_a_form_without_instances_is_prefixed_with_its_name_and_instance_1() -> None:
    text = render(FormInstanceLine("ex/return", 1, (SUBTRACTED, TOTAL)))

    assert text == (
        "ex/return, instance 1: net_income: gross_rent 12000.00 less expenses 2000 = 10000.00 "
        "(half-up to 0.01)\n"
        "ex/return, instance 1: unit_total: item 1 unit_amount 100 + item 2 unit_amount 250.50 "
        "= 350.50"
    )


def test_the_trace_of_a_form_without_an_instances_list_reads_as_instance_1() -> None:
    forms = FormSet(
        [
            composition(
                "ex/return",
                [Subtract(CENT_ROUNDING, GROSS_RENT, EXPENSES, NET_INCOME)],
                exports=[NET_INCOME],
                starting=frozenset({GROSS_RENT, EXPENSES}),
            )
        ],
        inputs=frozenset({GROSS_RENT, EXPENSES}),
    )
    worksheets = forms.compute(Artifact(GROSS_RENT, D("12000")), Artifact(EXPENSES, D("2000")))

    (line,) = forms.trace(worksheets)

    assert isinstance(line, FormInstanceLine)
    assert render(line) == (
        "ex/return, instance 1: net_income: gross_rent 12000 less expenses 2000 = 10000.00 "
        "(half-up to 0.01)"
    )


def test_the_position_counts_from_1() -> None:
    text = render(FormInstanceLine("ex/rental", 1, (TOTAL,)))

    assert text.startswith("ex/rental, instance 1: unit_total: ")


def test_the_inner_lines_keep_their_order() -> None:
    reversed_lines = FormInstanceLine("ex/rental", 3, (TOTAL, SUBTRACTED))

    first, second = render(reversed_lines).split("\n")

    assert first.startswith("ex/rental, instance 3: unit_total")
    assert second.startswith("ex/rental, instance 3: net_income")


def test_the_trace_renderer_renders_form_lines_among_others() -> None:
    trace = (
        FormInstanceLine("ex/rental", 1, (TOTAL,)),
        FormInstanceLine("ex/rental", 2, (TOTAL,)),
        RecordTotalLine(UNIT_TOTAL, UNIT_AMOUNT, (D("1"), D("2")), D("3")),
    )

    assert EnglishTraceRenderer().render_all(trace) == (
        "ex/rental, instance 1: unit_total: item 1 unit_amount 100 + item 2 unit_amount 250.50 "
        "= 350.50",
        "ex/rental, instance 2: unit_total: item 1 unit_amount 100 + item 2 unit_amount 250.50 "
        "= 350.50",
        "unit_total: item 1 unit_amount 1 + item 2 unit_amount 2 = 3",
    )

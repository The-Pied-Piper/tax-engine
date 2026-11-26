"""NS428 (2025) line 27, the pension income amount, rejected above its printed maximum.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF; its text version
matches on this line): "Line 27 and line 58360: Pension income amount (maximum $1,173)". No
arithmetic is printed, so line 27 is an entry line: the entered amount is rejected above the
printed maximum, not capped. The maximum is the `ca-ns/pension_income_amount_maximum` dataset,
supplied by a first `core/credit_amount` step that carries a plain-words title and no line number
(it is not a line of the form); the second step, `core/at_most`, is line 27 and carries the title
"Pension income amount" and the reference "27". The input is optional and read as 0 when left out,
so the checked amount is never blank.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError, NegativeArtifactError
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import AtMostLine
from tests.jurisdictions.ca_ns import ns428_credits_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal
LINE_PART = s.NS_PARTS / "ns428_line_27.yaml"
NEEDS = (
    "ns428_line_27_input.yaml",
    "ns428_line_27.yaml",
)
EXPORTS = (s.LINE_27,)


def _sheet(tmp_path: Path, salary: str, *given: Artifact[Any]) -> Any:
    return s.sheet(tmp_path, salary, NEEDS, EXPORTS, given)


CASES = [("20000", "0"), ("30000", "0"), ("70000", "0")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_27_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert s.value(_sheet(tmp_path, salary), s.LINE_27) == D(expected)


KINDS = [
    (s.PENSION, ns_catalog.NS428_PENSION_INCOME_AMOUNT),
    (s.PENSION_MAXIMUM, ns_catalog.NS428_PENSION_INCOME_AMOUNT_MAXIMUM),
    (s.LINE_27, ns_catalog.NS428_PENSION_INCOME_AMOUNT_CHECKED_LINE_27),
]


@pytest.mark.parametrize(("identifier", "declared"), KINDS)
def test_each_kind_is_a_registered_non_negative_amount_kind(
    identifier: str, declared: AmountKind
) -> None:
    kind = nova_scotia_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is declared
    assert identifier in nova_scotia_kinds().identifiers()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_exactly_the_printed_steps() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["capabilities"] == [
        {
            "name": "core/credit_amount",
            "title": "Most you can claim for pension income",
            "unit": "ca/cad",
            "params": {"amount": "ca-ns/pension_income_amount_maximum"},
            "produces": {"output": "ca-ns/ns428_pension_income_amount_maximum"},
        },
        {
            "name": "core/at_most",
            "title": "Pension income amount",
            "reference": "27",
            "unit": "ca/cad",
            "consumes": {
                "amount": "ca-ns/ns428_pension_income_amount",
                "bound": "ca-ns/ns428_pension_income_amount_maximum",
            },
            "produces": {"output": "ca-ns/ns428_pension_income_amount_checked_line_27"},
        },
    ]


MAXIMUM = D("1173")


def _line(tmp_path: Path, pension: str | None = None, salary: str = "70000") -> Any:
    given = [] if pension is None else [Artifact(s.kind(s.PENSION), D(pension))]
    return _sheet(tmp_path, salary, *given)


@pytest.mark.parametrize(
    ("pension", "expected"), [("1173", "1173.00"), ("250.50", "250.50"), ("0", "0")]
)
def test_an_amount_up_to_the_maximum_passes_unchanged(
    tmp_path: Path, pension: str, expected: str
) -> None:
    assert s.value(_line(tmp_path, pension), s.LINE_27) == D(expected)


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line(tmp_path, "1173.01")


def test_a_negative_amount_is_refused_by_the_non_negative_kind() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(s.kind(s.PENSION), D("-0.01"))


def test_a_salary_only_run_passes_the_pension_on_as_zero(tmp_path: Path) -> None:
    line = _line(tmp_path).get(s.kind(s.LINE_27))

    assert not line.is_blank
    assert D(line.value) == D(0)


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_the_salary_does_not_change_the_checked_amount(tmp_path: Path, salary: str) -> None:
    assert s.value(_line(tmp_path, "250.50", salary), s.LINE_27) == D("250.50")


def test_the_sheet_prints_the_title_and_the_reference_of_line_27(tmp_path: Path) -> None:
    sheet = _line(tmp_path, "250.50")
    label = s.kind(s.LINE_27).label

    assert sheet.title(label) == "Pension income amount"
    assert sheet.reference(label) == "27"


def test_the_step_traces_one_at_most_line_against_the_printed_maximum(tmp_path: Path) -> None:
    sheet = _line(tmp_path, "250.50")

    (line,) = [
        t for t in sheet.trace if isinstance(t, AtMostLine) and t.output is s.kind(s.LINE_27)
    ]
    assert line.amount_kind is s.kind(s.PENSION)
    assert line.amount_value == D("250.50")
    assert line.bound is s.kind(s.PENSION_MAXIMUM)
    assert line.bound_value == MAXIMUM


def test_the_trace_row_for_line_27_reads_at_most_the_printed_maximum(tmp_path: Path) -> None:
    sheet = _line(tmp_path, "250.50")
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    (row,) = [r for r in rows if ", at most " in r and "(CA$250.50)" in r]
    assert row.index("(CA$250.50)") < row.index(", at most ")
    assert "(CA$1173.00)" in row.split(", at most ")[1]

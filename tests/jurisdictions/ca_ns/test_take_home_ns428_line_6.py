"""NS428 (2025) line 6, line 4 times the line 5 rate, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 2026-11-26): "Line 4 multiplied by the percentage from
line 5 =". The step is `core/multiply_by_rate` with `ca-ns/cent_rounding` (the form states no
rounding rule; half-up to the cent is the project's choice), no title.

Hand figures: 20,000 gives 19,835.00 x 8.79% = 1,743.4965, printed 1,743.50; 30,000 gives
29,735.00 x 8.79% = 2,613.7065, printed 2,613.71; 70,000 gives 8,320.00 x 16.67% = 1,386.944,
printed 1,386.94; 100,000 gives 3,043.00 x 17.5% = 532.525, which rounds half up to 532.53.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.trace import MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_ns import ns428_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal
LINES = (1, 3, 4, 5, 6)
EXPORTS = (s.LINE_4, s.LINE_5, s.LINE_6)


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return s.sheet(tmp_path, salary, LINES, EXPORTS)


def _part() -> Any:
    part = yaml.safe_load(s.part_path(6).read_text(encoding="utf-8"))
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": s.FORM_NAME}
    return part["capabilities"]


HAND = [
    ("20000", "19835.00", "0.0879", "1743.50"),
    ("30000", "29735.00", "0.0879", "2613.71"),
    ("40000", "9128.00", "0.1495", "1364.64"),
    ("70000", "8320.00", "0.1667", "1386.94"),
    ("100000", "3043.00", "0.175", "532.53"),
    ("200000", "44276.00", "0.21", "9297.96"),
]


@pytest.mark.parametrize(("salary", "line_4", "rate", "expected"), HAND)
def test_line_6_is_line_4_times_the_line_5_rate_rounded_half_up_to_the_cent(
    tmp_path: Path, salary: str, line_4: str, rate: str, expected: str
) -> None:
    figures = s.derived(D(salary))
    assert (figures[s.LINE_4], figures[s.LINE_5], figures[s.LINE_6]) == (
        D(line_4),
        D(rate),
        D(expected),
    )
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(s.kind(s.LINE_4)).value == D(line_4)
    assert sheet.get(s.kind(s.LINE_5)).value == D(rate)
    value = sheet.get(s.kind(s.LINE_6)).value
    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(("salary", "line_1"), s.EDGES)
def test_line_6_at_the_bound_values(tmp_path: Path, salary: str, line_1: str) -> None:
    expected = s.derived(D(salary))[s.LINE_6]

    assert _sheet(tmp_path, salary).get(s.kind(s.LINE_6)).value == expected


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("30779.80", "2681.57"),
        ("61595.96", "4560.95"),
        ("96957.00", "5812.50"),
        ("155724.00", "10284.23"),
    ],
)
def test_line_6_at_the_top_of_each_column_is_the_full_columns_tax(
    tmp_path: Path, salary: str, expected: str
) -> None:
    # The full-column tax (30,507 x 8.79%; 30,508 x 14.95%; 34,868 x 16.67%; 58,767 x 17.5%) printed
    # to the cent.
    assert _sheet(tmp_path, salary).get(s.kind(s.LINE_6)).value == D(expected)


@pytest.mark.parametrize("salary", s.ABOVE_TOP)
def test_line_6_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(s.kind(s.LINE_6))

    assert not artifact.is_blank
    assert artifact.value == s.cent((s.taxable_income(D(salary)) - D("154650")) * D("0.21"))


def test_the_trace_names_line_4_times_the_line_5_rate_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line = MultipliedByRateLine(
        output=s.kind(s.LINE_6),
        base_kind=s.kind(s.LINE_4),
        base_value=D("8320.00"),
        rate_kind=s.kind(s.LINE_5),
        rate_value=D("0.1667"),
        rounding=s.parameter_source().get(s.ROUNDING, 2025, ROUNDING_ONLY).rounding,
        result=D("1386.94"),
    )
    assert line in sheet.trace


def test_the_product_reads_in_english_with_its_rate_base_and_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [
        each
        for each in sheet.trace
        if isinstance(each, MultipliedByRateLine) and each.output is s.kind(s.LINE_6)
    ]
    text = EnglishTraceRenderer().render(line)

    assert "(16.67%)" in text
    assert "(8320.00)" in text
    assert text.endswith("gives 1386.94 (rounded to the nearest cent).")


def test_the_part_is_one_untitled_multiply_by_rate_step_over_lines_4_and_5() -> None:
    (step,) = _part()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/multiply_by_rate",
        "reference": "6",
        "unit": "ca/cad",
        "params": {"rounding": s.ROUNDING},
        "consumes": {"base": s.LINE_4, "rate": s.LINE_5},
        "produces": {"output": s.LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = nova_scotia_kinds()

    assert s.LINE_6 in kinds.identifiers()
    kind = kinds.kind(s.LINE_6)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_TAX_ON_EXCESS_LINE_6

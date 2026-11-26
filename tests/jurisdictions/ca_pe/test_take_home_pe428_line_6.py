"""PE428 (2025) line 6, line 4 times the line 5 rate, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26): "Line 4 multiplied by the percentage from
line 5". The step is `core/multiply_by_rate` with `ca-pe/cent_rounding` (the form states no
rounding rule; half-up to the cent is the project's choice), no title.

Hand figures: 20,000 gives 19,835.00 x 9.5% = 1,884.325 and 30,000 gives 29,735.00 x 9.5% =
2,824.825, both exactly halfway, so half up prints 1,884.33 and 2,824.83 (a float would round
down); 70,000 gives 4,679.00 x 16.6% = 776.714, printed 776.71; taxable income 50,000 gives
16,672.00 x 13.47% = 2,245.7184, printed 2,245.72; 120,000 gives 15,000.00 x 17.62% = 2,643.00;
200,000 gives 60,000.00 x 19% = 11,400.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe.catalog as pe_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.trace import MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_pe import pe428_support as s
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
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
    ("20000", "19835.00", "0.095", "1884.33"),
    ("30000", "29735.00", "0.095", "2824.83"),
    ("40000", "6307.00", "0.1347", "849.55"),
    ("50469.70", "16672.00", "0.1347", "2245.72"),
    ("70000", "4679.00", "0.166", "776.71"),
    ("100000", "34270.00", "0.166", "5688.82"),
    ("121074", "15000.00", "0.1762", "2643.00"),
    ("200000", "58926.00", "0.19", "11195.94"),
    ("201074", "60000.00", "0.19", "11400.00"),
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
        ("33629.29", "3166.16"),
        ("65273.74", "4219.88"),
        ("106074", "6697.10"),
        ("141074", "6167.00"),
    ],
)
def test_line_6_at_the_top_of_each_column_is_the_full_columns_tax(
    tmp_path: Path, salary: str, expected: str
) -> None:
    # The full-column tax (33,328 x 9.5%; 31,328 x 13.47%; 40,344 x 16.6%; 35,000 x 17.62%) printed
    # to the cent.
    assert _sheet(tmp_path, salary).get(s.kind(s.LINE_6)).value == D(expected)


@pytest.mark.parametrize("salary", s.ABOVE_TOP)
def test_line_6_has_no_blank_above_the_top_column(tmp_path: Path, salary: str) -> None:
    artifact = _sheet(tmp_path, salary).get(s.kind(s.LINE_6))

    assert not artifact.is_blank
    assert artifact.value == s.cent((s.taxable_income(D(salary)) - D("140000")) * D("0.19"))


def test_the_trace_names_line_4_times_the_line_5_rate_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line = MultipliedByRateLine(
        output=s.kind(s.LINE_6),
        base_kind=s.kind(s.LINE_4),
        base_value=D("4679.00"),
        rate_kind=s.kind(s.LINE_5),
        rate_value=D("0.166"),
        rounding=s.parameter_source().get(s.ROUNDING, 2025, ROUNDING_ONLY).rounding,
        result=D("776.71"),
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

    assert "(16.6%)" in text
    assert "(4679.00)" in text
    assert text.endswith("gives 776.71 (rounded to the nearest cent).")


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
    kinds = prince_edward_island_kinds()

    assert s.LINE_6 in kinds.identifiers()
    kind = kinds.kind(s.LINE_6)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is pe_catalog.PE428_TAX_ON_EXCESS_LINE_6

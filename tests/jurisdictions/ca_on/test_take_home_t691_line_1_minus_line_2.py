"""T691 Part 7, "line 1 minus line 2": the amount AB428 line 67, MB428 line 66 and SK428 line 68
read, as one cent-rounded subtraction with no floor.

Form text (AB428, MB428, SK428): "Form T691: line 1 minus line 2 of Part 7". T691 (2025) Part 7:
line 1 "Minimum amount from line 103 of Part 1", line 2 "Basic federal tax from line 7 of Part 2".
No floor is printed, so the result can be negative and its kind is signed.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tests.federal_forms import FEDERAL_FORMS, form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CODE = JurisdictionCode("CA-ON")
IN1 = "ca/t691_minimum_amount"
IN2 = "ca/t691_basic_federal_tax"
IN13 = "ca/t691_line_8_plus_line_12"
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""


def _figure(take_home_service: TakeHomeService, output: str, **given: str) -> Decimal:
    kinds = bundled_kinds()
    names = {"line_1": IN1, "line_2": IN2, "line_13": IN13}
    starting = [Artifact(kinds.kind(names[key]), D(value)) for key, value in given.items()]
    service = take_home_service(HEADER, "{}\n", *form_part_names("t691"))
    (sheet,) = service.compute(CODE, 2025, *starting)["ca/t691"]
    value = sheet.get(kinds.kind(output)).value
    assert isinstance(value, Decimal)
    return value


def _step(name: str) -> dict[str, Any]:
    part = yaml.safe_load((FEDERAL_FORMS / "t691" / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca/t691"}
    (step,) = part["capabilities"]
    return dict(step)


OUTPUT = "ca/t691_line_1_minus_line_2_of_part_7"


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # 5,000.00 minus 1,200.00.
        ({"line_1": "5000.00", "line_2": "1200.00"}, "3800.00"),
        # Line 2 above line 1: negative, not floored.
        ({"line_1": "1000.00", "line_2": "5000.00"}, "-4000.00"),
        # Line 2 left out reads 0.
        ({"line_1": "5000.00"}, "5000.00"),
        # Both left out read 0.
        ({}, "0.00"),
    ],
)
def test_the_figure_is_line_1_minus_line_2_with_blanks_read_as_0(
    take_home_service: TakeHomeService, given: dict[str, str], expected: str
) -> None:
    assert _figure(take_home_service, OUTPUT, **given) == D(expected)


def test_the_part_is_one_subtract_step_with_no_floor() -> None:
    assert _step("t691_line_1_minus_line_2.yaml") == {
        "name": "core/subtract",
        "title": "Line 1 minus line 2 of Part 7",
        "reference": "1 minus 2",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"amount": IN1, "less": IN2},
        "blank": {"amount": "0", "less": "0"},
        "produces": {"output": OUTPUT},
    }


def test_the_export_kind_is_a_signed_decimal_amount() -> None:
    kind = bundled_kinds().kind(OUTPUT)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)

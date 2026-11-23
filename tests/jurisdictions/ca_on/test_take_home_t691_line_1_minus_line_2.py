"""T691 Part 7, "line 1 minus line 2": the amount AB428 line 67, MB428 line 66 and SK428 line 68
read, as one cent-rounded subtraction.

Form text (AB428, MB428, SK428): "Form T691: line 1 minus line 2 of Part 7". T691 (2025) Part 7:
line 1 "Minimum amount from line 103 of Part 1", line 2 "Basic federal tax from line 7 of Part 2".
No floor is printed, but Part 7 is completed only when minimum tax is payable (Part 5: "If line 11
is positive, complete parts 6 and 7"), so the form's intent is a figure not below 0: the kind is
non-negative and the engine refuses a negative result here.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import CapabilityContractError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tests.federal_forms import FEDERAL_FORMS, form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds, non_negative

D = Decimal


CODE = JurisdictionCode("CA-ON")
NAMES = {
    "line_1": "ca/t691_minimum_amount",
    "line_2": "ca/t691_basic_federal_tax",
    "line_13": "ca/t691_line_8_plus_line_12",
}
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""


def _figure(take_home_service: TakeHomeService, output: str, **given: str) -> Decimal:
    """The T691 form's figure `output`, with the named lines given and the others left blank."""
    kinds = bundled_kinds()
    starting = [Artifact(kinds.kind(NAMES[key]), D(value)) for key, value in given.items()]
    service = take_home_service(HEADER, "{}\n", *form_part_names("t691"))
    (sheet,) = service.compute(TaxCalculationRequest(CODE, 2025, tuple(starting)))["ca/t691"]
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
        # A negative line 2 (no floor is printed on it) raises the figure: 1,000.00 minus -200.00.
        ({"line_1": "1000.00", "line_2": "-200.00"}, "1200.00"),
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


@pytest.mark.parametrize(
    "given",
    [
        # Line 2 above line 1: negative, refused here (the form's intent, see the kind).
        {"line_1": "1000.00", "line_2": "5000.00"},
        # Line 1 blank: any positive line 2 is a negative figure.
        {"line_2": "0.01"},
    ],
)
def test_a_negative_figure_is_refused(
    take_home_service: TakeHomeService, given: dict[str, str]
) -> None:
    with pytest.raises(CapabilityContractError, match="t691_line_1_minus_line_2_of_part_7 -"):
        _figure(take_home_service, OUTPUT, **given)


def test_the_part_is_one_subtract_step_over_the_cent_rounded_lines() -> None:
    assert _step("t691_line_1_minus_line_2.yaml") == {
        "name": "core/subtract",
        "title": "Line 1 minus line 2 of Part 7",
        "reference": "1 minus 2",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"amount": "ca/t691_line_1_amount", "less": "ca/t691_line_2_amount"},
        "produces": {"output": OUTPUT},
    }


def test_the_export_kind_is_a_non_negative_decimal_amount() -> None:
    kind = bundled_kinds().kind(OUTPUT)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

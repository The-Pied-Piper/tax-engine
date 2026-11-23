"""T691 Part 7 line 2: the typed line read as 0 when blank and rounded to the cent."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.federal_forms import FEDERAL_FORMS, form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import bundled_kinds

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


PART = FEDERAL_FORMS / "t691" / "t691_line_2.yaml"
INPUT = "ca/t691_basic_federal_tax"
OUTPUT = "ca/t691_line_2_amount"


def test_line_2_is_one_sum_step_that_reads_the_blank_as_zero_and_rounds_to_the_cent() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca/t691"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "2",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [INPUT]},
        "blank": {INPUT: "0"},
        "produces": {"output": OUTPUT},
    }


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # Line 1 is given large enough that line 1 minus line 2 (which the T691 refuses below 0)
        # is not negative; line 2 is what is read.
        # Left blank: read as 0.
        ({}, "0.00"),
        # A whole-cent figure is kept.
        ({"line_1": "100000.00", "line_2": "1234.56"}, "1234.56"),
        # A half cent rounds half up to the cent.
        ({"line_1": "100000.00", "line_2": "1000.005"}, "1000.01"),
        ({"line_1": "100000.00", "line_2": "0.004"}, "0.00"),
        # No floor is printed: a negative figure is kept, rounded half up to the cent.
        ({"line_1": "100000.00", "line_2": "-250.00"}, "-250.00"),
        ({"line_1": "100000.00", "line_2": "-1000.005"}, "-1000.01"),
    ],
)
def test_the_amount_reads_blank_as_0_and_rounds_to_the_cent(
    take_home_service: TakeHomeService, given: dict[str, str], expected: str
) -> None:
    value = _figure(take_home_service, OUTPUT, **given)

    assert value == D(expected)
    assert str(value) == expected

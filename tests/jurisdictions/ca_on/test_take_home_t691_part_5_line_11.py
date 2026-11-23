"""T691 Part 5 line 11: the typed line read as 0 when blank and rounded to the cent."""

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
NAMES = {"line_11": "ca/t691_line_7_minus_line_10"}
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


PART = FEDERAL_FORMS / "t691" / "t691_part_5_line_11.yaml"
INPUT = "ca/t691_line_7_minus_line_10"
OUTPUT = "ca/t691_part_5_line_11_amount"


def test_line_11_is_one_sum_step_that_reads_the_blank_as_zero_and_rounds_to_the_cent() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca/t691"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "Part 5 line 11",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [INPUT]},
        "blank": {INPUT: "0"},
        "produces": {"output": OUTPUT},
    }


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # Left blank: read as 0.
        ({}, "0.00"),
        # A whole-cent figure is kept.
        ({"line_11": "1234.56"}, "1234.56"),
        # A half cent rounds half up to the cent.
        ({"line_11": "1000.005"}, "1000.01"),
        ({"line_11": "0.004"}, "0.00"),
    ],
)
def test_the_amount_reads_blank_as_0_and_rounds_to_the_cent(
    take_home_service: TakeHomeService, given: dict[str, str], expected: str
) -> None:
    value = _figure(take_home_service, OUTPUT, **given)

    assert value == D(expected)
    assert str(value) == expected

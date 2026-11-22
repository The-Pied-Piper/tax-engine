"""ON428 (2025) line 48, computed from the real part file through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 48: Amount from line 14 of your federal Schedule
9 multiplied by 11.16% =". Schedule 9 line 14 comes from the real Schedule 9 parts, given line 12
as its input; this test declares a header and form of its own and loads the take-home folder's
`on428_line_48.yaml` beside them. The output is `ca-on/on428_donations_credit_at_rate_line_48`,
exported by the form. The hand figures are asserted (not a CRA example)."""

from __future__ import annotations

from decimal import Decimal

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import ONTARIO_PARTS, TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_12 = "ca/donations_and_gifts_line_12"
OUTPUT = "ca-on/on428_donations_credit_at_rate_line_48"
PART = "on428_line_48.yaml"

HEADER = "jurisdiction: CA-ON\nversion: 1\nvalid_from_tax_year: 2025\noutputs: []\n"


FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {OUTPUT}
capabilities: []
"""


def _compute(take_home_service: TakeHomeService, line_12: str) -> Decimal:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_12), D(line_12))]
    service = take_home_service(HEADER, FORM, *form_part_names("schedule_9"), PART)
    worksheet = service.compute(CODE, 2025, *given)["ca-on/on428"][0]
    value = worksheet.get(kinds.kind(OUTPUT)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_12", "expected"), [("1000", "89.28"), ("200.50", "0.06"), ("0", "0.00")]
)
def test_line_48(take_home_service: TakeHomeService, line_12: str, expected: str) -> None:
    assert _compute(take_home_service, line_12) == D(expected)


def test_the_part_starts_with_a_record_total_of_the_schedule_9_export() -> None:
    part = yaml.safe_load((ONTARIO_PARTS / PART).read_text(encoding="utf-8"))

    assert "inputs" not in part
    assert part["capabilities"][0] == {
        "name": "core/record_total",
        "title": "Amount from line 14 of your federal Schedule 9",
        "reference": "48 box A",
        "unit": "ca/cad",
        "consumes": {"records": "ca/schedule_9.donations_and_gifts_line_14"},
        "produces": {"output": "ca-on/on428_donations_amount_line_48"},
    }

"""ON428 (2025) lines 56, 58, 59 and 60, the Ontario minimum tax carryover, from the real parts.

Form text (Form ON428, CRA 5006-c-25e.txt, "Ontario minimum tax carryover:"): "Line 56: Enter the
amount from line 53 above."; "Line 57 and line and line 61520: Ontario dividend tax credit (use
Worksheet ON428)"; "Line 58: Line 56 minus line 57 (if negative, enter "0") ="; "Line 59: Amount
from line 40427 of your return multiplied by 24.63% ="; "Line 60 and line 61540: Enter whichever is
less: amount from line 58 or line 59."

Line 53 is declared as an input of a test-local form, line 57 is the real optional input part, and
line 40427 is the T1 lines copied by provinces input, read by line 59 as a record total of that
form's export (the T1 owns the input; line 59 has none of its own). The real parts of lines 56, 58,
59 and 60 are loaded beside them. The figures are hand-computed from the printed rate.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import ONTARIO_PARTS, TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_53 = "ca-on/on428_tax_minus_credits_line_53"
LINE_56 = "ca-on/on428_tax_minus_credits_line_56"
LINE_57 = "ca-on/on428_dividend_tax_credit_line_57"
LINE_58 = "ca-on/on428_tax_minus_dividend_tax_credit_line_58"
LINE_59_AMOUNT = "ca-on/on428_minimum_tax_carryover_amount_line_59"
LINE_59 = "ca-on/on428_minimum_tax_carryover_limit_line_59"
LINE_60 = "ca-on/on428_minimum_tax_carryover_line_60"
LINE_40427 = "ca/minimum_tax_carryover"
EXPORT = "ca/t1_lines_copied_by_provinces.minimum_tax_carryover_line_40427"
PARTS = (
    *form_part_names("t1_lines_copied_by_provinces"),
    "on428_line_57_inputs.yaml",
    "on428_line_56.yaml",
    "on428_line_58.yaml",
    "on428_line_59.yaml",
    "on428_line_60.yaml",
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""
FORM = f"""\
form:
  name: ca-on/on428
  required: true
  exports:
    - {LINE_56}
    - {LINE_58}
    - {LINE_59}
    - {LINE_60}
inputs:
  - name: {LINE_53}
    required: true
capabilities: []
"""


def _steps(name: str) -> list[dict[str, Any]]:
    part = yaml.safe_load((ONTARIO_PARTS / name).read_text(encoding="utf-8"))
    assert part["form"] == {"name": "ca-on/on428"}
    assert "inputs" not in part
    return list(part["capabilities"])


def _figures(
    take_home_service: TakeHomeService, line_53: str, line_57: str | None, line_40427: str | None
) -> dict[str, Decimal]:
    kinds = bundled_kinds()
    given = [Artifact(kinds.kind(LINE_53), D(line_53))]
    if line_57 is not None:
        given.append(Artifact(kinds.kind(LINE_57), D(line_57)))
    if line_40427 is not None:
        given.append(Artifact(kinds.kind(LINE_40427), D(line_40427)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(CODE, 2025, *given)["ca-on/on428"]
    return {
        name: sheet.get(kinds.kind(name)).value for name in (LINE_56, LINE_58, LINE_59, LINE_60)
    }


def test_line_56_58_59_and_60_follow_the_printed_lines_when_line_58_is_the_lesser(
    take_home_service: TakeHomeService,
) -> None:
    # Line 56 is 2,000.00 and line 57 is 500.00, so line 58 is 1,500.00; line 40427 of 1,000.00
    # times 24.63% is line 59, 246.30; the lesser is line 59.
    got = _figures(take_home_service, "2000.00", "500.00", "1000.00")

    assert got == {
        LINE_56: D("2000.00"),
        LINE_58: D("1500.00"),
        LINE_59: D("246.30"),
        LINE_60: D("246.30"),
    }


def test_line_60_is_line_58_when_line_58_is_less_than_line_59(
    take_home_service: TakeHomeService,
) -> None:
    # Line 57 of 1,950.00 leaves line 58 at 50.00, below line 59 of 246.30.
    got = _figures(take_home_service, "2000.00", "1950.00", "1000.00")

    assert got[LINE_58] == D("50.00")
    assert got[LINE_60] == D("50.00")


def test_line_58_is_0_when_line_57_is_not_less_than_line_56(
    take_home_service: TakeHomeService,
) -> None:
    got = _figures(take_home_service, "300.00", "1000.00", "1000.00")

    assert got[LINE_58] == D("0.00")
    assert got[LINE_60] == D("0.00")


def test_a_caller_who_leaves_out_lines_57_and_40427_gets_line_58_as_line_56_and_0_on_line_60(
    take_home_service: TakeHomeService,
) -> None:
    got = _figures(take_home_service, "3311.45", None, None)

    assert got == {
        LINE_56: D("3311.45"),
        LINE_58: D("3311.45"),
        LINE_59: D("0.00"),
        LINE_60: D("0.00"),
    }


def test_line_58_is_line_56_minus_line_57_not_below_zero() -> None:
    (step,) = _steps("on428_line_58.yaml")

    assert step["name"] == "core/subtract_not_below_zero"
    assert step["reference"] == "58"
    assert step["consumes"] == {"amount": LINE_56, "less": LINE_57}
    assert step["blank"] == {"less": "0"}
    assert step["produces"] == {"output": LINE_58}


def test_line_59_is_the_t1_line_40427_total_times_the_rate_of_24_63_percent() -> None:
    total, rate = _steps("on428_line_59.yaml")

    assert total["name"] == "core/record_total"
    assert total["consumes"] == {"records": EXPORT}
    assert total["produces"] == {"output": LINE_59_AMOUNT}
    assert rate["name"] == "core/apply_rate"
    assert rate["params"] == {"rate": "ca-on/minimum_tax_rate"}
    assert rate["consumes"] == {"base": LINE_59_AMOUNT}
    assert rate["produces"] == {"output": LINE_59}


def test_line_60_is_the_lesser_of_lines_58_and_59_under_the_existing_kind() -> None:
    (step,) = _steps("on428_line_60.yaml")

    assert step["name"] == "core/lesser_of"
    assert step["title"] == "Ontario minimum tax carryover"
    assert step["reference"] == "60"
    assert step["produces"] == {"output": LINE_60}
    assert step["consumes"] == {"amounts": [LINE_58, LINE_59]}

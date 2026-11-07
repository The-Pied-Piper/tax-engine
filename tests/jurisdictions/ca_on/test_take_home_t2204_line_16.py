"""T2204 (2025) line 16, computed from the real part file through the real engine.

T2204 line 16: "Enter whichever amount is the least: line 7, line 9 or line 12." The ticket
builds it as the least of three amounts, in this order: line 7 (`ca/t2204_line_7`, the amount from
line 3 less $2,000), line 4 (`ca/t2204_premiums_deducted`, the total premiums deducted) and line 10
(`ca/t2204_line_10`, the residents' EI premium capped at its maximum). The output is
`ca/t2204_line_16`. The three are produced by other parts, so this test declares them as inputs in a
header of its own and loads the take-home folder's `t2204_line_16.yaml` beside it.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.registrations import JURISDICTIONS, parameter_parsers
from tests.capabilities import bundled_capabilities
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
LINE_7 = "ca/t2204_line_7"
LINE_4 = "ca/t2204_premiums_deducted"
LINE_10 = "ca/t2204_line_10"
LINE_16 = "ca/t2204_line_16"
PART = (
    Path(__file__).parents[3]
    / "src/tax_engine/jurisdictions/ca_on/manifests/take_home/t2204_line_16.yaml"
)

HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_7}
    required: true
  - name: {LINE_4}
    required: true
  - name: {LINE_10}
    required: true
outputs:
  - {LINE_7}
capabilities: []
"""

FORM = f"""\
form:
  name: ca/t2204
  required: true
  exports:
    - {LINE_16}
capabilities: []
"""


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over an Ontario package whose take-home folder holds a test header, the form
    declaration and the real part file."""
    folder = tmp_path / "ca_on" / "manifests" / "take_home"
    folder.mkdir(parents=True)
    (folder / "a_manifest.yaml").write_text(dedent(HEADER), encoding="utf-8")
    (folder / "b_t2204.yaml").write_text(dedent(FORM), encoding="utf-8")
    shutil.copy(PART, folder / PART.name)
    roots = {**JURISDICTIONS.roots(), Namespace("ca-on"): tmp_path / "ca_on"}
    return TaxComputationService(
        YamlJurisdictionSource(roots, bundled_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        bundled_capabilities(),
    )


def _line_16(tmp_path: Path, line_7: str, line_4: str, line_10: str) -> Decimal:
    kinds = bundled_kinds()
    worksheet = _service(tmp_path).compute(
        CODE,
        2025,
        Artifact(kinds.kind(LINE_7), D(line_7)),
        Artifact(kinds.kind(LINE_4), D(line_4)),
        Artifact(kinds.kind(LINE_10), D(line_10)),
    )["ca/t2204"][0]
    value = worksheet.get(kinds.kind(LINE_16)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_7", "line_4", "line_10", "line_16"),
    [
        # A $70,000 salary: line 7 is 63,700.00, and line 4 and line 10 are both at the 1,077.48
        # cap, so the three are level and the value is kept.
        ("63700.00", "1077.48", "1077.48", "1077.48"),
        # The same salary with line 4 entered above the cap: line 10 is the least.
        ("63700.00", "1148.00", "1077.48", "1077.48"),
        # A $30,000 salary: line 7 is 28,000.00, and line 4 and line 10 are both 492.00.
        ("28000.00", "492.00", "492.00", "492.00"),
        # A $2,010 salary: line 7 is 10.00, the least of the three, so the refund case.
        ("10.00", "32.96", "32.96", "10.00"),
        # A $1,500 salary: line 7 is 0, so line 16 is 0.
        ("0", "0", "0", "0.00"),
        # Line 4 is the least of the three.
        ("63700.00", "500.00", "1077.48", "500.00"),
    ],
)
def test_line_16_is_the_least_of_lines_7_4_and_10(
    tmp_path: Path, line_7: str, line_4: str, line_10: str, line_16: str
) -> None:
    assert _line_16(tmp_path, line_7, line_4, line_10) == D(line_16)


PARTS = PART.parent
COMPOSED_PARTS = (
    "t2204_line_1.yaml",
    "t2204_line_3.yaml",
    "t2204_line_4.yaml",
    "t2204_line_7.yaml",
    "t2204_line_10.yaml",
    "t2204_line_16.yaml",
)
SALARY = "ca/employment_income"
LINE_4_GIVEN = "ca/t2204_premiums_deducted_given"
COMPOSED_HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {SALARY}
    required: true
  - name: ca/t2204_self_employment_earnings
    required: false
    default: null
    basis: "Total self-employment and other earnings eligible for the EI program"
  - name: {LINE_4_GIVEN}
    required: false
    default: null
    basis: "Total premiums deducted: Residents of other than Quebec"
outputs:
  - {SALARY}
capabilities: []
"""


def _composed_service(tmp_path: Path) -> TaxComputationService:
    """The engine over a test header, the form declaration and the real parts of lines 1, 3, 4, 7,
    10 and 16, so line 16 is computed from the salary alone."""
    folder = tmp_path / "ca_on" / "manifests" / "take_home"
    folder.mkdir(parents=True)
    (folder / "a_manifest.yaml").write_text(COMPOSED_HEADER, encoding="utf-8")
    (folder / "b_t2204.yaml").write_text(dedent(FORM), encoding="utf-8")
    for name in COMPOSED_PARTS:
        shutil.copy(PARTS / name, folder / f"c_{name}")
    roots = {**JURISDICTIONS.roots(), Namespace("ca-on"): tmp_path / "ca_on"}
    return TaxComputationService(
        YamlJurisdictionSource(roots, bundled_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        bundled_capabilities(),
    )


@pytest.mark.parametrize(
    ("salary", "line_4_given", "expected"),
    [
        # Line 4 left blank: the line 4 part computes it (1.64%, at most 1,077.48).
        ("70000", None, "1077.48"),
        ("30000", None, "492.00"),
        ("2010", None, "10.00"),
        ("1500", None, "0.00"),
        # Line 4 given above the cap: line 10 is the least.
        ("70000", "1148.00", "1077.48"),
    ],
)
def test_line_16_from_the_salary_with_line_4_blank_or_given(
    tmp_path: Path, salary: str, line_4_given: str | None, expected: str
) -> None:
    kinds = bundled_kinds()
    starting = [Artifact(kinds.kind(SALARY), D(salary))]
    if line_4_given is not None:
        starting.append(Artifact(kinds.kind(LINE_4_GIVEN), D(line_4_given)))
    worksheet = _composed_service(tmp_path).compute(CODE, 2025, *starting)["ca/t2204"][0]
    assert worksheet.get(kinds.kind(LINE_16)).value == D(expected)

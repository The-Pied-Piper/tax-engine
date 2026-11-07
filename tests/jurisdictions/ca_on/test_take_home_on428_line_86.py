"""ON428 (2025) line 86, computed from the real part files through the real engine.

Form text (Form ON428, CRA 5006-c-25e.txt, lines 275-280): "Line 85 and line 62140: Low-income
individuals and families tax (LIFT) credit (complete Schedule ON428-A)" and "Line 86: Line 84 minus
line 85 (if negative, enter "0") =". Line 84 is a copy of line 83, so line 86 is one
core/subtract_not_below_zero: line 83 (`ca-on/on428_tax_after_foreign_tax_credit_line_83`, required)
less line 85. Line 85 is read from Schedule ON428-A Part A line 20 (`ca-on/lift_credit_single`), a
cross-form read through the form's record list (`ca-on/on428_a.lift_credit_single`), so line 85 is
one core/record_total over that list (`ca-on/on428_lift_credit_line_85`, exported by the form).
Line 86 is `ca-on/on428_tax_after_lift_credit_line_86`, exported by the form.

Line 83 is built by another part, so this test declares it as a required input of its header as a
temporary stand-in. Schedule ON428-A is a second form of the same manifest, so the test writes its
form declaration itself (exporting `ca-on/lift_credit_single`) and loads the real
`on428_a_line_20.yaml` beside it, with its header inputs `ca-on/lift_maximum_credit` and
`ca-on/lift_reduction`. The line 85 and line 86 parts are loaded from the take-home folder.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_on.catalog import LIFT_MAXIMUM_CREDIT, LIFT_REDUCTION
from tax_engine.registrations import JURISDICTIONS, parameter_parsers
from tests.capabilities import bundled_capabilities
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
TAKE_HOME = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "take_home"
LINE_83 = "ca-on/on428_tax_after_foreign_tax_credit_line_83"
LINE_85 = "ca-on/on428_lift_credit_line_85"
LINE_86 = "ca-on/on428_tax_after_lift_credit_line_86"
ON428_A_PART = "on428_a_line_20.yaml"
PART_85 = "on428_line_85.yaml"
PART_86 = "on428_line_86.yaml"

HEADER = dedent(f"""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca-on/lift_maximum_credit
        required: true
      - name: ca-on/lift_reduction
        required: true
      - name: {LINE_83}
        required: true
    outputs:
      - {LINE_83}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: ca-on/on428
      required: true
      exports:
        - {LINE_85}
        - {LINE_86}
    capabilities: []
    """)
FORM_ON428_A = dedent("""\
    form:
      name: ca-on/on428_a
      required: true
      exports:
        - ca-on/lift_credit_single
    capabilities: []
    """)


def _part(name: str) -> bytes:
    """The bytes of the take-home part file `name`, wherever it sits in the folder."""
    found = next(TAKE_HOME.rglob(name), None)
    if found is None:
        pytest.fail(f"{name} is not in the take-home manifest yet")
    return found.read_bytes()


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Ontario take-home manifest: the test header, the ON428 and
    ON428-A form declarations, and the real parts of lines 85 and 86 and of ON428-A line 20.
    The three declarations sort ahead of the parts, because the folder is composed in file-name
    order. Every other namespace is the bundled one.
    """
    folder = tmp_path / "manifests" / "take_home"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_form_on428_a.yaml").write_text(FORM_ON428_A, encoding="utf-8")
    (folder / "03_on428_a_line_20.yaml").write_bytes(_part(ON428_A_PART))
    (folder / "04_on428_line_85.yaml").write_bytes(_part(PART_85))
    (folder / "05_on428_line_86.yaml").write_bytes(_part(PART_86))
    roots = {**JURISDICTIONS.roots(), Namespace("ca-on"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, bundled_kinds()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers()),
        bundled_capabilities(),
    )


def _on428(
    tmp_path: Path, line_83: str, maximum: str, reduction: str
) -> dict[str, tuple[Worksheet, ...]]:
    """The worksheets of the take-home manifest for line 83 and the ON428-A inputs."""
    kinds = bundled_kinds()
    given = [
        Artifact(kinds.kind(LINE_83), D(line_83)),
        Artifact(LIFT_MAXIMUM_CREDIT, D(maximum)),
        Artifact(LIFT_REDUCTION, D(reduction)),
    ]
    return _service(tmp_path).compute(CODE, 2025, *given)


def _value(worksheets: dict[str, tuple[Worksheet, ...]], identifier: str) -> Decimal:
    worksheet = worksheets["ca-on/on428"][0]
    value = worksheet.get(bundled_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("line_83", "maximum", "reduction", "line_85"),
    [
        # A $20,000 salary: line 83 is 12.28 and the LIFT credit is the full 875.00, so line 85
        # is 875.00. Line 19 (the reduction) is 0 at this salary.
        ("12.28", "875.00", "0", "875.00"),
        # A $70,000 salary: line 83 is 3,311.45 and the reduction takes the whole maximum, so
        # line 85 is 0.
        ("3311.45", "875.00", "875.00", "0"),
        # A $150,000 salary: line 83 is 14,102.14 and the reduction takes the whole maximum, so
        # line 85 is 0.
        ("14102.14", "875.00", "875.00", "0"),
        # Partly reduced: 875.00 less 356.75 is 518.25.
        ("1000.00", "875.00", "356.75", "518.25"),
        # Reduction above the maximum gives "0", as ON428-A line 20 says.
        ("3311.45", "875.00", "1841.75", "0"),
    ],
)
def test_line_85_is_schedule_on428_a_line_20(
    tmp_path: Path, line_83: str, maximum: str, reduction: str, line_85: str
) -> None:
    assert _value(_on428(tmp_path, line_83, maximum, reduction), LINE_85) == D(line_85)


@pytest.mark.parametrize(
    ("line_83", "maximum", "reduction", "line_86"),
    [
        # A $20,000 salary: line 83 is 12.28 and line 85 is 875.00, so line 86 is 0.
        ("12.28", "875.00", "0", "0.00"),
        # A $70,000 salary: line 83 is 3,311.45 and line 85 is 0, so line 86 is 3,311.45.
        ("3311.45", "875.00", "875.00", "3311.45"),
        # A $150,000 salary: line 83 is 14,102.14 and line 85 is 0, so line 86 is 14,102.14.
        ("14102.14", "875.00", "875.00", "14102.14"),
    ],
)
def test_line_86_is_line_83_minus_line_85_at_each_salary(
    tmp_path: Path, line_83: str, maximum: str, reduction: str, line_86: str
) -> None:
    worksheets = _on428(tmp_path, line_83, maximum, reduction)
    assert _value(worksheets, LINE_86) == D(line_86)


def test_line_86_is_line_83_less_the_partly_reduced_lift_credit(tmp_path: Path) -> None:
    # Line 83 is 1,000.00 and line 85 is 518.25 (875.00 less 356.75), so line 86 is 481.75.
    worksheets = _on428(tmp_path, "1000.00", "875.00", "356.75")
    assert _value(worksheets, LINE_85) == D("518.25")
    assert _value(worksheets, LINE_86) == D("481.75")


@pytest.mark.parametrize(
    ("line_83", "maximum", "reduction", "line_86"),
    [
        # Line 85 (875.00) above line 83 (300.00) gives "0", as the form says.
        ("300.00", "875.00", "0", "0"),
        # Exactly equal: the difference is zero.
        ("875.00", "875.00", "0", "0"),
    ],
)
def test_line_86_is_0_when_line_85_is_not_less_than_line_83(
    tmp_path: Path, line_83: str, maximum: str, reduction: str, line_86: str
) -> None:
    assert _value(_on428(tmp_path, line_83, maximum, reduction), LINE_86) == D(line_86)

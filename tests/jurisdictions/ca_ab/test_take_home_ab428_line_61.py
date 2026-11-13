"""AB428 (2025) line 61, line 59 plus line 60, real parts.

Form text (Form AB428, CRA 5009-c): "Line 61: Line 59 plus line 60 = ^". The form prints no title
for the line beyond its label, so the step is untitled.

Line 61 is one core/sum step (`ab428_line_61.yaml`, as Ontario's line 55 is), rounded through
`ca-ab/cent_rounding`, over line 59 (`ca-ab/ab428_alberta_tax_on_taxable_income_line_59`) and
line 60 (`ca-ab/ab428_tax_on_split_income_line_60`, Form T1206). Line 60 is an optional input that a
salary-only caller leaves out: it is read as blank, the step reads that blank as 0 and prints its
own "Left blank, taken as 0" row. The output is `ca-ab/ab428_tax_line_61`, on the form
`ca-ab/ab428`.

The test composes the real parts that lead to line 59 (the salary, the federal T1 taxable income
parts, AB428 lines 1 to 15 and line 59), the real line 60 inputs part and the new
`ab428_line_61.yaml`, and types in only the salary (line 60 is given only where a test says so). Two
form declarations are test-local: `ca-ab/ab428_credits` exports lines 1, 3 to 8 and 10 to 15, and
`ca-ab/ab428` exports lines 59 and 61 (the real `ab428.yaml` exports line 75, which is not built).

Figures (hand-computed from the printed forms and the repo figures, not a CRA example; a salary of
20,000 / 70,000 / 200,000 is a taxable income of 19,835.00 / 69,335.00 / 198,926.00): line 59 is
1,586.80 / 5,733.50 / 19,820.89 and line 60 is blank (0), so line 61 is the same.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_ab.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_ALBERTA_TAX_ON_TAXABLE_INCOME_LINE_59,
    AB428_TAX_LINE_61,
    AB428_TAX_ON_SPLIT_INCOME_LINE_60,
)
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-AB")
CREDITS = "ca-ab/ab428_credits"
TAX = "ca-ab/ab428"
LINE_1 = "ca-ab/ab428_taxable_income_line_1"
LINE_3 = "ca-ab/ab428_bracket_lower_bound_line_3"
LINE_4 = "ca-ab/ab428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-ab/ab428_bracket_rate_line_5"
LINE_6 = "ca-ab/ab428_tax_on_excess_line_6"
LINE_7 = "ca-ab/ab428_bracket_tax_at_start_line_7"
LINE_8 = "ca-ab/ab428_tax_on_taxable_income_line_8"
LINE_10 = "ca-ab/ab428_bracket_lower_bound_line_10"
LINE_11 = "ca-ab/ab428_taxable_income_over_lower_bound_line_11"
LINE_12 = "ca-ab/ab428_bracket_rate_line_12"
LINE_13 = "ca-ab/ab428_tax_on_excess_line_13"
LINE_14 = "ca-ab/ab428_bracket_tax_at_start_line_14"
LINE_15 = "ca-ab/ab428_tax_on_taxable_income_line_15"
LINE_59 = "ca-ab/ab428_alberta_tax_on_taxable_income_line_59"
LINE_60 = "ca-ab/ab428_tax_on_split_income_line_60"
LINE_61 = "ca-ab/ab428_tax_line_61"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = ALBERTA_PARTS / "ab428_line_61.yaml"
# The real Alberta parts, in composition order: line 1, lines 3 to 8, lines 10 to 15, line 59, the
# line 60 input and line 61.
ALBERTA_LINE_PARTS = (
    "ab428_credits_line_1.yaml",
    "ab428_line_3.yaml",
    "ab428_line_4.yaml",
    "ab428_credits_line_5.yaml",
    "ab428_line_6.yaml",
    "ab428_line_7.yaml",
    "ab428_line_8.yaml",
    "ab428_line_10.yaml",
    "ab428_line_11.yaml",
    "ab428_line_12.yaml",
    "ab428_line_13.yaml",
    "ab428_line_14.yaml",
    "ab428_line_15.yaml",
    "ab428_line_59.yaml",
    "ab428_line_60_inputs.yaml",
    PART.name,
)
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS}
      title: "Form AB428: Alberta Tax and Credits"
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
        - {LINE_5}
        - {LINE_6}
        - {LINE_7}
        - {LINE_8}
        - {LINE_10}
        - {LINE_11}
        - {LINE_12}
        - {LINE_13}
        - {LINE_14}
        - {LINE_15}
    capabilities: []
    """)
TAX_FORM = dedent(f"""\
    form:
      name: {TAX}
      title: "Form AB428: Alberta Tax and Credits"
      required: true
      exports:
        - {LINE_59}
        - {LINE_61}
    capabilities: []
    """)
# salary, line 59 (line 60 left out, read as 0), line 61: re-derived from the printed forms.
CASES = [
    ("20000", "1586.80", "1586.80"),
    ("70000", "5733.50", "5733.50"),
    ("200000", "19820.89", "19820.89"),
]


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield "salary.yaml", (ALBERTA_PARTS / "salary.yaml").read_text(encoding="utf-8")
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    for name in ALBERTA_LINE_PARTS:
        yield name, (ALBERTA_PARTS / name).read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest: a test header, the two test-local form
    declarations and the real parts from the salary to line 61."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_tax_form.yaml").write_text(TAX_FORM, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=3):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, line_60: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_60 is not None:
        given.append(Artifact(AB428_TAX_ON_SPLIT_INCOME_LINE_60, D(line_60)))
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
    (sheet,) = worksheets[TAX]
    return sheet


@pytest.mark.parametrize(("salary", "line_59", "expected"), CASES)
def test_line_61_is_line_59_when_line_60_is_left_out(
    tmp_path: Path, salary: str, line_59: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(AB428_ALBERTA_TAX_ON_TAXABLE_INCOME_LINE_59).value == D(line_59)
    assert sheet.get(AB428_TAX_LINE_61).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "line_60", "expected"),
    [
        # Line 59 is 5,733.50 at 70,000; line 60 is added to it.
        ("70000", "100.00", "5833.50"),
        # A line 60 of 0.00 given is the same as blank.
        ("70000", "0.00", "5733.50"),
        # A line 60 with cents: 1,586.80 + 12.34 = 1,599.14.
        ("20000", "12.34", "1599.14"),
        # The upper table: 19,820.89 + 1,234.56 = 21,055.45.
        ("200000", "1234.56", "21055.45"),
        # The form prints no floor for line 61, so a line 60 below minus line 59 is not refused.
        ("70000", "-6000.00", "-266.50"),
    ],
)
def test_line_61_is_line_59_plus_line_60_when_line_60_is_given(
    tmp_path: Path, salary: str, line_60: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_60)

    assert sheet.get(AB428_TAX_LINE_61).value == D(expected)


def test_line_61_is_rounded_half_up_to_the_cent(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "0.005")

    # 5,733.50 plus 0.005 is 5,733.505, rounded half-up to 5,733.51.
    assert sheet.get(AB428_TAX_LINE_61).value == D("5733.51")


def _left_blank_rows(rows: Sequence[str]) -> int:
    return sum("Left blank, taken as 0" in row for row in rows)


def test_the_trace_has_a_gives_row_for_line_61(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000", "100.00").trace)

    assert any("5833.50" in row and "gives" in row for row in rows)


def test_a_left_out_line_60_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    given_dir = tmp_path / "given"
    given_dir.mkdir()
    blank = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)
    given = EnglishTraceRenderer().render_all(_sheet(given_dir, "70000", "100.00").trace)

    # Other steps on the sheet print their own blank rows either way; line 61's is the difference.
    assert _left_blank_rows(blank) == _left_blank_rows(given) + 1
    assert any("5733.50" in row and "gives" in row for row in blank)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": TAX}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step["name"] == "core/sum"
    assert step["reference"] == "61"
    assert step["unit"] == "ca/cad"
    assert step["params"] == {"rounding": "ca-ab/cent_rounding"}
    assert step["consumes"] == {"parts": [LINE_59, LINE_60]}
    assert step["blank"] == {LINE_60: "0"}
    assert step["produces"] == {"output": LINE_61}


def test_line_61_is_a_registered_signed_amount_kind() -> None:
    kinds = alberta_kinds()

    assert LINE_61 in kinds.identifiers()
    kind = kinds.kind(LINE_61)
    assert isinstance(kind, AmountKind)
    assert not kind.non_negative
    assert kind is AB428_TAX_LINE_61

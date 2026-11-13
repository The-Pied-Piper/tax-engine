"""AB428 (2025) line 59, Alberta tax on taxable income from line 8 or line 15, real parts.

Form text (Form AB428, CRA 5009-c): "Line 59: Alberta tax on taxable income from line 8 or line 15
^". Under line 8: "If you completed lines 2 to 8 for a column above, enter the amount from line 8
on line 59 and continue on line 16." Under line 15: "If you completed lines 9 to 15 for a column
above, enter the amount from line 15 on line 59 and continue on line 16."

Line 59 is one calculation step, the Alberta capability `ca-ab/tax_on_taxable_income`
(`ab428_line_59.yaml`), not a copy line: it reads the line 8 and line 15 exports of
`ca-ab/ab428_credits` as record lists (another form reads an export only as a record list, and
`core/record_total` and `core/sum` read one list or plain amounts), and gives the one that has a
figure. The other is blank, because line 1 is outside its table. Its output is
`ca-ab/ab428_alberta_tax_on_taxable_income_line_59`, on the form `ca-ab/ab428`.

The salary is the only input. Line 59 is composed from the real parts that lead to it: the salary,
the federal T1 taxable income parts, line 1 (`ab428_credits_line_1.yaml`), lines 3, 4, 5, 6, 7 and
8 (`ab428_line_3.yaml`, `ab428_line_4.yaml`, `ab428_credits_line_5.yaml`, `ab428_line_6.yaml`,
`ab428_line_7.yaml`, `ab428_line_8.yaml`), lines 10 to 15 (`ab428_line_10.yaml` to
`ab428_line_15.yaml`) and line 59. Two form declarations are test-local: `ca-ab/ab428_credits`
exports lines 1, 3 to 8 and 10 to 15, and `ca-ab/ab428` exports line 59 only (the real
`ab428.yaml` exports line 75, which is not built).

Figures (hand-computed from the printed forms and the repo figures, not a CRA example; a salary of
20,000 / 70,000 / 200,000 is a taxable income, line 1, of 19,835.00 / 69,335.00 / 198,926.00):
- 19,835.00 is in the table of lines 2 to 8: line 8 = 19,835.00 x 8% = 1,586.80.
- 69,335.00: line 8 = 60,000 x 8% + 9,335.00 x 10% = 4,800.00 + 933.50 = 5,733.50.
- 198,926.00 is in the table of lines 9 to 15, column 1 (over 181,481): line 15 =
  17,553.04 + 17,445.00 x 13% = 17,553.04 + 2,267.85 = 19,820.89, where 17,553.04 =
  4,800.00 + 9,123.40 + 3,629.64 is the tax on the first 181,481.
Line 59 is 1,586.80 / 5,733.50 / 19,820.89.
"""

from __future__ import annotations

from collections.abc import Iterator
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
)
from tax_engine.jurisdictions.ca_ab.trace import TaxOnTaxableIncomeLine
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative
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
TITLE = "Alberta tax on taxable income from line 8 or line 15"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = ALBERTA_PARTS / "ab428_line_59.yaml"
# The real Alberta parts, in composition order: line 1, lines 3 to 8, lines 10 to 15, line 59.
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
# The AB428 credits declaration, test-local: lines 1, 3 to 8 and 10 to 15 are composed, so it
# exports those (line 59 reads lines 8 and 15 from it).
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
    capabilities: []
    """)
# salary, the line line 59 takes, line 59: line 8 gives the first two, line 15 the third.
CASES = [
    ("20000", LINE_8, "1586.80"),
    ("70000", LINE_8, "5733.50"),
    ("200000", LINE_15, "19820.89"),
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
    declarations and the real parts from the salary to line 59."""
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


def _sheets(tmp_path: Path, salary: str) -> tuple[Worksheet, Worksheet]:
    """The credits sheet (lines 8 and 15) and the tax sheet (line 59) for one salary."""
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (credits_sheet,) = worksheets[CREDITS]
    (tax_sheet,) = worksheets[TAX]
    return credits_sheet, tax_sheet


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    return _sheets(tmp_path, salary)[1]


def _kind(identifier: str) -> AmountKind:
    kind = alberta_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("salary", "used", "expected"), CASES)
def test_line_59_is_the_line_that_has_a_figure(
    tmp_path: Path, salary: str, used: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_59)).value == D(expected)


@pytest.mark.parametrize(("salary", "used", "expected"), CASES)
def test_line_59_traces_one_line_naming_the_line_it_took(
    tmp_path: Path, salary: str, used: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    (line,) = [t for t in sheet.trace if isinstance(t, TaxOnTaxableIncomeLine)]
    blank = LINE_15 if used == LINE_8 else LINE_8
    assert line == TaxOnTaxableIncomeLine(
        output=_kind(LINE_59),
        used=_kind(used),
        used_amount=D(expected),
        left_blank=_kind(blank),
    )


def test_line_59_equals_the_real_line_8_for_a_salary_in_the_lines_2_to_8_table(
    tmp_path: Path,
) -> None:
    credits_sheet, tax_sheet = _sheets(tmp_path, "20000")

    assert tax_sheet.get(_kind(LINE_59)).value == credits_sheet.get(_kind(LINE_8)).value


def test_line_59_equals_the_real_line_15_for_a_salary_in_the_lines_9_to_15_table(
    tmp_path: Path,
) -> None:
    credits_sheet, tax_sheet = _sheets(tmp_path, "200000")

    assert tax_sheet.get(_kind(LINE_59)).value == credits_sheet.get(_kind(LINE_15)).value


def test_the_english_trace_names_the_forms_lines_and_shows_cents(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")

    sentences = EnglishTraceRenderer().render_all(
        [t for t in sheet.trace if isinstance(t, TaxOnTaxableIncomeLine)], sheet
    )

    assert sentences == (
        "Line 8 of AB428 (CA$1586.80), with line 15 of AB428 left blank, gives CA$1586.80.",
    )


# The two refusals (both lines blank, both lines with a figure) cannot arise from a salary: line 1
# is always in exactly one of the two tables. They are pinned on the capability itself in
# tests/jurisdictions/ca_ab/capabilities/test_tax_on_taxable_income.py.


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": TAX}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_step_that_reads_the_two_exports_across_the_form_boundary() -> None:
    assert _step() == {
        "name": "ca-ab/tax_on_taxable_income",
        "title": TITLE,
        "reference": "59",
        "unit": "ca/cad",
        "consumes": {
            "line_8": f"{CREDITS}.{LINE_8[len('ca-ab/') :]}",
            "line_15": f"{CREDITS}.{LINE_15[len('ca-ab/') :]}",
        },
        "blank": {
            "line_8": {LINE_8: "compute"},
            "line_15": {LINE_15: "compute"},
        },
        "produces": {"output": LINE_59},
    }


def test_the_step_consumes_the_record_lists_ca_ab_ab428_credits_exports() -> None:
    consumes = _step()["consumes"]

    assert consumes == {
        "line_8": "ca-ab/ab428_credits.ab428_tax_on_taxable_income_line_8",
        "line_15": "ca-ab/ab428_credits.ab428_tax_on_taxable_income_line_15",
    }


def test_the_step_keys_are_in_the_order_of_the_other_alberta_parts() -> None:
    # name, title, reference, unit, then the slots (no params here): consumes, blank, produces.
    assert list(_step()) == [
        "name",
        "title",
        "reference",
        "unit",
        "consumes",
        "blank",
        "produces",
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = alberta_kinds().kind(LINE_59)

    assert kind is AB428_ALBERTA_TAX_ON_TAXABLE_INCOME_LINE_59
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_59
    assert kind.value_type is Decimal
    assert non_negative(kind)

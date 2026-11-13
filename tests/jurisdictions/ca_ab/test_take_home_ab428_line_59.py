"""AB428 (2025) line 59, Alberta tax on taxable income from line 8 or line 15, real part.

Form text (Form AB428, CRA 5009-c): "Line 59: Alberta
tax on taxable income from line 8 or line 15 ^". Under line 8: "If you completed lines 2 to 8 for a
column above, enter the amount from line 8 on line 59 and continue on line 16." Under line 15: "If
you completed lines 9 to 15 for a column above, enter the amount from line 15 on line 59 and
continue on line 16."

Line 59 is one calculation step, the Alberta capability `ca-ab/tax_on_taxable_income`
(`ab428_line_59.yaml`), not a copy line: it reads the line 8 and line 15 exports of
`ca-ab/ab428_credits` as record lists (another form reads an export only as a record list, and
`core/record_total` and `core/sum` read one list or plain amounts), and gives the one that has a
figure. The other is blank, because line 1 is outside its table. Its output is
`ca-ab/ab428_alberta_tax_on_taxable_income_line_59`, on the form `ca-ab/ab428`.

STAND-IN: the line 8 and line 15 parts are not built yet. This test supplies them as two optional
inputs of the line 8 and line 15 kinds, and a test-local `ca-ab/ab428_credits` form that exports
them, so the line 8 and line 15 record lists exist and the real line 59 part can read them. It is
replaced by the real line 8 and line 15 parts, with the salary as the only input, once they are on
main. The test-local `ca-ab/ab428` form declaration exports line 59 only.

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

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
import tax_engine.jurisdictions.ca_ab.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import ValidationError
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

D = Decimal
CODE = JurisdictionCode("CA-AB")
CREDITS = "ca-ab/ab428_credits"
TAX = "ca-ab/ab428"
LINE_8 = "ca-ab/ab428_tax_on_taxable_income_line_8"
LINE_15 = "ca-ab/ab428_tax_on_taxable_income_line_15"
LINE_59 = "ca-ab/ab428_alberta_tax_on_taxable_income_line_59"
TITLE = "Alberta tax on taxable income from line 8 or line 15"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
PART = ALBERTA_PARTS / "ab428_line_59.yaml"

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The stand-in for the line 8 and line 15 parts: two optional inputs, blank when left out, and the
# form that exports them.
STAND_IN_INPUTS = dedent(f"""\
    inputs:
      - name: {LINE_8}
        reference: "8"
        unit: ca/cad
        required: false
        default: null
        basis: stand-in for AB428 line 8 until the line 8 part is built
      - name: {LINE_15}
        reference: "15"
        unit: ca/cad
        required: false
        default: null
        basis: stand-in for AB428 line 15 until the line 15 part is built
    """)
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS}
      title: "Form AB428: Alberta Tax and Credits"
      required: true
      exports:
        - {LINE_8}
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
# salary, line 8, line 15, line 59: line 8 gives the first two, line 15 the third.
CASES = [
    ("20000", "1586.80", None, "1586.80"),
    ("70000", "5733.50", None, "5733.50"),
    ("200000", None, "19820.89", "19820.89"),
]


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest: a test header, the stand-in for lines 8 and
    15, a form declaration for line 59 and the real salary and line 59 parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    texts = [
        ("header.yaml", HEADER),
        ("credits_form.yaml", CREDITS_FORM),
        ("tax_form.yaml", TAX_FORM),
        ("stand_in_inputs.yaml", STAND_IN_INPUTS),
        ("salary.yaml", (ALBERTA_PARTS / "salary.yaml").read_text(encoding="utf-8")),
        (PART.name, PART.read_text(encoding="utf-8")),
    ]
    for number, (name, text) in enumerate(texts):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, line_8: str | None, line_15: str | None) -> Worksheet:
    kinds = alberta_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_8 is not None:
        given.append(Artifact(kinds.kind(LINE_8), D(line_8)))
    if line_15 is not None:
        given.append(Artifact(kinds.kind(LINE_15), D(line_15)))
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)[TAX]
    return sheet


@pytest.mark.parametrize(("salary", "line_8", "line_15", "expected"), CASES)
def test_line_59_is_the_line_that_has_a_figure(
    tmp_path: Path, salary: str, line_8: str | None, line_15: str | None, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_8, line_15)

    assert sheet.get(alberta_kinds().kind(LINE_59)).value == D(expected)


@pytest.mark.parametrize(("salary", "line_8", "line_15", "expected"), CASES)
def test_line_59_traces_one_line_naming_the_line_it_took(
    tmp_path: Path, salary: str, line_8: str | None, line_15: str | None, expected: str
) -> None:
    kinds = alberta_kinds()
    sheet = _sheet(tmp_path, salary, line_8, line_15)

    (line,) = [t for t in sheet.trace if isinstance(t, TaxOnTaxableIncomeLine)]
    used, blank = (LINE_8, LINE_15) if line_8 is not None else (LINE_15, LINE_8)
    assert line == TaxOnTaxableIncomeLine(
        output=kinds.kind(LINE_59),
        used=kinds.kind(used),
        used_amount=D(expected),
        left_blank=kinds.kind(blank),
    )


def test_the_english_trace_names_the_forms_lines_and_shows_cents(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000", "1586.80", None)

    sentences = EnglishTraceRenderer().render_all(
        [t for t in sheet.trace if isinstance(t, TaxOnTaxableIncomeLine)], sheet
    )

    assert sentences == (
        "Line 8 of AB428 (CA$1586.80), with line 15 of AB428 left blank, gives CA$1586.80.",
    )


def test_both_lines_blank_is_refused_naming_the_lines(tmp_path: Path) -> None:
    # A form cannot leave both blank: line 1 is in exactly one of the two tables.
    with pytest.raises(ValidationError, match=r"line 8.*line 15|line 15.*line 8"):
        _sheet(tmp_path, "20000", None, None)


def test_both_lines_with_a_figure_is_refused_naming_the_lines(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match=r"line 8.*line 15|line 15.*line 8"):
        _sheet(tmp_path, "20000", "1586.80", "19820.89")


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

"""BC428 (2025) line 8, the British Columbia tax on taxable income, real engine.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Column 1: Line 1 is $49,279 or less / Line 8:
Line 6 plus line 7 British Columbia tax on taxable income = ^", and the same Line 8 under "Column 2:
Line 1 is more than $49,279 but not more than $98,560", "Column 3: Line 1 is more than $98,560 but
not more than $113,158" and "Column 4: Line 1 is more than $113,158 but not more than $137,407".
Line 6 is the tax on the taxable income over the column's lower bound, rounded to the cent, and line
7 is the printed tax at the start of that column (0.00, 2,493.52, 6,288.15, 7,820.94), so line 8 is
their sum. The sum is taken once, rounded half-up to the cent by `ca-bc/cent_rounding`, which
changes nothing since both parts are already in cents. It is blank when lines 6 and 7 are blank (a
line 1 above 137,407, where the lines 2 to 8 table does not apply).

Lines 1, 3, 4, 5, 6 and 7 are composed from their real parts as they are: line 1
`ca-bc/bc428_taxable_income_line_1` (`bc428_line_1.yaml`), line 3
`ca-bc/bc428_bracket_lower_bound_line_3` (`bc428_line_3.yaml`), line 4
`ca-bc/bc428_taxable_income_over_lower_bound_line_4` (`bc428_line_4.yaml`), line 5
`ca-bc/bc428_bracket_rate_line_5` (`bc428_line_5.yaml`), line 6 `ca-bc/bc428_bracket_tax_line_6`
(`bc428_line_6.yaml`) and line 7 `ca-bc/bc428_bracket_tax_at_start_line_7` (`bc428_line_7.yaml`).
Line 8 is one `core/sum` step over lines 6 and 7, output `ca-bc/bc428_tax_on_taxable_income_line_8`,
in the part `bc428_line_8.yaml`. The form declaration is test-local. The service is built over the
package list of `support.py`.

Figures (ticket, hand-computed, not a CRA example): taxable income is the salary less the CPP
enhanced and second-ceiling amounts, 16,865.00 / 69,335.00 / 198,926.00, so
line 8 is 853.37 + 0.00 / 1,544.31 + 2,493.52 = 4,037.83 /
blank, for salaries of 17,000 / 70,000 / 200,000.

Column edges (the two kept here) are driven from a given line 1 (the T1 parts are left out), with
line 6 = (line 1 - lower bound) x rate, half-up to the cent, and line 8 = line 6 + printed start: -
49,279.00: 49,279.00 x 0.0506 = 2,493.5174, so 2,493.52; + 0.00 = 2,493.52. - 98,560.00: 49,281.00 x
0.077 = 3,794.637, so 3,794.64; + 2,493.52 = 6,288.16 (one cent over the printed 6,288.15 start of
column 3: the form's own printed figures do not tie at this edge).
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_TAX_ON_TAXABLE_INCOME_LINE_8,
    BC428_TAXABLE_INCOME_LINE_1,
)
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_3 = "ca-bc/bc428_bracket_lower_bound_line_3"
LINE_4 = "ca-bc/bc428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-bc/bc428_bracket_rate_line_5"
LINE_6 = "ca-bc/bc428_bracket_tax_line_6"
LINE_7 = "ca-bc/bc428_bracket_tax_at_start_line_7"
LINE_8 = "ca-bc/bc428_tax_on_taxable_income_line_8"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_1_PART = BC_PARTS / "bc428_line_1.yaml"
LINE_3_PART = BC_PARTS / "bc428_line_3.yaml"
LINE_4_PART = BC_PARTS / "bc428_line_4.yaml"
LINE_5_PART = BC_PARTS / "bc428_line_5.yaml"
LINE_6_PART = BC_PARTS / "bc428_line_6.yaml"
LINE_7_PART = BC_PARTS / "bc428_line_7.yaml"
LINE_8_PART = BC_PARTS / "bc428_line_8.yaml"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 1, 3, 4, 5, 6, 7 and 8 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
        - {LINE_5}
        - {LINE_6}
        - {LINE_7}
        - {LINE_8}
    capabilities: []
    """)

DIRECT_HEADER = dedent(f"""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - {LINE_1}
    capabilities: []
    """)
# The input line 1 is the caller's, owned by the BC428 form that reads it.
DIRECT_INPUT = dedent(f"""\
    form:
      name: {FORM}
    inputs:
      - name: {LINE_1}
        required: true
    """)
DIRECT_FORM = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_8}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    for found in form_parts("schedule_8"):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            found.read_text("utf-8"),
        )
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
    yield LINE_3_PART.name, LINE_3_PART.read_text(encoding="utf-8")
    yield LINE_4_PART.name, LINE_4_PART.read_text(encoding="utf-8")
    yield LINE_5_PART.name, LINE_5_PART.read_text(encoding="utf-8")
    yield LINE_6_PART.name, LINE_6_PART.read_text(encoding="utf-8")
    yield LINE_7_PART.name, LINE_7_PART.read_text(encoding="utf-8")
    yield LINE_8_PART.name, LINE_8_PART.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _direct(tmp_path: Path, taxable_income: str) -> Artifact[Decimal]:
    """Line 8 from a given line 1, through the real parts and dataset, without the T1 parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(DIRECT_HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(DIRECT_FORM, encoding="utf-8")
    (folder / "01_input.yaml").write_text(DIRECT_INPUT, encoding="utf-8")
    parts = (LINE_3_PART, LINE_4_PART, LINE_5_PART, LINE_6_PART, LINE_7_PART, LINE_8_PART)
    for number, part in enumerate(parts, start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    given = Artifact(BC428_TAXABLE_INCOME_LINE_1, D(taxable_income))
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    service = TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )
    (sheet,) = service.compute(CODE, 2025, given)[FORM]
    return sheet.get(_kind(LINE_8))


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 6 is 853.37 and line 7 is 0.00 (column 1).
        ("17000", "853.37"),
        # Line 6 is 1,544.31 and line 7 is 2,493.52 (column 2).
        ("70000", "4037.83"),
    ],
)
def test_line_8_is_line_6_plus_line_7_for_the_worked_salaries(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_8)).value == D(expected)


def test_line_8_is_blank_when_line_1_is_above_137407(tmp_path: Path) -> None:
    assert _sheet(tmp_path, "200000").get(_kind(LINE_8)).is_blank


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        # Column 1 at its top: line 6 2,493.52 (49,279.00 x 5.06% = 2,493.5174), line 7 0.00.
        ("49279.00", "2493.52"),
        # Column 2 at its top: line 6 3,794.64 (49,281.00 x 7.7% = 3,794.637), line 7 2,493.52.
        ("98560.00", "6288.16"),
    ],
)
def test_line_8_at_and_just_above_each_column_boundary(
    tmp_path: Path, taxable_income: str, expected: str
) -> None:
    assert _direct(tmp_path, taxable_income).value == D(expected)


def test_line_8_one_cent_above_the_table_is_blank(tmp_path: Path) -> None:
    assert _direct(tmp_path, "137407.01").is_blank


def test_the_blank_line_8_says_it_passed_on_the_blanks_of_lines_6_and_7(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    # The kinds in `because` are sorted by identifier: line 7 (bracket_tax_at_start) before line 6.
    line = BlankPassedOnLine(_kind(LINE_8), (_kind(LINE_7), _kind(LINE_6)))

    assert line in sheet.trace
    assert EnglishTraceRenderer().render(line).endswith("were blank.")
    assert not any(
        isinstance(each, SumLine) and each.output is _kind(LINE_8) for each in sheet.trace
    )


def test_the_sum_is_traced_with_its_parts_in_the_order_they_are_wired(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_8)
    )
    assert [(kind, value) for kind, value in line.parts] == [
        (_kind(LINE_6), D("1544.31")),
        (_kind(LINE_7), D("2493.52")),
    ]
    assert line.total == D("4037.83")


def test_the_sum_is_traced_in_english(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_8)
    )
    text = EnglishTraceRenderer().render(line)
    assert "1544.31" in text
    assert "2493.52" in text
    assert "4037.83" in text


def test_the_part_is_one_sum_step_over_lines_6_and_7() -> None:
    part = yaml.safe_load(LINE_8_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "title": "British Columbia tax on taxable income",
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {"parts": [LINE_6, LINE_7]},
        "blank": {LINE_6: "pass_on", LINE_7: "pass_on"},
        "produces": {"output": LINE_8},
    }


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_8)

    assert kind is BC428_TAX_ON_TAXABLE_INCOME_LINE_8
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

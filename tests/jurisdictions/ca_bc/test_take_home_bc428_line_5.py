"""BC428 (2025) line 5, the rate of the column for lines 2 to 8, from the salary alone.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Column 1: Line 1 is $49,279 or less / Line 5:
Rate 5.06%", "Column 2: Line 1 is more than $49,279 but not more than $98,560 / Line 5: Rate 7.7%",
"Column 3: Line 1 is more than $98,560 but not more than $113,158 / Line 5: Rate 10.5%", "Column 4:
Line 1 is more than $113,158 but not more than $137,407 / Line 5: Rate 12.29%". Above 137,407 the
table (`ca-bc/brackets_lines_2_to_8`) does not apply (lines 9 to 15 do), so line 5 is blank.

Line 5 is one `core/bracket_column_rate` step over line 1 with that schedule, output
`ca-bc/bc428_bracket_rate_line_5`, in the part `bc428_line_5.yaml`. The rate is a Decimal artifact,
not rounded; the ticket table's 0.05 is rounded, the dataset's printed rate is 0.0506.

Line 1 is the real `bc428_line_1.yaml` (#903). The real parts composed: the British Columbia salary,
Schedule 8, the T1 taxable-income parts, `bc428_line_1.yaml` and `bc428_line_5.yaml`. The form
declaration is test-local, exporting lines 1 and 5. The service is built over the package list of
`support.py`.

Figures (ticket, hand-computed, not a CRA example): taxable income is the salary less the CPP
enhanced and second-ceiling amounts, 16,865.00 / 69,335.00 / 198,926.00, so
line 5 is 0.0506 for $17,000, 0.077 for $70,000 and blank for $200,000.
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
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketOutsideRangeLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_BRACKET_RATE_LINE_5,
    BC428_TAXABLE_INCOME_LINE_1,
)
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_INPUT

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_5 = "ca-bc/bc428_bracket_rate_line_5"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc428_line_5.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 1 and 3 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_5}
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
        - {LINE_5}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield T1_LINE_10100_INPUT.name, T1_LINE_10100_INPUT.read_text(encoding="utf-8")
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            found.read_text("utf-8"),
        )
    yield "bc428_line_1.yaml", (BC_PARTS / "bc428_line_1.yaml").read_text(encoding="utf-8")
    yield LINE_PART.name, LINE_PART.read_text(encoding="utf-8")


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


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("17000", "0.0506"),
        ("70000", "0.077"),
    ],
)
def test_line_5_is_the_rate_of_the_column_line_1_falls_in_for_the_worked_salaries(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_5)).value == D(expected)


@pytest.mark.parametrize("salary", ["200000", "138482"])
def test_line_5_is_blank_when_line_1_is_above_137407(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_5)).is_blank


def _direct(tmp_path: Path, taxable_income: str) -> Artifact[Decimal]:
    """Line 5 from a given line 1, through the real part and dataset, without the T1 parts."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(DIRECT_HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(DIRECT_FORM, encoding="utf-8")
    (folder / "01_input.yaml").write_text(DIRECT_INPUT, encoding="utf-8")
    (folder / "02_bc428_line_5.yaml").write_text(
        LINE_PART.read_text(encoding="utf-8"), encoding="utf-8"
    )
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
    given = Artifact(BC428_TAXABLE_INCOME_LINE_1, D(taxable_income))
    (sheet,) = service.compute(CODE, 2025, given)[FORM]
    return sheet.get(BC428_BRACKET_RATE_LINE_5)


@pytest.mark.parametrize(
    ("taxable_income", "expected"),
    [
        ("49279.00", "0.0506"),
        ("49279.01", "0.077"),
    ],
)
def test_line_5_at_and_just_above_each_threshold(
    tmp_path: Path, taxable_income: str, expected: str
) -> None:
    assert _direct(tmp_path, taxable_income).value == D(expected)


def test_line_5_one_cent_above_the_table_is_blank(tmp_path: Path) -> None:
    assert _direct(tmp_path, "137407.01").is_blank


def test_the_blank_says_why_in_the_trace(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    line = BracketOutsideRangeLine(_kind(LINE_5), _kind(LINE_1), D("198926.00"))

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith("(198926.00) is outside the range of the bracket table, so it is left blank.")
    )


def test_the_part_is_one_bracket_column_rate_step_over_line_1() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_rate",
        "title": "Rate",
        "reference": "5",
        "params": {"schedule": "ca-bc/brackets_lines_2_to_8"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_5},
    }


def test_line_5_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_5)

    assert kind is BC428_BRACKET_RATE_LINE_5
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

"""BC428 (2025) line 10, the lower bound of the column for lines 9 to 15, from the real parts.

Form text (Form BC428, CRA 5010-c-25e.txt, read 2026-11-14): "Column 1: Line 1 is more than $137,407
but not more than $186,306  Line 10: 137,407.00", "Column 2: Line 1 is more than $186,306 but not
more than $259,829  Line 10: 186,306.00", "Column 3: Line 1 is more than $259,829  Line 10:
259,829.00". Line 9 is a copy of line 1 and has no step. Line 10 is
`core/bracket_column_lower_bound` over line 1 (`ca-bc/bc428_taxable_income_line_1`) with the
`ca-bc/brackets_lines_9_to_15` schedule, output `ca-bc/bc428_bracket_lower_bound_line_10`, as
Alberta's line 10 is.

The table covers only a line 1 above 137,407.00, so line 10 is left blank there: at $17,000
and $70,000 it is blank, at $200,000 (line 1 is 198,926.00) it is 186,306.00. A
blank output is read from the Worksheet as an artifact whose `is_blank` is true (its `value`
raises), and its trace is one `BracketOutsideRangeLine` (output, base, base amount).

Line 1 is a salary's T1 taxable income, so the exact thresholds (137,407.00 and 137,407.01 and the
others) are tested through the capability and the real dataset directly.

The real parts composed: the British Columbia salary, Schedule 8, the T1 taxable-income parts, the
line 1 part (`bc428_line_1.yaml`) and `bc428_line_10.yaml`. The form declaration and header are
test-local, and the service is built over the package list of `support.py`.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.blank import BLANK
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketOutsideRangeLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_BRACKET_LOWER_BOUND_LINE_10
from tax_engine.jurisdictions.core.capabilities.bracket_column_figure import (
    BracketColumnLowerBound,
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
BC = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_10 = "ca-bc/bc428_bracket_lower_bound_line_10"
SCHEDULE = "ca-bc/brackets_lines_9_to_15"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
PART = BC_PARTS / "bc428_line_10.yaml"
LINE_1_PART = BC_PARTS / "bc428_line_1.yaml"
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 1 and 10 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_10}
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
    yield PART.name, PART.read_text(encoding="utf-8")


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
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(BC, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("17000", "16865.00"),
        ("200000", "198926.00"),
    ],
)
def test_line_1_is_the_t1_taxable_income(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(british_columbia_kinds().kind(LINE_1)).value == D(expected)


@pytest.mark.parametrize("salary", ["17000", "70000"])
def test_line_10_is_blank_when_line_1_is_137407_or_less(tmp_path: Path, salary: str) -> None:
    # Line 1 is 16,865.00 and 69,335.00: in the low table's columns, outside this table's range.
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(british_columbia_kinds().kind(LINE_10)).is_blank


def test_a_salary_of_200000_gives_the_column_2_lower_bound(tmp_path: Path) -> None:
    # Line 1 is 198,926.00, over 186,306 and not over 259,829: column 2.
    sheet = _sheet(tmp_path, "200000")

    assert sheet.get(british_columbia_kinds().kind(LINE_10)).value == D("186306.00")


def test_a_blank_line_10_traces_one_outside_range_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, BracketOutsideRangeLine)]
    assert line == BracketOutsideRangeLine(
        output=kinds.kind(LINE_10), base=kinds.kind(LINE_1), base_amount=D("19835.00")
    )


def test_a_covered_line_10_has_no_outside_range_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")

    assert not [t for t in sheet.trace if isinstance(t, BracketOutsideRangeLine)]


def _line_10_at(base: str) -> Artifact[Decimal]:
    """Line 10 over a given line 1, the capability the part builds with the real dataset."""
    kinds = british_columbia_kinds()
    line_1, line_10 = kinds.kind(LINE_1), kinds.kind(LINE_10)
    assert isinstance(line_1, AmountKind) and isinstance(line_10, AmountKind)
    dataset = YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(SCHEDULE, 2025, BRACKETS)
    result = BracketColumnLowerBound(line_1, line_10, dataset).run((Artifact(line_1, D(base)),))
    (output,) = result.outputs
    return output


def test_line_1_of_exactly_137407_leaves_line_10_blank() -> None:
    # A base at a threshold is in the lower column, which lines 2 to 8 cover.
    output = _line_10_at("137407.00")

    assert output == Artifact(british_columbia_kinds().kind(LINE_10), BLANK)


def test_line_1_of_137407_01_gives_137407() -> None:
    assert _line_10_at("137407.01").value == D("137407.00")


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        ("186306.00", "137407.00"),
        ("186306.01", "186306.00"),
    ],
)
def test_the_other_thresholds_give_the_column_line_1_falls_in(base: str, expected: str) -> None:
    assert _line_10_at(base).value == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_bracket_column_lower_bound_step_over_line_1() -> None:
    # Line 9 is a copy of line 1 and has no step; line 10 prints no title.
    assert _step() == {
        "name": "core/bracket_column_lower_bound",
        "reference": "10",
        "unit": "ca/cad",
        "params": {"schedule": SCHEDULE},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_10},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = british_columbia_kinds().kind(LINE_10)

    assert kind is BC428_BRACKET_LOWER_BOUND_LINE_10
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_10
    assert kind.value_type is Decimal
    assert non_negative(kind)

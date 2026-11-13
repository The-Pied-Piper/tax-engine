"""AB428 (2025) line 12, the rate of the column for lines 9 to 15, from the real parts.

Form text (Form AB428, CRA 5009-c-25e.txt, in the cra-docs repo): "Column 1: Line 1 is
more than $181,481 but not more than $241,974  Line 12: Rate 13%", "Column 2: Line 1 is more than
$241,974 but not more than $362,961  Line 12: Rate 14%", "Column 3: Line 1 is more than $362,961
Line 12: Rate 15%". Line 12 is `core/bracket_column_rate` over line 1
(`ca-ab/ab428_taxable_income_line_1`) with the `ca-ab/brackets_lines_9_to_15` schedule, output
`ca-ab/ab428_bracket_rate_line_12`, as Ontario's line 5 is.

The table covers only a line 1 above 181,481.00 (a line 1 of 181,481 or less is in lines 2 to 8, the
low table), so line 12 is left blank there: at $20,000 and $70,000 it is blank, at $200,000 (line 1
is 198,926.00) it is 13%. A blank output is read from the Worksheet as an artifact whose `is_blank`
is true (its `value` raises), and its trace is one `BracketOutsideRangeLine`.

Line 1 is a salary's T1 taxable income, so the exact thresholds are tested through the capability
and the real dataset directly, as
`tests/jurisdictions/core/capabilities/test_bracket_column_figure_range.py` does.

The real parts composed: the Alberta salary, Schedule 8, the T1 taxable-income parts, the line 1
part (`ab428_credits_line_1.yaml`) and `ab428_line_12.yaml`. The form declaration and header are
test-local.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
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
from tax_engine.jurisdictions.ca_ab.catalog import AB428_BRACKET_RATE_LINE_12
from tax_engine.jurisdictions.core.capabilities.bracket_column_figure import (
    BracketColumnRate,
)
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
ALBERTA = JurisdictionCode("CA-AB")
FORM = "ca-ab/ab428_credits"
LINE_1 = "ca-ab/ab428_taxable_income_line_1"
LINE_12 = "ca-ab/ab428_bracket_rate_line_12"
SCHEDULE = "ca-ab/brackets_lines_9_to_15"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = ALBERTA_PARTS / "ab428_line_12.yaml"
LINE_1_PART = ALBERTA_PARTS / "ab428_credits_line_1.yaml"
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
# The AB428 declaration, test-local: lines 1 and 12 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_12}
    """)


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
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
    yield PART.name, PART.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(ALBERTA, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "19835.00"), ("70000", "69335.00"), ("200000", "198926.00")],
)
def test_line_1_is_the_t1_taxable_income(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(alberta_kinds().kind(LINE_1)).value == D(expected)


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_line_12_is_blank_when_line_1_is_181481_or_less(tmp_path: Path, salary: str) -> None:
    # Line 1 is 19,835.00 and 69,335.00: in the low table's columns, outside this table's range.
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(alberta_kinds().kind(LINE_12)).is_blank


def test_a_salary_of_200000_gives_the_column_1_rate(tmp_path: Path) -> None:
    # Line 1 is 198,926.00, over 181,481 and not over 241,974: column 1.
    sheet = _sheet(tmp_path, "200000")

    assert sheet.get(alberta_kinds().kind(LINE_12)).value == D("0.13")


def test_a_blank_line_12_traces_one_outside_range_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")
    kinds = alberta_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, BracketOutsideRangeLine)]
    assert line == BracketOutsideRangeLine(
        output=kinds.kind(LINE_12), base=kinds.kind(LINE_1), base_amount=D("19835.00")
    )


def test_a_covered_line_12_has_no_outside_range_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")

    assert not [t for t in sheet.trace if isinstance(t, BracketOutsideRangeLine)]


def _line_12_at(base: str) -> Artifact[Decimal]:
    """Line 12 over a given line 1, the capability the part builds with the real dataset."""
    kinds = alberta_kinds()
    line_1, line_12 = kinds.kind(LINE_1), kinds.kind(LINE_12)
    assert isinstance(line_1, AmountKind) and isinstance(line_12, AmountKind)
    dataset = YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    ).get(SCHEDULE, 2025, BRACKETS)
    result = BracketColumnRate(line_1, line_12, dataset).run((Artifact(line_1, D(base)),))
    (output,) = result.outputs
    return output


def test_line_1_of_exactly_181481_leaves_line_12_blank() -> None:
    # A base at a threshold is in the lower column, which lines 2 to 8 cover.
    assert _line_12_at("181481.00") == Artifact(alberta_kinds().kind(LINE_12), BLANK)


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        ("181481.01", "0.13"),
        ("241974.00", "0.13"),
        ("241974.01", "0.14"),
        ("362961.00", "0.14"),
        ("362961.01", "0.15"),
    ],
)
def test_the_thresholds_give_the_rate_of_the_column_line_1_falls_in(
    base: str, expected: str
) -> None:
    assert _line_12_at(base).value == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_bracket_column_rate_step_over_line_1() -> None:
    # Line 12 prints "Rate" with each percentage; a rate is not money, so no unit, as on Ontario's
    # line 5.
    assert _step() == {
        "name": "core/bracket_column_rate",
        "title": "Rate",
        "reference": "12",
        "params": {"schedule": SCHEDULE},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_12},
    }


def test_the_step_keys_mirror_the_ontario_on428_line_5_step() -> None:
    assert list(_step()) == ["name", "title", "reference", "params", "consumes", "produces"]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = alberta_kinds().kind(LINE_12)

    assert kind is AB428_BRACKET_RATE_LINE_12
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_12
    assert kind.value_type is Decimal
    assert non_negative(kind)

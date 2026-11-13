"""AB428 (2025) line 11, line 1 minus line 10 (not below 0), from the real parts.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 11: Line 9 minus line 10 (cannot be negative) =".
Line 9 is "Amount from line 1" and has no step. Line 11 is `core/subtract_not_below_zero` of
`ca-ab/ab428_bracket_lower_bound_line_10` from `ca-ab/ab428_taxable_income_line_1`, rounded by
`ca-ab/cent_rounding`, output `ca-ab/ab428_taxable_income_over_lower_bound_line_11`, as Ontario's
line 53 is.

Line 10 is blank when line 1 is 181,481.00 or less, so line 11 is blank there (a blank `less` is
passed on): at $20,000 and $70,000 (line 1 is 19,835.00 and 69,335.00) it is blank, and at $200,000
(line 1 is 198,926.00, line 10 is 181,481.00) it is 17,445.00. A blank output is read from the
Worksheet as an artifact whose `is_blank` is true, and its trace is one `BlankPassedOnLine` naming
line 10; a covered line 11 traces one `SubtractedNotBelowZeroLine`.

Line 10 is a printed lower bound, so a line 1 just above a threshold is tested through the
capability and the real cent rounding dataset directly.

The real parts composed: the Alberta salary, Schedule 8, the T1 taxable-income parts, the line 1
part (`ab428_credits_line_1.yaml`), `ab428_line_10.yaml` and `ab428_line_11.yaml`. The form
declaration and header are test-local.
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
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
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
LINE_10 = "ca-ab/ab428_bracket_lower_bound_line_10"
LINE_11 = "ca-ab/ab428_taxable_income_over_lower_bound_line_11"
ROUNDING = "ca-ab/cent_rounding"
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = ALBERTA_PARTS / "ab428_line_11.yaml"
LINE_1_PART = ALBERTA_PARTS / "ab428_credits_line_1.yaml"
LINE_10_PART = ALBERTA_PARTS / "ab428_line_10.yaml"
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
# The AB428 declaration, test-local: lines 1, 10 and 11 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_10}
        - {LINE_11}
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
    for part in (LINE_1_PART, LINE_10_PART, PART):
        yield part.name, part.read_text(encoding="utf-8")


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
def test_line_11_is_blank_when_line_10_is_blank(tmp_path: Path, salary: str) -> None:
    # Line 1 is 19,835.00 and 69,335.00: line 10 is blank, so line 11 is blank.
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(alberta_kinds().kind(LINE_10)).is_blank
    assert sheet.get(alberta_kinds().kind(LINE_11)).is_blank


def test_a_salary_of_200000_gives_line_1_minus_line_10(tmp_path: Path) -> None:
    # Line 1 is 198,926.00 and line 10 is 181,481.00: 17,445.00.
    sheet = _sheet(tmp_path, "200000")

    assert sheet.get(alberta_kinds().kind(LINE_11)).value == D("17445.00")


def test_a_blank_line_11_traces_one_blank_passed_on_line_naming_line_10(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")
    kinds = alberta_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, BlankPassedOnLine) and t.output == kinds.kind(LINE_11)
    ]
    assert line == BlankPassedOnLine(output=kinds.kind(LINE_11), because=(kinds.kind(LINE_10),))
    assert not [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]


def _rounding() -> Any:
    return YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def test_a_covered_line_11_traces_one_subtracted_not_below_zero_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")
    kinds = alberta_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_11),
        minuend=kinds.kind(LINE_1),
        minuend_amount=D("198926.00"),
        subtrahend=kinds.kind(LINE_10),
        subtrahend_amount=D("181481.00"),
        rounding=_rounding().rounding,
        result=D("17445.00"),
    )
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def _line_11_at(line_1_amount: str, line_10_amount: str | None) -> Artifact[Decimal]:
    """Line 11 over given lines 1 and 10: the capability the part builds, with the real dataset."""
    kinds = alberta_kinds()
    line_1, line_10, line_11 = kinds.kind(LINE_1), kinds.kind(LINE_10), kinds.kind(LINE_11)
    assert isinstance(line_1, AmountKind)
    assert isinstance(line_10, AmountKind)
    assert isinstance(line_11, AmountKind)
    capability = SubtractNotBelowZero(_rounding(), line_1, line_10, line_11)
    less = BLANK if line_10_amount is None else D(line_10_amount)
    result = capability.run((Artifact(line_1, D(line_1_amount)), Artifact(line_10, less)))
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_1", "line_10", "expected"),
    [
        ("181481.01", "181481.00", "0.01"),
        ("241974.01", "241974.00", "0.01"),
        ("362961.01", "362961.00", "0.01"),
        ("198926.00", "181481.00", "17445.00"),
        ("241974.00", "241974.00", "0.00"),
        ("200000.00", "241974.00", "0.00"),
    ],
)
def test_line_11_is_line_1_minus_line_10_not_below_zero_to_the_cent(
    line_1: str, line_10: str, expected: str
) -> None:
    assert _line_11_at(line_1, line_10).value == D(expected)


def test_a_blank_line_10_blanks_line_11_through_the_capability_with_the_part_rule() -> None:
    kinds = alberta_kinds()
    line_1, line_10, line_11 = kinds.kind(LINE_1), kinds.kind(LINE_10), kinds.kind(LINE_11)
    assert isinstance(line_1, AmountKind)
    assert isinstance(line_10, AmountKind)
    assert isinstance(line_11, AmountKind)
    capability = SubtractNotBelowZero(_rounding(), line_1, line_10, line_11).with_blank_rules(
        {"less": PASS_ON}
    )

    result = capability.run((Artifact(line_1, D("19835.00")), Artifact(line_10, BLANK)))

    assert result.outputs == (Artifact(line_11, BLANK),)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_subtract_not_below_zero_step_over_line_1_and_line_10() -> None:
    # Line 9 is a copy of line 1 and has no step; line 11 prints no title. Line 10 is blank at a
    # line 1 of 181,481.00 or less, so the `less` slot passes a blank on and line 11 is blank.
    assert _step() == {
        "name": "core/subtract_not_below_zero",
        "reference": "11",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_1, "less": LINE_10},
        "blank": {"less": "pass_on"},
        "produces": {"output": LINE_11},
    }


def test_the_step_keys_are_in_the_house_order() -> None:
    assert list(_step()) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    from tax_engine.jurisdictions.ca_ab.catalog import (  # noqa: PLC0415
        AB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_11,
    )

    kind = alberta_kinds().kind(LINE_11)

    assert kind is AB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_11
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_11
    assert kind.value_type is Decimal
    assert non_negative(kind)

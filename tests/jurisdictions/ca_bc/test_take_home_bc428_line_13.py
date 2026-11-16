"""BC428 (2025) line 13, line 11 multiplied by the line 12 rate, from the real parts.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 13: Line 11 multiplied by the percentage
from line 12 = ^", printed in each of the columns "Line 1 is more than $137,407 but not more than
$186,306", "Line 1 is more than $186,306 but not more than $259,829" and "Line 1 is more than
$259,829". Line 11 is the part of line 1 over the column's lower bound and line 12 is the column's
printed rate (14.7%, 16.8% or 20.5%), so line 13 is their product, rounded half-up to the cent by
`ca-bc/cent_rounding`. Line 13 prints no title. It is blank when line 11 and line 12 are blank (a
line 1 of 137,407.00 or less, where the table of lines 9 to 15 does not apply).

Line 13 is one `core/multiply_by_rate` step with `base` = line 11 and `rate` = line 12, output
`ca-bc/bc428_bracket_tax_line_13`, in the part `bc428_line_13.yaml`. The capability refuses a blank
in a slot with no blank rule, so both slots carry `pass_on`, as Alberta's line 6 does.

The real parts composed: the British Columbia salary, Schedule 8, the T1 taxable-income parts and
`bc428_line_1.yaml`, `bc428_line_10.yaml`, `bc428_line_11.yaml`, `bc428_line_12.yaml` and
`bc428_line_13.yaml`. The form declaration and header are test-local, and the service is built over
the package list of `support.py`.

Figures (ticket, hand-computed, not a CRA example): line 1 is 16,865.00 / 19,835.00 / 29,735.00 /
69,335.00 / 198,926.00, so line 13 is blank for the first four, and for $200,000 line 11 is
12,620.00 (198,926.00 less 186,306.00) at 16.8%, so 2,120.16.

Boundary cases go through the capability and the real cent rounding dataset directly, with line 11
recomputed by hand from the printed bounds (137,407 / 186,306 / 259,829) and rates (14.7% / 16.8% /
20.5%). A line 1 of 137,407.01 is column 1 (line 11 0.01, tax 0.00147, so 0.00); 186,306.00 is
column 1 (line 11 48,899.00, tax 7,188.153, so 7,188.15) and 186,306.01 is column 2 (0.01 at 16.8%,
so 0.00); 186,307.00 is column 2 (line 11 1.00, 0.168, so 0.17); 259,829.00 is column 2 (line 11
73,523.00, tax 12,351.864, so 12,351.86); 259,829.01 is column 3 (0.01 at 20.5%, so 0.00) and
259,830.00 is column 3 (line 11 1.00, 0.205, so 0.21: half-up, where half-even gives 0.20).
300,000.00 is column 3 (line 11 40,171.00, tax 8,235.055, so 8,235.06).
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
from tax_engine.domain.blank import BLANK, PASS_ON
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_BRACKET_TAX_LINE_13
from tax_engine.jurisdictions.core.capabilities.multiply_by_rate import MultiplyByRate
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
BC = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_1 = "ca-bc/bc428_taxable_income_line_1"
LINE_10 = "ca-bc/bc428_bracket_lower_bound_line_10"
LINE_11 = "ca-bc/bc428_taxable_income_over_lower_bound_line_11"
LINE_12 = "ca-bc/bc428_bracket_rate_line_12"
LINE_13 = "ca-bc/bc428_bracket_tax_line_13"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = BC_PARTS / "bc428_line_13.yaml"
LINE_PARTS = tuple(
    BC_PARTS / f"bc428_line_{number}.yaml" for number in ("1", "10", "11", "12", "13")
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
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 1, 10, 11, 12 and 13 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_10}
        - {LINE_11}
        - {LINE_12}
        - {LINE_13}
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield "salary.yaml", (BC_PARTS / "salary.yaml").read_text(encoding="utf-8")
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
    for part in LINE_PARTS:
        yield part.name, part.read_text(encoding="utf-8")


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
    worksheets = _service(tmp_path).compute(BC, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "line_1"),
    [
        ("17000", "16865.00"),
        ("20000", "19835.00"),
        ("30000", "29735.00"),
        ("70000", "69335.00"),
        ("200000", "198926.00"),
    ],
)
def test_the_salaries_give_the_line_1_figures_the_line_13_cases_rest_on(
    tmp_path: Path, salary: str, line_1: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_1)).value == D(line_1)


@pytest.mark.parametrize("salary", ["17000", "20000", "30000", "70000"])
def test_line_13_is_blank_when_lines_11_and_12_are_blank(tmp_path: Path, salary: str) -> None:
    # Line 1 is 16,865.00 to 69,335.00, at or below 137,407: lines 11 and 12 are blank.
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_11)).is_blank
    assert sheet.get(_kind(LINE_12)).is_blank
    assert sheet.get(_kind(LINE_13)).is_blank


def test_a_salary_of_200000_gives_line_11_times_the_line_12_rate(tmp_path: Path) -> None:
    # Line 11 is 12,620.00 at 16.8%: 2,120.16 exactly.
    sheet = _sheet(tmp_path, "200000")

    assert sheet.get(_kind(LINE_11)).value == D("12620.00")
    assert sheet.get(_kind(LINE_12)).value == D("0.168")
    assert sheet.get(_kind(LINE_13)).value == D("2120.16")


def test_the_blank_line_13_says_it_passed_on_the_blanks_of_lines_11_and_12(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "20000")
    # The kinds in `because` are sorted by identifier: line 12 (bracket_rate) before line 11.
    line = BlankPassedOnLine(_kind(LINE_13), (_kind(LINE_12), _kind(LINE_11)))

    assert line in sheet.trace
    assert EnglishTraceRenderer().render(line).endswith("were blank.")
    assert not any(
        isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_13)
        for each in sheet.trace
    )


def test_the_product_is_traced_with_its_base_and_rate(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")

    (line,) = (
        each
        for each in sheet.trace
        if isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_13)
    )
    assert line.base_kind is _kind(LINE_11)
    assert line.base_value == D("12620.00")
    assert line.rate_kind is _kind(LINE_12)
    assert line.rate_value == D("0.168")
    assert line.result == D("2120.16")
    assert not [
        each
        for each in sheet.trace
        if isinstance(each, BlankPassedOnLine) and each.output is _kind(LINE_13)
    ]


def _rounding() -> Any:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _capability() -> MultiplyByRate:
    """Line 13 as the part builds it: line 11 times line 12, with the real rounding dataset."""
    return MultiplyByRate(_rounding(), _kind(LINE_11), _kind(LINE_12), _kind(LINE_13))


def _line_13_at(line_11: str, rate: str) -> Artifact[Decimal]:
    capability = _capability()
    result = capability.run(
        (Artifact(_kind(LINE_11), D(line_11)), Artifact(_kind(LINE_12), D(rate)))
    )
    (output,) = result.outputs
    return output


# Line 11 is line 1 less the column's printed lower bound (137,407 / 186,306 / 259,829), worked
# out by hand; the rate is the column's printed rate.
@pytest.mark.parametrize(
    ("line_1", "bound", "rate", "expected"),
    [
        # Just above 137,407: column 1, line 11 0.01, 0.00147.
        ("137407.01", "137407", "0.147", "0.00"),
        # Column 1 at its upper bound: 48,899.00 x 14.7% = 7,188.153.
        ("186306.00", "137407", "0.147", "7188.15"),
        # Just above 186,306: column 2, 0.01 x 16.8% = 0.00168.
        ("186306.01", "186306", "0.168", "0.00"),
        # 186,307: column 2, line 11 1.00 x 16.8% = 0.168.
        ("186307.00", "186306", "0.168", "0.17"),
        # Column 2 at its upper bound: 73,523.00 x 16.8% = 12,351.864.
        ("259829.00", "186306", "0.168", "12351.86"),
        # Just above 259,829: column 3, 0.01 x 20.5% = 0.00205.
        ("259829.01", "259829", "0.205", "0.00"),
        # 259,830: column 3, line 11 1.00 x 20.5% = 0.205, half-up 0.21 (half-even gives 0.20).
        ("259830.00", "259829", "0.205", "0.21"),
        # Column 3: 40,171.00 x 20.5% = 8,235.055, half-up.
        ("300000.00", "259829", "0.205", "8235.06"),
        # The $200,000 salary: 12,620.00 x 16.8% = 2,120.16.
        ("198926.00", "186306", "0.168", "2120.16"),
    ],
)
def test_line_13_at_the_column_boundaries_to_the_cent(
    line_1: str, bound: str, rate: str, expected: str
) -> None:
    line_11 = D(line_1) - D(bound)
    product = line_11 * D(rate)

    assert _line_13_at(str(line_11), rate).value == D(expected)
    assert product.quantize(D("0.01"), rounding="ROUND_HALF_UP") == D(expected)


@pytest.mark.parametrize(
    ("line_11", "rate", "expected"),
    [
        # 1.00 x 20.5% = 0.205: exactly half goes up (half-up, not half-even 0.20).
        ("1.00", "0.205", "0.21"),
        # 0.04 x 20.5% = 0.0082 and 0.05 x 20.5% = 0.01025: both round to 0.01.
        ("0.04", "0.205", "0.01"),
        ("0.05", "0.205", "0.01"),
        # 5.00 x 14.7% = 0.735: exactly half goes up.
        ("5.00", "0.147", "0.74"),
        # 15.00 x 14.7% = 2.205: exactly half goes up (half-even gives 2.20).
        ("15.00", "0.147", "2.21"),
        # 25.00 x 14.7% = 3.675: exactly half goes up.
        ("25.00", "0.147", "3.68"),
        # 0.02 x 14.7% = 0.00294: down.
        ("0.02", "0.147", "0.00"),
    ],
)
def test_line_13_is_rounded_half_up_to_the_cent(line_11: str, rate: str, expected: str) -> None:
    assert _line_13_at(line_11, rate).value == D(expected)


def test_a_blank_line_11_and_line_12_blank_line_13_through_the_capability_with_the_part_rules() -> (
    None
):
    capability = _capability().with_blank_rules({"base": PASS_ON, "rate": PASS_ON})

    result = capability.run((Artifact(_kind(LINE_11), BLANK), Artifact(_kind(LINE_12), BLANK)))

    assert result.outputs == (Artifact(_kind(LINE_13), BLANK),)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_multiply_by_rate_step_over_lines_11_and_12() -> None:
    # Line 13 prints no title. Both slots pass a blank on, so line 13 is blank when line 1 is
    # 137,407.00 or less.
    assert _step() == {
        "name": "core/multiply_by_rate",
        "reference": "13",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"base": LINE_11, "rate": LINE_12},
        "blank": {"base": "pass_on", "rate": "pass_on"},
        "produces": {"output": LINE_13},
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


def test_line_13_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_13)

    assert kind is BC428_BRACKET_TAX_LINE_13
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_13
    assert kind.value_type is Decimal
    assert non_negative(kind)

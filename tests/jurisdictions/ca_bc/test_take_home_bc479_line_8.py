"""BC479 (2025) line 8, income for the sales tax credit, from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14, as recorded on the ticket): "Line 8: Line 6
minus line 7 (if negative, enter "0") Income for the sales tax credit = ^". So line 8 is one
core/subtract_not_below_zero step (`bc479_line_8.yaml`), rounded through `ca-bc/cent_rounding`,
titled "Income for the sales tax credit" with reference "8". It consumes line 6
(`ca-bc/bc479_adjusted_family_net_income_line_6`) as the amount and line 7
(`ca-bc/bc479_threshold_line_7`) as `less`, and produces
`ca-bc/bc479_income_for_sales_tax_credit_line_8`, a non-negative kind.
Line 7 is always a printed amount, so the step has no blank declaration.

The test composes the real British Columbia salary part, the real Schedule 8 parts, the real T1
taxable income parts, the real line 1 to line 7 parts and the new line 8 part, and types in only the
salary (and, in other tests, line 4). The form declaration is made up here, exporting only line 8.

Figures (hand-computed from the printed forms, not a CRA example): line 6 is 16,865.00 / 198,926.00
at 17,000 / 200,000 and line 7 is 15,000.00, so line 8 is 1,865.00 / 183,926.00. At 10,000 line 6 is
below 15,000.00, so line 8 is 0.00.
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
import tax_engine.jurisdictions.ca_bc.catalog as bc_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC479_UCCB_RDSP_INCOME_LINE_4
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
)
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
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc479"
LINE_6 = "ca-bc/bc479_adjusted_family_net_income_line_6"
LINE_7 = "ca-bc/bc479_threshold_line_7"
LINE_8 = "ca-bc/bc479_income_for_sales_tax_credit_line_8"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc479_line_8.yaml"
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
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_8}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield BC_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield _federal(name)
    yield BC_PARTS / "bc479_line_1.yaml"
    yield BC_PARTS / "bc479_line_2_input.yaml"
    yield BC_PARTS / "bc479_line_3.yaml"
    yield BC_PARTS / "bc479_line_4_input.yaml"
    yield BC_PARTS / "bc479_line_5.yaml"
    yield BC_PARTS / "bc479_line_6.yaml"
    yield BC_PARTS / "bc479_line_7.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _line_4(amount: str) -> Artifact[Decimal]:
    return Artifact(BC479_UCCB_RDSP_INCOME_LINE_4, D(amount))


def _rounding() -> Any:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


# salary, line 8 (line 6 less the 15,000.00 threshold, not below 0).
CASES = [
    ("17000", "1865.00"),
    ("200000", "183926.00"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_8_is_line_6_less_line_7_for_a_single_filer(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_8 = _sheet(tmp_path, salary).get(_kind(LINE_8)).value

    assert line_8 == D(expected)
    assert str(line_8) == expected
    assert line_8.as_tuple().exponent == -2
    assert not line_8.is_signed()


def test_line_8_is_0_when_line_6_is_below_line_7(tmp_path: Path) -> None:
    # Line 6 is below 15,000.00 at a salary of 10,000, so the difference is negative and is
    # entered as 0.
    line_8 = _sheet(tmp_path, "10000").get(_kind(LINE_8)).value

    assert line_8 == D("0.00")
    assert str(line_8) == "0.00"
    assert not line_8.is_signed()


def test_line_8_is_0_when_line_6_equals_line_7(tmp_path: Path) -> None:
    # Line 6 is 16,865.00 at 17,000; line 4 of 1,865.00 makes line 6 exactly 15,000.00.
    sheet = _sheet(tmp_path, "17000", _line_4("1865.00"))

    assert sheet.get(_kind(LINE_6)).value == D("15000.00")
    assert sheet.get(_kind(LINE_8)).value == D("0.00")


def test_line_8_follows_line_6_when_line_4_is_given(tmp_path: Path) -> None:
    line_8 = _sheet(tmp_path, "17000", _line_4("1000.00")).get(_kind(LINE_8)).value

    assert line_8 == D("865.00")
    assert str(line_8) == "865.00"


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "17000")
    kinds = british_columbia_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_8)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_8),
        minuend=kinds.kind(LINE_6),
        minuend_amount=D("16865.00"),
        subtrahend=kinds.kind(LINE_7),
        subtrahend_amount=D("15000.00"),
        rounding=_rounding().rounding,
        result=D("1865.00"),
    )


@pytest.mark.parametrize(
    ("line_6", "line_7", "expected"),
    [
        ("16865.00", "15000.00", "1865.00"),
        ("9865.00", "15000.00", "0.00"),
    ],
)
def test_line_8_is_line_6_minus_line_7_not_below_zero_to_the_cent(
    line_6: str, line_7: str, expected: str
) -> None:
    kinds = (_kind(LINE_6), _kind(LINE_7), _kind(LINE_8))
    capability = SubtractNotBelowZero(_rounding(), *kinds)
    result = capability.compute((Artifact(kinds[0], D(line_6)), Artifact(kinds[1], D(line_7))))

    (output,) = result.outputs
    assert output.value == D(expected)
    assert D(expected) == max(D(line_6) - D(line_7), D("0.00"))


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_titled_subtract_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "title": "Income for the sales tax credit",
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_6, "less": LINE_7},
        "produces": {"output": LINE_8},
    }
    assert "blank" not in step


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_8 in kinds.identifiers()
    kind = kinds.kind(LINE_8)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC479_INCOME_FOR_SALES_TAX_CREDIT_LINE_8"]

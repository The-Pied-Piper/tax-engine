"""BC479 (2025) line 12, line 8 multiplied by 2%, from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14, as recorded on the ticket): "Line 12: Amount
from line 8 ^ multiplied by 2% = ^". The 2% is printed in the line text, so it is the
`ca-bc/sales_tax_credit_rate` dataset figure (0.02) and has no step. Line 12 is one
`core/apply_rate` step (`bc479_line_12.yaml`): `ca-bc/bc479_income_for_sales_tax_credit_line_8`
times that rate, rounded half-up to the cent by the dataset's rule, output
`ca-bc/bc479_income_reduction_line_12`, a non-negative kind, with reference "12". Line 8 is never
blank (it is floored at 0), so the step has no blank rule. A line 8 of 0.00 gives a computed 0.00,
not a blank. The form prints no title for the line, so the step has none.

The test composes the real British Columbia salary part, the real Schedule 8 parts, the real T1
taxable income parts, the real line 1 to line 8 parts and the new line 12 part, and types in only
the salary. The form declaration is made up here, exporting lines 8 and 12.

Figures (hand-computed from the ticket, not a CRA example): line 8 is 1,865.00 / 183,926.00 at
17,000 / 200,000, so line 12 is 37.30 / 3,678.52 (183,926.00 x 0.02 is 3,678.52 exactly). At 10,000
line 6 is below the 15,000.00 threshold, so line 8 is 0.00 and line 12 is 0.00.
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
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, RateAppliedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate
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
LINE_8 = "ca-bc/bc479_income_for_sales_tax_credit_line_8"
LINE_12 = "ca-bc/bc479_income_reduction_line_12"
RATE_FAMILY = "ca-bc/sales_tax_credit_rate"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = BC_PARTS / "bc479_line_12.yaml"
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
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
    "t1_uccb_rdsp.yaml",
    "t1_uccb_rdsp_line_11700_inputs.yaml",
    "t1_uccb_rdsp_line_12500_inputs.yaml",
    "t1_uccb_rdsp_line_21300_inputs.yaml",
    "t1_uccb_rdsp_line_23200_inputs.yaml",
    "t1_uccb_rdsp_line_11700.yaml",
    "t1_uccb_rdsp_line_12500.yaml",
    "t1_uccb_rdsp_line_21300.yaml",
    "t1_uccb_rdsp_line_23200.yaml",
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
        - {LINE_12}
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
    yield BC_PARTS / "bc479_line_2.yaml"
    yield BC_PARTS / "bc479_line_3.yaml"
    yield BC_PARTS / "bc479_line_4.yaml"
    yield BC_PARTS / "bc479_line_5.yaml"
    yield BC_PARTS / "bc479_line_6.yaml"
    yield BC_PARTS / "bc479_line_7.yaml"
    yield BC_PARTS / "bc479_line_8.yaml"
    yield PART


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
        ("17000", "37.30"),
        ("200000", "3678.52"),
    ],
)
def test_line_12_is_line_8_times_2_percent_rounded_half_up(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_12 = _sheet(tmp_path, salary).get(_kind(LINE_12)).value

    assert line_12 == D(expected)
    assert str(line_12) == expected


def test_line_12_is_a_computed_zero_when_line_8_is_zero(tmp_path: Path) -> None:
    # Line 6 is below the 15,000.00 threshold at a salary of 10,000, so line 8 is floored at 0.00;
    # line 12 is 0.00 and it is computed, so it is not blank.
    sheet = _sheet(tmp_path, "10000")

    assert sheet.get(_kind(LINE_8)).value == D("0.00")
    line_12 = sheet.get(_kind(LINE_12))
    assert not line_12.is_blank
    assert line_12.value == D("0.00")
    assert str(line_12.value) == "0.00"


def test_a_covered_line_12_traces_one_rate_applied_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000")

    (line,) = [t for t in sheet.trace if isinstance(t, RateAppliedLine)]
    assert line == RateAppliedLine(
        output=_kind(LINE_12),
        base=_kind(LINE_8),
        base_amount=D("1865.00"),
        rate=Rate(D("0.02")),
        rounding=_rate().rounding,
        result=D("37.30"),
    )
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def _rate() -> ParameterDataset[Rate]:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(RATE_FAMILY, 2025, RATE)


def _line_12_at(line_8_amount: str) -> Artifact[Decimal]:
    """Line 12 over a given line 8: the capability the part builds, with the real dataset."""
    line_8, line_12 = _kind(LINE_8), _kind(LINE_12)
    capability = ApplyRate(_rate(), line_8, line_12)
    result = capability.run((Artifact(line_8, D(line_8_amount)),))
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_8", "expected"),
    [
        # 0.25 x 2% = 0.0050, rounded half-up to 0.01 (not down to 0.00).
        ("0.25", "0.01"),
        # 1,865.00 x 2% = 37.30.
        ("1865.00", "37.30"),
    ],
)
def test_line_12_is_line_8_times_the_rate_to_the_cent(line_8: str, expected: str) -> None:
    assert _line_12_at(line_8).value == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_apply_rate_step_over_line_8_and_the_rate() -> None:
    # Line 12 prints no title: the form's line 12 is only "Amount from line 8 ^ multiplied by 2% =
    # ^". The 2% is the dataset rate, so the step reads it as a parameter, not a line.
    assert _step() == {
        "name": "core/apply_rate",
        "reference": "12",
        "unit": "ca/cad",
        "params": {"rate": RATE_FAMILY},
        "consumes": {"base": LINE_8},
        "produces": {"output": LINE_12},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = british_columbia_kinds().kind(LINE_12)

    assert kind is vars(bc_catalog)["BC479_INCOME_REDUCTION_LINE_12"]
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_12
    assert kind.value_type is Decimal
    assert non_negative(kind)

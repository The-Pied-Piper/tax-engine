"""BC479 (2025) line 15, line 13 plus line 14, from the salary alone with the renovation expenses
input given or left out.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14, as recorded on the ticket): "Line 15: Line 13
plus line 14 = ^". Line 15 is one core/sum step (`bc479_line_15.yaml`), rounded through
`ca-bc/cent_rounding`, over line 13 (`ca-bc/bc479_sales_tax_credit_line_13`) and line 14
(`ca-bc/bc479_home_renovation_credit_line_14`), producing `ca-bc/bc479_page_1_total_line_15`, a
non-negative kind, reference "15", with no title (the form prints none). Neither part is ever blank
(line 13 is a computed figure, line 14 reads its blank expenses as 0), so the step has no blank
rule. Line 16 is a page carry with no step. The spouse branch of line 10 is not built, so
there is no spouse gate here.

The test composes the real salary part, the real Schedule 8 and T1 taxable income parts, the real
line 1 to line 14 parts and the new line 15 part, and types in the salary and, in some tests, the
expenses. The form declaration is made up here, exporting only line 15. Figures are hand-computed
from the printed forms (not a CRA example): line 13 is 37.70 at 17,000 and 0.00 at every higher
salary, line 14 is 0.00 with no expenses, so line 15 is 37.70 at 17,000 and 0.00 above.
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
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
LINE_13 = "ca-bc/bc479_sales_tax_credit_line_13"
LINE_14 = "ca-bc/bc479_home_renovation_credit_line_14"
LINE_15 = "ca-bc/bc479_page_1_total_line_15"
EXPENSES = bc_catalog.BC479_HOME_RENOVATION_EXPENSES_LINE_14
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = BC_PARTS / "bc479_line_15.yaml"
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
        - {LINE_15}
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
    yield BC_PARTS / "bc479_line_9.yaml"
    yield BC_PARTS / "bc479_line_11.yaml"
    yield BC_PARTS / "bc479_line_12.yaml"
    yield BC_PARTS / "bc479_line_13.yaml"
    yield BC_PARTS / "bc479_home_renovation_expenses_maximum.yaml"
    yield BC_PARTS / "bc479_line_14_input.yaml"
    yield BC_PARTS / "bc479_line_14_check.yaml"
    yield BC_PARTS / "bc479_line_14.yaml"
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


# salary, line 15 (line 13 plus line 14 with no expenses).
CASES = [
    ("17000", "37.70"),
    ("20000", "0.00"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_15_is_line_13_plus_line_14_for_a_single_filer(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_15 = _sheet(tmp_path, salary).get(_kind(LINE_15)).value

    assert line_15 == D(expected)
    assert str(line_15) == expected
    assert not line_15.is_signed()


def test_line_15_adds_the_renovation_credit_to_line_13(tmp_path: Path) -> None:
    # 1,234.56 of expenses gives line 14 of 123.46; line 13 is 37.70 at 17,000.
    sheet = _sheet(tmp_path, "17000", Artifact(EXPENSES, D("1234.56")))

    assert sheet.get(_kind(LINE_13)).value == D("37.70")
    assert sheet.get(_kind(LINE_14)).value == D("123.46")
    assert sheet.get(_kind(LINE_15)).value == D("161.16")


def test_line_15_is_a_computed_zero_when_both_parts_are_zero(tmp_path: Path) -> None:
    line_15 = _sheet(tmp_path, "70000").get(_kind(LINE_15))

    assert not line_15.is_blank
    assert line_15.value == D("0.00")
    assert str(line_15.value) == "0.00"


def test_the_step_traces_one_sum_line_over_lines_13_and_14_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(EXPENSES, D("1234.56")))
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(LINE_15)]
    assert line.parts == (
        (kinds.kind(LINE_13), D("37.70")),
        (kinds.kind(LINE_14), D("123.46")),
    )
    assert line.total == D("161.16")
    assert line.rounding.apply(D("0.005")) == D("0.01")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_with_no_blank_rule() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "15",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_13, LINE_14]},
        "produces": {"output": LINE_15},
    }


def test_line_15_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_15 in kinds.identifiers()
    kind = kinds.kind(LINE_15)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC479_PAGE_1_TOTAL_LINE_15"]

"""BC428 (2025) line 60, line 58 plus line 59, from the salary alone.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 60 and line 61500: Line 58 plus line 59
Enter this amount on line 64." Line 58 is the subtotal of the credit amounts at the rate and the
donations and gifts (`ca-bc/bc428_subtotal_line_58`), and line 59 is the qualifying gifts at 25%
(`ca-bc/bc428_farmers_food_donation_credit_line_59`). Line 60 is one core/sum over those two parts,
with no blank rule of its own: both parts are always produced, since their own steps read a blank
input as 0.

The test composes everything the line 58 test composes plus the line 59 input part, the new
`bc428_line_59.yaml` and the new `bc428_line_60.yaml`, and types in only the salary (and, in one
test, the gifts from line 59 and the donations and gifts from line 57). The form declaration is made
up here, exporting only line 60. The figures are hand-computed from the printed forms (not a CRA
example): with no gifts, line 60 is line 58.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_DONATIONS_AND_GIFTS_LINE_57,
    BC428_NON_REFUNDABLE_CREDITS_LINE_60,
    BC428_QUALIFYING_GIFTS_LINE_59,
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
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc428_line_60.yaml"
LINE_58 = "ca-bc/bc428_subtotal_line_58"
LINE_59 = "ca-bc/bc428_farmers_food_donation_credit_line_59"
IDENTIFIER = "ca-bc/bc428_non_refundable_credits_line_60"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_non_refundable_credits_line_60
    capabilities: []
    """)

# salary, line 60 with no gifts (line 58, which is line 56 plus a blank line 57). At $200,000 lines
# 27 and 29 are at their maximums.
CASES = [
    ("17000", "702.28"),
    ("200000", "878.70"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield BC_PARTS / "bc428_line_16.yaml"
    yield BC_PARTS / "bc428_line_17_worksheet_lines_1_to_3.yaml"
    yield BC_PARTS / "bc428_line_17_worksheet_lines_4_to_7.yaml"
    yield BC_PARTS / "bc428_line_17.yaml"
    yield BC_PARTS / "bc428_line_25.yaml"
    yield BC_PARTS / "bc428_line_27.yaml"
    yield BC_PARTS / "bc428_line_29.yaml"
    yield BC_PARTS / "bc428_line_33.yaml"
    yield BC_PARTS / "bc428_line_35.yaml"
    yield BC_PARTS / "bc428_line_36_input.yaml"
    yield BC_PARTS / "bc428_line_36.yaml"
    yield BC_PARTS / "bc428_line_37.yaml"
    yield BC_PARTS / "bc428_line_40.yaml"
    yield BC_PARTS / "bc428_line_45.yaml"
    yield BC_PARTS / "bc428_line_46.yaml"
    yield BC_PARTS / "bc428_line_47.yaml"
    yield BC_PARTS / "bc428_line_49.yaml"
    yield BC_PARTS / "bc428_line_50.yaml"
    yield BC_PARTS / "bc428_line_51.yaml"
    yield BC_PARTS / "bc428_line_52_input.yaml"
    yield BC_PARTS / "bc428_line_53.yaml"
    yield BC_PARTS / "bc428_line_54.yaml"
    yield BC_PARTS / "bc428_line_56.yaml"
    yield BC_PARTS / "bc428_line_57_input.yaml"
    yield BC_PARTS / "bc428_line_58.yaml"
    yield BC_PARTS / "bc428_line_59_input.yaml"
    yield BC_PARTS / "bc428_line_59.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
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
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-BC"), 2025, tuple(given))
    )
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_60_is_line_58_when_no_gifts_are_given(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(BC428_NON_REFUNDABLE_CREDITS_LINE_60).value == D(expected)


def test_line_60_adds_line_59_to_line_58(tmp_path: Path) -> None:
    # Line 58 is 875.44 at $70,000 with no line 57; line 59 is 100.00 times 25%, 25.00.
    sheet = _sheet(tmp_path, "70000", Artifact(BC428_QUALIFYING_GIFTS_LINE_59, D("100.00")))

    assert sheet.get(BC428_NON_REFUNDABLE_CREDITS_LINE_60).value == D("900.44")


def test_line_60_adds_line_57_through_line_58_as_well_as_line_59(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(BC428_DONATIONS_AND_GIFTS_LINE_57, D("100.00")),
        Artifact(BC428_QUALIFYING_GIFTS_LINE_59, D("100.00")),
    )

    # Line 58 is 975.44 with the line 57 gifts; line 59 is 25.00.
    assert sheet.get(BC428_NON_REFUNDABLE_CREDITS_LINE_60).value == D("1000.44")


def _part() -> dict[str, object]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_line_58_and_line_59() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    capabilities = part["capabilities"]
    assert isinstance(capabilities, list)
    (step,) = capabilities
    assert isinstance(step, dict)
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "60",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {"parts": [LINE_58, LINE_59]},
        "produces": {"output": IDENTIFIER},
    }


def test_line_60_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(IDENTIFIER)

    assert kind is BC428_NON_REFUNDABLE_CREDITS_LINE_60
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)

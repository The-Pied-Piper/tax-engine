"""BC428 (2025) line 63, line 61 plus line 62, from the salary alone, real parts.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 63: Line 61 plus line 62 = ^". Line 62
(British Columbia tax on split income, from Form T1206) is an optional input a salary-only caller
leaves out, read as blank and then as 0 by the step's own blank rule, as Alberta line 61 reads its
line 60 input; line 63 is one core/sum over line 61 and line 62.

The test composes the real salary part, the real Schedule 8 and T1 parts, the real line 1, 3 to 8,
10 to 15 and 61 parts, the line 62 input part and the new `bc428_line_63.yaml`, and types in only
the salary (and, in one test, line 62). The form declaration is made up here, exporting only line
63. The figures are hand-computed from the printed forms (not a CRA example): with line 62 blank,
line 63 is line 61.
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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC428_TAX_ON_SPLIT_INCOME_LINE_62,
    BC428_TAX_WITH_SPLIT_INCOME_LINE_63,
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
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc428_line_63.yaml"
LINE_61_PART = BC_PARTS / "bc428_line_61.yaml"
LINE_62_PART = BC_PARTS / "bc428_line_62_input.yaml"
IDENTIFIER = "ca-bc/bc428_tax_with_split_income_line_63"
LINE_62 = "ca-bc/bc428_tax_on_split_income_line_62"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_tax_with_split_income_line_63
    capabilities: []
    """)

# The real British Columbia parts, in composition order: line 1, lines 3 to 8, lines 10 to 15,
# line 61, the line 62 input, line 63.
LINE_PARTS = (
    *(BC_PARTS / f"bc428_line_{number}.yaml" for number in (1, 3, 4, 5, 6, 7, 8)),
    *(BC_PARTS / f"bc428_line_{number}.yaml" for number in (10, 11, 12, 13, 14, 15)),
    LINE_61_PART,
    LINE_62_PART,
    LINE_PART,
)
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

# salary, line 63 (line 61 plus a blank line 62). Line 61 is line 8 for the first four salaries
# and line 15 for the fifth.
CASES = [
    ("17000", "853.37"),
    ("200000", "20109.46"),
]


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
    for part in LINE_PARTS:
        yield part.name, part.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest: a test header, the test-local form
    declaration and the real parts from the salary to line 63."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-BC"), 2025, *given)
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_63_is_line_61_when_line_62_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(BC428_TAX_WITH_SPLIT_INCOME_LINE_63).value == D(expected)


def test_line_63_adds_line_62_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(BC428_TAX_ON_SPLIT_INCOME_LINE_62, D("100.00")))

    assert sheet.get(BC428_TAX_WITH_SPLIT_INCOME_LINE_63).value == D("4137.83")


def _part() -> dict[str, object]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_line_61_and_line_62() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc428"}
    capabilities = part["capabilities"]
    assert isinstance(capabilities, list)
    (step,) = capabilities
    assert isinstance(step, dict)
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "63",
        "unit": "ca/cad",
        "params": {"rounding": "ca-bc/cent_rounding"},
        "consumes": {
            "parts": [
                "ca-bc/bc428_british_columbia_tax_on_taxable_income_line_61",
                LINE_62,
            ]
        },
        "blank": {LINE_62: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_63_is_a_registered_signed_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert not non_negative(kind)
    assert kind is BC428_TAX_WITH_SPLIT_INCOME_LINE_63

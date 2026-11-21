"""NL428 (2025) line 52, the lesser of $2,410 or line 51, from the salary, real parts.

Form text (Form NL428, CRA 5001-C, confirmed 2026-11-18): "Line 52: Enter whichever is less:
$2,410 or the amount on line 51." The $2,410 is the printed ceiling, the
`ca-nl/medical_expense_dollar_limit` dataset, and has no step of its own. Line 52 is one
core/capped_amount step over line 51 (`nl428_credits_line_51.yaml`) capped by that dataset. The
form prints no label for the line, so the step has no title.

The test composes the real Schedule 8 parts, the real T1 taxable income parts and the real line 49,
line 51 and line 52 parts, and types in only the salary. The header, the salary input and the form
declaration are made up here, the form exporting line 52.

The hand figures are asserted (not a CRA example): net income is the salary less the enhanced CPP
deduction, line 51 is 3% of it half-up to the cent, and line 52 is the lesser of that and 2,410.00.
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
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_49_PART = NL_PARTS / "nl428_credits_line_49.yaml"
LINE_51_PART = NL_PARTS / "nl428_credits_line_51.yaml"
LINE_PART = NL_PARTS / "nl428_credits_line_52.yaml"
FORM_NAME = "ca-nl/nl428_credits"
LINE_51 = "ca-nl/nl428_medical_expenses_rate_amount_line_51"
KIND = "ca-nl/nl428_medical_expenses_limited_amount_line_52"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 49 to 52.
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_medical_expenses_limited_amount_line_52
    capabilities: []
    """)

# salary, line 51 (3% of net income), line 52 (the lesser of line 51 and 2,410.00). Net income is
# 19,835.00 / 198,926.00.
CASES = [
    ("20000", "595.05", "595.05"),
    ("200000", "5967.78", "2410.00"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_49_PART
    yield LINE_51_PART
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "line_51", "expected"), CASES)
def test_line_52_is_the_lesser_of_2410_and_line_51(
    tmp_path: Path, salary: str, line_51: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _value(sheet, LINE_51) == D(line_51)
    assert _value(sheet, KIND) == D(expected)


def test_line_52_at_a_line_51_just_above_the_ceiling_is_2410(tmp_path: Path) -> None:
    # Salary 82,000: the enhanced CPP deduction is 678.00 (1% of 67,800) plus 396.00 (4% of 9,900),
    # so net income is 80,926.00 and line 51 is 2,427.78, above the 2,410.00 ceiling.
    sheet = _sheet(tmp_path, "82000")

    assert _value(sheet, LINE_51) == D("2427.78")
    assert _value(sheet, KIND) == D("2410.00")


def _step() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_untitled_capped_amount_step_over_line_51() -> None:
    assert _step() == {
        "name": "core/capped_amount",
        "reference": "52",
        "unit": "ca/cad",
        "params": {"cap": "ca-nl/medical_expense_dollar_limit"},
        "consumes": {"base": LINE_51},
        "produces": {"output": KIND},
    }


def test_line_52_is_a_registered_non_negative_amount_kind() -> None:
    kinds = newfoundland_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is nl_catalog.NL428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_52

"""MB479 (2025) line 17, total credits, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC, 5007-tc-25e.txt): "Line 17 and line 61050: Add lines 7, 8, and
12 to 16. Total credits". Line 17 is one core/sum over the line 7 basic credit (195.00) and the six
optional inputs of the line 17 inputs part: line 8 (age credit for self), line 12 (the printed sum
of lines 9 to 11), line 13 (eligible dependant), and the product boxes of lines 14, 15 and 16. A
salary-only filer leaves all six blank: each blank input is read as 0 and the step prints its own
"left blank, taken as 0" row, so the total is the basic credit alone.

The test composes the real line 7 part, the real line 17 inputs part and the real line 17 part, and
types in only the salary (and, in some tests, the credit boxes). The MB479 form declaration is made
up here, exporting only line 17.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import (
    MB479_AGE_CREDIT_LINE_8,
    MB479_DEPENDENT_CHILDREN_CREDIT_LINE_16,
    MB479_DISABILITY_CREDIT_LINE_14,
    MB479_DISABLED_DEPENDANTS_CREDIT_LINE_15,
    MB479_ELIGIBLE_DEPENDANT_CREDIT_LINE_13,
    MB479_SPOUSE_CREDITS_LINE_12,
)
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb479_line_17.yaml"
PARTS = (
    MB_PARTS / "mb479_line_7.yaml",
    MB_PARTS / "mb479_line_17_inputs.yaml",
    LINE_PART,
)
FORM_NAME = "ca-mb/mb479"
KIND = "ca-mb/mb479_total_credits_line_17"
BASIC = "ca-mb/mb479_basic_credit_line_7"
INPUTS = (
    MB479_AGE_CREDIT_LINE_8,
    MB479_SPOUSE_CREDITS_LINE_12,
    MB479_ELIGIBLE_DEPENDANT_CREDIT_LINE_13,
    MB479_DISABILITY_CREDIT_LINE_14,
    MB479_DISABLED_DEPENDANTS_CREDIT_LINE_15,
    MB479_DEPENDENT_CHILDREN_CREDIT_LINE_16,
)
INPUT_NAMES = [
    "ca-mb/mb479_age_credit_line_8",
    "ca-mb/mb479_spouse_credits_line_12",
    "ca-mb/mb479_eligible_dependant_credit_line_13",
    "ca-mb/mb479_disability_credit_line_14",
    "ca-mb/mb479_disabled_dependants_credit_line_15",
    "ca-mb/mb479_dependent_children_credit_line_16",
]

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_total_credits_line_17
    """)

SALARIES = ["10000", "200000"]
# One value per input, in INPUTS order, each alone: the credit it adds to the basic 195.00.
ALONE = [
    ("113", "308.00"),
    ("390", "585.00"),
    ("195", "390.00"),
    ("226", "421.00"),
    ("124", "319.00"),
    ("52", "247.00"),
]


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(PARTS, start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, *artifacts: Artifact[Any]) -> Worksheet:
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *artifacts)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _total(sheet: Worksheet) -> Decimal:
    value: Decimal = sheet.get(manitoba_kinds().kind(KIND)).value
    return value


@pytest.mark.parametrize("salary", SALARIES)
def test_line_17_is_the_basic_credit_when_every_input_is_blank(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, Artifact(EMPLOYMENT_INCOME, D(salary)))

    assert _total(sheet) == D("195.00")


@pytest.mark.parametrize(("index", "case"), list(enumerate(ALONE)))
def test_line_17_adds_each_input_alone_to_the_basic_credit(
    tmp_path: Path, index: int, case: tuple[str, str]
) -> None:
    value, expected = case
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(INPUTS[index], D(value)),
    )

    assert _total(sheet) == D(expected)


def test_line_17_adds_all_six_inputs_and_the_basic_credit(tmp_path: Path) -> None:
    values = [D(value) for value, _ in ALONE]
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        *(Artifact(kind, value) for kind, value in zip(INPUTS, values, strict=True)),
    )

    assert _total(sheet) == D("195.00") + sum(values, D(0))
    assert _total(sheet) == D("1295.00")


def test_blank_inputs_print_one_left_blank_row_each(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, Artifact(EMPLOYMENT_INCOME, D("70000")))

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert sum("left blank, taken as 0" in row.lower() for row in rows) == 6


def test_a_given_input_prints_no_left_blank_row_of_its_own(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(MB479_AGE_CREDIT_LINE_8, D("113")),
    )

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert sum("left blank, taken as 0" in row.lower() for row in rows) == 5


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_total_credits_sum_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "title": "Total credits",
        "reference": "17",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [BASIC, *INPUT_NAMES]},
        "blank": {name: "0" for name in INPUT_NAMES},
        "produces": {"output": KIND},
    }


def test_line_17_is_a_registered_non_negative_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB479_TOTAL_CREDITS_LINE_17

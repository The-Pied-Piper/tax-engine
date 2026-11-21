"""NL428 (2025) line 35, add lines 27 to 34, from the salary alone, real parts.

Form text (Form NL428, CRA 5001-c-25e.txt, lines 120 to 129): "Line 27 and line 58240: Amount from
line 30800 of your return ^", "Line 28 and line 58280: Amount from line 31000 of your return ^",
"Line 29 and line 58300: Amount from line 31200 of your return ^", "Line 30 and line 58305: Amount
from line 31217 of your return ^", "Line 31 and line 58315: Volunteer firefighters' amount ^",
"Line 32 and line 58316: Search and rescue volunteers' amount ^", "Line 33 and line 58320: Child
care amount ^", "Line 34 and line 58330: Adoption expenses ^" and "Line 35: Add lines 27 to 34. =
^". Line 35 is one core/sum over lines 27 to 34 in line order. Lines 27 and 29 are computed from the
salary; lines 28, 30, 31, 32, 33 and 34 are optional inputs a salary-only caller leaves out, which
the sum reads as 0, as Manitoba's line 33 does.

The test composes the real Schedule 8 and T2204 parts, the real parts of lines 27, 28, 29, 30, 31,
32, 33 and 34 and the new `nl428_credits_line_35.yaml`, and types in only the salary (and, in some
tests, the optional inputs). The header and the form declaration, exporting only line 35, are made
up here, because the real ones are owned by another change. The figures are hand-computed from the
printed forms (not a CRA example): line 27 is the CPP base contribution amount (816.75 /
3,356.10) and line 29 the EI premiums (328.00 / 1,077.48), at salaries of 20,000 /
200,000.
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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_FORM, T1_LINE_10100_INPUT

D = Decimal
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_PART = NL_PARTS / "nl428_credits_line_35.yaml"
IDENTIFIER = "ca-nl/nl428_cpp_ei_and_other_line_35"
FORM_NAME = "ca-nl/nl428_credits"
LINE_27 = "ca-nl/nl428_cpp_contributions_line_27"
LINE_28 = "ca-nl/nl428_qpp_contributions_line_28"
LINE_29 = "ca-nl/nl428_ei_premiums_line_29"
LINE_30 = "ca-nl/nl428_ei_premiums_line_30"
LINE_31 = "ca-nl/nl428_volunteer_firefighters_amount_line_31"
LINE_32 = "ca-nl/nl428_search_and_rescue_volunteers_amount_line_32"
LINE_33 = "ca-nl/nl428_child_care_amount_line_33"
LINE_34 = "ca-nl/nl428_adoption_expenses_line_34"
LINES = [LINE_27, LINE_28, LINE_29, LINE_30, LINE_31, LINE_32, LINE_33, LINE_34]
OPTIONAL_LINES = [LINE_28, LINE_30, LINE_31, LINE_32, LINE_33, LINE_34]
CREDIT_PARTS = (
    "nl428_credits_line_27.yaml",
    "nl428_credits_line_28_input.yaml",
    "nl428_credits_line_29.yaml",
    "nl428_credits_line_30_input.yaml",
    "nl428_credits_line_31_input.yaml",
    "nl428_credits_line_32_input.yaml",
    "nl428_credits_line_33_input.yaml",
    "nl428_credits_line_34_input.yaml",
)

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
        - ca-nl/nl428_cpp_ei_and_other_line_35
    capabilities: []
    """)

# salary, line 35: line 27 plus line 29, the six optional lines being left out.
CASES = [
    ("20000", "1144.75"),
    ("200000", "4433.58"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield T1_LINE_10100_FORM
    yield FEDERAL_FORMS / "t1_employment_income" / "t1_employment_income_line_10100.yaml"
    for name in CREDIT_PARTS:
        yield NL_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Newfoundland and Labrador manifest of a test header, a form
    declaration and the real part files, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "00_t1_salary.yaml").write_text(
        T1_LINE_10100_INPUT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(),
            newfoundland_parameter_parsers(),
            newfoundland_units(),
        ),
        newfoundland_capabilities(),
    )


def _line_35(tmp_path: Path, salary: str, given_lines: dict[str, str] | None = None) -> Decimal:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    kinds = newfoundland_kinds()
    for identifier, amount in (given_lines or {}).items():
        given.append(Artifact(kinds.kind(identifier), D(amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return D(sheet.get(kinds.kind(IDENTIFIER)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_35_adds_lines_27_and_29_and_the_blank_optional_lines_read_as_0(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _line_35(tmp_path, salary) == D(expected)


@pytest.mark.parametrize("identifier", [LINE_28, LINE_34])
def test_line_35_adds_each_optional_line_when_given(tmp_path: Path, identifier: str) -> None:
    # Line 27 plus line 29 at a 20,000 salary is 1,144.75; a given 100.25 makes 1,245.00.
    assert _line_35(tmp_path, "20000", {identifier: "100.25"}) == D("1245.00")


def test_line_35_adds_all_the_optional_lines_together(tmp_path: Path) -> None:
    given = {
        LINE_28: "10.01",
        LINE_30: "20.02",
        LINE_31: "30.03",
        LINE_32: "40.04",
        LINE_33: "50.05",
        LINE_34: "60.06",
    }

    # 1,144.75 plus 210.21.
    assert _line_35(tmp_path, "20000", given) == D("1354.96")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_lines_27_to_34() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
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
        "reference": "35",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nl/cent_rounding"},
        "consumes": {"parts": LINES},
        "blank": dict.fromkeys(OPTIONAL_LINES, "0"),
        "produces": {"output": IDENTIFIER},
    }


def test_lines_27_and_29_have_no_blank_mapping_and_the_optional_lines_read_as_0() -> None:
    (step,) = _part()["capabilities"]

    assert LINE_27 not in step["blank"]
    assert LINE_29 not in step["blank"]
    assert set(step["blank"]) == set(OPTIONAL_LINES)
    assert set(step["blank"].values()) == {"0"}


def test_line_35_consumes_the_line_29_kind_not_an_input_kind() -> None:
    (step,) = _part()["capabilities"]

    assert step["consumes"]["parts"][2] == LINE_29
    assert step["consumes"]["parts"][0] == LINE_27


def test_line_35_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(IDENTIFIER)

    assert kind is nl_catalog.NL428_CPP_EI_AND_OTHER_LINE_35
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)

"""NB428 (2025) line 10, the age amount, over the optional year of birth (`ca/birth_year`).

Form text (Form NB428, CRA 5004-C): "Line 10 and line 58080: Age amount (if you were born in 1960 or
earlier) (use Worksheet NB428) (maximum $6,037)". Worksheet NB428 (CRA 5004-D), "Line 58080 - Age
amount": line 1 maximum 6,037.00; line 2 amount from line 23600; line 3 income threshold 44,945.00;
line 4 line 2 minus line 3 (if negative, enter "0"); line 5 rate 15%; line 6 line 4 times line 5;
line 7 line 1 minus line 6 (if negative, enter "0"). A request that leaves the year out is not born
in 1960 or earlier: line 10 is 0.00. Built as Nova Scotia's line 10 is; real parts.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)

D = Decimal
NB_PARTS = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025"
IDENTIFIER = "ca-nb/nb428_age_amount_line_10"
LINE_2 = "ca-nb/worksheet_nb428_age_amount_net_income_line_2"
FEDERAL_FORM_NAMES = ("schedule_8", "t2204", "t1_employment_income", "t1_taxable_income")
NB_PART_NAMES = (
    "nb428_line_10_input.yaml",
    "nb428_line_10_worksheet_lines_1_to_3.yaml",
    "nb428_line_10_worksheet_lines_4_to_7.yaml",
    "nb428_line_10.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-NB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-nb/nb428
      required: true
      exports:
        - ca-nb/nb428_age_amount_line_10
        - ca-nb/worksheet_nb428_age_amount_net_income_line_2
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    for form in FEDERAL_FORM_NAMES:
        yield from form_parts(form)
    for name in NB_PART_NAMES:
        yield NB_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary New Brunswick manifest of a test header, a form declaration
    and the real part files, every other namespace being the package list's own. The header and
    the form declaration are made up here, because the shared scaffold owns them."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**new_brunswick_packages().roots(), Namespace("ca-nb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, new_brunswick_kinds(), new_brunswick_units()),
        YamlParameterSource(
            new_brunswick_packages().roots(),
            new_brunswick_parameter_parsers(),
            new_brunswick_units(),
        ),
        new_brunswick_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, year: int | None = None) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if year is not None:
        given.append(Artifact(BIRTH_YEAR, year))
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NB"), 2025, tuple(given))
    )
    (sheet,) = worksheets["ca-nb/nb428"]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(new_brunswick_kinds().kind(identifier)).value)


@pytest.mark.parametrize(
    ("salary", "expected"), [("20000", "6037.00"), ("40000", "6037.00"), ("100000", "0.00")]
)
def test_line_10_born_in_1960_or_earlier(tmp_path: Path, salary: str, expected: str) -> None:
    assert _value(_sheet(tmp_path, salary, 1960), IDENTIFIER) == D(expected)


def test_line_10_in_the_reduction_range_is_the_worksheet_arithmetic(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "60000", 1950)
    net_income = _value(sheet, LINE_2)
    expected = (D("6037") - D("0.15") * (net_income - D("44945"))).quantize(D("0.01"))

    assert D("44945") < net_income < D("85192")
    assert _value(sheet, IDENTIFIER) == expected


@pytest.mark.parametrize("year", [None, 1961, 1990])
def test_line_10_is_zero_when_the_year_is_left_out_or_after_1960(
    tmp_path: Path, year: int | None
) -> None:
    assert _value(_sheet(tmp_path, "20000", year), IDENTIFIER) == D("0.00")

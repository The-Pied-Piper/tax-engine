"""Schedule 8 (5000-S8, 2025) from the salary alone: the form's real parts composed end to end.

Every line part has its own test with its neighbours typed in. This module composes the whole form:
it copies every `schedule_8*.yaml` part, plus `salary.yaml`, from the package into a temporary
manifest folder beside a test-only header, and types in only what the take-home caller types in,
the gross salary (`ca/employment_income`). The real header is not used because its output, T1 line
167, is not built yet. This is not a worked return: no return file, no slips, one form.

Form text: CRA 5000-S8 (2025), Part 3 lines 1 to 28 and the "Monthly proration for 2025" table.
The expected figures are the ones the full-form audit produced from this same composition.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca_on
import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError, NoAmountForCountError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.deductions import (
    CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_BASIC_EXEMPTION,
    CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    CPP_MONTHS,
    CPP_PART_3_LINE_2,
    CPP_PART_3_LINE_4,
    CPP_PART_3_LINE_5,
    CPP_PART_3_LINE_7,
    CPP_PART_3_LINE_11,
    CPP_PART_3_LINE_12,
    CPP_PART_3_LINE_22,
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
)
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.rc381_cpp_qpp import (
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)

D = Decimal
TAKE_HOME = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "take_home"
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)

# Part 2 and Part 3 lines by form line; line A (months) is an input, read by its own kind.
LINES = {
    "B": CPP_MAXIMUM_PENSIONABLE_EARNINGS,
    "D": CPP_ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    "E": CPP_BASIC_EXEMPTION,
    "1": T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
    "2": CPP_PART_3_LINE_2,
    "4": CPP_PART_3_LINE_4,
    "5": CPP_PART_3_LINE_5,
    "7": CPP_PART_3_LINE_7,
    "11": CPP_PART_3_LINE_11,
    "12": CPP_PART_3_LINE_12,
    "22": CPP_PART_3_LINE_22,
    "25": SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    "28": SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
}
CENT_LINES = ("11", "12", "22", "25", "28")


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "00_header.yaml").write_text(HEADER)
    for part in [TAKE_HOME / "salary.yaml", *sorted(TAKE_HOME.glob("schedule_8*.yaml"))]:
        shutil.copy(part, parts / part.name)
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def schedule_8(tmp_path: Path, salary: str, months: int | None = None) -> Worksheet:
    given: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if months is not None:
        given.append(Artifact(CPP_MONTHS, months))
    worksheets = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *given)
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet


def figures(sheet: Worksheet) -> dict[str, Decimal]:
    return {line: sheet.get(kind).value for line, kind in LINES.items()}


FULL_YEAR_70K = {
    "B": "71300.00",
    "D": "81200.00",
    "E": "3500.00",
    "1": "70000.00",
    "2": "70000.00",
    "4": "0",
    "5": "70000.00",
    "7": "66500.00",
    "11": "3291.75",
    "12": "665.00",
    "22": "0.00",
    "25": "3291.75",
    "28": "665.00",
}
FULL_YEAR_90K = {
    "B": "71300.00",
    "D": "81200.00",
    "E": "3500.00",
    "1": "81200.00",
    "2": "81200.00",
    "4": "9900.00",
    "5": "71300.00",
    "7": "67800.00",
    "11": "3356.10",
    "12": "678.00",
    "22": "396.00",
    "25": "3356.10",
    "28": "1074.00",
}
SIX_MONTHS_70K = {
    "B": "35650.00",
    "D": "40600.00",
    "E": "1750.00",
    "1": "70000.00",
    "2": "40600.00",
    "4": "4950.00",
    "5": "35650.00",
    "7": "33900.00",
    "11": "1678.05",
    "12": "339.00",
    "22": "198.00",
    "25": "1678.05",
    "28": "537.00",
}


@pytest.mark.parametrize(
    ("salary", "months", "expected"),
    [
        ("70000", None, FULL_YEAR_70K),
        ("90000", None, FULL_YEAR_90K),
        ("70000", 6, SIX_MONTHS_70K),
    ],
)
def test_every_line_matches_the_printed_form(
    tmp_path: Path, salary: str, months: int | None, expected: dict[str, str]
) -> None:
    result = figures(schedule_8(tmp_path, salary, months))

    assert result == {line: D(value) for line, value in expected.items()}


def test_a_full_year_salary_gives_twelve_months_on_line_a(tmp_path: Path) -> None:
    sheet = schedule_8(tmp_path, "70000")

    assert sheet.get(CPP_MONTHS).value == 12


def test_the_form_exports_are_the_return_lines_25_and_28(tmp_path: Path) -> None:
    sheet = schedule_8(tmp_path, "70000")

    assert sheet.get(SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3291.75")
    assert sheet.get(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("665.00")


@pytest.mark.parametrize("salary", ["70000", "90000", "12345.67"])
def test_the_cent_lines_have_exactly_two_decimals(tmp_path: Path, salary: str) -> None:
    result = figures(schedule_8(tmp_path, salary))

    for line in CENT_LINES:
        assert result[line].as_tuple().exponent == -2, line


def test_a_zero_month_request_is_refused(tmp_path: Path) -> None:
    with pytest.raises(NoAmountForCountError):
        schedule_8(tmp_path, "70000", 0)


def test_a_negative_salary_is_refused(tmp_path: Path) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        schedule_8(tmp_path, "-1")

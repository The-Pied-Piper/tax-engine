"""NL428 (2025) line 17, the age amount, from the salary alone, real parts.

Form text (Form NL428, CRA 5001-c-25e.txt): "Line 17 and line 58080: Age amount (if you were born in
1960 or earlier) (use Worksheet NL428) (maximum $7,064) ^". The amount is Worksheet NL428 line 7
(5001-d-25e.txt), claimed only if the filer was born in 1960 or earlier.

The part has five steps: `core/first_record_count` reads the T1's age 65 flag (`ca/age_65_or_older`,
worked out once there from the year of birth; a blank passes on, read as 0 by the times step);
`core/record_total` reads Worksheet NL428 line 7 and line 1 from its form; `core/times_count`
multiplies line 7 by the flag, rounded through `ca-nl/cent_rounding`, as line 40 does for its claim;
`core/at_most` checks it against the printed maximum. A salary-only filer leaves the year out, so
line 17 is 0.00. Worksheet line 7 is 7,064.00 at a 20,000 salary and 0.00 at 200,000
(hand-computed, not a CRA example).

The real federal parts Worksheet NL428 needs and the real worksheet parts are loaded under a
test-local header and form declarations over the package list of `support.py`.
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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import TimesCountLine
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    BIRTH_YEAR,
)
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
LINE_PART = NL_PARTS / "nl428_credits_line_17.yaml"
IDENTIFIER = "ca-nl/nl428_age_amount_line_17"
WORKSHEET_AMOUNT = "ca-nl/nl428_age_amount_worksheet_line_17"
FORM_NAME = "ca-nl/nl428_credits"
FEDERAL_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
NL_PART_NAMES = (
    "worksheet_nl428_line_4.yaml",
    "worksheet_nl428_line_6.yaml",
    "worksheet_nl428_line_7.yaml",
    "nl428_credits_line_17.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORMS = dedent("""\
    form:
      name: ca-nl/nl428_worksheet
      required: true
      exports:
        - ca-nl/worksheet_nl428_age_amount_maximum_line_1
        - ca-nl/worksheet_nl428_age_amount_line_7
    capabilities: []
    ---
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_age_amount_line_17
        - ca-nl/nl428_age_amount_worksheet_line_17
        - ca-nl/nl428_age_amount_maximum_line_17
        - ca-nl/nl428_age_amount_claimed_line_17
    capabilities: []
    """)

# salary, line 7 of the worksheet.
WORKSHEET_LINE_7 = [("20000", "7064.00"), ("200000", "0.00")]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in NL_PART_NAMES:
        yield NL_PARTS / name


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Newfoundland and Labrador manifest of a test header, the form
    declarations and the real part files, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    forms = FORMS.split("---\n")
    for number, text in enumerate(forms, start=1):
        (folder / f"01_form_{number}.yaml").write_text(text, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str, given_lines: dict[str, str] | None = None) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    kinds = newfoundland_kinds()
    for identifier, amount in (given_lines or {}).items():
        given.append(Artifact(kinds.kind(identifier), D(amount)))
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NL"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


def _born(tmp_path: Path, salary: str, born: int) -> Any:
    given: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(BIRTH_YEAR, born),
    ]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NL"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_17_is_0_for_a_salary_only_filer(tmp_path: Path, salary: str) -> None:
    assert _value(_sheet(tmp_path, salary), IDENTIFIER) == D("0.00")


@pytest.mark.parametrize(("salary", "worksheet"), WORKSHEET_LINE_7)
def test_line_17_is_worksheet_line_7_when_born_in_1960_or_earlier(
    tmp_path: Path, salary: str, worksheet: str
) -> None:
    assert _value(_born(tmp_path, salary, 1960), IDENTIFIER) == D(worksheet)


def test_line_17_is_0_when_born_after_1960(tmp_path: Path) -> None:
    assert _value(_born(tmp_path, "20000", 1961), IDENTIFIER) == D("0.00")


def test_a_blank_year_is_not_born_in_1960_or_earlier(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")

    assert sheet.get(nl_catalog.NL428_AGE_65_OR_OLDER).is_blank


def test_the_trace_records_the_yes_or_no_check_and_the_times_count_step(tmp_path: Path) -> None:
    trace = _born(tmp_path, "20000", 1960).trace

    (times,) = [line for line in trace if isinstance(line, TimesCountLine)]
    assert times.output is nl_catalog.NL428_AGE_AMOUNT_CLAIMED_LINE_17
    assert times.amount_kind is nl_catalog.NL428_AGE_AMOUNT_WORKSHEET_LINE_17
    assert times.amount_value == D("7064.00")
    assert times.count_kind is nl_catalog.NL428_AGE_65_OR_OLDER
    assert times.count == 1
    assert times.result == D("7064.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_the_five_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert [step["name"] for step in steps] == [
        "core/first_record_count",
        "core/record_total",
        "core/record_total",
        "core/times_count",
        "core/at_most",
    ]
    assert [step.get("reference") for step in steps] == [None, None, None, None, "17"]
    assert steps[1]["consumes"] == {
        "records": "ca-nl/nl428_worksheet.worksheet_nl428_age_amount_line_7"
    }
    assert steps[2]["consumes"] == {
        "records": "ca-nl/nl428_worksheet.worksheet_nl428_age_amount_maximum_line_1"
    }
    assert steps[4]["title"] == "Age amount"


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (IDENTIFIER, nl_catalog.NL428_AGE_AMOUNT_LINE_17),
        (WORKSHEET_AMOUNT, nl_catalog.NL428_AGE_AMOUNT_WORKSHEET_LINE_17),
    ],
)
def test_the_new_kinds_are_registered_non_negative_decimal_amount_kinds(
    identifier: str, constant: AmountKind
) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert kind is constant
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_line_17_is_the_claimed_amount_checked_against_the_printed_maximum(
    tmp_path: Path,
) -> None:
    sheet = _born(tmp_path, "20000", 1960)

    assert _value(sheet, "ca-nl/nl428_age_amount_maximum_line_17") == D("7064.00")
    assert _value(sheet, "ca-nl/nl428_age_amount_claimed_line_17") == D("7064.00")

"""NL428 (2025) line 17, the age amount, from the salary alone, real parts.

Form text (Form NL428, CRA 5001-c-25e.txt): "Line 17 and line 58080: Age amount (if you were born in
1960 or earlier) (use Worksheet NL428) (maximum $7,064) ^". The amount is Worksheet NL428 line 7
(5001-d-25e.txt), claimed only if the filer was born in 1960 or earlier.

The part has three steps: `ca/yes_or_no_count` reads the shared `ca/born_in_1960_or_earlier` count
(blank read as 0) and refuses a count above 1; `core/record_total` reads Worksheet NL428 line 7 from
its form; `core/times_count` multiplies it by the checked count, rounded through
`ca-nl/cent_rounding`, as line 40 does for its claim. A salary-only filer leaves the answer out, so
line 17 is 0.00. Worksheet line 7 is 7,064.00 at a 20,000 salary and 0.00 at
200,000 (hand-computed, not a CRA example).

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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import TimesCountLine, YesOrNoCountLine
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    BORN_IN_1960_OR_EARLIER,
    BORN_IN_1960_OR_EARLIER_CHECKED,
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
    "worksheet_nl428_line_58080_input.yaml",
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
        - ca-nl/worksheet_nl428_age_amount_line_7
    capabilities: []
    ---
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_age_amount_line_17
        - ca-nl/nl428_age_amount_worksheet_line_17
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
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


def _born(tmp_path: Path, salary: str, born: int) -> Any:
    given: list[Artifact[Any]] = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(BORN_IN_1960_OR_EARLIER, born),
    ]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_17_is_0_for_a_salary_only_filer(tmp_path: Path, salary: str) -> None:
    assert _value(_sheet(tmp_path, salary), IDENTIFIER) == D("0.00")


@pytest.mark.parametrize(("salary", "worksheet"), WORKSHEET_LINE_7)
def test_line_17_is_worksheet_line_7_when_born_in_1960_or_earlier(
    tmp_path: Path, salary: str, worksheet: str
) -> None:
    assert _value(_born(tmp_path, salary, 1), IDENTIFIER) == D(worksheet)


def test_line_17_is_0_when_the_answer_is_0(tmp_path: Path) -> None:
    assert _value(_born(tmp_path, "20000", 0), IDENTIFIER) == D("0.00")


def test_a_born_in_1960_count_above_1_is_refused(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _born(tmp_path, "20000", 2)


def test_a_blank_answer_is_checked_as_0(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000")

    assert sheet.get(BORN_IN_1960_OR_EARLIER_CHECKED).value == 0


def test_the_trace_records_the_yes_or_no_check_and_the_times_count_step(tmp_path: Path) -> None:
    trace = _born(tmp_path, "20000", 1).trace

    assert (
        YesOrNoCountLine(
            output=BORN_IN_1960_OR_EARLIER_CHECKED, count_kind=BORN_IN_1960_OR_EARLIER, count=1
        )
        in trace
    )
    (times,) = [line for line in trace if isinstance(line, TimesCountLine)]
    assert times.output is nl_catalog.NL428_AGE_AMOUNT_LINE_17
    assert times.amount_kind is nl_catalog.NL428_AGE_AMOUNT_WORKSHEET_LINE_17
    assert times.amount_value == D("7064.00")
    assert times.count_kind is BORN_IN_1960_OR_EARLIER_CHECKED
    assert times.count == 1
    assert times.result == D("7064.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_the_three_steps_in_order() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert [step["name"] for step in steps] == [
        "ca/yes_or_no_count",
        "core/record_total",
        "core/times_count",
    ]
    assert [step.get("reference") for step in steps] == [None, None, "17"]
    assert steps[1]["consumes"] == {
        "records": "ca-nl/nl428_worksheet.worksheet_nl428_age_amount_line_7"
    }
    assert steps[2]["title"] == "Age amount"


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

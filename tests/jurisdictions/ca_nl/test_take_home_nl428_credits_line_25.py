"""NL428 (2025) line 25, add lines 16, 17, 23 and 24 (line 20 left out), from the salary alone, real
parts.

Form text (Form NL428, CRA 5001-c-25e.txt, lines 98 to 115): "Line 16 and line 58040: Basic personal
amount Claim $11,067 ^", "Line 17 and line 58080: Age amount (if you were born in 1960 or earlier)
(use Worksheet NL428) (maximum $7,064) ^", "Line 20 and line 58120: Line 18 minus line 19 (if
negative, enter "0") (maximum $9,043) =", "Line 23 and line 58160: Line 21 minus line 22 (if
negative, enter "0") (maximum $9,043) =", "Line 24 and line 58200: Amount for infirm dependants age
18 or older (use Worksheet NL428) ^" and "Line 25: Add lines 16, 17, 20, 23, and 24. = ^".

Line 25 is one core/sum over lines 16, 17, 23 and 24 in line order: line 20 is the spouse amount,
which the take-home leaves out (single filer, owner ruling 23 Nov 2026, as Quebec was in #1925), so
the sum has no line 20. Line 17 is Worksheet NL428 line 7 read
from its form (core/record_total) and claimed only if the filer was born in 1960 or earlier (the
shared `ca/born_in_1960_or_earlier` count, checked by ca/yes_or_no_count, then core/times_count, as
line 40 claims its amount); a salary-only filer leaves the answer out, so line 17 is 0.00. Line 23
is blank for a filer with no eligible dependant and line 24 is an optional input; the sum reads each
blank as 0.

The test composes the real federal parts Worksheet NL428 needs, the real worksheet parts, the real
parts of lines 16, 17, 22, 23, 24 and 25 and types in the salary (and, in some tests, the
optional inputs). The header and the two form declarations are made up here, because the shared
scaffold owns them. Figures hand-computed (not a CRA example): the basic personal amount is
11,067.00; the age amount, when claimed, is Worksheet NL428 line 7, 7,064.00 at a 20,000 salary,
2,470.55 at 70,000 (net income 69,335.00, line 4 30,623.00, line 6 4,593.45) and 0.00 at 200,000.
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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BORN_IN_1960_OR_EARLIER
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
LINE_PART = NL_PARTS / "nl428_credits_line_25.yaml"
IDENTIFIER = "ca-nl/nl428_credits_subtotal_line_25"
FORM_NAME = "ca-nl/nl428_credits"
LINE_16 = "ca-nl/basic_personal_amount"
LINE_17 = "ca-nl/nl428_age_amount_line_17"
LINE_23 = "ca-nl/nl428_eligible_dependant_amount_line_23"
LINE_24 = "ca-nl/nl428_infirm_dependants_amount_line_24"
LINES = [LINE_16, LINE_17, LINE_23, LINE_24]
OPTIONAL_LINES = [LINE_23, LINE_24]
DEPENDANT_NET_INCOME = "ca-nl/nl428_eligible_dependant_net_income_line_22"
FEDERAL_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
NL_PART_NAMES = (
    "worksheet_nl428_line_4.yaml",
    "worksheet_nl428_line_6.yaml",
    "worksheet_nl428_line_7.yaml",
    "worksheet_nl428_line_58080_input.yaml",
    "nl428_credits_line_16.yaml",
    "nl428_credits_line_17.yaml",
    "nl428_credits_line_22_input.yaml",
    "nl428_credits_line_23.yaml",
    "nl428_credits_line_24_input.yaml",
    "nl428_credits_line_25.yaml",
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
        - ca-nl/nl428_credits_subtotal_line_25
    capabilities: []
    """)

# salary, line 7 of the worksheet.
WORKSHEET_LINE_7 = [("20000", "7064.00"), ("70000", "2470.55"), ("200000", "0.00")]


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
    for number, found in enumerate(dict.fromkeys(_part_files()), start=2):
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
        Artifact(BORN_IN_1960_OR_EARLIER, born),
    ]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NL"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def test_line_25_adds_the_eligible_dependant_amount_when_line_22_is_given(tmp_path: Path) -> None:
    # Line 21 9,948.00 less 5,000.00 is 4,948.00, under the 9,043 maximum.
    sheet = _sheet(tmp_path, "20000", {DEPENDANT_NET_INCOME: "5000"})

    assert _value(sheet, LINE_23) == D("4948.00")
    assert _value(sheet, IDENTIFIER) == D("16015.00")


def test_line_25_adds_the_infirm_dependants_amount_when_line_24_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "20000", {LINE_24: "100.25"})

    assert _value(sheet, IDENTIFIER) == D("11167.25")


def test_line_25_adds_every_line_together(tmp_path: Path) -> None:
    given = {DEPENDANT_NET_INCOME: "9948", LINE_24: "10.01"}
    sheet = _sheet(tmp_path, "20000", given)

    # 11,067.00 plus 0.00 plus 0.00 plus 10.01.
    assert _value(sheet, IDENTIFIER) == D("11077.01")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_sum_step_over_lines_16_17_23_and_24() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "25",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nl/cent_rounding"},
        "consumes": {"parts": LINES},
        "blank": dict.fromkeys(OPTIONAL_LINES, "0"),
        "produces": {"output": IDENTIFIER},
    }


def test_lines_16_and_17_have_no_blank_mapping() -> None:
    (step,) = _part()["capabilities"]

    assert LINE_16 not in step["blank"]
    assert LINE_17 not in step["blank"]


@pytest.mark.parametrize(
    ("identifier", "constant"),
    [
        (IDENTIFIER, nl_catalog.NL428_CREDITS_SUBTOTAL_LINE_25),
    ],
)
def test_line_25_is_a_registered_non_negative_decimal_amount_kind(
    identifier: str, constant: AmountKind
) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert kind is constant
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

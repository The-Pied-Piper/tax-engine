"""NL428 (2025) line 100, the low-income threshold, real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 100: If you claimed an amount on line 96
or line 97, enter $40,460; if not, enter $23,928." A salary-only caller claims neither, so line 100
is 23,928 (the printed figure, not a CRA example); a claim on line 96 or on line 97 gives 40,460.
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
from tax_engine.domain.kinds import CountKind
from tax_engine.domain.registry import Namespace
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
LINE_PART = NL_PARTS / "nl428_line_100.yaml"
LINE_22 = "ca-nl/nl428_eligible_dependant_net_income_line_22"
IDENTIFIER = "ca-nl/nl428_low_income_threshold_line_100"
LINE_96 = "ca-nl/nl428_reduction_for_spouse_or_common_law_partner_claimed_line_96"
FORM_NAME = "ca-nl/nl428"
FEDERAL_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
NL_PART_NAMES = (
    "worksheet_nl428_line_4.yaml",
    "worksheet_nl428_line_6.yaml",
    "worksheet_nl428_line_7.yaml",
    "worksheet_nl428_line_58080_input.yaml",
    "worksheet_nl428_line_58440_input.yaml",
    "worksheet_nl428_line_3_input.yaml",
    "worksheet_nl428_58440_line_5.yaml",
    "worksheet_nl428_58440_line_6.yaml",
    "worksheet_nl428_58440_line_7.yaml",
    "nl428_credits_line_16.yaml",
    "nl428_credits_line_17.yaml",
    "nl428_credits_line_19_input.yaml",
    "nl428_credits_line_20.yaml",
    "nl428_credits_line_22_input.yaml",
    "nl428_credits_line_23.yaml",
    "nl428_credits_line_24_input.yaml",
    "nl428_credits_line_25.yaml",
    "nl428_credits_line_27.yaml",
    "nl428_credits_line_28.yaml",
    "nl428_credits_line_29.yaml",
    "nl428_credits_line_30.yaml",
    "nl428_credits_line_31_input.yaml",
    "nl428_credits_line_32_input.yaml",
    "nl428_credits_line_33_input.yaml",
    "nl428_credits_line_34_input.yaml",
    "nl428_credits_line_35.yaml",
    "nl428_credits_line_36.yaml",
    "nl428_credits_line_37_input.yaml",
    "nl428_credits_line_37.yaml",
    "nl428_credits_line_38_input.yaml",
    "nl428_credits_line_39.yaml",
    "nl428_credits_line_40_input.yaml",
    "nl428_credits_line_40.yaml",
    "nl428_credits_line_41_input.yaml",
    "nl428_credits_line_42.yaml",
    "nl428_credits_line_43.yaml",
    "nl428_credits_line_44_input.yaml",
    "nl428_credits_line_45_input.yaml",
    "nl428_credits_line_46_input.yaml",
    "nl428_credits_line_47.yaml",
    "nl428_credits_line_48.yaml",
    "nl428_credits_line_49.yaml",
    "nl428_credits_line_51.yaml",
    "nl428_credits_line_52.yaml",
    "nl428_credits_line_53.yaml",
    "nl428_credits_line_54_input.yaml",
    "nl428_credits_line_55.yaml",
    "nl428_credits_line_56.yaml",
    "nl428_credits_line_58.yaml",
    "nl428_credits_line_59.yaml",
    "nl428_credits_line_60.yaml",
    "nl428_credits_line_61.yaml",
    "nl428_credits_line_62.yaml",
    "nl428_line_96_input.yaml",
    "nl428_line_96.yaml",
    "nl428_line_97.yaml",
    "nl428_line_100.yaml",
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
        - ca-nl/worksheet_nl428_disability_self_line_7
    capabilities: []
    ---
    form:
      name: ca-nl/nl428_credits
      required: true
      exports:
        - ca-nl/nl428_eligible_dependant_amount_line_23
        - ca-nl/nl428_non_refundable_credits_line_62
    capabilities: []
    ---
    form:
      name: ca-nl/nl428
      required: true
      exports:
        - ca-nl/nl428_low_income_reduction_dependant_line_97
        - ca-nl/nl428_low_income_threshold_line_100
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("schedule_9")
    yield from form_parts("t2204")
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


def _sheet(
    tmp_path: Path,
    salary: str,
    form: str,
    given_lines: dict[str, str] | None = None,
) -> Any:
    given: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    kinds = newfoundland_kinds()
    for identifier, amount in (given_lines or {}).items():
        kind = kinds.kind(identifier)
        given.append(Artifact(kind, int(amount) if isinstance(kind, CountKind) else D(amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-NL"), 2025, *given)
    (sheet,) = worksheets[form]
    return sheet


def _value(sheet: Any, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


def _line_100(tmp_path: Path, salary: str, given_lines: dict[str, str] | None = None) -> Any:
    return _sheet(tmp_path, salary, FORM_NAME, given_lines).get(
        newfoundland_kinds().kind(IDENTIFIER)
    )


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_100_is_23928_for_a_salary_only_filer(tmp_path: Path, salary: str) -> None:
    assert _line_100(tmp_path, salary).value == D("23928")


def test_line_100_is_40460_when_an_amount_is_claimed_on_line_96(tmp_path: Path) -> None:
    assert _line_100(tmp_path, "70000", {LINE_96: "1"}).value == D("40460")


def test_line_100_is_40460_when_an_amount_is_claimed_on_line_97(tmp_path: Path) -> None:
    assert _line_100(tmp_path, "70000", {LINE_22: "0"}).value == D("40460")


def test_line_100_is_23928_when_line_97_comes_to_nothing(tmp_path: Path) -> None:
    assert _line_100(tmp_path, "70000", {LINE_22: "9948"}).value == D("23928")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_counts_the_claims_and_chooses_between_the_two_printed_figures() -> None:
    part = _part()

    assert part["form"] == {"name": FORM_NAME}
    counted, *figures, choice = part["capabilities"]
    assert counted["name"] == "ca/count_by_conditions"
    assert counted["consumes"]["amounts"] == [
        "ca-nl/nl428_reduction_for_spouse_or_common_law_partner_line_96",
        "ca-nl/nl428_low_income_reduction_dependant_line_97",
    ]
    assert counted["blank"] == {"amounts": "0"}
    assert [figure["params"]["amount"] for figure in figures] == [
        "ca-nl/low_income_threshold",
        "ca-nl/low_income_threshold_with_spouse_or_dependant",
    ]
    assert choice == {
        "name": "core/choose_by_count",
        "reference": "100",
        "unit": "ca/cad",
        "consumes": {
            "count": "ca-nl/nl428_low_income_threshold_conditions_count_line_100",
            "when_none": "ca-nl/low_income_threshold",
            "when_any": "ca-nl/low_income_threshold_with_spouse_or_dependant",
        },
        "produces": {"output": IDENTIFIER},
    }


@pytest.mark.parametrize(
    ("identifier", "kind"),
    [
        ("ca-nl/low_income_threshold", nl_catalog.LOW_INCOME_THRESHOLD),
        (
            "ca-nl/low_income_threshold_with_spouse_or_dependant",
            nl_catalog.LOW_INCOME_THRESHOLD_WITH_SPOUSE_OR_DEPENDANT,
        ),
        (
            "ca-nl/nl428_low_income_threshold_conditions_count_line_100",
            nl_catalog.NL428_LOW_INCOME_THRESHOLD_CONDITIONS_COUNT_LINE_100,
        ),
        (IDENTIFIER, nl_catalog.NL428_LOW_INCOME_THRESHOLD_LINE_100),
    ],
)
def test_line_100_kinds_are_registered_non_negative(identifier: str, kind: Any) -> None:
    registered = newfoundland_kinds().kind(identifier)

    assert registered is kind
    assert non_negative(registered)

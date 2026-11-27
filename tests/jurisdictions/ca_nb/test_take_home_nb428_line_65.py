"""NB428 (2025) line 65, from the salary alone, real parts.

Form text: Form NB428, CRA 5004-C (on the ticket, read 26 Nov 2026); the part file's comment
quotes it.
One core/sum step, as the part declares. Figures hand-computed from the printed form
(line 8 less line 53, the optional lines blank).
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
import tax_engine.jurisdictions.ca_nb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)
from tests.kinds import non_negative

D = Decimal
NB_PARTS = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025"
LINE_PART = NB_PARTS / "nb428_line_65.yaml"
IDENTIFIER = "ca-nb/nb428_tax_with_minimum_tax_line_65"
FEDERAL_FORM_NAMES = (
    "schedule_9",
    "schedule_8",
    "t2204",
    "t1_employment_income",
    "t1_taxable_income",
    "t1_lines_copied_by_provinces",
)
NB_PART_NAMES = (
    "nb428_line_1.yaml",
    "nb428_line_3.yaml",
    "nb428_line_4.yaml",
    "nb428_line_5.yaml",
    "nb428_line_6.yaml",
    "nb428_line_7.yaml",
    "nb428_line_8.yaml",
    "nb428_line_55_input.yaml",
    "nb428_line_56.yaml",
    "nb428_line_9.yaml",
    "nb428_line_10_worksheet_lines_1_to_3.yaml",
    "nb428_line_10_worksheet_lines_4_to_7.yaml",
    "nb428_line_10.yaml",
    "nb428_line_18.yaml",
    "nb428_line_19.yaml",
    "nb428_line_21.yaml",
    "nb428_line_25.yaml",
    "nb428_line_26.yaml",
    "nb428_line_30.yaml",
    "nb428_line_33.yaml",
    "nb428_line_38.yaml",
    "nb428_line_46_input.yaml",
    "nb428_line_47.yaml",
    "nb428_line_49.yaml",
    "nb428_line_50.yaml",
    "nb428_line_51.yaml",
    "nb428_line_52.yaml",
    "nb428_line_53.yaml",
    "nb428_line_58.yaml",
    "nb428_line_60_input.yaml",
    "nb428_line_61_input.yaml",
    "nb428_line_62.yaml",
    "nb428_line_63.yaml",
    "nb428_line_64_input.yaml",
    "nb428_line_65.yaml",
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
        - ca-nb/nb428_tax_with_minimum_tax_line_65
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
    for number, found in enumerate(dict.fromkeys(_part_files()), start=2):
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


def _kind(identifier: str) -> AmountKind:
    kind = new_brunswick_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _value(tmp_path: Path, salary: str, given: dict[str, str] | None = None) -> Decimal:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(_kind(name), D(value)) for name, value in (given or {}).items()]
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NB"), 2025, tuple(artifacts))
    )
    (sheet,) = worksheets["ca-nb/nb428"]
    return D(sheet.get(_kind(IDENTIFIER)).value)


CASES = [("20000", "497.66"), ("30000", "1366.31"), ("70000", "5676.89")]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_65_at_the_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert _value(tmp_path, salary) == D(expected)


def test_line_65_case_1(tmp_path: Path) -> None:
    # Line 63 at 70,000 is 5,676.89; plus a line 64 of 25.
    given: dict[str, str] = {"ca-nb/nb428_additional_tax_minimum_tax_line_64": "25"}

    assert _value(tmp_path, "70000", given) == D("5701.89")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = new_brunswick_kinds().kind(IDENTIFIER)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_part_names_the_form_and_has_the_one_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-nb/nb428"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "reference": "65",
        "unit": "ca/cad",
        "params": {"rounding": "ca-nb/cent_rounding"},
        "consumes": {
            "parts": ["ca-nb/nb428_tax_line_63", "ca-nb/nb428_additional_tax_minimum_tax_line_64"]
        },
        "blank": {"ca-nb/nb428_additional_tax_minimum_tax_line_64": "0"},
        "produces": {"output": IDENTIFIER},
    }

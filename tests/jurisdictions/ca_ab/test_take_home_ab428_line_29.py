"""AB428 (2025) line 29, the employment insurance premiums, from the salary alone, real parts.

Form text (Form AB428, CRA 5009-c-25e.txt): "Employment insurance premiums: Line 29 and line
58300: Amount from line 31200 of your return". Line 31200 is T2204 line 16, the EI premiums credit
amount. Another form's export arrives only as a record list of one amount, so line 29 is a
core/record_total over that export, as Ontario's line 21 is.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts and the real
`ab428_line_29.yaml`, and types in only the salary. The AB428 form declaration is made up here,
exporting only line 29, because the real header is owned by another change. Alberta is not in
`registrations.JURISDICTIONS`, so the service is built over the Alberta package list of
`support.py`.
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
import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import AB428_EI_PREMIUMS_LINE_29
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = ALBERTA_PARTS / "ab428_line_29.yaml"
IDENTIFIER = "ca-ab/ab428_ei_premiums_line_29"

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_ei_premiums_line_29
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield ALBERTA_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, a form declaration and the
    real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _line_29(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet.get(AB428_EI_PREMIUMS_LINE_29).value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428_credits"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


# The EI rate is 1.64% to the maximum insurable earnings of $65,700, so $1,077.48 from there up.
@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "328.00"), ("70000", "1077.48"), ("200000", "1077.48")],
)
def test_line_29_is_the_t2204_line_16_ei_premiums(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _line_29(tmp_path, salary) == D(expected)


def test_the_part_is_one_record_total_step_over_the_t2204_line_16_records() -> None:
    assert _step() == {
        "name": "core/record_total",
        "title": "Employment insurance premiums",
        "reference": "29",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t2204.t2204_line_16"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_step_keys_mirror_the_ontario_on428_line_21_part() -> None:
    assert list(_step()) == ["name", "title", "reference", "unit", "consumes", "produces"]


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = alberta_kinds().kind(IDENTIFIER)

    assert kind is AB428_EI_PREMIUMS_LINE_29
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

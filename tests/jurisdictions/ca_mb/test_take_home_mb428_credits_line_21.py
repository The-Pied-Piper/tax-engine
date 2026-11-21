"""MB428 (2025) line 21, the employment insurance premiums, from the salary alone, real parts.

Form text (Form MB428, Manitoba Tax, CRA 5007-c-25e.txt): "Employment insurance premiums: Line 21
and line 58300: Amount from line 31200 of your return". Line 31200 is T2204 line 16, the EI premiums
credit amount. Another form's export arrives only as a record list of one amount, so line 21 is a
core/record_total over that export, as British Columbia's line 29 is.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts and the real
`mb428_credits_line_21.yaml`, and types in only the salary. The MB428 form declaration is made up
here, exporting only line 21, because the real header is owned by another change. Manitoba is not
yet in `registrations.JURISDICTIONS`, so the service is built over the Manitoba package list of
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
import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import MB428_EI_PREMIUMS_LINE_21
from tests.federal_forms import form_parts
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
PART = MB_PARTS / "mb428_credits_line_21.yaml"
IDENTIFIER = "ca-mb/mb428_ei_premiums_line_21"

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb428_credits
      required: true
      exports:
        - ca-mb/mb428_ei_premiums_line_21
    capabilities: []
    """)


def _part_files() -> Iterator[Path]:
    yield from form_parts("t1_employment_income")
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = found.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(),
            manitoba_parameter_parsers(),
            manitoba_units(),
        ),
        manitoba_capabilities(),
    )


def _line_21(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-mb/mb428_credits"]
    return sheet.get(MB428_EI_PREMIUMS_LINE_21).value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-mb/mb428_credits"}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


# The EI rate is 1.64% to the maximum insurable earnings of $65,700, so $1,077.48 from there up.
@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("0", "0.00"),
        ("10000", "164.00"),
        ("65701", "1077.48"),
    ],
)
def test_line_21_is_the_t2204_line_16_ei_premiums(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert _line_21(tmp_path, salary) == D(expected)


def test_the_part_is_one_record_total_step_over_the_t2204_line_16_records() -> None:
    assert _step() == {
        "name": "core/record_total",
        "title": "Employment insurance premiums",
        "reference": "21",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t2204.t2204_line_16"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is MB428_EI_PREMIUMS_LINE_21
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

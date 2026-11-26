"""NB428 (2025) line 51, from the salary alone, real parts.

Form text (Form NB428, CRA 5004-C, on the ticket, read 26 Nov 2026):
"Line 51: Amount from line 14 of your federal Schedule 9 multiplied by 17.95% =". The amount (box A)
is the Schedule 9 line 14 export totalled by the first step; the second step applies the printed
17.95% from the `ca-nb/donations_credit_rate_line_51` dataset. A blank Schedule 9 reads as 0.
The hand figures are asserted (not a CRA example). The test types in the T1 donations total.
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
LINE_PART = NB_PARTS / "nb428_line_51.yaml"
IDENTIFIER = "ca-nb/nb428_donations_credit_at_rate_line_51"
FEDERAL_FORM_NAMES = ("schedule_9", "t1_employment_income", "schedule_8", "t2204")
NB_PART_NAMES = ("nb428_line_51.yaml",)

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
        - ca-nb/nb428_donations_credit_at_rate_line_51
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


LINE_12 = "ca/donations_and_gifts_line_12"


CASES = [("1000", "143.60"), ("150.55", "0.00")]


@pytest.mark.parametrize(("amount", "expected"), CASES)
def test_line_51_is_the_schedule_9_amount_at_the_printed_rate(
    tmp_path: Path, amount: str, expected: str
) -> None:
    # Line 14 is the donations beyond the printed 200, times 17.95%, half-up to the cent:
    # 800 x 17.95% = 143.60; 150.55 is not beyond 200.
    assert _value(tmp_path, "70000", {LINE_12: amount}) == D(expected)


def test_line_51_is_0_when_the_amount_is_left_blank(tmp_path: Path) -> None:
    assert _value(tmp_path, "70000") == D("0.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = new_brunswick_kinds().kind(IDENTIFIER)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


def test_the_part_is_a_record_total_of_the_schedule_9_export_then_one_rate_step() -> None:
    assert _part() == {
        "form": {"name": "ca-nb/nb428"},
        "capabilities": [
            {
                "name": "core/record_total",
                "title": "Amount from line 14 of your federal Schedule 9",
                "reference": "51 box A",
                "unit": "ca/cad",
                "consumes": {"records": "ca/schedule_9.donations_and_gifts_line_14"},
                "produces": {"output": "ca-nb/nb428_donations_amount_line_51"},
            },
            {
                "name": "core/apply_rate",
                "reference": "51 box B",
                "unit": "ca/cad",
                "params": {"rate": "ca-nb/donations_credit_rate_line_51"},
                "consumes": {"base": "ca-nb/nb428_donations_amount_line_51"},
                "blank": {"base": "0"},
                "produces": {"output": IDENTIFIER},
            },
        ],
    }

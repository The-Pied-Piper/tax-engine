"""What the SK428 age line tests (2025) share: composing the real parts over a test-local form
declaration, typing in only the salary (plus, in some tests, the year of birth).

Each test composes the T1 employment income and taxable income forms and the real SK428 parts it
needs. The form declaration is made up here, exporting the lines read.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)

D = Decimal
CENT = D("0.01")
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FORM_NAME = "ca-sk/sk428_credits"
FEDERAL_FORM_NAMES = (
    "schedule_8",
    "t2204",
    "t1_employment_income",
    "t1_taxable_income",
    "t1_lines_copied_by_provinces",
    "schedule_9",
)
HEADER = (
    "jurisdiction: CA-SK\nversion: 1\nvalid_from_tax_year: 2025\noutputs: []\ncapabilities: []\n"
)


def cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _form(exports: tuple[str, ...]) -> str:
    listed = "\n".join(f"    - {each}" for each in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{listed}\ncapabilities: []\n"


def _part_files(lines: tuple[str, ...]) -> Iterator[Path]:
    yield from form_parts(*FEDERAL_FORM_NAMES)
    for name in lines:
        yield SK_PARTS / name


def service(
    tmp_path: Path, lines: tuple[str, ...], exports: tuple[str, ...]
) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real part files named in `lines`, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(_form(exports), encoding="utf-8")
    for number, part in enumerate(_part_files(lines), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def sheet(
    tmp_path: Path,
    salary: str,
    lines: tuple[str, ...],
    exports: tuple[str, ...],
    given: tuple[Artifact[Any], ...] = (),
) -> Worksheet:
    worksheets = service(tmp_path, lines, exports).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-SK"),
            2025,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), *given),
        )
    )
    (result,) = worksheets[FORM_NAME]
    return result


def value(worksheet: Worksheet, identifier: str) -> Decimal:
    found = saskatchewan_kinds().kind(identifier)
    assert isinstance(found, AmountKind)
    return D(worksheet.get(found).value)

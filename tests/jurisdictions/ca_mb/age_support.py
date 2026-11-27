"""What the Manitoba age line tests (MB428 line 10, Schedule MB428-A line 4, MB479 line 8, 2025)
share: composing the real parts over a test-local form declaration.

Each test composes the real T1 forms the age lines read (the T1 employment income, taxable income
and copied-lines forms, the last holding the year of birth) and the real Manitoba line parts it
needs, and types in only the salary and, where it wants one, the year of birth. The form
declaration is made up here, exporting the lines read, because the shared scaffold owns them.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca_mb
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
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)

D = Decimal
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORM_NAMES = (
    "schedule_8",
    "t1_employment_income",
    "t1_taxable_income",
    "t1_lines_copied_by_provinces",
)
HEADER = (
    "jurisdiction: CA-MB\nversion: 1\nvalid_from_tax_year: 2025\noutputs: []\ncapabilities: []\n"
)


def cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _form(form_name: str, exports: tuple[str, ...]) -> str:
    listed = "\n".join(f"    - {each}" for each in exports)
    return f"form:\n  name: {form_name}\n  required: true\n  exports:\n{listed}\ncapabilities: []\n"


def _part_files(lines: tuple[str, ...]) -> Iterator[Path]:
    yield from form_parts(*FEDERAL_FORM_NAMES)
    for name in lines:
        yield MB_PARTS / name


def sheet(
    tmp_path: Path,
    form_name: str,
    salary: str,
    lines: tuple[str, ...],
    exports: tuple[str, ...],
    given: tuple[Artifact[Any], ...] = (),
) -> Worksheet:
    """The one worksheet of `form_name` over a temporary Manitoba manifest of a test header, a form
    declaration and the real part files named in `lines`, every other namespace being the package
    list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(_form(form_name, exports), encoding="utf-8")
    for number, part in enumerate(_part_files(lines), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    service = TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )
    worksheets = service.compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-MB"),
            2025,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), *given),
        )
    )
    (result,) = worksheets[form_name]
    return result


def value(worksheet: Worksheet, identifier: str) -> Decimal:
    found = manitoba_kinds().kind(identifier)
    assert isinstance(found, AmountKind)
    return D(worksheet.get(found).value)

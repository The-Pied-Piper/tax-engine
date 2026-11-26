"""What the NS428 Part C line tests (lines 54 to 64, 2025) share: composing the real parts over a
test-local form declaration, the optional lines a caller may type in, and the figures the form
arithmetic gives for a salary-only filer.

Each test composes the federal forms the form reads (Schedule 8, T2204, Schedule 9, T691, the T1
employment income, taxable income and copied-lines forms) and every real NS428 line part, and types
in only the salary plus the optional lines the test is about. The real form part declares no exports
yet, so the form declaration is made up here, exporting the lines read.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_ns import ns428_credits_support as base
from tests.jurisdictions.ca_ns.ns428_credits_support import parameter_source
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_capabilities,
    nova_scotia_kinds,
    nova_scotia_packages,
    nova_scotia_units,
)

D = Decimal
NS_PARTS = base.NS_PARTS
FORM_NAME = base.FORM_NAME
FEDERAL_FORM_NAMES = (*base.FEDERAL_FORM_NAMES, "t691")

LINE_8 = "ca-ns/ns428_tax_on_taxable_income_line_8"
LINE_52 = base.LINE_52
LINE_54 = "ca-ns/ns428_tax_on_split_income_line_54"
LINE_55 = "ca-ns/ns428_tax_line_55"
LINE_57 = "ca-ns/ns428_dividend_tax_credit_line_57"
LINE_58_AMOUNT = "ca-ns/ns428_minimum_tax_carryover_amount_line_58"
LINE_58 = "ca-ns/ns428_minimum_tax_carryover_line_58"
LINE_59 = "ca-ns/ns428_credits_subtotal_line_59"
LINE_60 = "ca-ns/ns428_tax_line_60"
LINE_61_AMOUNT = "ca-ns/ns428_minimum_tax_t691_amount_line_61"
LINE_61 = "ca-ns/ns428_minimum_tax_additional_line_61"
LINE_62 = "ca-ns/ns428_tax_line_62"
LINE_63 = "ca-ns/ns428_provincial_foreign_tax_credit_line_63"
LINE_64 = "ca-ns/ns428_tax_after_credits_line_64"
CARRYOVER = "ca/minimum_tax_carryover"
RATE = "ca-ns/minimum_tax_rate"

# (salary, line 8 = 53 = 55, line 52 = 56 = 59, line 60 = 62 = 64): the ticket's figures, each
# derived by hand from the form's arithmetic.
CASES = [
    ("20000", "1743.50", "1132.92", "610.58"),
    ("30000", "2613.71", "1190.85", "1422.86"),
    ("70000", "8629.45", "1416.35", "7213.10"),
]


def _part_names() -> list[Path]:
    def number(path: Path) -> int:
        return int(path.name.split("_")[2].split(".")[0])

    return sorted(NS_PARTS.glob("ns428_line_*.yaml"), key=lambda path: (number(path), path.name))


def _form(exports: tuple[str, ...]) -> str:
    listed = "\n".join(f"    - {each}" for each in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{listed}\ncapabilities: []\n"


def service(tmp_path: Path, exports: tuple[str, ...]) -> TaxComputationService:
    """The engine over a temporary Nova Scotia manifest of a test header, a form declaration and
    every real line part of the form, the other namespaces being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(base.HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(_form(exports), encoding="utf-8")
    parts = [*form_parts(*FEDERAL_FORM_NAMES), *_part_names()]
    for number, part in enumerate(parts, start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**nova_scotia_packages().roots(), Namespace("ca-ns"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, nova_scotia_kinds(), nova_scotia_units()),
        parameter_source(),
        nova_scotia_capabilities(),
    )


def sheet(
    tmp_path: Path, salary: str, exports: tuple[str, ...], given: dict[str, str] | None = None
) -> Worksheet:
    """The form's sheet for `salary`, with the optional lines in `given` (kind identifier to
    amount) typed in."""
    kinds = nova_scotia_kinds()
    typed: list[Artifact[Any]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    for identifier, amount in (given or {}).items():
        typed.append(Artifact(kinds.kind(identifier), D(amount)))
    worksheets = service(tmp_path, exports).compute(
        TaxCalculationRequest(JurisdictionCode("CA-NS"), 2025, tuple(typed))
    )
    (result,) = worksheets[FORM_NAME]
    return result


def value(worksheet: Worksheet, identifier: str) -> Decimal:
    return base.value(worksheet, identifier)


def line(
    tmp_path: Path, salary: str, identifier: str, given: dict[str, str] | None = None
) -> Decimal:
    """The figure of the kind `identifier` on the form's sheet for `salary`."""
    # Line 64 is read by a later form, so it is always exported; the requested kind joins it.
    exports = tuple(dict.fromkeys((identifier, LINE_64)))
    return value(sheet(tmp_path, salary, exports, given), identifier)


def part(name: str) -> dict[str, Any]:
    """The real part file `name`, parsed."""
    import yaml

    parsed = yaml.safe_load((NS_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed

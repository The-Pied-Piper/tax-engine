"""What the NS428 Part B line tests from line 27 on (2025) share: composing the real parts over a
test-local form declaration, and the figures the form arithmetic gives for a salary-only filer.

Each test composes the federal forms the credits read (Schedule 8, T2204, Schedule 9, the T1
employment income, taxable income and copied-lines forms) and the real NS428 line parts it needs,
and types in only the salary (plus, in some tests, the pension income amount). The real form part
declares no exports yet, so the form declaration is made up here, exporting the lines read.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca_ns
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
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_capabilities,
    nova_scotia_kinds,
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
    nova_scotia_units,
)

D = Decimal
CENT = D("0.01")
NS_PARTS = Path(tax_engine.jurisdictions.ca_ns.__file__).parent / "manifests" / "2025"
FORM_NAME = "ca-ns/ns428"
FEDERAL_FORM_NAMES = (
    "schedule_8",
    "t2204",
    "t1_employment_income",
    "t1_taxable_income",
    "t1_lines_copied_by_provinces",
    "schedule_9",
)
# The real NS428 parts that give line 26, which line 29 reads, in line order (the part file names).
CHAIN = (
    "ns428_line_9.yaml",
    "ns428_line_10_input.yaml",
    "ns428_line_10_worksheet_lines_1_to_3.yaml",
    "ns428_line_10_worksheet_lines_4_to_7.yaml",
    "ns428_line_10.yaml",
    "ns428_line_19.yaml",
    "ns428_line_21.yaml",
    "ns428_line_22.yaml",
    "ns428_line_23.yaml",
    "ns428_line_24.yaml",
    "ns428_line_25.yaml",
    "ns428_line_26.yaml",
)
HEADER = (
    "jurisdiction: CA-NS\nversion: 1\nvalid_from_tax_year: 2025\noutputs: []\ncapabilities: []\n"
)

LINE_26 = "ca-ns/ns428_credits_subtotal_line_26"
PENSION = "ca-ns/ns428_pension_income_amount"
PENSION_MAXIMUM = "ca-ns/ns428_pension_income_amount_maximum"
LINE_27 = "ca-ns/ns428_pension_income_amount_checked_line_27"
LINE_29 = "ca-ns/ns428_credits_subtotal_line_29"
LINE_32 = "ca-ns/ns428_credits_subtotal_line_32"
LINE_33 = "ca-ns/ns428_student_loan_interest_line_33"
LINE_37 = "ca-ns/ns428_credits_subtotal_line_37"
LINE_38 = "ca-ns/ns428_medical_expenses_line_38"
LINE_39 = "ca-ns/ns428_net_income_line_39"
LINE_41 = "ca-ns/ns428_medical_expenses_rate_amount_line_41"
LINE_42 = "ca-ns/ns428_medical_expenses_limited_amount_line_42"
LINE_43 = "ca-ns/ns428_medical_expenses_over_limit_line_43"
LINE_45 = "ca-ns/ns428_medical_expenses_line_45"
LINE_46 = "ca-ns/ns428_credits_total_line_46"
LINE_48 = "ca-ns/ns428_credits_at_rate_line_48"
LINE_49_A = "ca-ns/ns428_donations_amount_line_49"
LINE_49_B = "ca-ns/ns428_donations_credit_at_rate_line_49"
LINE_50_A = "ca-ns/ns428_donations_amount_line_50"
LINE_50_B = "ca-ns/ns428_donations_credit_at_rate_line_50"
LINE_51 = "ca-ns/ns428_donations_credit_line_51"
LINE_52 = "ca-ns/ns428_non_refundable_credits_line_52"

# (salary, line 26, line 39, line 41, line 42), hand-computed: line 26 is the basic personal amount
# plus the CPP and EI amounts (the line 26 ticket's figures), line 39 the salary less the enhanced
# CPP deduction, line 41 is 3% of it and line 42 the lesser of that and the printed $1,637.
CASES = [
    ("20000", "12888.75", "19835.00", "595.05", "595.05"),
    ("30000", "13547.75", "29735.00", "892.05", "892.05"),
    ("70000", "16113.23", "69335.00", "2080.05", "1637.00"),
]
# (salary, line 46, line 48): line 46 is line 26 with no other claim, line 48 is 8.79% of it, half
# up to the cent. The 70,000 and 30,000 and 20,000 figures are the ticket's.
CREDITS = [
    ("20000", "12888.75", "1132.92"),
    ("30000", "13547.75", "1190.85"),
    ("70000", "16113.23", "1416.35"),
]


def cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def part_path(name: str) -> Path:
    return NS_PARTS / name


def _form(exports: tuple[str, ...]) -> str:
    listed = "\n".join(f"    - {each}" for each in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{listed}\ncapabilities: []\n"


def _part_files(lines: tuple[str, ...]) -> Iterator[Path]:
    yield from form_parts(*FEDERAL_FORM_NAMES)
    for name in lines:
        yield part_path(name)


def parameter_source() -> YamlParameterSource:
    return YamlParameterSource(
        nova_scotia_packages().roots(), nova_scotia_parameter_parsers(), nova_scotia_units()
    )


def service(
    tmp_path: Path, lines: tuple[str, ...], exports: tuple[str, ...]
) -> TaxComputationService:
    """The engine over a temporary Nova Scotia manifest of a test header, a form declaration and
    the real part files named in `lines`, every other namespace being the package list's
    own. The header and the form declaration are made up here, because the shared scaffold owns
    them."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(_form(exports), encoding="utf-8")
    for number, part in enumerate(_part_files(lines), start=2):
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
    tmp_path: Path,
    salary: str,
    lines: tuple[str, ...],
    exports: tuple[str, ...],
    given: tuple[Artifact[Any], ...] = (),
) -> Worksheet:
    worksheets = service(tmp_path, lines, exports).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NS"),
            2025,
            (Artifact(EMPLOYMENT_INCOME, D(salary)), *given),
        )
    )
    (result,) = worksheets[FORM_NAME]
    return result


def kind(identifier: str) -> AmountKind:
    found = nova_scotia_kinds().kind(identifier)
    assert isinstance(found, AmountKind)
    return found


def value(worksheet: Worksheet, identifier: str) -> Decimal:
    return D(worksheet.get(kind(identifier)).value)

"""What the PE428 Part A line tests (lines 1 to 8, 2025) share: composing the real parts over a
test-local form declaration, the figures the form prints, and the form's arithmetic in Decimal.

Each test composes the T1 employment income form, the real Schedule 8 and T1 taxable income parts
and the real PE428 line parts it needs, and types in only the salary. The form declaration is made
up here, exporting the lines read, unless a test passes the real `pe428.yaml`.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent

import tax_engine.jurisdictions.ca_pe
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
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_capabilities,
    prince_edward_island_kinds,
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
    prince_edward_island_units,
)

D = Decimal
CENT = D("0.01")
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
FORM_NAME = "ca-pe/pe428"
ROUNDING = "ca-pe/cent_rounding"
BRACKETS = "ca-pe/brackets"
LINE_1 = "ca-pe/pe428_taxable_income_line_1"
LINE_3 = "ca-pe/pe428_bracket_lower_bound_line_3"
LINE_4 = "ca-pe/pe428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-pe/pe428_bracket_rate_line_5"
LINE_6 = "ca-pe/pe428_tax_on_excess_line_6"
LINE_7 = "ca-pe/pe428_bracket_tax_at_start_line_7"
LINE_8 = "ca-pe/pe428_tax_on_taxable_income_line_8"
LINE_54 = "ca-pe/pe428_non_refundable_credits_line_54"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-PE
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)

# The five columns as printed (Form PE428, CRA 5002-C, 2025): line 3, line 5 and line 7 of each.
COLUMNS = [
    (D("0.00"), D("0.095"), D("0.00")),
    (D("33328.00"), D("0.1347"), D("3166.16")),
    (D("64656.00"), D("0.166"), D("7386.04")),
    (D("105000.00"), D("0.1762"), D("14083.15")),
    (D("140000.00"), D("0.19"), D("20250.15")),
]

# (salary, line 1): hand-derived taxable income, the salary less the enhanced CPP deduction.
CASES = [
    ("20000", "19835.00"),
    ("30000", "29735.00"),
    ("40000", "39635.00"),
    ("50469.70", "50000.00"),
    ("70000", "69335.00"),
    ("100000", "98926.00"),
    ("121074", "120000.00"),
    ("200000", "198926.00"),
    ("201074", "200000.00"),
]
# Salaries whose taxable income is exactly a column's upper bound, and one cent more: a line 1 at a
# bound is still in the lower column.
EDGES = [
    ("33629.29", "33328.00"),
    ("33629.30", "33328.01"),
    ("65273.74", "64656.00"),
    ("65273.75", "64656.01"),
    ("106074", "105000.00"),
    ("106074.01", "105000.01"),
    ("141074", "140000.00"),
    ("141074.01", "140000.01"),
]
ABOVE_TOP = ["500000", "5000000"]


def cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def taxable_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200, each rounded half-up to the cent."""
    enhanced = cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def column(line_1: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """The lower bound (line 3), the rate (line 5) and the tax at the start (line 7) printed for
    the column line 1 falls in; a line 1 at a column's upper bound is in that column."""
    chosen = COLUMNS[0]
    for each in COLUMNS:
        if line_1 > each[0]:
            chosen = each
    return chosen


def derived(salary: Decimal) -> dict[str, Decimal]:
    """Lines 1, 3, 4, 5, 6, 7 and 8 by the form's arithmetic, in Decimal."""
    line_1 = taxable_income(salary)
    lower, rate, line_7 = column(line_1)
    line_4 = max(line_1 - lower, D(0))
    line_6 = cent(line_4 * rate)
    return {
        LINE_1: line_1,
        LINE_3: lower,
        LINE_4: line_4,
        LINE_5: rate,
        LINE_6: line_6,
        LINE_7: line_7,
        LINE_8: line_6 + line_7,
    }


def part_path(number: int) -> Path:
    return PE_PARTS / f"pe428_line_{number}.yaml"


def _form(exports: tuple[str, ...]) -> str:
    listed = "\n".join(f"    - {each}" for each in exports)
    return f"form:\n  name: {FORM_NAME}\n  required: true\n  exports:\n{listed}\ncapabilities: []\n"


def _part_files(lines: tuple[int, ...]) -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for number in lines:
        yield part_path(number)


def service(
    tmp_path: Path,
    lines: tuple[int, ...],
    exports: tuple[str, ...],
    form_part: Path | None = None,
) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    declaration = _form(exports) if form_part is None else form_part.read_text(encoding="utf-8")
    (folder / "01_form.yaml").write_text(declaration, encoding="utf-8")
    for number, part in enumerate(_part_files(lines), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**prince_edward_island_packages().roots(), Namespace("ca-pe"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, prince_edward_island_kinds(), prince_edward_island_units()),
        parameter_source(),
        prince_edward_island_capabilities(),
    )


def parameter_source() -> YamlParameterSource:
    return YamlParameterSource(
        prince_edward_island_packages().roots(),
        prince_edward_island_parameter_parsers(),
        prince_edward_island_units(),
    )


def sheet(
    tmp_path: Path,
    salary: str,
    lines: tuple[int, ...],
    exports: tuple[str, ...],
    form_part: Path | None = None,
) -> Worksheet:
    worksheets = service(tmp_path, lines, exports, form_part).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-PE"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (result,) = worksheets[FORM_NAME]
    return result


def kind(identifier: str) -> AmountKind:
    found = prince_edward_island_kinds().kind(identifier)
    assert isinstance(found, AmountKind)
    return found

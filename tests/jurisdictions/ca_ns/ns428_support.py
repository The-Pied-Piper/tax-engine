"""What the NS428 Part A line tests (lines 1 to 8, 2025) share: composing the real parts over a
test-local form declaration, the figures the form prints, and the form's arithmetic in Decimal.

Each test composes the T1 employment income form, the real Schedule 8 and T1 taxable income parts
and the real NS428 line parts it needs, and types in only the salary. The real form part does not
exist yet, so the form declaration is made up here, exporting the lines read.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent

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
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
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
ROUNDING = "ca-ns/cent_rounding"
BRACKETS = "ca-ns/brackets"
LINE_1 = "ca-ns/ns428_taxable_income_line_1"
LINE_3 = "ca-ns/ns428_bracket_lower_bound_line_3"
LINE_4 = "ca-ns/ns428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-ns/ns428_bracket_rate_line_5"
LINE_6 = "ca-ns/ns428_tax_on_excess_line_6"
LINE_7 = "ca-ns/ns428_bracket_tax_at_start_line_7"
LINE_8 = "ca-ns/ns428_tax_on_taxable_income_line_8"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-NS
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)

# The five columns as printed (Form NS428, CRA 5003-C, 2025): line 3, line 5 and line 7 of each.
COLUMNS = [
    (D("0.00"), D("0.0879"), D("0.00")),
    (D("30507.00"), D("0.1495"), D("2681.57")),
    (D("61015.00"), D("0.1667"), D("7242.51")),
    (D("95883.00"), D("0.175"), D("13055.01")),
    (D("154650.00"), D("0.21"), D("23339.23")),
]

# (salary, line 1): hand-derived taxable income, the salary less the enhanced CPP deduction.
CASES = [
    ("20000", "19835.00"),
    ("30000", "29735.00"),
    ("40000", "39635.00"),
    ("70000", "69335.00"),
    ("100000", "98926.00"),
    ("200000", "198926.00"),
]
# Salaries whose taxable income is exactly a column's upper bound, and one cent more: a line 1 at a
# bound is still in the lower column.
EDGES = [
    ("30779.80", "30507.00"),
    ("30779.81", "30507.01"),
    ("61595.96", "61015.00"),
    ("61595.97", "61015.01"),
    ("96957.00", "95883.00"),
    ("96957.01", "95883.01"),
    ("155724.00", "154650.00"),
    ("155724.01", "154650.01"),
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
    return NS_PARTS / f"ns428_line_{number}.yaml"


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
    tmp_path: Path, lines: tuple[int, ...], exports: tuple[str, ...]
) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(_form(exports), encoding="utf-8")
    for number, part in enumerate(dict.fromkeys(_part_files(lines)), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**nova_scotia_packages().roots(), Namespace("ca-ns"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, nova_scotia_kinds(), nova_scotia_units()),
        parameter_source(),
        nova_scotia_capabilities(),
    )


def parameter_source() -> YamlParameterSource:
    return YamlParameterSource(
        nova_scotia_packages().roots(), nova_scotia_parameter_parsers(), nova_scotia_units()
    )


def sheet(
    tmp_path: Path, salary: str, lines: tuple[int, ...], exports: tuple[str, ...]
) -> Worksheet:
    worksheets = service(tmp_path, lines, exports).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NS"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (result,) = worksheets[FORM_NAME]
    return result


def kind(identifier: str) -> AmountKind:
    found = nova_scotia_kinds().kind(identifier)
    assert isinstance(found, AmountKind)
    return found

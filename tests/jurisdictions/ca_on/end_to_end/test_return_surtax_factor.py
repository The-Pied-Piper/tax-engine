"""CA-ON 2025 end to end: the return summary's Ontario surtax base and surtax factor.

The return reads ON428 line 65, the surtax base (`ca-on/on428_surtax_base_line_65`), now an export
of the form, with `core/record_total` into its own `ca-on/ontario_surtax_base`, as it reads T1 line
167. A second step, `ca-on/surtax_factor`, reads that figure and the two datasets
`ca-on/surtax_line_66` and `ca-on/surtax_line_67` (ON428 line 66 "(Line 65 minus $5,710)
multiplied by 20%" and line 67 "(Line 65 minus $7,307) multiplied by 36%") and produces
`ca-on/ontario_surtax_factor`: 1 plus the rate of each tier whose threshold line 65 is over. A line
65 at a threshold is not over it. The factor is a plain figure with no unit.

The figures are runs of the real parts for a single filer whose salary is the only input (Ontario
resident, 2025). Line 65 by salary: $20,000 is 300.14, $70,000 is 3,311.45, $100,000 is 6,015.78,
$110,000 is 6,994.12, $120,000 is 8,110.12 and $150,000 is 11,458.12. So the factor is 1 at
$20,000 and $70,000, 1.20 at $100,000 and $110,000 (between 5,710 and 7,307) and 1.56 at $120,000
and $150,000 (above 7,307). The salaries are chosen by a run of the engine, not a CRA example.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import pytest

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import ON428_SURTAX_BASE_LINE_65
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService, header_without_imports
from tests.kinds import bundled_kinds, non_negative

D = Decimal
CODE = JurisdictionCode("CA-ON")
BASE = "ca-on/ontario_surtax_base"
FACTOR = "ca-on/ontario_surtax_factor"
HEADER = header_without_imports()
RETURN = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
PARTS = (
    "salary.yaml",
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml", "salary.yaml"}
    ),
)

# Salary, line 65 and the factor, from runs of the real parts.
FIGURES = [
    ("20000", "300.14", "1"),
    ("70000", "3311.45", "1"),
    ("100000", "6015.78", "1.20"),
    ("110000", "6994.12", "1.20"),
    ("120000", "8110.12", "1.56"),
    ("150000", "11458.12", "1.56"),
]


def _run(take_home_service: TakeHomeService, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return take_home_service(HEADER, RETURN, *PARTS).compute(
        CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


def _return_sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    (sheet,) = _run(take_home_service, salary)["ca-on/return"]
    return sheet


def _factor_line(sheet: Worksheet) -> Any:
    """The one trace line of the factor step, found by its class."""
    from tax_engine.jurisdictions.ca_on.trace import SurtaxFactorLine

    (line,) = [line for line in sheet.trace if isinstance(line, SurtaxFactorLine)]
    return line


@pytest.mark.parametrize(("salary", "line_65", "factor"), FIGURES)
def test_the_return_reads_line_65_and_gives_the_surtax_factor(
    take_home_service: TakeHomeService, salary: str, line_65: str, factor: str
) -> None:
    sheet = _return_sheet(take_home_service, salary)
    kinds = bundled_kinds()

    base = sheet.get(kinds.kind(BASE)).value
    assert base == D(line_65)
    assert base.as_tuple().exponent == -2
    assert sheet.get(kinds.kind(FACTOR)).value == D(factor)


@pytest.mark.parametrize(("salary", "line_65", "factor"), FIGURES)
def test_the_return_base_is_line_65_of_on428(
    take_home_service: TakeHomeService, salary: str, line_65: str, factor: str
) -> None:
    worksheets = _run(take_home_service, salary)
    (on428,) = worksheets["ca-on/on428"]
    (summary,) = worksheets["ca-on/return"]

    assert on428.get(ON428_SURTAX_BASE_LINE_65).value == D(line_65)
    assert summary.get(bundled_kinds().kind(BASE)).value == D(line_65)


def test_the_bundled_return_gives_the_factor_1_at_70000() -> None:
    # No fixture: the bundled Ontario manifest, as the calculator loads it.
    worksheets = build_tax_computation().compute(
        CODE, 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (summary,) = worksheets["ca-on/return"]
    kinds = bundled_kinds()

    assert summary.get(kinds.kind(BASE)).value == D("3311.45")
    assert summary.get(kinds.kind(FACTOR)).value == D("1")
    assert summary.get(kinds.kind("ca/refund_or_balance_owing")).value == D("11497.09")


def test_the_return_steps_for_the_base_and_the_factor_carry_no_line_reference() -> None:
    worksheets = build_tax_computation().compute(
        CODE, 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (summary,) = worksheets["ca-on/return"]
    kinds = bundled_kinds()

    assert summary.reference(kinds.kind(BASE).label) is None
    assert summary.reference(kinds.kind(FACTOR).label) is None


@pytest.mark.parametrize(
    ("salary", "line_65", "thresholds"),
    [
        ("70000", "3311.45", ()),
        ("100000", "6015.78", (D("5710"),)),
        ("150000", "11458.12", (D("5710"), D("7307"))),
    ],
)
def test_the_factor_is_traced_with_the_tiers_line_65_is_over(
    take_home_service: TakeHomeService,
    salary: str,
    line_65: str,
    thresholds: tuple[Decimal, ...],
) -> None:
    sheet = _return_sheet(take_home_service, salary)

    line = _factor_line(sheet)
    assert line.base_amount == D(line_65)
    assert tuple(tier.threshold for tier in line.tiers) == thresholds
    assert line.factor == sheet.get(bundled_kinds().kind(FACTOR)).value


@pytest.mark.parametrize(
    ("salary", "figure", "reason", "factor"),
    [
        (
            "70000",
            "3311.45",
            "is over no surtax threshold, so no rate is added to 1.00",
            "1.00",
        ),
        (
            "100000",
            "6015.78",
            "is over the surtax threshold of 5710.00, so its rate 20% is added to 1.00",
            "1.20",
        ),
        (
            "150000",
            "11458.12",
            "is over the surtax thresholds of 5710.00 and 7307.00, "
            "so their rates 20% and 36% are added to 1.00",
            "1.56",
        ),
    ],
)
def test_the_factor_is_explained_in_english(
    take_home_service: TakeHomeService, salary: str, figure: str, reason: str, factor: str
) -> None:
    sheet = _return_sheet(take_home_service, salary)
    line = _factor_line(sheet)

    sentence = EnglishTraceRenderer().render(line, sheet)

    # The base is named as the return names it (any printed name, and its unit's text if it has
    # one before the figure); the factor is a plain figure with no unit.
    assert re.fullmatch(
        rf".+ \((?:CA\$)?{re.escape(figure)}\) {re.escape(reason)}, gives {re.escape(factor)}\.?",
        sentence,
    )


def test_the_new_kinds_are_registered_and_never_below_zero() -> None:
    kinds = bundled_kinds()

    for identifier in (BASE, FACTOR):
        assert kinds.kind(identifier).identifier == identifier
        assert non_negative(kinds.kind(identifier)) is True
        assert kinds.kind(identifier).value_type is Decimal

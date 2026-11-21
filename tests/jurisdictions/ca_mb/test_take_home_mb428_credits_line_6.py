"""MB428 (2025) line 6, the tax on the taxable income over the column's lower bound, real engine.

Form text (Form MB428, CRA 5007-C, read 2026-11-14,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt): "Line 6: Line 4
multiplied by the percentage from line 5 =". Line 6 is line 4 times the rate of line 5 (the
printed rate of the column, 10.8%, 12.75% or 17.4%), rounded half-up to the cent by
`ca-mb/cent_rounding`: the form states no rounding rule.

Lines 4 and 5 are never blank in Manitoba (line 3 is never blank, and the last column of line 5 has
no upper boundary), so line 6 is never blank either: there is no blank case to test here.

Line 6 is `core/multiply_by_rate` with base `ca-mb/mb428_taxable_income_over_lower_bound_line_4` and
rate `ca-mb/mb428_bracket_rate_line_5`, output `ca-mb/mb428_tax_on_excess_line_6`, in the part
`mb428_credits_line_6.yaml`.

The test composes the real parts: the Manitoba salary, the real Schedule 8, the T1 taxable-income
parts, and the real `mb428_credits_line_1.yaml`, `mb428_credits_line_3.yaml`,
`mb428_credits_line_4.yaml`, `mb428_credits_line_5.yaml` and `mb428_credits_line_6.yaml`, and types
in only the salary. The form declaration is test-local, exporting lines 1, 3, 4, 5 and 6.

Figures (hand-computed in `_derived` below, not a CRA example): taxable income is the salary less
the enhanced CPP deduction, 9,935.00 / 198,926.00. Line 4 is that less the column's lower bound
(0.00 or 100,000.00), so 9,935.00 / 98,926.00. Line 6 is line 4 at 10.8% / 17.4%: 1,072.98 /
17,213.12. The boundary salaries are derived below as in the line 5 and line 4 tests.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_1_PART = MB_PARTS / "mb428_credits_line_1.yaml"
LINE_3_PART = MB_PARTS / "mb428_credits_line_3.yaml"
LINE_4_PART = MB_PARTS / "mb428_credits_line_4.yaml"
LINE_5_PART = MB_PARTS / "mb428_credits_line_5.yaml"
LINE_6_PART = MB_PARTS / "mb428_credits_line_6.yaml"
FORM_NAME = "ca-mb/mb428_credits"
ROUNDING = "ca-mb/cent_rounding"
LINE_1 = "ca-mb/mb428_taxable_income_line_1"
LINE_3 = "ca-mb/mb428_bracket_lower_bound_line_3"
LINE_4 = "ca-mb/mb428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-mb/mb428_bracket_rate_line_5"
LINE_6 = "ca-mb/mb428_tax_on_excess_line_6"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The MB428 declaration, test-local: lines 1, 3, 4, 5 and 6 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
        - {LINE_5}
        - {LINE_6}
    capabilities: []
    """)

# (salary, line 1, line 4, line 5 rate, line 6): line 4 is line 1 less the lower bound of its
# column, and line 6 is line 4 times the rate, rounded half-up to the cent.
CASES = [
    ("10000", "9935.00", "9935.00", "0.108", "1072.98"),
    ("200000", "198926.00", "98926.00", "0.174", "17213.12"),
]
# Salaries whose taxable income sits on a column's edge: line 1 is 47,000.00 or less in column 1,
# more than 47,000.00 and not more than 100,000.00 in column 2. One cent more is the next column.
EDGES = [
    ("101074.00", "100000.00", "53000.00", "0.1275", "6757.50"),
]
# Rounding, half-up to the cent: 0.20 x 12.75% = 0.0255 is exactly half a cent and goes up to 0.03
# (not half-even, which would give 0.02); 0.19 x 12.75% = 0.024225 goes down to 0.02.
ROUNDING_CASES = [
    ("47439.59", "47000.19", "0.19", "0.1275", "0.02"),
    ("47439.60", "47000.20", "0.20", "0.1275", "0.03"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_1_PART
    yield LINE_3_PART
    yield LINE_4_PART
    yield LINE_5_PART
    yield LINE_6_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = manitoba_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _rounding() -> Any:
    return YamlParameterSource(
        manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _taxable_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _column(line_1: Decimal) -> tuple[Decimal, Decimal]:
    """The lower bound (line 3) and the rate (line 5) of the column line 1 falls in."""
    if line_1 <= D("47000"):
        return D("0"), D("0.108")
    if line_1 <= D("100000"):
        return D("47000"), D("0.1275")
    return D("100000"), D("0.174")


def _derived(salary: Decimal) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Line 1, line 4, the line 5 rate and line 6 by the form's arithmetic, in Decimal."""
    line_1 = _taxable_income(salary)
    lower, rate = _column(line_1)
    line_4 = max(line_1 - lower, D(0))
    return line_1, line_4, rate, _cent(line_4 * rate)


@pytest.mark.parametrize(
    ("salary", "line_1", "line_4", "rate", "expected"),
    [*CASES, *EDGES, *ROUNDING_CASES],
)
def test_line_4_is_line_1_less_the_lower_bound_of_its_column(
    tmp_path: Path, salary: str, line_1: str, line_4: str, rate: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_4)).value == D(line_4)


@pytest.mark.parametrize(
    ("salary", "line_1", "line_4", "rate", "expected"),
    [*CASES, *EDGES, *ROUNDING_CASES],
)
def test_line_6_is_line_4_times_the_line_5_rate_rounded_half_up_to_the_cent(
    tmp_path: Path, salary: str, line_1: str, line_4: str, rate: str, expected: str
) -> None:
    # The table is the form's arithmetic in Decimal, checked before the engine is asked.
    assert _derived(D(salary)) == (D(line_1), D(line_4), D(rate), D(expected))
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_5)).value == D(rate)
    value = sheet.get(_kind(LINE_6)).value
    assert value == D(expected)
    assert isinstance(value, Decimal)


@pytest.mark.parametrize(("salary", "expected"), [("500000", "69413.12"), ("5000000", "852413.12")])
def test_line_6_has_no_blank_above_the_top_column(
    tmp_path: Path, salary: str, expected: str
) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_6))

    assert not artifact.is_blank
    assert artifact.value == D(expected)


def test_the_trace_names_line_4_times_the_line_5_rate_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line = MultipliedByRateLine(
        output=_kind(LINE_6),
        base_kind=_kind(LINE_4),
        base_value=D("22335.00"),
        rate_kind=_kind(LINE_5),
        rate_value=D("0.1275"),
        rounding=_rounding().rounding,
        result=D("2847.71"),
    )
    assert line in sheet.trace


def test_the_product_reads_in_english_with_its_rate_base_and_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [
        each
        for each in sheet.trace
        if isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_6)
    ]
    text = EnglishTraceRenderer().render(line)

    assert "(12.75%)" in text
    assert "(22335.00)" in text
    assert text.endswith("gives 2847.71 (rounded to the nearest cent).")


def test_the_part_is_one_multiply_by_rate_step_over_lines_4_and_5() -> None:
    part: Any = yaml.safe_load(LINE_6_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/multiply_by_rate",
        "reference": "6",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"base": LINE_4, "rate": LINE_5},
        "produces": {"output": LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert LINE_6 in kinds.identifiers()
    kind = kinds.kind(LINE_6)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_TAX_ON_EXCESS_LINE_6

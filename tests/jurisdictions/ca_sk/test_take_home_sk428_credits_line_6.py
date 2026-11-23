"""SK428 (2025) line 6, the tax on the taxable income over the column's lower bound, real engine.

Form text (Form SK428, CRA 5008-C, line 6, read 2026-11-14): "Line 6: Line 4 multiplied by the
percentage from line 5 =". Line 6 is line 4 times the rate of line 5 (the printed rate of the
column, 10.5%, 12.5% or 14.5%), rounded half-up to the cent by `ca-sk/cent_rounding`: the form
states no rounding rule. The form prints no label for line 6, so the step has no title.

Lines 4 and 5 are never blank in Saskatchewan (line 3 is never blank, and the last column of line 5
has no upper boundary), so line 6 is never blank either: there is no blank case to test here.

Line 6 is `core/multiply_by_rate` with base `ca-sk/sk428_taxable_income_over_lower_bound_line_4` and
rate `ca-sk/sk428_bracket_rate_line_5`, output `ca-sk/sk428_tax_on_excess_line_6`, in the part
`sk428_credits_line_6.yaml`.

The test composes the real parts: the Saskatchewan salary, the real Schedule 8, the T1
taxable-income parts, and the real `sk428_credits_line_1.yaml`, `sk428_credits_line_3.yaml`,
`sk428_credits_line_4.yaml`, `sk428_credits_line_5.yaml` and `sk428_credits_line_6.yaml`, and types
in only the salary. The form declaration is test-local, exporting lines 1, 3, 4, 5 and 6.

Figures (re-derived in `_derived` below with Decimal, not a CRA example): at salary 70,000 taxable
income is 69,335.00 (the salary less the enhanced CPP deduction), line 4 is that less the column's
lower bound 53,463.00, so 15,872.00, and line 6 is line 4 at 12.5%: 1,984.00. The rounding salaries
are derived below. The column edges and the other columns are covered by the line 5 and line 4
tests.
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
import tax_engine.jurisdictions.ca_sk
import tax_engine.jurisdictions.ca_sk.catalog as sk_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
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
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_1_PART = SK_PARTS / "sk428_credits_line_1.yaml"
LINE_3_PART = SK_PARTS / "sk428_credits_line_3.yaml"
LINE_4_PART = SK_PARTS / "sk428_credits_line_4.yaml"
LINE_5_PART = SK_PARTS / "sk428_credits_line_5.yaml"
LINE_6_PART = SK_PARTS / "sk428_credits_line_6.yaml"
FORM_NAME = "ca-sk/sk428_credits"
ROUNDING = "ca-sk/cent_rounding"
LINE_1 = "ca-sk/sk428_taxable_income_line_1"
LINE_3 = "ca-sk/sk428_bracket_lower_bound_line_3"
LINE_4 = "ca-sk/sk428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-sk/sk428_bracket_rate_line_5"
LINE_6 = "ca-sk/sk428_tax_on_excess_line_6"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The SK428 declaration, test-local: lines 1, 3, 4, 5 and 6 are composed, so it exports those.
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
    ("70000", "69335.00", "15872.00", "0.125", "1984.00"),
]
# Rounding, half-up to the cent: 0.04 x 12.5% = 0.005 is exactly half a cent and goes up to 0.01
# (not half-even, which would give 0.00); 0.03 x 12.5% = 0.00375 goes down to 0.00.
ROUNDING_CASES = [
    ("53967.71", "53463.03", "0.03", "0.125", "0.00"),
    ("53967.72", "53463.04", "0.04", "0.125", "0.01"),
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
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-SK"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = saskatchewan_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _rounding() -> Any:
    return YamlParameterSource(
        saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
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
    if line_1 <= D("53463"):
        return D("0"), D("0.105")
    if line_1 <= D("152750"):
        return D("53463"), D("0.125")
    return D("152750"), D("0.145")


def _derived(salary: Decimal) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Line 1, line 4, the line 5 rate and line 6 by the form's arithmetic, in Decimal."""
    line_1 = _taxable_income(salary)
    lower, rate = _column(line_1)
    line_4 = max(line_1 - lower, D(0))
    return line_1, line_4, rate, _cent(line_4 * rate)


@pytest.mark.parametrize(
    ("salary", "line_1", "line_4", "rate", "expected"),
    [*CASES, *ROUNDING_CASES],
)
def test_line_4_is_line_1_less_the_lower_bound_of_its_column(
    tmp_path: Path, salary: str, line_1: str, line_4: str, rate: str, expected: str
) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_4)).value == D(line_4)


@pytest.mark.parametrize(
    ("salary", "line_1", "line_4", "rate", "expected"),
    [*CASES, *ROUNDING_CASES],
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


@pytest.mark.parametrize(("salary", "expected"), [("500000", "50195.52"), ("5000000", "702695.52")])
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
        base_value=D("15872.00"),
        rate_kind=_kind(LINE_5),
        rate_value=D("0.125"),
        rounding=_rounding().rounding,
        result=D("1984.00"),
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

    assert "(12.5%)" in text
    assert "(15872.00)" in text
    assert text.endswith("gives 1984.00 (rounded to the nearest cent).")


def test_the_part_is_one_multiply_by_rate_step_over_lines_4_and_5() -> None:
    part: Any = yaml.safe_load(LINE_6_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/multiply_by_rate",
        "reference": "6",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"base": LINE_4, "rate": LINE_5},
        "produces": {"output": LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert LINE_6 in kinds.identifiers()
    kind = kinds.kind(LINE_6)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_TAX_ON_EXCESS_LINE_6

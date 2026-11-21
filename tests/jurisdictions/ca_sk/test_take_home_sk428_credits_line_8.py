"""SK428 (2025) line 8, the Saskatchewan tax on taxable income, real engine.

Form text (Form SK428, CRA 5008-c-25e, confirmed 2026-11-14): "Line 8: Line 6 plus line 7
Saskatchewan tax on taxable income =". The form prints that label, so the step is titled
"Saskatchewan tax on taxable income" and carries the reference "8". Line 8 is line 6 plus line 7,
a `core/sum` with `ca-sk/cent_rounding`: line 6 is already rounded to the cent and line 7 is a
printed amount in cents, so the exact sum is unchanged by the rounding.

Line 8 is one `core/sum` over `ca-sk/sk428_tax_on_excess_line_6` and
`ca-sk/sk428_bracket_tax_at_start_line_7`, output `ca-sk/sk428_tax_on_taxable_income_line_8`, in
the part `sk428_credits_line_8.yaml`. Lines 6 and 7 are never blank in Saskatchewan, so line 8 is
never blank either.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T1 taxable income
parts, the real `sk428_credits_line_1.yaml`, `sk428_credits_line_3.yaml`,
`sk428_credits_line_4.yaml`, `sk428_credits_line_5.yaml`, `sk428_credits_line_6.yaml`,
`sk428_credits_line_7.yaml` and `sk428_credits_line_8.yaml`, and types in only the salary. The
form declaration is test-local, exporting lines 6, 7 and 8.

Figures (re-derived in `_derived` below with Decimal, not a CRA example): at salary 0 every line is
0.00; at salary 70,000 taxable income is 69,335.00 (the salary less the enhanced CPP deduction),
line 6 is 1,984.00 and line 7 is 5,613.62, so line 8 is 7,597.62. The column edges are derived in
the line 6 and line 7 tests.
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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
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
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_1_PART = SK_PARTS / "sk428_credits_line_1.yaml"
LINE_3_PART = SK_PARTS / "sk428_credits_line_3.yaml"
LINE_4_PART = SK_PARTS / "sk428_credits_line_4.yaml"
LINE_5_PART = SK_PARTS / "sk428_credits_line_5.yaml"
LINE_6_PART = SK_PARTS / "sk428_credits_line_6.yaml"
LINE_7_PART = SK_PARTS / "sk428_credits_line_7.yaml"
LINE_8_PART = SK_PARTS / "sk428_credits_line_8.yaml"
FORM_NAME = "ca-sk/sk428_credits"
ROUNDING = "ca-sk/cent_rounding"
LINE_1 = "ca-sk/sk428_taxable_income_line_1"
LINE_3 = "ca-sk/sk428_bracket_lower_bound_line_3"
LINE_4 = "ca-sk/sk428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-sk/sk428_bracket_rate_line_5"
LINE_6 = "ca-sk/sk428_tax_on_excess_line_6"
LINE_7 = "ca-sk/sk428_bracket_tax_at_start_line_7"
LINE_8 = "ca-sk/sk428_tax_on_taxable_income_line_8"
TITLE = "Saskatchewan tax on taxable income"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The SK428 declaration, test-local: lines 6, 7 and 8 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_6}
        - {LINE_7}
        - {LINE_8}
    capabilities: []
    """)

# (salary, line 1, line 6, line 7, line 8): line 8 is line 6 plus line 7.
ALL = [
    ("0", "0.00", "0.00", "0.00", "0.00"),
    ("70000", "69335.00", "1984.00", "5613.62", "7597.62"),
]


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_1_PART
    yield LINE_3_PART
    yield LINE_4_PART
    yield LINE_5_PART
    yield LINE_6_PART
    yield LINE_7_PART
    yield LINE_8_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
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
        JurisdictionCode("CA-SK"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
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


def _column(line_1: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """The lower bound (line 3), the rate (line 5) and the tax at the start (line 7) printed for
    the column line 1 falls in."""
    if line_1 <= D("53463"):
        return D("0"), D("0.105"), D("0.00")
    if line_1 <= D("152750"):
        return D("53463"), D("0.125"), D("5613.62")
    return D("152750"), D("0.145"), D("18024.49")


def _derived(salary: Decimal) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Line 1, line 6, line 7 and line 8 by the form's arithmetic, in Decimal."""
    line_1 = _taxable_income(salary)
    lower, rate, line_7 = _column(line_1)
    line_6 = _cent(max(line_1 - lower, D(0)) * rate)
    return line_1, line_6, line_7, line_6 + line_7


@pytest.mark.parametrize(("salary", "line_1", "line_6", "line_7", "expected"), ALL)
def test_the_salaries_give_the_line_6_and_line_7_figures_the_line_8_cases_rest_on(
    tmp_path: Path, salary: str, line_1: str, line_6: str, line_7: str, expected: str
) -> None:
    # The table is the form's arithmetic in Decimal, checked before the engine is asked.
    assert _derived(D(salary)) == (D(line_1), D(line_6), D(line_7), D(expected))
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_1)).value == D(line_1)
    assert sheet.get(_kind(LINE_6)).value == D(line_6)
    assert sheet.get(_kind(LINE_7)).value == D(line_7)


@pytest.mark.parametrize(("salary", "line_1", "line_6", "line_7", "expected"), ALL)
def test_line_8_is_line_6_plus_line_7(
    tmp_path: Path, salary: str, line_1: str, line_6: str, line_7: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_8)).value

    assert value == D(expected)
    assert isinstance(value, Decimal)
    assert str(value) == expected


@pytest.mark.parametrize(("salary", "line_1", "line_6", "line_7", "expected"), ALL)
def test_line_8_equals_line_6_plus_line_7_exactly(
    tmp_path: Path, salary: str, line_1: str, line_6: str, line_7: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    six, seven = sheet.get(_kind(LINE_6)).value, sheet.get(_kind(LINE_7)).value
    assert isinstance(six, Decimal)
    assert isinstance(seven, Decimal)

    assert sheet.get(_kind(LINE_8)).value == six + seven


@pytest.mark.parametrize(("salary", "expected"), [("500000", "68220.01"), ("5000000", "720720.01")])
def test_line_8_has_no_blank_above_the_top_column(
    tmp_path: Path, salary: str, expected: str
) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_8))

    assert not artifact.is_blank
    assert artifact.value == D(expected)
    assert _derived(D(salary))[3] == D(expected)


def test_the_sheet_prints_the_title_and_the_reference_of_line_8(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = _kind(LINE_8).label

    assert sheet.title(label) == TITLE
    assert sheet.reference(label) == "8"


def test_the_trace_adds_line_6_and_line_7_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line = SumLine(
        output=_kind(LINE_8),
        parts=((_kind(LINE_6), D("1984.00")), (_kind(LINE_7), D("5613.62"))),
        rounding=_rounding().rounding,
        total=D("7597.62"),
    )
    assert line in sheet.trace


def test_the_sum_reads_in_english_as_line_6_plus_line_7_with_its_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_8)
    ]
    text = EnglishTraceRenderer().render(line)

    assert " plus " in text
    assert "1984.00" in text
    assert "5613.62" in text
    assert text.endswith("7597.62 (rounded to the nearest cent).")


def test_the_part_is_one_titled_sum_step_over_lines_6_and_7() -> None:
    part: Any = yaml.safe_load(LINE_8_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "title": TITLE,
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_6, LINE_7]},
        "produces": {"output": LINE_8},
    }


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert LINE_8 in kinds.identifiers()
    kind = kinds.kind(LINE_8)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_TAX_ON_TAXABLE_INCOME_LINE_8

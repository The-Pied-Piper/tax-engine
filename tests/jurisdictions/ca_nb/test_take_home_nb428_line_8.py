"""NB428 (2025) line 8, the New Brunswick tax on taxable income, real engine.

Form text (Form NB428, CRA 5004-c-25e, confirmed 2026-11-26): "Line 8: Line 6 plus line 7
New Brunswick tax on taxable income =". The form prints that label, so the step is titled
"New Brunswick tax on taxable income" and carries the reference "8". Line 8 is line 6 plus line 7,
a `core/sum` with `ca-nb/cent_rounding`: line 6 is already rounded to the cent and line 7 is a
printed amount in cents, so the exact sum is unchanged by the rounding.

Line 8 is one `core/sum` over `ca-nb/nb428_tax_on_excess_line_6` and
`ca-nb/nb428_bracket_tax_at_start_line_7`, output `ca-nb/nb428_tax_on_taxable_income_line_8`, in
the part `nb428_line_8.yaml`. Lines 6 and 7 are never blank in New Brunswick, so line 8 is
never blank either.

The test composes the T1 employment income form, the real Schedule 8 and T1 taxable income
parts, the real `nb428_line_1.yaml`, `nb428_line_3.yaml`,
`nb428_line_4.yaml`, `nb428_line_5.yaml`, `nb428_line_6.yaml`,
`nb428_line_7.yaml` and `nb428_line_8.yaml`, and types in only the salary. The
form declaration is test-local, exporting lines 6, 7 and 8.

Figures (re-derived in `_derived` below with Decimal, not a CRA example): at salary 0 every line is
0.00; at salary 70,000 taxable income is 69,335.00 (the salary less the enhanced CPP deduction),
line 6 is 2,524.06 and line 7 is 4,822.76, so line 8 is 7,346.82. The column edges are derived in
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
import tax_engine.jurisdictions.ca_nb
import tax_engine.jurisdictions.ca_nb.catalog as nb_catalog
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
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
    new_brunswick_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
NB_PARTS = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025"
LINE_1_PART = NB_PARTS / "nb428_line_1.yaml"
LINE_3_PART = NB_PARTS / "nb428_line_3.yaml"
LINE_4_PART = NB_PARTS / "nb428_line_4.yaml"
LINE_5_PART = NB_PARTS / "nb428_line_5.yaml"
LINE_6_PART = NB_PARTS / "nb428_line_6.yaml"
LINE_7_PART = NB_PARTS / "nb428_line_7.yaml"
LINE_8_PART = NB_PARTS / "nb428_line_8.yaml"
FORM_NAME = "ca-nb/nb428"
ROUNDING = "ca-nb/cent_rounding"
LINE_1 = "ca-nb/nb428_taxable_income_line_1"
LINE_3 = "ca-nb/nb428_bracket_lower_bound_line_3"
LINE_4 = "ca-nb/nb428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-nb/nb428_bracket_rate_line_5"
LINE_6 = "ca-nb/nb428_tax_on_excess_line_6"
LINE_7 = "ca-nb/nb428_bracket_tax_at_start_line_7"
LINE_8 = "ca-nb/nb428_tax_on_taxable_income_line_8"
TITLE = "New Brunswick tax on taxable income"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-NB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The NB428 declaration, test-local: lines 6, 7 and 8 are composed, so it exports those.
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
    ("20000", "19835.00", "1864.49", "0.00", "1864.49"),
    ("30000", "29735.00", "2795.09", "0.00", "2795.09"),
    ("70000", "69335.00", "2524.06", "4822.76", "7346.82"),
    ("51788.89", "51306.00", "4822.76", "0.00", "4822.76"),
    ("51788.90", "51306.01", "0.00", "4822.76", "4822.76"),
    ("103688", "102614.00", "7183.12", "4822.76", "12005.88"),
    ("103688.01", "102614.01", "0.00", "12005.88", "12005.88"),
    ("191134", "190060.00", "13991.36", "12005.88", "25997.24"),
    ("191135", "190061.00", "0.20", "25997.24", "25997.44"),
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
    yield LINE_7_PART
    yield LINE_8_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(dict.fromkeys(_part_files()), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**new_brunswick_packages().roots(), Namespace("ca-nb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, new_brunswick_kinds(), new_brunswick_units()),
        YamlParameterSource(
            new_brunswick_packages().roots(),
            new_brunswick_parameter_parsers(),
            new_brunswick_units(),
        ),
        new_brunswick_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-NB"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = new_brunswick_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _rounding() -> Any:
    return YamlParameterSource(
        new_brunswick_packages().roots(), new_brunswick_parameter_parsers(), new_brunswick_units()
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
    if line_1 <= D("51306"):
        return D("0"), D("0.094"), D("0.00")
    if line_1 <= D("102614"):
        return D("51306"), D("0.14"), D("4822.76")
    if line_1 <= D("190060"):
        return D("102614"), D("0.16"), D("12005.88")
    return D("190060"), D("0.195"), D("25997.24")


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


@pytest.mark.parametrize(("salary", "expected"), [("500000", "86226.11"), ("5000000", "963726.11")])
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
        parts=((_kind(LINE_6), D("2524.06")), (_kind(LINE_7), D("4822.76"))),
        rounding=_rounding().rounding,
        total=D("7346.82"),
    )
    assert line in sheet.trace


def test_the_sum_reads_in_english_as_line_6_plus_line_7_with_its_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_8)
    ]
    text = EnglishTraceRenderer().render(line)

    assert " plus " in text
    assert "2524.06" in text
    assert "4822.76" in text
    assert text.endswith("7346.82 (rounded to the nearest cent).")


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
    kinds = new_brunswick_kinds()

    assert LINE_8 in kinds.identifiers()
    kind = kinds.kind(LINE_8)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is nb_catalog.NB428_TAX_ON_TAXABLE_INCOME_LINE_8

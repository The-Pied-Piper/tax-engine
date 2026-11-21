"""BC479 (2025) line 5, line 3 minus line 4 (not below 0), from the salary alone, real parts.

Form text (Form BC479, CRA 5010-TC, as recorded on the ticket): 'Line 5: Line 3 minus line 4 (if
negative, enter "0")'. Line 3 is the income with repayments
(`ca-bc/bc479_income_with_repayments_line_3`, signed, from `bc479_line_3.yaml`) and line 4 is the
UCCB and RDSP income input (`ca-bc/bc479_uccb_rdsp_income_line_4`), which a salary-only caller
leaves out, read as blank and then as 0 by the step's own blank rule, as the line 3 step reads its
line 2. The form floors line 5 at 0, so the output `ca-bc/bc479_adjusted_net_income_line_5` is a
non-negative kind.

Line 5 is one core/subtract_not_below_zero step (`bc479_line_5.yaml`), rounded through
`ca-bc/cent_rounding`, with `amount` line 3 and `less` line 4. The test composes the real British
Columbia salary part, the real Schedule 8 parts, the real T1 taxable income parts, the real line
1, line 2 and line 3 parts, the line 4 input part and the new `bc479_line_5.yaml`, and types in
only the salary (and, in other tests, line 4, or a negative line 1 through the social benefits
repayment). The form declaration is made up here, exporting only line 5.

Figures (hand-computed from the printed forms, not a CRA example): with line 4 blank, line 5 is line
3, which is line 1 of the same salary: 16,865.00 / 198,926.00 at 17,000 / 200,000. With line 4 of
1,000.00 at 17,000, line 5 is 15,865.00. With line 4 above line 3, line 5 is 0.00.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, UCCB_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import (
    BC479_ADJUSTED_NET_INCOME_LINE_5,
)
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
)
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative

D = Decimal
CODE = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc479"
LINE_3 = "ca-bc/bc479_income_with_repayments_line_3"
LINE_4 = "ca-bc/bc479_uccb_rdsp_income_line_4"
LINE_5 = "ca-bc/bc479_adjusted_net_income_line_5"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = BC_PARTS / "bc479_line_5.yaml"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_5}
    capabilities: []
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield _federal(name)
    yield BC_PARTS / "bc479_line_1.yaml"
    yield BC_PARTS / "bc479_line_2.yaml"
    yield BC_PARTS / "bc479_line_3.yaml"
    yield BC_PARTS / "bc479_line_4.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary British Columbia manifest of a test header, a form declaration
    and the real part files, every other namespace being the British Columbia package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        text = part.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(CODE, 2025, *given)
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _rounding() -> Any:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


# salary, line 5 (line 4 left blank, read as 0, so line 5 is line 3 of the same salary).
CASES = [
    ("17000", "16865.00"),
    ("200000", "198926.00"),
]


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_5_is_line_3_when_line_4_is_blank(tmp_path: Path, salary: str, expected: str) -> None:
    line_5 = _sheet(tmp_path, salary).get(BC479_ADJUSTED_NET_INCOME_LINE_5).value

    assert line_5 == D(expected)
    assert str(line_5) == expected
    assert line_5.as_tuple().exponent == -2
    assert not line_5.is_signed()


def test_line_5_takes_line_4_off_line_3_when_line_4_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(UCCB_INCOME, D("1000.00")))

    assert sheet.get(BC479_ADJUSTED_NET_INCOME_LINE_5).value == D("15865.00")


def test_line_5_is_0_when_line_4_is_above_line_3(tmp_path: Path) -> None:
    # Line 3 is 16,865.00 at 17,000 and line 4 is 20,000.00: the floor.
    sheet = _sheet(tmp_path, "17000", Artifact(UCCB_INCOME, D("20000.00")))

    line_5 = sheet.get(BC479_ADJUSTED_NET_INCOME_LINE_5).value
    assert line_5 == D("0.00")
    assert str(line_5) == "0.00"
    assert not line_5.is_signed()


def test_line_5_is_0_when_line_4_equals_line_3(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(UCCB_INCOME, D("16865.00")))

    assert sheet.get(BC479_ADJUSTED_NET_INCOME_LINE_5).value == D("0.00")


def test_line_5_is_0_when_line_3_is_negative(tmp_path: Path) -> None:
    # Line 23500 of 75,000 is more than line 23400 of 69,335.00, so line 1 is -5,665.00. Line 3 is
    # that line 1 with a blank line 2, so it stays negative, and line 5 floors it at 0 with a blank
    # line 4.
    kinds = british_columbia_kinds()
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(kinds.kind("ca/social_benefits_repayment"), D("75000")),
    )

    assert sheet.get(BC479_ADJUSTED_NET_INCOME_LINE_5).value == D("0.00")


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "17000", Artifact(UCCB_INCOME, D("1000.00")))
    kinds = british_columbia_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_5)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_5),
        minuend=kinds.kind(LINE_3),
        minuend_amount=D("16865.00"),
        subtrahend=kinds.kind(LINE_4),
        subtrahend_amount=D("1000.00"),
        rounding=_rounding().rounding,
        result=D("15865.00"),
    )


def _line_5_at(line_3_amount: str, line_4_amount: str) -> Artifact[Decimal]:
    """Line 5 over given lines 3 and 4: the capability the part builds, with the real dataset."""
    line_3, line_4, line_5 = _kind(LINE_3), _kind(LINE_4), _kind(LINE_5)
    capability = SubtractNotBelowZero(_rounding(), line_3, line_4, line_5)
    result = capability.compute(
        (Artifact(line_3, D(line_3_amount)), Artifact(line_4, D(line_4_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_3", "line_4", "expected"),
    [
        ("16865.00", "1000.00", "15865.00"),
        ("16865.00", "16865.01", "0.00"),
        # Line 3 is signed (a negative line 1), so a negative minuend is accepted and floored.
        ("-350.00", "0.00", "0.00"),
        # Half-up to the cent: 0.005 rounds to 0.01.
        ("100.005", "100.00", "0.01"),
    ],
)
def test_line_5_is_line_3_minus_line_4_not_below_zero_to_the_cent(
    line_3: str, line_4: str, expected: str
) -> None:
    line_5 = _line_5_at(line_3, line_4).value

    assert line_5 == D(expected)
    assert str(line_5) == expected
    assert line_5.as_tuple().exponent == -2
    assert not line_5.is_signed()


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_subtract_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "5",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_3, "less": LINE_4},
        "produces": {"output": LINE_5},
    }
    assert "title" not in step


def test_line_5_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = british_columbia_kinds().kind(LINE_5)

    assert kind is BC479_ADJUSTED_NET_INCOME_LINE_5
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_line_3_stays_signed_while_line_5_is_floored() -> None:
    assert not non_negative(_kind(LINE_3))
    assert non_negative(_kind(LINE_5))

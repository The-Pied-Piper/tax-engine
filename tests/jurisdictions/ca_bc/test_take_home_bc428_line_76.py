"""BC428 (2025) line 76, line 74 minus line 75 (if negative, enter "0"), from the real parts.

Form text (Form BC428, CRA 5010-c-25e.txt): "Line 76: Line 74 minus line 75 (if negative, enter
"0") =". Line 76 is one `core/subtract_not_below_zero` step: `ca-bc/bc428_net_income_line_74` less
`ca-bc/bc428_base_amount_line_75`, rounded by `ca-bc/cent_rounding`, output
`ca-bc/bc428_net_income_over_base_line_76`. Neither input is ever blank (line 74 is computed from
the salary and line 75 is the printed base amount), so the step has no blank rule. A line 74 below
line 75 gives a computed 0.00, not a blank. Line 76 has no income gate: at $70,000 it is 44,315.00.

The real parts composed: the British Columbia salary, Schedule 8, the T1 taxable-income parts, the
line 74 part (`bc428_line_74.yaml`), the line 75 part (`bc428_line_75.yaml`) and
`bc428_line_76.yaml`. The form declaration and header are test-local, and the service is built over
the British Columbia package list of `support.py`.
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
from tax_engine.domain.trace import BlankPassedOnLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_NET_INCOME_OVER_BASE_LINE_76
from tax_engine.jurisdictions.core.capabilities.subtract_not_below_zero import (
    SubtractNotBelowZero,
)
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
BC = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_74 = "ca-bc/bc428_net_income_line_74"
LINE_75 = "ca-bc/bc428_base_amount_line_75"
LINE_76 = "ca-bc/bc428_net_income_over_base_line_76"
ROUNDING = "ca-bc/cent_rounding"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = BC_PARTS / "bc428_line_76.yaml"
LINE_74_PART = BC_PARTS / "bc428_line_74.yaml"
LINE_75_PART = BC_PARTS / "bc428_line_75.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 74, 75 and 76 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_74}
        - {LINE_75}
        - {LINE_76}
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield "salary.yaml", (BC_PARTS / "salary.yaml").read_text(encoding="utf-8")
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    for part in (LINE_74_PART, LINE_75_PART, PART):
        yield part.name, part.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(BC, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        ("17000", "0.00"),
        ("30000", "4715.00"),
    ],
)
def test_line_76_is_line_74_minus_line_75_not_below_zero(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line_76 = sheet.get(british_columbia_kinds().kind(LINE_76)).value

    assert line_76 == D(expected)
    assert str(line_76) == expected


@pytest.mark.parametrize(("salary", "line_74"), [("17000", "16865.00"), ("20000", "19835.00")])
def test_line_76_is_a_computed_zero_when_line_74_is_below_line_75(
    tmp_path: Path, salary: str, line_74: str
) -> None:
    # Line 74 is 16,865.00 and 19,835.00, below the 25,020.00 of line 75: line 76 is 0.00, and it
    # is computed, so it is not blank.
    sheet = _sheet(tmp_path, salary)
    kinds = british_columbia_kinds()

    assert sheet.get(kinds.kind(LINE_74)).value == D(line_74)
    line_76 = sheet.get(kinds.kind(LINE_76))
    assert not line_76.is_blank
    assert line_76.value == D("0.00")
    assert str(line_76.value) == "0.00"


def test_a_covered_line_76_traces_one_subtracted_not_below_zero_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_76),
        minuend=kinds.kind(LINE_74),
        minuend_amount=D("69335.00"),
        subtrahend=kinds.kind(LINE_75),
        subtrahend_amount=D("25020.00"),
        rounding=_rounding().rounding,
        result=D("44315.00"),
    )
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def _rounding() -> Any:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _line_76_at(line_74_amount: str, line_75_amount: str) -> Artifact[Decimal]:
    """Line 76 over given lines 74 and 75: the capability the part builds, with the real dataset."""
    kinds = british_columbia_kinds()
    line_74, line_75, line_76 = kinds.kind(LINE_74), kinds.kind(LINE_75), kinds.kind(LINE_76)
    assert isinstance(line_74, AmountKind)
    assert isinstance(line_75, AmountKind)
    assert isinstance(line_76, AmountKind)
    capability = SubtractNotBelowZero(_rounding(), line_74, line_75, line_76)
    result = capability.run(
        (Artifact(line_74, D(line_74_amount)), Artifact(line_75, D(line_75_amount)))
    )
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_74", "expected"),
    [
        ("25020.00", "0.00"),
        ("25020.01", "0.01"),
    ],
)
def test_line_76_is_line_74_minus_the_base_amount_to_the_cent(line_74: str, expected: str) -> None:
    assert _line_76_at(line_74, "25020.00").value == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_subtract_not_below_zero_step_over_line_74_and_line_75() -> None:
    # Line 76 prints no title and has no blank rule: line 74 is always computed and line 75 is
    # always the printed base amount.
    assert _step() == {
        "name": "core/subtract_not_below_zero",
        "reference": "76",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_74, "less": LINE_75},
        "produces": {"output": LINE_76},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = british_columbia_kinds().kind(LINE_76)

    assert kind is BC428_NET_INCOME_OVER_BASE_LINE_76
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_76
    assert kind.value_type is Decimal
    assert non_negative(kind)

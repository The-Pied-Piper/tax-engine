"""BC428 (2025) line 78, line 76 multiplied by the percentage from line 77, from the real parts.

Form text (Form BC428, CRA 5010-c-25e.txt): "Line 77: Applicable rate 3.56%" and "Line 78: Line 76
multiplied by the percentage from line 77 = ^". Line 77 is a printed rate, so it is the
`ca-bc/tax_reduction_rate` dataset figure (0.0356) and has no step. Line 78 is one
`core/apply_rate` step: `ca-bc/bc428_net_income_over_base_line_76` times that rate, rounded half-up
to the cent by the dataset's rule, output `ca-bc/bc428_reduction_clawback_line_78`. Line 76 is never
blank (it is computed from line 74 and the printed base amount), so the step has no blank rule. A
line 76 of 0.00 gives a computed 0.00, not a blank. The form prints no title for the line, so the
step has none.

The expected figures are hand-computed from the ticket and re-derived here, not taken from a CRA
example. Taxable income (line 74) is the salary less the CPP enhanced amount (1% of the earnings
from 3,500.00 to 71,300.00) and the CPP second-ceiling amount (4% of the earnings from 71,300.00 to
81,200.00): 16,865.00 at $17,000 and 29,735.00 at $30,000. Line 76 is line 74 less the 25,020.00
base, not below zero: 0.00 and 4,715.00. Line 78 is line 76 times 0.0356, rounded half-up to the
cent: 0.00 and 167.85 (167.854); 44,315.00 gives 1,577.61 (1,577.614).

The real parts composed: the British Columbia salary, Schedule 8, the T1 taxable-income parts, the
line 74 part (`bc428_line_74.yaml`), the line 75 part (`bc428_line_75.yaml`), the line 76 part
(`bc428_line_76.yaml`) and `bc428_line_78.yaml`. The form declaration and header are test-local, and
the service is built over the British Columbia package list of `support.py`.
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
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, RateAppliedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_REDUCTION_CLAWBACK_LINE_78
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_INPUT

D = Decimal
BC = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_74 = "ca-bc/bc428_net_income_line_74"
LINE_75 = "ca-bc/bc428_base_amount_line_75"
LINE_76 = "ca-bc/bc428_net_income_over_base_line_76"
LINE_78 = "ca-bc/bc428_reduction_clawback_line_78"
RATE_FAMILY = "ca-bc/tax_reduction_rate"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = BC_PARTS / "bc428_line_78.yaml"
LINE_74_PART = BC_PARTS / "bc428_line_74.yaml"
LINE_75_PART = BC_PARTS / "bc428_line_75.yaml"
LINE_76_PART = BC_PARTS / "bc428_line_76.yaml"
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 74, 75, 76 and 78 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_74}
        - {LINE_75}
        - {LINE_76}
        - {LINE_78}
    """)


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    yield T1_LINE_10100_INPUT.name, T1_LINE_10100_INPUT.read_text(encoding="utf-8")
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            found.read_text("utf-8"),
        )
    for part in (LINE_74_PART, LINE_75_PART, LINE_76_PART, PART):
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
        ("30000", "167.85"),
    ],
)
def test_line_78_is_line_76_times_3_56_percent_rounded_half_up(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line_78 = sheet.get(british_columbia_kinds().kind(LINE_78)).value

    assert line_78 == D(expected)
    assert str(line_78) == expected


@pytest.mark.parametrize("salary", ["17000", "20000"])
def test_line_78_is_a_computed_zero_when_line_76_is_zero(tmp_path: Path, salary: str) -> None:
    # Line 76 is 0.00 at these salaries (line 74 is below the 25,020.00 base), so line 78 is 0.00
    # and it is computed, so it is not blank.
    sheet = _sheet(tmp_path, salary)
    kinds = british_columbia_kinds()

    assert sheet.get(kinds.kind(LINE_76)).value == D("0.00")
    line_78 = sheet.get(kinds.kind(LINE_78))
    assert not line_78.is_blank
    assert line_78.value == D("0.00")
    assert str(line_78.value) == "0.00"


def test_a_covered_line_78_traces_one_rate_applied_line(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = british_columbia_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, RateAppliedLine)]
    assert line == RateAppliedLine(
        output=kinds.kind(LINE_78),
        base=kinds.kind(LINE_76),
        base_amount=D("44315.00"),
        rate=Rate(D("0.0356")),
        rounding=_rate().rounding,
        result=D("1577.61"),
    )
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def _rate() -> ParameterDataset[Rate]:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    ).get(RATE_FAMILY, 2025, RATE)


def _line_78_at(line_76_amount: str) -> Artifact[Decimal]:
    """Line 78 over a given line 76: the capability the part builds, with the real dataset."""
    kinds = british_columbia_kinds()
    line_76, line_78 = kinds.kind(LINE_76), kinds.kind(LINE_78)
    assert isinstance(line_76, AmountKind)
    assert isinstance(line_78, AmountKind)
    capability = ApplyRate(_rate(), line_76, line_78)
    result = capability.run((Artifact(line_76, D(line_76_amount)),))
    (output,) = result.outputs
    return output


@pytest.mark.parametrize(
    ("line_76", "expected"),
    [
        # 12.50 x 3.56% = 0.4450, rounded half-up to 0.45 (not down to 0.44).
        ("12.50", "0.45"),
        # 44,315.00 x 3.56% = 1,577.614, rounded to 1,577.61.
        ("44315.00", "1577.61"),
    ],
)
def test_line_78_is_line_76_times_the_rate_to_the_cent(line_76: str, expected: str) -> None:
    assert _line_78_at(line_76).value == D(expected)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_apply_rate_step_over_line_76_and_the_rate() -> None:
    # Line 78 prints no title: the form's line 78 is only "Line 76 multiplied by the percentage from
    # line 77 = ^". Line 77 is the dataset rate, so the step reads it as a parameter, not a line.
    assert _step() == {
        "name": "core/apply_rate",
        "reference": "78",
        "unit": "ca/cad",
        "params": {"rate": RATE_FAMILY},
        "consumes": {"base": LINE_76},
        "produces": {"output": LINE_78},
    }


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = british_columbia_kinds().kind(LINE_78)

    assert kind is BC428_REDUCTION_CLAWBACK_LINE_78
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_78
    assert kind.value_type is Decimal
    assert non_negative(kind)

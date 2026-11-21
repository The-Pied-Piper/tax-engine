"""BC428 (2025) line 79, line 73 minus line 78 (not below 0), from the real parts.

Form text (Form BC428, CRA 5010-C): Line 79: Line 73 minus line 78 (if negative, enter "0")
British Columbia tax reduction = ^
The step carries the title "British Columbia tax reduction", which the form prints on the line
(the line 72 step has none because its form line prints none).

Line 79 is one core/subtract_not_below_zero step (`bc428_line_79.yaml`), rounded through
`ca-bc/cent_rounding`, taking the clawback on line 78 (`ca-bc/bc428_reduction_clawback_line_78`)
off the basic reduction on line 73 (`ca-bc/bc428_basic_reduction_line_73`, $562). Neither input is
ever blank, so the step has no blank rule. The output is
`ca-bc/bc428_british_columbia_tax_reduction_line_79`, a non-negative kind on the form `ca-bc/bc428`.
The printed instruction "if your net income is $40,807 or more, enter 0 on line 79" needs no
condition: 15,787 x 3.56% is 562.02, so the subtraction already gives 0.

Figures (hand-computed from the ticket, not a CRA example), re-derived here. Taxable income (line
74) is the salary less the CPP enhanced amount (1% of the earnings from 3,500.00 to 71,300.00) and
the CPP second-ceiling amount (4% of the earnings from 71,300.00 to 81,200.00): 29,735.00
and 198,926.00 at salaries of 30,000 and 200,000. Line 78 is (line 74 less 25,020.00, not below 0)
times 3.56%, rounded half-up to the cent: 167.85 and 6,191.05. Line 79 is 562.00 less that, not
below 0: 394.15 and 0.00.

The real parts composed: the British Columbia salary, Schedule 8, the T1 taxable-income parts,
BC428 lines 74, 75, 76, 78 and 73, plus `bc428_line_79.yaml`. The form declaration and header are
test-local, and the service is built over the British Columbia package list of `support.py`.
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
import tax_engine.jurisdictions.ca_bc
import tax_engine.jurisdictions.ca_bc.catalog as bc_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import RATE
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate
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
BC = JurisdictionCode("CA-BC")
FORM = "ca-bc/bc428"
LINE_73 = "ca-bc/bc428_basic_reduction_line_73"
LINE_74 = "ca-bc/bc428_net_income_line_74"
LINE_75 = "ca-bc/bc428_base_amount_line_75"
LINE_76 = "ca-bc/bc428_net_income_over_base_line_76"
LINE_78 = "ca-bc/bc428_reduction_clawback_line_78"
LINE_79 = "ca-bc/bc428_british_columbia_tax_reduction_line_79"
ROUNDING = "ca-bc/cent_rounding"
RATE_FAMILY = "ca-bc/tax_reduction_rate"
BC_PARTS = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
PART = BC_PARTS / "bc428_line_79.yaml"
LINE_PARTS = tuple(BC_PARTS / f"bc428_line_{n}.yaml" for n in ("74", "75", "76", "78", "73", "79"))
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The BC428 declaration, test-local: lines 73 and 79 are exported with the lines they read.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_73}
        - {LINE_74}
        - {LINE_78}
        - {LINE_79}
    """)

# Salary, line 74 (hand-computed), line 78 and the expected line 79.
CASES = [
    ("30000", "29735.00", "167.85", "394.15"),
    ("200000", "198926.00", "6191.05", "0.00"),
]


def _cent(value: Decimal) -> Decimal:
    return value.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def _line_78(line_74: str) -> Decimal:
    """Line 78 re-derived: (line 74 less the 25,020.00 base, not below 0) x 3.56%, to the cent."""
    return _cent(max(D(line_74) - D("25020.00"), D("0.00")) * D("0.0356"))


def _line_79(line_74: str) -> Decimal:
    """Line 79 re-derived from line 74: 562.00 less line 78, not below 0."""
    return max(D("562.00") - _line_78(line_74), D("0.00"))


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    for found in form_parts("schedule_8"):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            found.read_text("utf-8"),
        )
    for part in LINE_PARTS:
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


def _source() -> YamlParameterSource:
    return YamlParameterSource(
        british_columbia_packages().roots(),
        british_columbia_parameter_parsers(),
        british_columbia_units(),
    )


def _amount_kind(identifier: str) -> AmountKind:
    kind = british_columbia_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(("salary", "line_74", "line_78", "expected"), CASES)
def test_line_79_is_line_73_minus_line_78_not_below_zero(
    tmp_path: Path, salary: str, line_74: str, line_78: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = british_columbia_kinds()

    assert sheet.get(kinds.kind(LINE_74)).value == D(line_74)
    assert sheet.get(kinds.kind(LINE_73)).value == D("562.00")
    assert sheet.get(kinds.kind(LINE_78)).value == D(line_78) == _line_78(line_74)
    line_79 = sheet.get(kinds.kind(LINE_79))
    assert not line_79.is_blank
    assert line_79.value == D(expected) == _line_79(line_74)
    assert str(line_79.value) == expected


def test_a_line_78_above_562_gives_a_line_79_of_zero(tmp_path: Path) -> None:
    # At 200,000 the clawback (6,191.05) is far above the 562.00 reduction: floored at 0.00.
    sheet = _sheet(tmp_path, "200000")
    kinds = british_columbia_kinds()

    assert sheet.get(kinds.kind(LINE_78)).value > D("562.00")
    line_79 = sheet.get(kinds.kind(LINE_79))
    assert line_79.value == D("0.00")
    assert str(line_79.value) == "0.00"


def test_the_step_traces_one_subtracted_not_below_zero_line_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "30000")
    kinds = british_columbia_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output is kinds.kind(LINE_79)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_79),
        minuend=kinds.kind(LINE_73),
        minuend_amount=D("562.00"),
        subtrahend=kinds.kind(LINE_78),
        subtrahend_amount=D("167.85"),
        rounding=_source().get(ROUNDING, 2025, ROUNDING_ONLY).rounding,
        result=D("394.15"),
    )


@pytest.mark.parametrize(
    ("line_74", "positive"),
    [("40806.00", True), ("40807.00", False)],
)
def test_line_79_is_positive_at_net_income_40806_and_zero_from_40807(
    line_74: str, positive: bool
) -> None:
    # Line 74 through lines 76 and 78 (real rate dataset and rounding), then line 79: no condition
    # on net income is needed. 15,786 x 3.56% is 561.98 (line 79 0.02); 15,787 x 3.56% is 562.02.
    source = _source()
    rounding = source.get(ROUNDING, 2025, ROUNDING_ONLY)
    rate = source.get(RATE_FAMILY, 2025, RATE)
    k74, k75, k76, k78 = (_amount_kind(i) for i in (LINE_74, LINE_75, LINE_76, LINE_78))
    k73, k79 = _amount_kind(LINE_73), _amount_kind(LINE_79)
    (over_base,) = (
        SubtractNotBelowZero(rounding, k74, k75, k76)
        .compute((Artifact(k74, D(line_74)), Artifact(k75, D("25020.00"))))
        .outputs
    )
    (clawback,) = ApplyRate(rate, k76, k78).compute((over_base,)).outputs
    (reduction,) = (
        SubtractNotBelowZero(rounding, k73, k78, k79)
        .compute((Artifact(k73, D("562.00")), clawback))
        .outputs
    )

    assert reduction.value == _line_79(line_74)
    assert (reduction.value > 0) is positive
    if not positive:
        assert str(reduction.value) == "0.00"


@pytest.mark.parametrize(
    ("line_73", "line_78", "expected"),
    [
        ("562.00", "167.85", "394.15"),
        ("562.00", "562.02", "0.00"),
    ],
)
def test_line_79_is_line_73_minus_line_78_not_below_zero_to_the_cent(
    line_73: str, line_78: str, expected: str
) -> None:
    kinds = (_amount_kind(LINE_73), _amount_kind(LINE_78), _amount_kind(LINE_79))
    rounding = _source().get(ROUNDING, 2025, ROUNDING_ONLY)
    result = SubtractNotBelowZero(rounding, *kinds).compute(
        (Artifact(kinds[0], D(line_73)), Artifact(kinds[1], D(line_78)))
    )

    (output,) = result.outputs
    assert output.value == D(expected)
    assert D(expected) == max(D(line_73) - D(line_78), D("0.00"))


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


def test_the_part_is_one_titled_subtract_step_with_no_blank_rule() -> None:
    step = _step()

    assert step == {
        "name": "core/subtract_not_below_zero",
        "title": "British Columbia tax reduction",
        "reference": "79",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_73, "less": LINE_78},
        "produces": {"output": LINE_79},
    }
    assert "blank" not in step


def test_line_79_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = british_columbia_kinds()

    assert LINE_79 in kinds.identifiers()
    kind = kinds.kind(LINE_79)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(bc_catalog)["BC428_BRITISH_COLUMBIA_TAX_REDUCTION_LINE_79"]

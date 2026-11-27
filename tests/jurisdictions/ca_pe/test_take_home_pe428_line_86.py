"""PE428 (2025) line 86, line 84 at 5%, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 85: Applicable rate 5%; Line 86: Line 84 multiplied by the percentage from line 85 =

Line 85 is the printed 5%, a dataset figure with no step; one core/apply_rate, rounded half-up to
the cent. Hand figures: 7,085.00 x 5% = 354.25 at $30,000; 46,685.00 x 5% = 2,334.25 at $70,000;
2,350.00 x 5% = 117.50 at a net income of 25,000.00.

The test builds the engine over the real federal parts and the real parts of lines 1 to 86 through
the shared `take_home_service` fixture.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.trace import RateAppliedLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_REDUCTION_PHASE_OUT_LINE_86
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_86,
    HEADER,
    compute,
    exports_of,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
PART_NAME = "pe428_line_86.yaml"
OUTPUT = "ca-pe/pe428_reduction_phase_out_line_86"
PARTS = CHAIN_86
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_reduction_phase_out_line_86": "0.00"}),
    ("30000", {}, {"ca-pe/pe428_reduction_phase_out_line_86": "354.25"}),
    ("70000", {}, {"ca-pe/pe428_reduction_phase_out_line_86": "2334.25"}),
    ("25217.17", {}, {"ca-pe/pe428_reduction_phase_out_line_86": "117.50"}),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(*exports_of(PARTS)), *PARTS)
    return compute(service, salary, given)


@pytest.mark.parametrize(("salary", "given", "expected"), CASES)
def test_the_line_figures(
    take_home_service: TakeHomeService,
    salary: str,
    given: dict[str, str],
    expected: dict[str, str],
) -> None:
    sheet = _sheet(take_home_service, salary, given)

    for identifier, amount in expected.items():
        assert value(sheet, identifier) == D(amount)


def test_the_trace_is_line_84_times_the_printed_rate(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "30000")
    kinds = prince_edward_island_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, RateAppliedLine) and t.output is kinds.kind(OUTPUT)
    ]
    assert line.base.identifier == "ca-pe/pe428_income_over_base_amount_line_84"
    assert line.base_amount == D("7085.00")
    assert line.result == D("354.25")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/apply_rate",
            "reference": "86",
            "unit": "ca/cad",
            "params": {"rate": "ca-pe/low_income_reduction_rate"},
            "consumes": {"base": "ca-pe/pe428_income_over_base_amount_line_84"},
            "produces": {"output": "ca-pe/pe428_reduction_phase_out_line_86"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_REDUCTION_PHASE_OUT_LINE_86
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

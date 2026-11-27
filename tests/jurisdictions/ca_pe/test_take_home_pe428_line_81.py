"""PE428 (2025) line 81, reductions added, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version):
Line 81: Add lines 75 to 80 =

One core/sum over lines 75 to 80. Lines 76 to 80 are optional inputs a salary-only caller leaves
out, each read as 0, so the line is 350.00. With 250.00 on line 76, 350.00 on line 77, 250.00 on
line 78, 350.00 on line 79 and 300.00 on line 80 it is 1,850.00.

The test builds the engine over the real federal parts and the real parts of lines 1 to 81 through
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
from tax_engine.domain.trace import SumLine
from tax_engine.jurisdictions.ca_pe.catalog import PE428_LOW_INCOME_REDUCTIONS_TOTAL_LINE_81
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_81,
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
PART_NAME = "pe428_line_81.yaml"
OUTPUT = "ca-pe/pe428_low_income_reductions_total_line_81"
PARTS = CHAIN_81
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {"ca-pe/pe428_low_income_reductions_total_line_81": "350.00"}),
    ("30000", {}, {"ca-pe/pe428_low_income_reductions_total_line_81": "350.00"}),
    ("70000", {}, {"ca-pe/pe428_low_income_reductions_total_line_81": "350.00"}),
    (
        "20000",
        {
            "ca-pe/pe428_age_reduction_for_self_line_76": "250",
            "ca-pe/pe428_reduction_for_spouse_or_common_law_partner_line_77": "350",
            "ca-pe/pe428_age_reduction_for_spouse_or_common_law_partner_line_78": "250",
            "ca-pe/pe428_reduction_for_eligible_dependant_line_79": "350",
            "ca-pe/pe428_reduction_for_dependent_children_line_80": "300",
        },
        {"ca-pe/pe428_low_income_reductions_total_line_81": "1850.00"},
    ),
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


def test_the_trace_is_one_sum_of_lines_75_to_80_with_the_blank_parts_read_as_0(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "20000")
    kinds = prince_edward_island_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(OUTPUT)]
    assert [(kind.identifier, amount) for kind, amount in line.parts] == [
        ("ca-pe/low_income_reduction_basic", D("350.00")),
        ("ca-pe/pe428_age_reduction_for_self_line_76", D("0")),
        ("ca-pe/pe428_reduction_for_spouse_or_common_law_partner_line_77", D("0")),
        ("ca-pe/pe428_age_reduction_for_spouse_or_common_law_partner_line_78", D("0")),
        ("ca-pe/pe428_reduction_for_eligible_dependant_line_79", D("0")),
        ("ca-pe/pe428_reduction_for_dependent_children_line_80", D("0")),
    ]
    assert line.total == D("350.00")


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / PART_NAME).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/sum",
            "reference": "81",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {
                "parts": [
                    "ca-pe/low_income_reduction_basic",
                    "ca-pe/pe428_age_reduction_for_self_line_76",
                    "ca-pe/pe428_reduction_for_spouse_or_common_law_partner_line_77",
                    "ca-pe/pe428_age_reduction_for_spouse_or_common_law_partner_line_78",
                    "ca-pe/pe428_reduction_for_eligible_dependant_line_79",
                    "ca-pe/pe428_reduction_for_dependent_children_line_80",
                ]
            },
            "blank": {
                "ca-pe/pe428_age_reduction_for_self_line_76": "0",
                "ca-pe/pe428_reduction_for_spouse_or_common_law_partner_line_77": "0",
                "ca-pe/pe428_age_reduction_for_spouse_or_common_law_partner_line_78": "0",
                "ca-pe/pe428_reduction_for_eligible_dependant_line_79": "0",
                "ca-pe/pe428_reduction_for_dependent_children_line_80": "0",
            },
            "produces": {"output": "ca-pe/pe428_low_income_reductions_total_line_81"},
        }
    ]


def test_the_kind_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = prince_edward_island_kinds().kind(OUTPUT)

    assert kind is PE428_LOW_INCOME_REDUCTIONS_TOTAL_LINE_81
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

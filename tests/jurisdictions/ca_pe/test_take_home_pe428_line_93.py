"""PE428 (2025) line 93, line 90 minus line 92, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version): "Line 93: Line 90
minus line 92 (if negative, enter "0") =". One core/subtract_not_below_zero; line 92 is blank for a
salary-only filer and read as 0. Figures: 33.83 / 1,261.72 / 6,355.92 at $20,000 / $30,000 /
$70,000; with 300.00 on line 92 at $70,000 it is 6,055.92, and 400.00 at $20,000 floors it at 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_93,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
LINE_90 = "ca-pe/pe428_tax_line_90"
LINE_92 = "ca-pe/pe428_political_contribution_tax_credit_line_92"
LINE_92_INPUT = "ca-pe/pe428_political_contribution_tax_credit_claimed_line_92"
LINE_93 = "ca-pe/pe428_tax_line_93"
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {LINE_93: "33.83"}),
    ("30000", {}, {LINE_93: "1261.72"}),
    ("70000", {}, {LINE_93: "6355.92"}),
    ("70000", {LINE_92_INPUT: "300.00"}, {LINE_93: "6055.92"}),
    ("20000", {LINE_92_INPUT: "400.00"}, {LINE_93: "0.00"}),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(LINE_90, LINE_92, LINE_93), *CHAIN_93)
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


def _part() -> dict[str, Any]:
    part = yaml.safe_load((PE_PARTS / "pe428_line_93.yaml").read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "93",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {"amount": LINE_90, "less": LINE_92},
            "blank": {"less": "0"},
            "produces": {"output": LINE_93},
        }
    ]


def test_the_kinds_are_registered_non_negative_decimal_amount_kinds() -> None:
    kinds = prince_edward_island_kinds()

    for identifier in (LINE_90, LINE_93):
        kind = kinds.kind(identifier)
        assert isinstance(kind, AmountKind)
        assert kind.value_type is Decimal
        assert non_negative(kind)

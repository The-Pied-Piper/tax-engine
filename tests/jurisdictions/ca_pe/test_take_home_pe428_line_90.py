"""PE428 (2025) line 90, line 88 minus line 89, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version): "Line 90: Line 88
minus line 89 (if negative, enter "0") =". One core/subtract_not_below_zero; line 89 is an
optional input read as 0 when blank. Figures: line 88 is 33.83 / 1,261.72 / 6,355.92 at $20,000 /
$30,000 / $70,000, so line 90 is the same with line 89 blank; with 100.00 on line 89 at $70,000 it
is 6,255.92, and a line 89 above line 88 floors it at 0.00.
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
    CHAIN_90,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
LINE_88 = "ca-pe/pe428_tax_line_88"
LINE_89 = "ca-pe/pe428_provincial_foreign_tax_credit_line_89"
LINE_90 = "ca-pe/pe428_tax_line_90"
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {LINE_90: "33.83"}),
    ("30000", {}, {LINE_90: "1261.72"}),
    ("70000", {}, {LINE_90: "6355.92"}),
    ("70000", {LINE_89: "100.00"}, {LINE_90: "6255.92"}),
    ("70000", {LINE_89: "9000.00"}, {LINE_90: "0.00"}),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(LINE_88, LINE_90), *CHAIN_90)
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
    part = yaml.safe_load((PE_PARTS / "pe428_line_90.yaml").read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "90",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {"amount": LINE_88, "less": LINE_89},
            "blank": {"less": "0"},
            "produces": {"output": LINE_90},
        }
    ]


def test_the_kinds_are_registered_non_negative_decimal_amount_kinds() -> None:
    kinds = prince_edward_island_kinds()

    for identifier in (LINE_89, LINE_90):
        kind = kinds.kind(identifier)
        assert isinstance(kind, AmountKind)
        assert kind.value_type is Decimal
        assert non_negative(kind)

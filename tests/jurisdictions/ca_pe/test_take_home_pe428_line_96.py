"""PE428 (2025) line 96, line 94 plus line 95 (maximum $7,000), real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version): "Line 96: Line 94
plus line 95 (maximum $7,000) =". A core/sum of lines 94 and 95 (each read as 0 when blank), then
core/capped_amount with the printed maximum, the `ca-pe/equity_tax_credit_maximum` dataset. Figures:
0.00 with both blank; 1,000.00 plus 250.50 is 1,250.50; 6,000.00 plus 3,000.00 is 9,000.00 before
the maximum and 7,000.00 on line 96.
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
    CHAIN_96,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
LINE_94 = "ca-pe/pe428_equity_tax_credit_line_94"
LINE_95 = "ca-pe/pe428_unused_equity_tax_credit_line_95"
LINE_96_SUM = "ca-pe/pe428_equity_tax_credit_before_maximum_line_96"
LINE_96 = "ca-pe/pe428_equity_tax_credit_line_96"
LINE_93 = "ca-pe/pe428_tax_line_93"
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("70000", {}, {LINE_96_SUM: "0.00", LINE_96: "0.00"}),
    (
        "70000",
        {LINE_94: "1000.00", LINE_95: "250.50"},
        {LINE_96_SUM: "1250.50", LINE_96: "1250.50"},
    ),
    (
        "70000",
        {LINE_94: "6000.00", LINE_95: "3000.00"},
        {LINE_96_SUM: "9000.00", LINE_96: "7000.00"},
    ),
    ("70000", {LINE_95: "7000.00"}, {LINE_96: "7000.00"}),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(LINE_93, LINE_96_SUM, LINE_96), *CHAIN_96)
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
    part = yaml.safe_load((PE_PARTS / "pe428_line_96.yaml").read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/sum",
            "title": "Equity tax credit before the maximum",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {"parts": [LINE_94, LINE_95]},
            "blank": {LINE_94: "0", LINE_95: "0"},
            "produces": {"output": LINE_96_SUM},
        },
        {
            "name": "core/capped_amount",
            "reference": "96",
            "unit": "ca/cad",
            "params": {"cap": "ca-pe/equity_tax_credit_maximum"},
            "consumes": {"base": LINE_96_SUM},
            "produces": {"output": LINE_96},
        },
    ]


def test_the_kinds_are_registered_non_negative_decimal_amount_kinds() -> None:
    kinds = prince_edward_island_kinds()

    for identifier in (LINE_94, LINE_95, LINE_96_SUM, LINE_96):
        kind = kinds.kind(identifier)
        assert isinstance(kind, AmountKind)
        assert kind.value_type is Decimal
        assert non_negative(kind)

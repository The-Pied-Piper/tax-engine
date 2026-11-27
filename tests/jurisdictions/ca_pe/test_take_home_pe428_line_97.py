"""PE428 (2025) line 97, line 93 minus line 96, the Prince Edward Island tax, real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version): "Line 97: Line 93
minus line 96 (if negative, enter "0") Enter this amount on line 42800 of your return. Prince
Edward Island tax =". One core/subtract_not_below_zero. Figures (hand-computed, independently
reproduced): 33.83 / 1,261.72 / 6,355.92 at $20,000 / $30,000 / $70,000, line 96 being 0.00; the
unrounded line 97 at $70,000 is 6,355.92715 and the printed line is 6,355.92. With 1,000.00 on
line 94 at $70,000 it is 5,355.92; a line 96 above line 93 floors it at 0.00.
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
    CHAIN_97,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
LINE_93 = "ca-pe/pe428_tax_line_93"
LINE_94 = "ca-pe/pe428_equity_tax_credit_line_94"
LINE_96 = "ca-pe/pe428_equity_tax_credit_line_96"
LINE_97 = "ca-pe/pe428_prince_edward_island_tax_line_97"
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("20000", {}, {LINE_97: "33.83"}),
    ("30000", {}, {LINE_97: "1261.72"}),
    ("70000", {}, {LINE_97: "6355.92"}),
    ("70000", {LINE_94: "1000.00"}, {LINE_93: "6355.92", LINE_96: "1000.00", LINE_97: "5355.92"}),
    ("70000", {LINE_94: "7000.00"}, {LINE_97: "0.00"}),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(LINE_93, LINE_96, LINE_97), *CHAIN_97)
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
    part = yaml.safe_load((PE_PARTS / "pe428_line_97.yaml").read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/subtract_not_below_zero",
            "reference": "97",
            "unit": "ca/cad",
            "params": {"rounding": "ca-pe/cent_rounding"},
            "consumes": {"amount": LINE_93, "less": LINE_96},
            "produces": {"output": LINE_97},
        }
    ]


def test_the_kinds_are_registered_non_negative_decimal_amount_kinds() -> None:
    kinds = prince_edward_island_kinds()

    for identifier in (LINE_93, LINE_96, LINE_97):
        kind = kinds.kind(identifier)
        assert isinstance(kind, AmountKind)
        assert kind.value_type is Decimal
        assert non_negative(kind)

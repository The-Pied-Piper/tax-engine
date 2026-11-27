"""PE428 (2025) line 92, the political contribution tax credit (maximum $500), real parts.

Form text (Form PE428, CRA 5002-C, confirmed 2026-11-26 from the text version): "Line 92: Prince
Edward Island political contribution tax credit (use Worksheet PE428) (maximum $500)". The
worksheet is not built, so the credit is one optional input; core/credit_amount supplies the
printed maximum (the `ca-pe/political_contribution_tax_credit_maximum` dataset) and core/at_most
is line 92: the amount passed on, a blank passed on blank, an amount above $500 refused, not
capped (as NS428 line 90).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import (
    CHAIN_92,
    HEADER,
    compute,
    form,
    value,
)
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PE_PARTS = Path(tax_engine.jurisdictions.ca_pe.__file__).parent / "manifests" / "2025"
LINE_92_INPUT = "ca-pe/pe428_political_contribution_tax_credit_claimed_line_92"
LINE_92_MAX = "ca-pe/pe428_political_contribution_tax_credit_maximum"
LINE_90 = "ca-pe/pe428_tax_line_90"
LINE_92 = "ca-pe/pe428_political_contribution_tax_credit_line_92"
CASES: list[tuple[str, dict[str, str], dict[str, str]]] = [
    ("70000", {LINE_92_INPUT: "300.00"}, {LINE_92_MAX: "500.00", LINE_92: "300.00"}),
    ("70000", {LINE_92_INPUT: "500.00"}, {LINE_92: "500.00"}),
]


def _sheet(
    take_home_service: TakeHomeService, salary: str, given: dict[str, str] | None = None
) -> Any:
    service = take_home_service(HEADER, form(LINE_90, LINE_92_MAX, LINE_92), *CHAIN_92)
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
    part = yaml.safe_load((PE_PARTS / "pe428_line_92.yaml").read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-pe/pe428"}
    return part


def test_the_part_is_the_steps_the_form_prints() -> None:
    assert _part()["capabilities"] == [
        {
            "name": "core/credit_amount",
            "unit": "ca/cad",
            "params": {"amount": "ca-pe/political_contribution_tax_credit_maximum"},
            "produces": {"output": LINE_92_MAX},
        },
        {
            "name": "core/at_most",
            "title": "Prince Edward Island political contribution tax credit",
            "reference": "92",
            "unit": "ca/cad",
            "consumes": {"amount": LINE_92_INPUT, "bound": LINE_92_MAX},
            "blank": {"amount": "pass_on"},
            "produces": {"output": LINE_92},
        },
    ]


def test_the_kinds_are_registered_non_negative_decimal_amount_kinds() -> None:
    kinds = prince_edward_island_kinds()

    for identifier in (LINE_92_INPUT, LINE_92_MAX, LINE_92):
        kind = kinds.kind(identifier)
        assert isinstance(kind, AmountKind)
        assert kind.value_type is Decimal
        assert non_negative(kind)


def test_an_amount_above_the_printed_maximum_is_refused_not_capped(
    take_home_service: TakeHomeService,
) -> None:
    with pytest.raises(InputAboveBoundError):
        _sheet(take_home_service, "70000", {LINE_92_INPUT: "500.01"})

"""Revenu Quebec TP-1 (2025) line 397, "Multiply line 397.1 by 10%. Tax credit for union,
professional or other dues", as the Quebec take-home manifest wires it: one `core/apply_rate` over
line 397.1 with the printed rate from the dataset `ca-qc/tp1_line_397_rate`, rounded half-up to the
cent by the dataset's rule. Line 397.1 is one optional input, read as 0 when the caller leaves it
out. The expected figures are hand-computed from the printed lines, not a Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_UNION_DUES_CREDIT_LINE_397,
    TP1_UNION_DUES_LINE_397_1,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp1_credits_support import LINE_397_PARTS, credits_sheet
from tests.kinds import non_negative

D = Decimal
FORM = "ca-qc/tp1_credits"
PART = "tp1_credits_line_397.yaml"
IDENTIFIER = "ca-qc/tp1_union_dues_credit_line_397"
EXPORTS = (IDENTIFIER,)


def test_line_397_with_line_397_1_blank_is_zero(take_home_service: TakeHomeService) -> None:
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_397_PARTS)

    assert str(sheet.get(TP1_UNION_DUES_CREDIT_LINE_397).value) == "0.00"


def test_line_397_is_line_397_1_at_10_percent(take_home_service: TakeHomeService) -> None:
    given = Artifact(TP1_UNION_DUES_LINE_397_1, D("525.55"))
    sheet = credits_sheet(take_home_service, EXPORTS, LINE_397_PARTS, given)

    # 525.55 x 0.10 = 52.555, rounded half-up to the cent.
    assert str(sheet.get(TP1_UNION_DUES_CREDIT_LINE_397).value) == "52.56"


def _part() -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / PART).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_apply_rate_over_line_397_1_with_the_printed_title() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/apply_rate",
        "title": "Tax credit for union, professional or other dues",
        "reference": "397",
        "unit": "ca/cad",
        "params": {"rate": "ca-qc/tp1_line_397_rate"},
        "consumes": {"base": "ca-qc/tp1_union_dues_line_397_1"},
        "blank": {"base": "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_the_output_kind_is_a_registered_non_negative_amount() -> None:
    assert quebec_kinds().kind(IDENTIFIER) is TP1_UNION_DUES_CREDIT_LINE_397
    assert isinstance(TP1_UNION_DUES_CREDIT_LINE_397, AmountKind)
    assert non_negative(TP1_UNION_DUES_CREDIT_LINE_397)

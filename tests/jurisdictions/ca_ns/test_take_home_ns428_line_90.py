"""NS428 (2025) line 90, the labour-sponsored venture capital tax credit, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 90 Labour-sponsored
venture capital tax credit: Cost of shares from Form NSLSV ... multiplied by 20% (maximum $2,000)".
Three steps (`ns428_line_90.yaml`): a `core/credit_amount` that supplies the printed maximum, a
`core/apply_rate` that multiplies the entered amount by the printed 20% (read as 0 when the line is
left blank) and a `core/at_most`, which is line 90. A product above the printed maximum is refused,
not capped. The line is an optional input a salary-only caller leaves out, so its credit is 0.00.
Figures are hand-computed from the printed form (not a CRA example).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative


def test_a_blank_line_90_is_a_credit_of_0(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_90)) == "0.00"


def test_the_entered_amount_is_multiplied_by_20_percent(tmp_path: Path) -> None:
    given = {s.LINE_90_INPUT: "5000"}

    assert str(s.line(tmp_path, "70000", s.LINE_90_AT_RATE, given)) == "1000.00"
    assert str(s.line(tmp_path, "70000", s.LINE_90, given)) == "1000.00"


def test_the_printed_maximum_is_2000(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_90_MAXIMUM)) == "2000.00"


def test_a_product_at_the_maximum_is_allowed(tmp_path: Path) -> None:
    given = {s.LINE_90_INPUT: "10000"}

    assert str(s.line(tmp_path, "70000", s.LINE_90, given)) == "2000.00"


def test_a_product_above_the_maximum_is_refused_not_capped(tmp_path: Path) -> None:
    given = {s.LINE_90_INPUT: "10000.05"}

    with pytest.raises(InputAboveBoundError):
        s.line(tmp_path, "70000", s.LINE_90, given)


def test_the_part_has_three_steps_and_only_the_last_has_the_reference() -> None:
    steps = s.part("ns428_line_90.yaml")["capabilities"]

    assert [step["name"] for step in steps] == [
        "core/credit_amount",
        "core/apply_rate",
        "core/at_most",
    ]
    assert [step.get("reference") for step in steps] == [None, None, "90"]
    assert steps[2]["consumes"] == {"amount": s.LINE_90_AT_RATE, "bound": s.LINE_90_MAXIMUM}
    assert steps[2]["produces"] == {"output": s.LINE_90}


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_90)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_LABOUR_SPONSORED_CREDIT_LINE_90

"""NS428 (2025) line 86, the political contribution tax credit, real parts.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 86 Total political
contributions made in 2025 ... multiplied by 75% (maximum $750)". Three steps
(`ns428_line_86.yaml`): a `core/credit_amount` that supplies the printed maximum, a
`core/apply_rate` that multiplies the entered amount by the printed 75% (read as 0 when the line is
left blank) and a `core/at_most`, which is line 86. A product above the printed maximum is refused,
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


def test_a_blank_line_86_is_a_credit_of_0(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_86)) == "0.00"


def test_the_entered_amount_is_multiplied_by_75_percent(tmp_path: Path) -> None:
    given = {s.LINE_86_INPUT: "400"}

    assert str(s.line(tmp_path, "70000", s.LINE_86_AT_RATE, given)) == "300.00"
    assert str(s.line(tmp_path, "70000", s.LINE_86, given)) == "300.00"


def test_the_printed_maximum_is_750(tmp_path: Path) -> None:
    assert str(s.line(tmp_path, "70000", s.LINE_86_MAXIMUM)) == "750.00"


def test_a_product_at_the_maximum_is_allowed(tmp_path: Path) -> None:
    given = {s.LINE_86_INPUT: "1000"}

    assert str(s.line(tmp_path, "70000", s.LINE_86, given)) == "750.00"


def test_a_product_above_the_maximum_is_refused_not_capped(tmp_path: Path) -> None:
    given = {s.LINE_86_INPUT: "1000.01"}

    with pytest.raises(InputAboveBoundError):
        s.line(tmp_path, "70000", s.LINE_86, given)


def test_the_part_has_three_steps_and_only_the_last_has_the_reference() -> None:
    steps = s.part("ns428_line_86.yaml")["capabilities"]

    assert [step["name"] for step in steps] == [
        "core/credit_amount",
        "core/apply_rate",
        "core/at_most",
    ]
    assert [step.get("reference") for step in steps] == [None, None, "86"]
    assert steps[2]["consumes"] == {"amount": s.LINE_86_AT_RATE, "bound": s.LINE_86_MAXIMUM}
    assert steps[2]["produces"] == {"output": s.LINE_86}


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_86)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_POLITICAL_CONTRIBUTIONS_CREDIT_LINE_86

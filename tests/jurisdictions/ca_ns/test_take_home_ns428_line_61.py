"""NS428 (2025) line 61, the additional tax for minimum tax purposes.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Nova Scotia additional
tax for minimum tax purposes: Amount from line 14 of Part 7 of Form T691 multiplied by 57.5%". The
amount is a record total of the T691's line 14 export; the printed 57.5% is a dataset rate, rounded
half-up to the cent. A salary-only caller has no T691 amount, so the line is 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative
from tests.t691_support import line_14

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_a_salary_only_caller_has_no_additional_tax(tmp_path: Path, salary: str) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_61)) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [("1000.00", "575.00"), ("0.01", "0.01"), ("0.08", "0.05")],
)
def test_line_61_is_57_point_5_percent_of_t691_line_14_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    given = {artifact.kind.identifier: str(artifact.value) for artifact in line_14(amount)}

    assert str(s.line(tmp_path, "70000", s.LINE_61, given)) == expected
    assert s.line(tmp_path / "amount", "70000", s.LINE_61_AMOUNT, given) == D(amount)


def test_the_part_is_a_record_total_of_the_t691_export_then_the_rate() -> None:
    part = s.part("ns428_line_61.yaml")

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["capabilities"] == [
        {
            "name": "core/record_total",
            "title": "Amount from line 14 of Part 7 of Form T691",
            "reference": "61 box A",
            "unit": "ca/cad",
            "consumes": {
                "records": "ca/t691.t691_additional_taxes_for_minimum_tax_carryover_line_14"
            },
            "produces": {"output": s.LINE_61_AMOUNT},
        },
        {
            "name": "core/apply_rate",
            "title": "Nova Scotia additional tax for minimum tax purposes",
            "reference": "61 box B",
            "unit": "ca/cad",
            "params": {"rate": s.RATE},
            "consumes": {"base": s.LINE_61_AMOUNT},
            "produces": {"output": s.LINE_61},
        },
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_61)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_MINIMUM_TAX_ADDITIONAL_LINE_61


def test_the_amount_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_61_AMOUNT)

    assert kind is ns_catalog.NS428_MINIMUM_TAX_T691_AMOUNT_LINE_61
    assert non_negative(kind)

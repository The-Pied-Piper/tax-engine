"""NS428 (2025) line 71, the basic reduction, claimed whole.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Line 71 and 61950:
Basic reduction Claim $300". Eligibility (Nova Scotia resident on 31 December and 19 or older, or
with a spouse, or a parent; not confined to prison over six months) is the calculator's stated
assumption, so there is no input. The figure is the `ca-ns/low_income_reduction_basic` dataset
through core/credit_amount, the same at every salary. Lines 72 and 73 are deferred.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative


@pytest.mark.parametrize("salary", ["0", "20000", "70000"])
def test_line_71_is_300_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_71)) == "300.00"


def test_the_part_is_one_credit_amount_step() -> None:
    assert s.part("ns428_line_71.yaml")["capabilities"] == [
        {
            "name": "core/credit_amount",
            "title": "Basic reduction",
            "reference": "71",
            "unit": "ca/cad",
            "params": {"amount": "ca-ns/low_income_reduction_basic"},
            "produces": {"output": s.LINE_71},
        }
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_71)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.LOW_INCOME_REDUCTION_BASIC

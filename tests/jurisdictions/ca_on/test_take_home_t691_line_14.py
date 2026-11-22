"""T691 Part 7 line 14: one cent-rounded sum step reading the blank as 0, exported to the provinces.

Form text (T691 E (25), Part 7): "Line 1 minus line 13 (if negative, enter "0") / Additional taxes
paid for minimum tax carryover = 14". Lines 1 to 13 are not built, so line 14 is one typed input.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.domain.kinds import AmountKind
from tax_engine.registrations import artifact_kinds
from tests.federal_forms import FEDERAL_FORMS
from tests.kinds import non_negative

NAME = "ca/t691_additional_taxes_for_minimum_tax_carryover"
OUTPUT = "ca/t691_additional_taxes_for_minimum_tax_carryover_line_14"
TITLE = "Additional taxes paid for minimum tax carryover"


def test_line_14_is_one_sum_step_that_reads_its_blank_as_zero() -> None:
    part: Any = yaml.safe_load((FEDERAL_FORMS / "t691" / "t691_line_14.yaml").read_text("utf-8"))

    assert part["form"] == {"name": "ca/t691"}
    (step,) = part["capabilities"]
    assert step == {
        "name": "core/sum",
        "title": TITLE,
        "reference": "14",
        "unit": "ca/cad",
        "params": {"rounding": "ca/cent_rounding"},
        "consumes": {"parts": [NAME]},
        "blank": {NAME: "0"},
        "produces": {"output": OUTPUT},
    }


def test_the_export_kind_is_a_non_negative_decimal_amount() -> None:
    kind = artifact_kinds().kind(OUTPUT)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)

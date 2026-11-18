"""The plain-words titles of the unprinted steps that a numbered line's sentence names, pinned."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

TITLES = [
    (
        "ca/schedule_8",
        "cpp_part_3_line_7_difference",
        "Earnings left after the Canada Pension Plan exemption",
    ),
    ("ca/t1_taxable_income", "net_income_signed", "Net income, which can be below zero"),
    ("ca/t2204", "t2204_line_1_count", "Multiplier that is 1 unless the low-pay rule applies"),
    (
        "ca/t2204",
        "t2204_line_1_plus_2",
        "Insured pay plus self-employment and other earnings eligible for EI, before the limit",
    ),
    ("ca/t2204", "t2204_exemption", "Set amount taken off earnings"),
    ("ca-on/on428_a", "lift_credit_before_maximum", "LIFT credit before the most is applied"),
    (
        "ca-on/on428",
        "on428_tax_reduction_before_conditions_line_80",
        "Reduction before any exceptions",
    ),
    (
        "ca-on/on428",
        "on428_tax_reduction_conditions_count_line_80",
        "Multiplier that is 0 when minimum tax was added",
    ),
]


@pytest.mark.parametrize(("form", "label", "title"), TITLES)
def test_an_unprinted_step_is_titled_in_plain_words(form: str, label: str, title: str) -> None:
    sheets = build_tax_computation().compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, Decimal("70000"))
    )

    (sheet,) = sheets[form]

    assert sheet.title(label) == title
    assert sheet.reference(label) is None

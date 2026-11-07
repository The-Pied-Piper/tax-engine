"""Registered and money kinds of the federal catalog family `taxable_income`."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_NET_INCOME,
    NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
)


def test_the_taxable_income_kinds_are_money() -> None:
    for kind in (
        NET_CAPITAL_LOSS_NUMERATOR_ONE_2000,
        DEDUCTIONS_FROM_NET_INCOME,
    ):
        assert kind.value_type is Decimal, kind.identifier


# --- more than one disposition: notes (1) to (3) and the order of the claims ---------------------
#
# The kinds are the sums of the earlier runs and the lines as corrected, each with a docstring that
# quotes the form's own words (`docs/cra-forms-2025/t2048-25e.pdf`).

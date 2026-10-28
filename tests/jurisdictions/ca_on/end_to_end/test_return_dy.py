"""CA-ON 2025 end to end: return DY, the memo lines of the T1, Schedule 11 and Schedule 15.

Return DY is `returns/2025_return_dy.yaml`: Return DT with sixteen printed memo lines entered. Each
memo line is carried to its declared output as entered, and no total reads it, so the totals are
Return DT's, computed here without any memo line.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    EI_MATERNITY_PARENTAL_BENEFITS,
    EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME,
    FHSA_FIRST_OPENED_IN_YEAR,
    FHSA_HOME_ADDRESS_SAME,
    FHSA_QUALIFYING_WITHDRAWALS,
    NET_INCOME,
    PENSION_ADJUSTMENT,
    REFUND_OR_BALANCE_OWING,
    SPECIFIED_FOREIGN_PROPERTY_OVER_100K,
    SUPPORT_PAYMENTS_MADE_TOTAL,
    SUPPORT_PAYMENTS_RECEIVED_TOTAL,
    T4_COMMISSIONS,
    T4AP_DISABILITY_BENEFITS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TUITION_CANNOT_BE_FULL_TIME_STUDENT,
    TUITION_FULL_TIME_MONTHS,
    TUITION_PART_TIME_MONTHS,
    UCCB_DESIGNATED_TO_DEPENDANT,
    WAGE_LOSS_REPLACEMENT_CONTRIBUTIONS,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, compute, service, starting

# The sixteen memo lines with their chosen figures, as in `returns/2025_return_dy.yaml`: the
# amounts are dollars and cents, the ticks and the Yes answer are 1, the months are counts.
MEMO_LINES: tuple[tuple[ArtifactKind[Any], Any], ...] = (
    (EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME, D("1500.00")),
    (T4_COMMISSIONS, D("5000.00")),
    (WAGE_LOSS_REPLACEMENT_CONTRIBUTIONS, D("2000.00")),
    (T4AP_DISABILITY_BENEFITS, D("3000.00")),
    (UCCB_DESIGNATED_TO_DEPENDANT, D("1200.00")),
    (EI_MATERNITY_PARENTAL_BENEFITS, D("4000.00")),
    (SUPPORT_PAYMENTS_RECEIVED_TOTAL, D("6000.00")),
    (PENSION_ADJUSTMENT, D("7000.00")),
    (FHSA_FIRST_OPENED_IN_YEAR, 1),
    (FHSA_QUALIFYING_WITHDRAWALS, D("8000.00")),
    (FHSA_HOME_ADDRESS_SAME, 1),
    (SUPPORT_PAYMENTS_MADE_TOTAL, D("9000.00")),
    (SPECIFIED_FOREIGN_PROPERTY_OVER_100K, 1),
    (TUITION_CANNOT_BE_FULL_TIME_STUDENT, 1),
    (TUITION_PART_TIME_MONTHS, 6),
    (TUITION_FULL_TIME_MONTHS, 0),
)


def base_return() -> Worksheet:
    """Return DT's inputs, as in `returns/2025_return_dt.yaml`, without any memo line."""
    return compute("0", (), "0", "0", "0", "0", "0", flipped_property_disposed=1)


def return_dy(**overrides: Any) -> Worksheet:
    """Return DY: Return DT's inputs with the sixteen memo lines entered, each at its chosen figure
    unless `overrides` names it by the last part of its identifier, such as `t4_commissions`."""
    memo_lines: dict[str, Any] = {
        kind.identifier.rpartition("/")[2]: str(value) if isinstance(value, Decimal) else value
        for kind, value in MEMO_LINES
    }
    memo_lines.update({k: str(v) if isinstance(v, Decimal) else v for k, v in overrides.items()})
    result = service().compute(
        CA_ON,
        2025,
        *starting("0", (), "0", "0", "0", "0", "0", flipped_property_disposed=1, **memo_lines),
    )
    return result["ca-on/return"][0]


@pytest.mark.parametrize(
    ("kind", "value"), MEMO_LINES, ids=[kind.identifier for kind, _ in MEMO_LINES]
)
def test_each_memo_line_is_carried_to_its_output_as_entered(
    kind: ArtifactKind[Any], value: Any
) -> None:
    # Each memo line is a caller's input and a declared output: the output is the figure entered,
    # as a Decimal for dollars and cents and as an int for a tick, a Yes answer or a count of
    # months.
    worksheet = return_dy()

    assert worksheet.get(kind).value == value
    assert type(worksheet.get(kind).value) is type(value)


def test_the_memo_lines_change_no_total() -> None:
    # Return DT's totals are nil (no income, no deduction, no credit): entering the sixteen memo
    # lines, which the General Guide says are already included in lines 10100, 11400 and 11900 or
    # which no line reads, adds nothing to total income, net income, taxable income or the refund.
    base = base_return()
    dy = return_dy()

    for kind in (TOTAL_INCOME, NET_INCOME, TAXABLE_INCOME, REFUND_OR_BALANCE_OWING):
        assert dy.get(kind).value == base.get(kind).value, kind.identifier
    assert dy.get(TOTAL_INCOME).value == D("0.00")
    assert dy.get(REFUND_OR_BALANCE_OWING).value == D("0.00")


def test_other_chosen_memo_figures_change_no_total() -> None:
    # The totals do not depend on the figures entered: a larger commission and a "No" for the
    # home address tick, each still carried as entered, leave every total as Return DT's.
    base = base_return()
    dy = return_dy(t4_commissions=D("9999.00"), fhsa_home_address_same=0)

    assert dy.get(T4_COMMISSIONS).value == D("9999.00")
    assert dy.get(FHSA_HOME_ADDRESS_SAME).value == 0
    for kind in (TOTAL_INCOME, NET_INCOME, TAXABLE_INCOME, REFUND_OR_BALANCE_OWING):
        assert dy.get(kind).value == base.get(kind).value, kind.identifier


def test_the_memo_lines_change_no_total_of_a_return_with_income() -> None:
    # On a return with employment income of 80000 the totals are not nil, so a memo line leaking
    # into total income, net income, taxable income or the refund would show.
    income = ("80000", (), "0", "0", "0", "0", "0")
    memo_lines: dict[str, Any] = {
        kind.identifier.rpartition("/")[2]: str(value) if isinstance(value, Decimal) else value
        for kind, value in MEMO_LINES
    }
    without = service().compute(CA_ON, 2025, *starting(*income))["ca-on/return"][0]
    with_memo = service().compute(CA_ON, 2025, *starting(*income, **memo_lines))["ca-on/return"][0]

    assert without.get(TOTAL_INCOME).value == D("80000.00")
    for kind in (TOTAL_INCOME, NET_INCOME, TAXABLE_INCOME, REFUND_OR_BALANCE_OWING):
        assert with_memo.get(kind).value == without.get(kind).value, kind.identifier

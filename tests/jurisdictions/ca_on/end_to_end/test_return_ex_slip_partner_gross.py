"""CA-ON 2025 end to end: return ex, a rental partner who received a T5013 slip types a gross rent.

Guide T4036: a partner who received a T5013 slip fills in only the partnership business number,
the ownership percentage and amount 7 (and may adjust it by lines 9974 and 9943). A gross rent (the
Part 3 rows, line 8141) on that statement is refused, not totalled onto line 12599 (#881)."""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputOutOfRangeError
from tests.jurisdictions.ca_on.end_to_end.test_return_ex import RENTAL_ONE, RENTAL_TWO, run_ex

REFUSED = "rental_t5013_slip_conflict 1 is refused"


def test_a_gross_rent_on_a_slip_partners_statement_is_refused() -> None:
    # Statement 2 is a partnership with a slip (amount 7 of 9000); one row of rents of 1,000 is
    # entered on it too.
    statement = {**RENTAL_TWO, "rental_properties": ((1, "0", "1000"),)}

    with pytest.raises(InputOutOfRangeError, match=REFUSED):
        run_ex(rental_statements=(RENTAL_ONE, statement))


def test_a_gross_rent_on_a_partners_statement_without_a_slip_is_not_refused() -> None:
    # The Guide's fill-in-all-the-parts case: the same rents with the slip answer 0 are no conflict.
    statement = {
        **RENTAL_TWO,
        "rental_partner_t5013_slip": 0,
        "rental_partner_share": "0",
        "rental_partner_percentage": "50",
        "rental_properties": ((1, "0", "1000"),),
    }

    run_ex(rental_statements=(RENTAL_ONE, statement))

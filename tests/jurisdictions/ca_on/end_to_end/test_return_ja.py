"""CA-ON 2025 end to end: return ja, the journalism credit read from the T2125 statements.

Return JA is `returns/2025_return_ja.yaml`: a filer whose only income is the business income of two
Form T2125 statements of partnerships, each with amount 5B, the Canadian journalism labour tax
credit allocated to the filer (box 236 of the T5013 slip), of $1,000 and $500. Amount 5B is also
business income (the T1 guide's line 47555 note), so line 162 (47555) is the total of the
statements' 5B, $1,500, and the return has no input for it. A return with no statement has a
credit of 0.

The tests read the credit from the statements, trace it as the total of its items, and show that
the credit is refunded because nothing else is payable. Figures are Return JA's, worked out in its
description.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping, Sequence
from typing import Any

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    BUSINESS_INCOME,
    BUSINESS_PARTNERSHIP_TOTAL,
    JOURNALISM_LABOUR_TAX_CREDIT,
    NET_INCOME,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# Return JA's two statements: a partnership (partner count 1, its share from the T5013 slip 0) whose
# only amount is amount 5B.
JA_STATEMENTS = (
    {"business": {"journalism_labour_tax_credit": "1000"}, "business_partner": 1},
    {"business": {"journalism_labour_tax_credit": "500"}, "business_partner": 1},
)


def inputs(**overrides: Any) -> tuple[Artifact[Any], ...]:
    """The inputs of return JA (no employment, the two statements), `overrides` over them."""
    given: dict[str, Any] = {
        "business_statements": JA_STATEMENTS,
        "resident_in_canada_throughout_2025": 1,
        "aged_18_or_older_at_end_of_2025": 1,
        "cpp_months": 12,
        "qpp_months": 12,
    }
    return starting("0", (), "0", "0", "0", "0", "0", **{**given, **overrides})


def results(**overrides: Any) -> Mapping[str, Sequence[Worksheet]]:
    return service().compute(CA_ON, 2025, *inputs(**overrides))


def return_ja(**overrides: Any) -> Worksheet:
    return results(**overrides)["ca-on/return"][0]


def render(worksheet: Worksheet) -> str:
    return "\n".join(EnglishTraceRenderer().render_all(worksheet.trace))


def test_the_credit_is_not_an_input_of_the_return() -> None:
    # The credit is read from the statements' amount 5B, so no `starting` input carries it.
    assert "journalism_labour_tax_credit" not in inspect.signature(starting).parameters
    assert "ca/journalism_labour_tax_credit" not in {
        artifact.kind.identifier for artifact in inputs()
    }


def test_line_162_is_the_total_of_the_two_statements_amount_5b() -> None:
    assert return_ja().get(JOURNALISM_LABOUR_TAX_CREDIT).value == D("1500")


def test_the_total_is_traced_as_the_two_items_of_amount_5b() -> None:
    rendered = render(return_ja())

    assert (
        "journalism_labour_tax_credit: item 1 business_journalism_labour_tax_credit 1000 "
        "+ item 2 business_journalism_labour_tax_credit 500 = 1500"
    ) in rendered


def test_each_statement_is_business_income_on_its_own_and_so_is_the_credit() -> None:
    # Each statement's line 9946 is its amount 5B (no gross, no expenses, no partner share).
    found = results()

    assert found["ca/t2125"][0].get(BUSINESS_PARTNERSHIP_TOTAL).value == D("1000")
    assert found["ca/t2125"][0].get(BUSINESS_INCOME).value == D("1000")
    assert found["ca/t2125"][1].get(BUSINESS_PARTNERSHIP_TOTAL).value == D("500")
    assert found["ca/t2125"][1].get(BUSINESS_INCOME).value == D("500")


def test_the_credit_adds_to_net_income_and_is_refunded_in_full() -> None:
    worksheet = return_ja()

    assert worksheet.get(TOTAL_INCOME).value == D("1500.00")
    assert worksheet.get(NET_INCOME).value == D("1500.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("0.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("1500.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1500.00")
    assert worksheet.get(REFUND).value == D("1500.00")


def test_with_no_statement_the_credit_on_line_162_is_0() -> None:
    worksheet = return_ja(business_statements=None)

    assert worksheet.get(JOURNALISM_LABOUR_TAX_CREDIT).value == D("0")
    assert worksheet.get(TOTAL_INCOME).value == D("0")
    assert worksheet.get(REFUND).value == D("0")

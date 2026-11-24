"""The British Columbia return summary carries one marginal rate, `ca-bc/marginal_tax_rate`.

The kind is the province's name for the common output `marginal_tax_rate` (one name in every
province), a non-negative decimal amount in the `core/percent` unit. The rate is not printed on any
form, so its step has no title and no line reference, and the return summary prints it as a
percentage. It is the last figure of the return's trace, after every part it sums. Its values are
in `test_return_marginal_tax_rate_values.py`, its gates in
`test_return_marginal_tax_rate_gates.py`, and the check against two runs of the engine in
`test_return_marginal_tax_rate_extra_run.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.kinds import bundled_kinds, non_negative

D = Decimal
MARGINAL = "ca-bc/marginal_tax_rate"
RATE_KINDS = [
    MARGINAL,
    "ca-bc/british_columbia_marginal_rate",
    "ca-bc/marginal_net_income_rate",
    "ca-bc/marginal_credit_contribution_rate",
    "ca-bc/marginal_federal_rate",
    "ca-bc/marginal_contribution_rate",
    "ca-bc/marginal_british_columbia_credit_rate",
    "ca-bc/marginal_british_columbia_contribution_credit_rate",
    "ca-bc/marginal_british_columbia_bracket_rate",
    "ca-bc/marginal_british_columbia_rate_after_credits",
    "ca-bc/marginal_british_columbia_reduction_rate",
    "ca-bc/british_columbia_bracket_rate_with_reduction",
]


def _summary(salary: str) -> Worksheet:
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(
            JurisdictionCode("CA-BC"), 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),)
        )
    )
    (summary,) = worksheets["ca-bc/return"]
    return summary


@pytest.mark.parametrize("name", RATE_KINDS)
def test_the_rate_kinds_are_non_negative_decimal_amounts(name: str) -> None:
    kind = bundled_kinds().kind(name)

    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_marginal_rate_is_a_percentage_with_no_title_and_no_reference() -> None:
    summary = _summary("70000")
    label = bundled_kinds().kind(MARGINAL).label
    unit = summary.unit(label)

    assert unit is not None
    assert unit.identifier == "core/percent"
    assert summary.title(label) is None
    assert summary.reference(label) is None


def test_the_marginal_rate_is_not_rounded() -> None:
    value = _summary("30000").get(bundled_kinds().kind(MARGINAL)).value

    assert value == D("0.29189796")


def test_the_marginal_rate_is_the_last_figure_of_the_trace() -> None:
    summary = _summary("100000")
    labels = [line.label for line in summary.trace]
    label = bundled_kinds().kind(MARGINAL).label

    assert labels.count(label) == 1
    assert labels[-1] == label

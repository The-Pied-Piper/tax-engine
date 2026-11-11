"""Unit tests for the English text of the federal Canada trace lines, with made-up kinds."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import ContributionTier
from tax_engine.jurisdictions.ca.trace import AmountByCountLine, ContributionTierLine

D = Decimal
OUT = AmountKind("ex/contribution")
EARNINGS = AmountKind("ex/earnings")
CHILDREN = CountKind("ex/children")
CENT = RoundTo(increment=D("0.01"), mode=RoundingMode.HALF_UP)


def test_a_contribution_tier() -> None:
    tier = ContributionTier(Rate(D("0.0595")), D("3500"), D("68500"), D("3867.50"))
    line = ContributionTierLine(OUT, EARNINGS, D("80000"), tier, CENT, D("65000"), D("3867.50"))

    assert EnglishTraceRenderer().render(line) == (
        "5.95% of the part of earnings (80000.00) between 3500.00 and 68500.00, which is "
        "65000.00, at most 3867.50, gives 3867.50 (rounded to the nearest cent)."
    )


def test_an_amount_by_count() -> None:
    line = AmountByCountLine(OUT, CHILDREN, 3, D("1200"), NO_ROUNDING, D("1200"))

    assert EnglishTraceRenderer().render(line) == (
        "The table amount for children (3) is 1200.00 (not rounded)."
    )

"""The 2026 `ca/cwb_maximum` dataset: 1,665 (single filer).

Provisional, from the CRA page "Indexation adjustment for personal income tax and benefit
amounts", until the 2026 Schedule 6 is published.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
PROVISIONAL_HEADER = (
    '# Provisional: taken from the CRA page "Indexation adjustment for personal income tax and '
    'benefit amounts" (2026); to be confirmed against the 2026 form text when CRA publishes it.'
)
CRA_PAGE = "https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/adjustment-personal-income-tax-benefit-amounts.html"


def test_2026_cwb_maximum() -> None:
    data = SOURCE.get("ca/cwb_maximum", 2026, CREDIT)

    assert data.values == Credit(amount=D("1665"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_PAGE,)
    assert data.tax_year == 2026


def test_2026_cwb_maximum_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (root / "parameters" / "cwb_maximum" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER

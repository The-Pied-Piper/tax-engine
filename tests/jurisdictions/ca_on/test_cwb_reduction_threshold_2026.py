"""The 2026 `ca/cwb_reduction_threshold` dataset: 27,392 (single filer).

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
CRA_PAGE = "https://www.canada.ca/en/revenue-agency/services/tax/individuals/frequently-asked-questions-individuals/adjustment-personal-income-tax-benefit-amounts.html"


def test_2026_cwb_reduction_threshold() -> None:
    data = SOURCE.get("ca/cwb_reduction_threshold", 2026, CREDIT)

    assert data.values == Credit(amount=D("27392"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_PAGE,)
    assert data.tax_year == 2026


def test_2026_cwb_reduction_threshold_is_a_provisional_file() -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (root / "parameters" / "cwb_reduction_threshold" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER

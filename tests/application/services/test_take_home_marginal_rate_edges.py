"""The take-home marginal rate at the exact edges of the 2026 CPP bands and the federal taper.

At exactly $74,600 (the CPP base ceiling and the start of the second additional band) and at
exactly $259,609 (the end of the federal basic personal amount taper), a contribution tier reads
the band it starts and a bracket or taper reads the band below, so the rate matches the cent
either side where the same figure applies (ticket #1975). Salary only, single, include_rates.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_take_home
from tax_engine.application.models.take_home_request import TakeHomeRequest
from tax_engine.application.services.take_home import TakeHomeService
from tax_engine.domain.jurisdiction_code import JurisdictionCode


@pytest.fixture(scope="module")
def service() -> TakeHomeService:
    return build_take_home()


@pytest.mark.parametrize(
    ("code", "salary", "rate"),
    [
        ("CA-ON", "74599.99", "0.3436"),
        ("CA-ON", "74600", "0.3246"),
        ("CA-ON", "74600.01", "0.3246"),
        ("CA-ON", "259608.99", "0.4982"),
        ("CA-ON", "259609", "0.4982"),
        ("CA-ON", "259609.01", "0.5353"),
        ("CA-QC", "74599.99", "0.4182"),
        ("CA-QC", "74600", "0.3905"),
        ("CA-QC", "74600.01", "0.3905"),
        ("CA-QC", "259608.99", "0.5021"),
        ("CA-QC", "259609", "0.5021"),
        ("CA-QC", "259609.01", "0.5331"),
    ],
)
def test_the_marginal_rate_at_an_edge_matches_the_cent_either_side(
    service: TakeHomeService, code: str, salary: str, rate: str
) -> None:
    got = service.compute(
        TakeHomeRequest(JurisdictionCode(code), 2026, Decimal(salary), include_rates=True)
    )

    assert got.marginal_tax_rate is not None
    assert got.marginal_tax_rate.value == Decimal(rate)

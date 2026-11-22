"""The services implement the inbound ports, and take-home depends on the calculation port."""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_take_home, build_tax_computation
from tax_engine.adapters.inbound.take_home_text import EnglishTakeHomeText
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.models.calculation_result import TaxCalculationResult
from tax_engine.application.models.take_home_request import TakeHomeRequest
from tax_engine.application.ports.take_home_calculation import TakeHomeCalculation
from tax_engine.application.ports.tax_calculation import TaxCalculation
from tax_engine.application.services.take_home import TakeHomeService
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units

ON = JurisdictionCode("CA-ON")


def test_the_services_are_the_ports_the_factory_builds() -> None:
    calculation: TaxCalculation = build_tax_computation()
    take_home: TakeHomeCalculation = build_take_home()
    assert calculation is not None
    assert take_home.compute(TakeHomeRequest(ON, 2025, Decimal(70000))).take_home == Decimal(
        "53468.68"
    )


class _Counting:
    """A TaxCalculation that passes each request on and counts them."""

    def __init__(self, inner: TaxCalculation) -> None:
        self._inner = inner
        self.requests: list[TaxCalculationRequest] = []

    def compute(self, request: TaxCalculationRequest) -> TaxCalculationResult:
        self.requests.append(request)
        return self._inner.compute(request)


def test_take_home_computes_through_the_calculation_port() -> None:
    counting = _Counting(build_tax_computation())
    service = TakeHomeService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()),
        counting,
        EnglishTakeHomeText(),
    )
    service.compute(TakeHomeRequest(ON, 2025, Decimal(70000)))
    (request,) = counting.requests
    assert (request.jurisdiction, request.tax_year) == (ON, 2025)

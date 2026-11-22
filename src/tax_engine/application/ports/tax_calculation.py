"""Inbound port: running the forms of a return for a request."""

from __future__ import annotations

from typing import Protocol

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.models.calculation_result import TaxCalculationResult


class TaxCalculation(Protocol):
    def compute(self, request: TaxCalculationRequest) -> TaxCalculationResult:
        """The worksheets of every form, by form name, from the request's artifacts.

        The artifacts are one of each declared input kind, among them each form's instances. An
        optional input left out, or given blank where its default is a value, is read as its
        manifest default; a required one left out is refused, naming it. Each form has one
        worksheet per instance, in instance order.
        """
        ...

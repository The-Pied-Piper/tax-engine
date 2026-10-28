"""Tax computation engine and jurisdiction implementations."""

from tax_calculator.application.services.tax_computation import TaxComputationService
from tax_calculator.factory import build_tax_computation

__all__ = ["TaxComputationService", "build_tax_computation"]

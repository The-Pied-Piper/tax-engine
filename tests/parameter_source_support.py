"""Test support: parameter datasets written to disk and read through YamlParameterSource.

Values are made up. The datasets here are used by more than one layer's tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.parameter_parsers.amount_by_count import AmountByCountParser
from tax_engine.jurisdictions.ca.parameter_parsers.claim_reduction import ClaimReductionParser
from tax_engine.jurisdictions.ca.parameter_parsers.contribution_tier import (
    ContributionTierParser,
)
from tax_engine.jurisdictions.ca.parameter_parsers.taper import TaperParser
from tax_engine.jurisdictions.ca.parameter_parsers.year_amounts import YearAmountsParser
from tax_engine.jurisdictions.core.parameter_parsers.amount import AmountParser
from tax_engine.jurisdictions.core.parameter_parsers.brackets import BracketsParser
from tax_engine.jurisdictions.core.parameter_parsers.class_rates import ClassRatesParser
from tax_engine.jurisdictions.core.parameter_parsers.conditions import ConditionsParser
from tax_engine.jurisdictions.core.parameter_parsers.credit import CreditParser
from tax_engine.jurisdictions.core.parameter_parsers.factor import FactorParser
from tax_engine.jurisdictions.core.parameter_parsers.fraction import FractionParser
from tax_engine.jurisdictions.core.parameter_parsers.rate import RateParser
from tax_engine.jurisdictions.core.parameter_parsers.rate_table import RateTableParser
from tax_engine.jurisdictions.core.parameter_parsers.rounding_only import RoundingOnlyParser
from tax_engine.jurisdictions.core.parameter_parsers.surcharge_tiers import SurchargeTiersParser
from tax_engine.jurisdictions.core.parameter_parsers.threshold_rate import ThresholdRateParser

D = Decimal


def core_parsers() -> ParameterParserRegistry:
    """A fresh registry holding the core parsers, never the shared one."""
    registry = ParameterParserRegistry()
    registry.register_class(BracketsParser)
    registry.register_class(CreditParser)
    registry.register_class(RateParser)
    registry.register_class(AmountParser)
    registry.register_class(ThresholdRateParser)
    registry.register_class(SurchargeTiersParser)
    registry.register_class(FactorParser)
    registry.register_class(FractionParser)
    registry.register_class(RateTableParser)
    registry.register_class(ConditionsParser)
    registry.register_class(RoundingOnlyParser)
    registry.register_class(ClassRatesParser)
    return registry


def ca_parsers() -> ParameterParserRegistry:
    """A fresh registry holding the core parsers and the Canada-only parsers."""
    registry = core_parsers()
    registry.register_class(ClaimReductionParser)
    registry.register_class(YearAmountsParser)
    registry.register_class(ContributionTierParser)
    registry.register_class(TaperParser)
    registry.register_class(AmountByCountParser)
    return registry


BRACKETS_2025 = """\
family: ex/brackets
tax_year: 2025
kind: brackets
sources:
  - https://example.org/rates-2025
rounding: none
tax_at_start_rounding: none
brackets:
  - {from: "0", rate: "0.10"}
  - {from: "100", rate: "0.20"}
"""


CREDIT_2025 = """\
family: ex/personal_credit
tax_year: 2025
kind: credit
sources:
  - https://example.org/credits-2025
rounding: none
amount: "1000"
"""


RATE_2025 = """\
family: ex/credit_rate
tax_year: 2025
kind: rate
sources:
  - https://example.org/credit-rate-2025
rounding: none
rate: "0.125"
"""


AMOUNT_2025 = """\
family: ex/amount_cap
tax_year: 2025
kind: amount
sources:
  - https://example.org/amount-cap-2025
rounding: none
amount: "1471"
"""


EX = Namespace("ex")


def roots(directory: Path) -> Mapping[Namespace, Path]:
    """One made-up package, namespace `ex`, whose directory is `<directory>/ex`."""
    return {EX: directory / "ex"}


def write(directory: Path, relative: str, content: str) -> None:
    path = directory / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content), encoding="utf-8")

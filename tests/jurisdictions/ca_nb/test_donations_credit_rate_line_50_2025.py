"""The 2025 `ca-nb/donations_credit_rate_line_50` dataset, Form NB428 (5004-c-25e.txt) line 50:
"Line 50: Amount from line 13 of your federal Schedule 9 multiplied by 9.4% ="

Rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
NEW_BRUNSWICK_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_nb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-nb"): NEW_BRUNSWICK_DIR}, PARAMETER_PARSERS)


def test_2025_donations_credit_rate_line_50_is_0_094() -> None:
    data = SOURCE.get("ca-nb/donations_credit_rate_line_50", 2025, RATE)

    assert data.values == Rate(D("0.094"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)

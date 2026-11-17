"""The 2025 `ca-mb/cent_rounding` dataset: the one rule shared by every Manitoba step that rounds
a dollars-and-cents box of MB428 (5007-C), the MB428 worksheet (5007-D), Schedule MB428-A (5007-A)
and MB479 (5007-TC). It carries nothing but its rule, half-up to the cent. It cites the four form
texts."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions
import tax_engine.jurisdictions.core
from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.registry import Namespace

MANITOBA_DIR = Path(tax_engine.jurisdictions.__path__[0]) / "ca_mb"
PARAMETER_PARSERS = ParameterParserRegistry()
JurisdictionPackages((tax_engine.jurisdictions.core,)).register_parameter_parsers(PARAMETER_PARSERS)
SOURCE = YamlParameterSource({Namespace("ca-mb"): MANITOBA_DIR}, PARAMETER_PARSERS)
FAMILY = "ca-mb/cent_rounding"


def test_2025_cent_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_cent_rounding_cites_the_mb428_worksheet_schedule_and_mb479_text() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-d/5007-d-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-a/5007-a-25e.txt",
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-tc/5007-tc-25e.txt",
    )

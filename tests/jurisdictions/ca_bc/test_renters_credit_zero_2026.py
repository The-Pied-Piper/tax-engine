"""The 2026 `ca-bc/renters_credit_zero` dataset
(Form BC479 line 44's printed zero),
carried from 2025 (provisional)."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/renters_credit_zero"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-tc/5010-tc-25e.txt"


def test_2026_renters_credit_zero_is_the_printed_figure() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=Decimal("0"))


def test_2026_renters_credit_zero_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2026_renters_credit_zero_cites_the_bc479_text() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2026_renters_credit_zero_says_in_its_header_that_it_is_provisional() -> None:
    text = (
        Path(tax_engine.jurisdictions.ca_bc.__file__).parent
        / "parameters"
        / FAMILY.split("/")[1]
        / "2026.yaml"
    ).read_text(encoding="utf-8")

    assert text.startswith("# Provisional: taken from the 2025 form text")
    assert "# Derivation: carried forward unchanged from the 2025 file" in text

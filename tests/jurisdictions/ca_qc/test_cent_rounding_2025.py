"""The 2025 `ca-qc/cent_rounding` dataset: the one rule shared by every Quebec step that rounds a
dollars-and-cents box of the two returns, CRA 5005-R and Revenu Quebec TP-1.D-V. It carries
nothing but its rule, half-up to the cent, because neither form states a rounding rule. It cites
both printed forms."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/cent_rounding"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-r/5005-r-25e.txt"
REVENU_QUEBEC_FORM = "Revenu Quebec TP-1.D-V (2025-12)"


def test_2025_cent_rounding_is_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_cent_rounding_rounds_half_a_cent_up_and_less_down() -> None:
    rounding = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY).rounding

    assert rounding.apply(D("0.005")) == D("0.01")
    assert rounding.apply(D("0.004")) == D("0.00")


def test_2025_cent_rounding_cites_both_printed_forms() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.sources == (CRA_FORM_TEXT, REVENU_QUEBEC_FORM)

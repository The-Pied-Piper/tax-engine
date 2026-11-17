"""The 2025 `ca-mb/exact_rounding` dataset: the rule of a Manitoba figure that is not a
dollars-and-cents box, so nothing is rounded (`rounding: none`). Worksheet MB428 (5007-D) line 6,
line 4 divided by line 5, uses it: the form prints no rounding for that ratio and line 4 over
200,000.00 always terminates, so the ratio is exact; line 8 later rounds the product to the cent.
The cent rule of `ca-mb/cent_rounding` must not touch it."""

from __future__ import annotations

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/exact_rounding"
YEAR = 2025


def test_the_exact_rounding_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == NO_ROUNDING
    assert data.tax_year == YEAR


def test_the_exact_rounding_cites_the_mb428_worksheet_text() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-d/5007-d-25e.txt",
    )

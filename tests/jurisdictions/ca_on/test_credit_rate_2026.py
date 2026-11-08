"""The 2026 rate of `ca/credit_rate`, taken from T4127 (122nd edition, January 2026).

T4127: "For 2026 and subsequent tax years, the lowest federal tax bracket will be 14%." The
credit rate is that lowest rate, a flat 0.14 for the whole of 2026. The product with the credit
amounts is a dollars-and-cents box, so it rounds half-up to the cent, as in 2025. The dataset is
provisional until the 2026 form text is published.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/credit_rate"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"

# Made up for this test and not registered: the credit amounts and the credits they give.
AMOUNTS = AmountKind("ex/credit_amounts")
CREDITS = AmountKind("ex/credits")


def test_2026_credit_rate_is_14_percent() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.14"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_credit_rate_cites_t4127() -> None:
    assert SOURCE.get(FAMILY, 2026, RATE).sources == (T4127_URL,)


def test_2026_credit_rate_is_a_provisional_file() -> None:
    from importlib.resources import files

    path = files("tax_engine.jurisdictions.ca").joinpath("parameters/credit_rate/2026.yaml")

    assert path.read_text().startswith(
        "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
        "when CRA publishes it.\n"
    )


def test_2025_credit_rate_is_unchanged() -> None:
    assert SOURCE.get(FAMILY, 2025, RATE).values == Rate(D("0.145"))


def test_credits_at_the_2026_rate() -> None:
    # 16,452.00 + 1,501.00 = 17,953.00 of credit amounts x 14% = 2,513.42.
    capability = ApplyRate(SOURCE.get(FAMILY, 2026, RATE), base=AMOUNTS, output=CREDITS)

    result = capability.compute((Artifact(AMOUNTS, D("17953.00")),))

    assert result.outputs == (Artifact(CREDITS, D("2513.42")),)

"""The 2026 Ontario surtax datasets read together: tiers 5,818 at 20% and 7,446 at 36% (T4127, Jan
2026, Table 8.2 row ON and the Ontario V1 formula), at the edge figures of the ticket."""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.surcharge_tiers import SURCHARGE_TIERS
from tax_engine.jurisdictions.core.capabilities.tiered_surcharge import TieredSurcharge

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)

# Made up for this test and not registered: the surtax base and a tier's surtax.
BASE = AmountKind("ex/surtax_base")
PART = AmountKind("ex/surtax_part")


def surtax(family: str, base: str) -> Decimal:
    tiers = SOURCE.get(family, 2026, SURCHARGE_TIERS)
    (out,) = TieredSurcharge(tiers, BASE, PART).compute((Artifact(BASE, D(base)),)).outputs
    value: Decimal = out.value
    return value


@pytest.mark.parametrize(
    ("base", "line_66", "line_67"),
    [
        # Up to the first threshold: nothing.
        ("0", "0", "0"),
        ("5818", "0", "0"),
        # At 7,446: 0.20 x 1,628 = 325.60; the second tier is still 0.
        ("7446", "325.60", "0"),
        # At 10,000: 0.20 x 4,182 = 836.40 and 0.36 x 2,554 = 919.44, together 1,755.84.
        ("10000", "836.40", "919.44"),
    ],
)
def test_2026_surtax_tiers(base: str, line_66: str, line_67: str) -> None:
    assert surtax("ca-on/surtax_line_66", base) == D(line_66)
    assert surtax("ca-on/surtax_line_67", base) == D(line_67)


def test_2026_surtax_at_10000_is_1755_84() -> None:
    total = surtax("ca-on/surtax_line_66", "10000") + surtax("ca-on/surtax_line_67", "10000")

    assert total == D("1755.84")

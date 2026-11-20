"""The 2025 `ca-qc/work_chart_201_rate` dataset: the 6% of Work Chart 201 line 8.

Revenu Quebec TP-1.D.GR-V (2025-12), Work Chart "Deduction for workers": "x 6% Multiply line 8 by
6%." The 6% is a rate (the `rate` kind). The product is not rounded by the rate dataset; the
maximum on line 9 rounds it once.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.core.capabilities.apply_rate import ApplyRate
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/work_chart_201_rate"

# Made up for this test and not registered: line 8 (the base) and the product.
LINE_8 = AmountKind("ex/line_8")
PRODUCT = AmountKind("ex/product")


def test_2025_the_rate_is_6_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.06"))
    assert data.rounding == NO_ROUNDING


def test_2025_the_rate_cites_the_form() -> None:
    assert SOURCE.get(FAMILY, 2025, RATE).sources == ("Revenu Quebec TP-1.D.GR-V (2025-12)",)


@pytest.mark.parametrize(
    ("line_8", "product"),
    [
        ("20000.00", "1200.00"),
        ("70000.00", "4200.00"),
        ("0", "0.00"),
        # 0.10 x 6% = 0.006, not rounded here.
        ("0.10", "0.006"),
    ],
)
def test_6_percent_of_line_8_is_not_rounded(line_8: str, product: str) -> None:
    capability = ApplyRate(SOURCE.get(FAMILY, 2025, RATE), LINE_8, PRODUCT)

    result = capability.compute((Artifact(LINE_8, D(line_8)),))

    assert result.outputs == (Artifact(PRODUCT, D(product)),)

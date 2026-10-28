"""The 2025 Part 1 line 94 basic exemption of Form T691: 177,882.00, checked against Form T691. Form
T691 (2025) Part 1 line 94: "Basic exemption 177,882.00". The amount is a printed figure of the
form, so it is claimed whole (the `credit` kind), and the dollars-and-cents line is rounded half-
up to the cent, the owner's decision, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
FAMILY = "ca/amt_basic_exemption"
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the claimed amount the dataset gives.
CLAIMED = ArtifactKind("ex/amt_basic_exemption_claimed", Decimal)


def test_2025_basic_exemption_is_177882() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("177882.00"))
    # Part 1 line 94, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_basic_exemption_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert T691_PDF in data.sources


def test_the_basic_exemption_is_claimed_whole() -> None:
    capability = CreditAmount(SOURCE.get(FAMILY, 2025, CREDIT), CLAIMED)

    result = capability.compute(())

    assert result.outputs == (Artifact(CLAIMED, D("177882.00")),)

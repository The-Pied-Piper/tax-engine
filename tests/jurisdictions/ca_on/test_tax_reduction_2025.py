"""The 2025 Ontario basic tax reduction, checked against CRA's ON428.

2025 ON428 (form 5006-C), Ontario tax reduction: line 74 "Basic reduction 294.00". The basic
reduction is a claimed amount (the `credit` kind, as the basic personal amount), a dollars-and-cents
box, so rounded half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.core.capabilities.credit_amount import CreditAmount

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
BASIC = "ca-on/tax_reduction_basic"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the basic reduction as an artifact, a count and its
# per-unit amount, the reduction amounts (line 77), the tax they are set against (line 73) and the
# reduction (line 80).
BASIC_REDUCTION = AmountKind("ex/basic_reduction")
COUNT = CountKind("ex/count")
COUNT_AMOUNT = AmountKind("ex/count_amount")
AMOUNTS = AmountKind("ex/reduction_amounts")
TAX = AmountKind("ex/tax")
REDUCTION = AmountKind("ex/reduction")


def test_2025_basic_reduction_is_294() -> None:
    data = SOURCE.get(BASIC, 2025, CREDIT)

    assert data.values == Credit(amount=D("294.00"))
    # ON428 line 74, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_datasets_cite_only_the_on428_text() -> None:
    assert SOURCE.get(BASIC, 2025, CREDIT).sources == (ON428_TEXT,)


def test_the_basic_reduction_is_claimed_whole() -> None:
    capability = CreditAmount(SOURCE.get(BASIC, 2025, CREDIT), BASIC_REDUCTION)

    result = capability.compute(())

    assert result.outputs == (Artifact(BASIC_REDUCTION, D("294.00")),)

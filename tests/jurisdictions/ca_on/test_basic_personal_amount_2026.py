"""The 2026 federal basic personal amount, taken from T4127 (122nd edition, January 2026).

T4127, Federal Basic Personal Amount (BPAF) Formula: "Where NI* <= $181,440, BPAF = $16,452.
Where $181,440 < NI* < $258,482, BPAF** = $16,452 - (NI* - $181,440) x ($1,623 / $77,042).
Where NI* >= $258,482, BPAF = $14,829." So the amount is a taper (the `taper` kind): base 14,829,
supplement 1,623, threshold 181,440, range 77,042 (T4127's printed divisor, taken as printed). The
dataset is provisional until the 2026 T1 and Federal Worksheet are published.
"""

from __future__ import annotations

from decimal import Decimal
from importlib.resources import files

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.capabilities.tapered_amount import TaperedAmount
from tax_engine.jurisdictions.ca.parameter_shapes.taper import TAPER, Taper

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/basic_personal_amount"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"

# Made up for this test and not registered: the net income and the basic personal amount.
NET_INCOME = AmountKind("ex/net_income")
AMOUNT = AmountKind("ex/basic_personal_amount")


def test_2026_amount_is_the_t4127_taper() -> None:
    data = SOURCE.get(FAMILY, 2026, TAPER)

    assert data.values == Taper(
        base=D("14829"), supplement=D("1623"), threshold=D("181440"), range=D("77042")
    )
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_amount_is_16452_at_most_as_printed() -> None:
    taper = SOURCE.get(FAMILY, 2026, TAPER).values

    # T4127's "BPAF = $16,452" is the base plus the supplement; "BPAF = $14,829" is the base.
    assert taper.base + taper.supplement == D("16452")
    # The printed divisor 77,042 is taken as printed: 258,482 - 181,440 = 77,042 too.
    assert taper.threshold + taper.range == D("258482")


def test_2026_amount_cites_t4127() -> None:
    assert SOURCE.get(FAMILY, 2026, TAPER).sources == (T4127_URL,)


def test_2026_amount_is_a_provisional_file() -> None:
    path = files("tax_engine.jurisdictions.ca").joinpath(
        "parameters/basic_personal_amount/2026.yaml"
    )

    assert path.read_text().startswith(
        "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
        "when CRA publishes it.\n"
    )


def test_2025_amount_is_unchanged() -> None:
    assert SOURCE.get(FAMILY, 2025, TAPER).values == Taper(
        base=D("14538"), supplement=D("1591"), threshold=D("177882"), range=D("75532")
    )


@pytest.mark.parametrize(
    ("net_income", "amount"),
    [
        # A $70,000 salary: below the threshold, so the full 16,452.
        ("70000", "16452.00"),
        ("0", "16452.00"),
        # At the threshold, and a cent past it: 16,452 - 1,623 x 0.01 / 77,042 = 16,451.99978...,
        # half-up to 16,452.00.
        ("181440", "16452.00"),
        ("181440.01", "16452.00"),
        # The midpoint of the range: 16,452 - (38,521 x 1,623 / 77,042) = 15,640.50.
        ("219961", "15640.50"),
        # At threshold plus range the whole supplement is gone, and past it the amount stays 14,829.
        ("258482", "14829.00"),
        ("258482.01", "14829.00"),
        ("275000", "14829.00"),
    ],
)
def test_tapers_net_income(net_income: str, amount: str) -> None:
    capability = TaperedAmount(SOURCE.get(FAMILY, 2026, TAPER), NET_INCOME, AMOUNT)

    result = capability.compute((Artifact(NET_INCOME, D(net_income)),))

    assert result.outputs == (Artifact(AMOUNT, D(amount)),)

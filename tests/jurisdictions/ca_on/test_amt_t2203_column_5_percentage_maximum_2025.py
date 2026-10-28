"""The 2025 maximum of the Form T2203 column 5 percentage, checked against Form T691 and Form T2203.

Form T691 (2025) Part 3 line 3: "If you have to pay tax to multiple jurisdictions, multiply the
amount from line 2 by the percentage in Column 5 of line 52220 on Form T2203." The form prints no
maximum on that percentage: the largest share is the whole of the amount, 100 for 100% as the
percentage is entered (50 for 50%), a choice and not a form rule. The credit kind is used because
the figure is taken whole, as the basic personal amount is.
"""

from __future__ import annotations

import re
from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
T691_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t691/t691-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

FAMILY = "ca/amt_t2203_column_5_percentage_maximum"


def dataset_header() -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (
        (root / "parameters" / "amt_t2203_column_5_percentage_maximum" / "2025.yaml")
        .read_text()
        .splitlines()
    )
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return re.sub(r"\s+", " ", "\n".join(lines[:first_key]).replace("#", " ")).strip()


def test_2025_percentage_maximum_is_100() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    # The form prints no maximum: the largest percentage is the whole of the amount, 100 for 100%.
    assert data.values == Credit(amount=D("100"))
    assert data.rounding == CENT


def test_2025_percentage_maximum_cites_the_form_it_is_checked_on() -> None:
    assert T691_PDF in SOURCE.get(FAMILY, 2025, CREDIT).sources


def test_2025_percentage_maximum_header_quotes_line_3_and_says_the_limit_is_a_choice() -> None:
    header = dataset_header().lower()

    assert "percentage in column 5 of line 52220" in header
    assert "a choice" in header


def test_the_credit_amount_capability_gives_the_percentage_maximum_as_an_artifact() -> None:
    figure = ArtifactKind("ex/t2203_percentage_maximum", Decimal)
    capability = CreditAmount(SOURCE.get(FAMILY, 2025, CREDIT), figure)

    (output,) = capability.compute(()).outputs

    assert output.kind == figure
    assert output.value == D("100.00")

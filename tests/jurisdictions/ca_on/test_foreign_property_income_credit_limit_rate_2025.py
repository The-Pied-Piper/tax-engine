"""The 2025 limit on the foreign tax credit for income from property (Form T2209 page 1 note),
checked against CRA's form.

2025 Form T2209, Federal Foreign Tax Credits, page 1: "If you paid tax on income from property
sourced outside of Canada (other than real or immovable property), your non-business foreign tax
credit for that income cannot be more than 15% of your net income from that property. However,
you may be able to deduct the part of the foreign taxes you paid over 15% on line 23200 of your
return." The printed 15% is a `rate` dataset; the product is a dollars-and-cents amount, so it
rounds half-up to the cent, the owner's decision, as the form states no rounding rule. The form is
a PDF with no published .txt, so the dataset cites the PDF.
"""

from __future__ import annotations

import re
from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
LIMIT_RATE = "ca/foreign_property_income_credit_limit_rate"
T2209_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2209/t2209-25e.pdf"


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return re.sub(r"\s+", " ", "\n".join(lines[:first_key]).replace("#", " ")).strip()


def test_2025_property_income_limit_is_15_percent_half_up_to_the_cent() -> None:
    data = SOURCE.get(LIMIT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.15"))
    assert data.rounding == CENT
    assert data.sources == (T2209_PDF,)


def test_the_property_income_limit_header_quotes_the_t2209_note_as_the_form_prints_it() -> None:
    header = dataset_header(LIMIT_RATE)

    for quoted in (
        "If you paid tax on income from property sourced outside of Canada (other than real or "
        "immovable property), your non-business foreign tax credit for that income cannot be more "
        "than 15% of your net income from that property.",
        "you may be able to deduct the part of the foreign taxes you paid over 15% on line 23200 "
        "of your return.",
    ):
        assert quoted in header, quoted

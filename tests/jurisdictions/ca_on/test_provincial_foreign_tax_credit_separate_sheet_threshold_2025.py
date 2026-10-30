"""The 2025 separate sheet threshold of Form T2036, checked against Form T2036.

Form T2036 (2025), Provincial or Territorial Foreign Tax Credit: "If you paid tax to more than one
foreign country, and the total of the non-business income taxes that you paid to all foreign
countries was more than $200, do the calculation on a separate form for each country in Canadian
dollars." Line 2 "Enter the amount from line 3 of Form T2209, unless you have to pay minimum
tax.(1)" and note (1), for a resident of Ontario at the end of the year: "If the total
non-business income taxes you paid to all foreign countries is $200 or less:" line 1 of the form
over the sum of line 1 and line 8 of Part 4 of Form T691, times the special foreign tax credit on
line 11; "If the total non-business income taxes you paid to all foreign countries is more than
$200, you must calculate for each country:". The $200 is taken as printed, an `amount` dataset
of 200.
The form is a PDF with no published .txt, so the dataset cites the PDF.
"""

from __future__ import annotations

import re
from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T2036_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2036/t2036-25e.pdf"

FAMILY = "ca-on/provincial_foreign_tax_credit_separate_sheet_threshold"


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    name = family.removeprefix("ca-on/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_separate_sheet_threshold_is_200() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("200"))


def test_2025_separate_sheet_threshold_cites_only_the_t2036_pdf() -> None:
    assert SOURCE.get(FAMILY, 2025, AMOUNT).sources == (T2036_PDF,)


def test_the_header_quotes_t2036_as_the_form_prints_it() -> None:
    header = dataset_header(FAMILY)

    for quoted in (
        "and the total of the non-business income taxes that you paid to all foreign countries "
        "was more than $200, do the calculation on a separate form for each country in Canadian "
        "dollars.",
        "Enter the amount from line 3 of Form T2209, unless you have to pay minimum tax.(1)",
        "If the total non-business income taxes you paid to all foreign countries is $200 or less:",
        "If the total non-business income taxes you paid to all foreign countries is more than "
        "$200, you must calculate for each country:",
    ):
        assert quoted in header, quoted

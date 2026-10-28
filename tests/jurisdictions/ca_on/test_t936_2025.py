"""The 2025 datasets of Form T936, checked against CRA's form.

Form T936 (Calculation of Cumulative Net Investment Loss (CNIL) to December 31, 2025, 2025 edition,
`docs/cra-forms-2025/t936-25e.pdf`; no .txt is published):

- Part 1 line 5 "50% of exploration and development expenses (line 22400)";
- Part 2 line 12 "50% of income from the recovery of exploration and development expenses (line
  13000)";
- Chart A line 10 "Inclusion rate × 50%", then line 11 "Line 9 multiplied by the percentage on line
  10 (if negative, enter "0")";
- Chart A line 18 "Inclusion rate × 50%", then line 19 "Line 17 multiplied by the percentage on
  line 18".

Every one of these is a dollars-and-cents box, so each product rounds half-up to the cent, the
repo convention, as the form states no rounding rule. The four 50% rates are one dataset each,
because each is a printed figure of its own line.
"""

from __future__ import annotations

import re
from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T936_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t936/t936-25e.pdf"

# The form lines each dataset header quotes, lowercased as the header is compared. CRA publishes no
# .txt of T936, so the quotes are checked against the form lines as copied from the PDF.
HEADER_QUOTES = {
    "ca/t936_exploration_expenses_rate": (
        "50% of exploration and development expenses (line 22400)",
    ),
    "ca/t936_exploration_recovery_rate": (
        "50% of income from the recovery of exploration and development expenses (line 13000)",
    ),
    "ca/t936_chart_a_inclusion_rate": (
        "inclusion rate × 50%",
        "line 9 multiplied by the percentage on line 10",
    ),
    "ca/t936_t3_inclusion_rate": (
        "inclusion rate × 50%",
        "line 17 multiplied by the percentage on line 18",
    ),
}

# Made up for this test and not registered.
BASE = ArtifactKind("ex/base", Decimal)
PRODUCT = ArtifactKind("ex/product", Decimal)


@pytest.mark.parametrize("family", HEADER_QUOTES)
def test_2025_each_t936_rate_is_half_to_the_cent(family: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(D("0.5"))
    assert data.rounding == CENT


@pytest.mark.parametrize("family", HEADER_QUOTES)
def test_2025_each_t936_rate_cites_the_form(family: str) -> None:
    assert T936_PDF in SOURCE.get(family, 2025, RATE).sources


@pytest.mark.parametrize("family", HEADER_QUOTES)
def test_each_t936_rate_is_the_one_dataset_of_its_own_line(family: str) -> None:
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]

    assert (root / "parameters" / family.removeprefix("ca/") / "2025.yaml").is_file()


@pytest.mark.parametrize(
    ("base", "product"),
    [
        # Chart A line 9 of 680000, line 11 is half of it.
        ("680000", "340000"),
        # Rounded half-up to the cent: 1234.57 x 50% is 617.285, a tie, up to 617.29.
        ("1234.57", "617.29"),
        ("0", "0"),
    ],
)
@pytest.mark.parametrize("family", HEADER_QUOTES)
def test_each_t936_rate_gives_half_of_its_line_rounded_half_up(
    family: str, base: str, product: str
) -> None:
    capability = ApplyRate(SOURCE.get(family, 2025, RATE), BASE, PRODUCT)

    result = capability.compute((Artifact(BASE, D(base)),))

    assert result.outputs == (Artifact(PRODUCT, D(product)),)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


@pytest.mark.parametrize(("family", "quotes"), HEADER_QUOTES.items())
def test_the_dataset_header_quotes_t936_as_the_form_prints_it(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family).lower()

    for quoted in quotes:
        assert quoted in header, quoted


@pytest.mark.parametrize("family", HEADER_QUOTES)
def test_the_dataset_header_states_the_half_up_cent_rule(family: str) -> None:
    assert "half-up to the cent" in dataset_header(family)

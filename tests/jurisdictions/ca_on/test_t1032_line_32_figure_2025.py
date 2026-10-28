"""The 2025 figure of Form T1032 Part B line 32, `ca/t1032_line_32_figure`, checked against the
form.

Form T1032 E (25), Step 4 Part B, page 3: "If all of the following conditions apply, calculate line
33 according to the instructions in note 1: the amount on line 32 is less than $2,000". The $2,000
is the figure line 32 is compared with. The form states no rounding rule, so the figure rounds
half-up to the cent, the owner's decision, the repo convention. The dataset is the `credit` kind,
claimed whole by `core/credit_amount`.

Form T1032 is at https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt
"""

from __future__ import annotations

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
FIGURE = "ca/t1032_line_32_figure"
T1032_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for these tests and not registered: the artifact the figure is claimed as.
CLAIMED = ArtifactKind("ex/t1032_line_32_figure", Decimal)


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, whitespace squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (
        (root / "parameters" / family.removeprefix("ca/") / "2025.yaml").read_text().splitlines()
    )
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return " ".join(" ".join(lines[:first_key]).split())


def test_2025_line_32_figure_is_2000() -> None:
    data = SOURCE.get(FIGURE, 2025, CREDIT)

    assert data.values == Credit(amount=D("2000"))
    assert data.rounding == CENT


def test_2025_line_32_figure_cites_form_t1032_by_its_page_and_line() -> None:
    data = SOURCE.get(FIGURE, 2025, CREDIT)

    assert data.sources == (T1032_TXT,)
    header = dataset_header(FIGURE)
    assert "Form T1032 E (25)" in header
    assert "the amount on line 32 is less than $2,000" in header


def test_the_figure_is_claimed_whole_by_the_credit_amount_capability() -> None:
    capability = CreditAmount(SOURCE.get(FIGURE, 2025, CREDIT), CLAIMED)

    (output,) = capability.compute(()).outputs

    assert output.kind == CLAIMED
    assert output.value == D("2000.00")

"""The 2025 ceiling of Form T1032 lines 5 and 13, `ca/t1032_rca_and_veterans_ceiling`, checked
against the printed form.

Form T1032 E (25), Step 2 "Calculate the maximum split-pension amount", page 2: "Line 5: 131,483.45"
for the retirement compensation arrangement calculation (lines 4 to 8) and "Line 13: 131,483.45" for
the veterans benefits calculation (lines 9 to 16), printed the same on both lines. The form states
no rounding rule, so the figure rounds half-up to the cent, the owner's decision, the repo
convention. The dataset is the `credit` kind, claimed whole by `core/credit_amount`.

Form T1032 is at https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CEILING = "ca/t1032_rca_and_veterans_ceiling"
T1032_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for these tests and not registered: the line the ceiling is checked against and the
# checked output.
AMOUNT = ArtifactKind("ex/t1032_line_3", Decimal)
BOUND = ArtifactKind("ex/t1032_ceiling", Decimal)
CHECKED = ArtifactKind("ex/t1032_line_checked", Decimal)


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, whitespace squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (
        (root / "parameters" / family.removeprefix("ca/") / "2025.yaml").read_text().splitlines()
    )
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return " ".join(" ".join(lines[:first_key]).split())


def ceiling() -> tuple[Artifact[Decimal], ...]:
    capability = CreditAmount(SOURCE.get(CEILING, 2025, CREDIT), BOUND)
    return capability.compute(()).outputs


def test_2025_rca_and_veterans_ceiling_is_131483_45() -> None:
    data = SOURCE.get(CEILING, 2025, CREDIT)

    assert data.values == Credit(amount=D("131483.45"))
    assert data.rounding == CENT


def test_2025_rca_and_veterans_ceiling_cites_form_t1032_by_its_page_and_lines() -> None:
    data = SOURCE.get(CEILING, 2025, CREDIT)

    assert data.sources == (T1032_TXT,)
    header = dataset_header(CEILING)
    assert "Form T1032 E (25)" in header
    assert "Line 5" in header
    assert "Line 13" in header


def test_the_ceiling_is_quoted_as_printed_on_lines_5_and_13() -> None:
    assert "131,483.45" in dataset_header(CEILING)


def test_the_ceiling_is_claimed_whole_by_the_credit_amount_capability() -> None:
    (output,) = ceiling()

    assert output.kind == BOUND
    assert output.value == D("131483.45")


def test_a_line_at_the_ceiling_is_accepted_as_it_is() -> None:
    (bound,) = ceiling()

    result = AtMost(AMOUNT, BOUND, CHECKED).compute((Artifact(AMOUNT, D("131483.45")), bound))

    assert result.outputs == (Artifact(CHECKED, D("131483.45")),)


def test_a_line_one_cent_above_the_ceiling_is_refused_not_capped() -> None:
    (bound,) = ceiling()

    with pytest.raises(InputAboveBoundError):
        AtMost(AMOUNT, BOUND, CHECKED).compute((Artifact(AMOUNT, D("131483.46")), bound))

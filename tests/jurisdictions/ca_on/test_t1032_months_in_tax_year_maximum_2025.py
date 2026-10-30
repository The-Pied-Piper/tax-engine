"""The 2025 months in the tax year of Form T1032 line 18, `ca/t1032_months_in_tax_year_maximum`,
checked against the printed form.

Form T1032 E (25), Step 2, page 2: "Divided by Number of months in the tax year (12) (Note 1)",
where
Note 1 replaces the 12 with the number of months up to and including the month of death for a
deceased transferring spouse. The 12 is the most the denominator of line 18 can be; a larger
denominator is refused, not capped, as the form prints no bound on it. The figure is a count of
months, claimed whole by `core/credit_amount`, as the other printed maxima are.

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
MONTHS_MAXIMUM = "ca/t1032_months_in_tax_year_maximum"
T1032_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for these tests and not registered: the months entered, the ceiling and the checked
# output.
MONTHS = ArtifactKind("ex/t1032_months_in_tax_year", Decimal)
BOUND = ArtifactKind("ex/t1032_months_in_tax_year_ceiling", Decimal)
CHECKED = ArtifactKind("ex/t1032_months_in_tax_year_checked", Decimal)


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, whitespace squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (
        (root / "parameters" / family.removeprefix("ca/") / "2025.yaml").read_text().splitlines()
    )
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return " ".join(" ".join(lines[:first_key]).split())


def maximum() -> Artifact[Decimal]:
    (output,) = CreditAmount(SOURCE.get(MONTHS_MAXIMUM, 2025, CREDIT), BOUND).compute(()).outputs
    return output


def test_2025_months_in_tax_year_maximum_is_12() -> None:
    data = SOURCE.get(MONTHS_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("12"))
    assert data.rounding == CENT


def test_2025_months_in_tax_year_maximum_cites_form_t1032_line_18() -> None:
    data = SOURCE.get(MONTHS_MAXIMUM, 2025, CREDIT)

    assert data.sources == (T1032_TXT,)
    header = dataset_header(MONTHS_MAXIMUM)
    assert "Form T1032 E (25)" in header
    assert "Line 18" in header
    assert "(12)" in header


def test_the_months_maximum_is_claimed_whole_by_the_credit_amount_capability() -> None:
    assert maximum() == Artifact(BOUND, D("12"))


@pytest.mark.parametrize("months", ["0", "5", "12"])
def test_a_months_count_up_to_the_maximum_is_accepted_as_it_is(months: str) -> None:
    result = AtMost(MONTHS, BOUND, CHECKED).compute((Artifact(MONTHS, D(months)), maximum()))

    assert result.outputs == (Artifact(CHECKED, D(months)),)


def test_a_months_count_of_13_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        AtMost(MONTHS, BOUND, CHECKED).compute((Artifact(MONTHS, D("13")), maximum()))

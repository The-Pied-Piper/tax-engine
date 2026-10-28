"""The 2025 short-year figure of the immediate expensing limit, checked against the Regulations.

Income Tax Regulations, subsection 1104(3.5), paragraph (b): "where an eligible person or
partnership has a taxation year that is less than 51 weeks, its immediate expensing limit for the
year is that proportion of its immediate expensing limit for the year determined without reference
to this paragraph that the number of days in the year is of 365". The 51 weeks are the figure the
Regulations print, taken as printed: 51 weeks of 7 days is 357 days, so a year of 357 days or more
is not prorated and a year of 356 days or fewer is. Guides T4002 and T4036, "Immediate expensing
incentive", say only "The limit is also prorated for tax years shorter than 365 days"; the
Regulations decide over the guides on this point.

The figure is a credit dataset like the immediate expensing cap datasets, so it rounds half-up to
the cent by the dataset's rule. It is tested with the credit amount capability that produces it,
on a made-up kind.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.capabilities.credit_amount import CreditAmount
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
SHORT_YEAR_DAYS = "ca/immediate_expensing_short_year_days"
REGULATIONS = "https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.,_c._945/section-1104.html"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the figure a credit dataset gives.
FIGURE = ArtifactKind("ex/printed_figure", Decimal)


def test_2025_short_year_days_is_357() -> None:
    data = SOURCE.get(SHORT_YEAR_DAYS, 2025, CREDIT)

    # 1104(3.5)(b) "less than 51 weeks": 51 weeks of 7 days, 357 days, is not less than 51 weeks.
    assert data.values == Credit(amount=D("357"))
    assert data.rounding == CENT


def test_2025_short_year_days_is_51_weeks_of_7_days() -> None:
    data = SOURCE.get(SHORT_YEAR_DAYS, 2025, CREDIT)

    assert data.values.amount == D("51") * D("7")


def test_2025_short_year_days_cites_the_regulations_it_is_printed_in() -> None:
    assert SOURCE.get(SHORT_YEAR_DAYS, 2025, CREDIT).sources == (REGULATIONS,)


def test_the_credit_amount_capability_gives_the_printed_figure() -> None:
    capability = CreditAmount(SOURCE.get(SHORT_YEAR_DAYS, 2025, CREDIT), FIGURE)

    (output,) = capability.compute(()).outputs

    assert output.kind == FIGURE
    assert output.value == D("357")

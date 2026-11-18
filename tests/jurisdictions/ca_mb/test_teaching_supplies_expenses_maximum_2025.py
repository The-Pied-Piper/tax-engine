"""The 2025 amount of `ca-mb/teaching_supplies_expenses_maximum`, checked against Form MB479
(5007-TC, 2025).

Form MB479, line 79: "Teaching expense tax credit: Line 79: Eligible teaching supplies expenses
(maximum $1,000) Line 61495 ^ multiplied by 15%". The maximum is printed, so the dataset holds it
as printed, bounding the entry: the `credit` kind, as `ca-mb/employee_share_purchase_credit_maximum`
is.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/teaching_supplies_expenses_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-tc/5007-tc-25e.txt"


def test_2025_teaching_supplies_expenses_maximum_is_1000() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("1000"))


def test_2025_teaching_supplies_expenses_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_teaching_supplies_expenses_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)

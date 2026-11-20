"""The 2025 `ca-qc/brackets_work_chart_401` dataset, taken from Revenu Quebec Work Chart 401
(TP-1.D.GR-V, 2025-12), "Income tax on taxable income".

Form text: the four columns A to D, chosen by "is $53,255 or less", "is more than $53,255 but not
more than $106,495", "is more than $106,495 but not more than $129,590" and "is more than
$129,590"; in each, line 3 the lower bound (0 00, 53,255 00, 106,495 00, 129,590 00), line 5 the
rate (14%, 19%, 24%, 25.75%) and line 7 the amount (0 00, 7,455 70, 17,571 30, 23,114 10).

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
amount (line 7), carried as printed. The dataset has no rounding rule; the take-home build rounds
the dollars-and-cents boxes in its own parts. There is no upper end: column D is open.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/brackets_work_chart_401"
FORM = "Revenu Quebec TP-1.D.GR-V (2025-12), Work Chart 401"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_four_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.14"), D("0.00")),
        (D("53255.00"), D("0.19"), D("7455.70")),
        (D("106495.00"), D("0.24"), D("17571.30")),
        (D("129590.00"), D("0.2575"), D("23114.10")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_the_chart() -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).sources == (FORM,)


def test_2025_brackets_have_no_upper_end() -> None:
    assert _schedule().up_to is None


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("18635.00", "0.00"),
        ("53255.00", "0.00"),
        ("53255.01", "53255.00"),
        ("67915.00", "53255.00"),
        ("106495.00", "53255.00"),
        ("106495.01", "106495.00"),
        ("129590.00", "106495.00"),
        ("129590.01", "129590.00"),
        ("197506.00", "129590.00"),
    ],
)
def test_the_column_is_the_one_the_instructions_print_for_the_amount(
    amount: str, lower: str
) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)

"""2025 `ca-sk/brackets`, checked against Form SK428 (CRA 5008-c, 2025), Part A.

Form text (read 2026-11-14, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt):
"Column 1: Line 1 is $53,463 or less", "Line 3: 0.00", "Line 5: Rata 10.5%", "Line 7: 0.00";
"Column 2: Line 1 is more than $53,463 but not more than $152,750", "Line 3: 53,463.00",
"Line 5: Rata 12.5%", "Line 7: 5,613.62"; "Column 3: Line 1 is more than $152,750",
"Line 3: 152,750.00", "Line 5: Rata 14.5%", "Line 7: 18,024.49".

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
tax at its start (line 7), carried as printed. The dataset has no rounding rule. Column 3 has no
upper boundary, so the schedule has no `up_to` and covers every amount.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_sk.support import saskatchewan_packages, saskatchewan_parameter_parsers

D = Decimal
# Saskatchewan is not in `registrations.JURISDICTIONS` yet, so the source is built over its own
# packages.
SOURCE = YamlParameterSource(saskatchewan_packages().roots(), saskatchewan_parameter_parsers())
FAMILY = "ca-sk/brackets"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_three_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.105"), D("0.00")),
        (D("53463.00"), D("0.125"), D("5613.62")),
        (D("152750.00"), D("0.145"), D("18024.49")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_sk428() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2025_brackets_have_no_upper_boundary() -> None:
    schedule = _schedule()

    assert schedule.up_to is None
    assert not schedule.has_range


@pytest.mark.parametrize("amount", ["0.00", "152750.00", "152750.01", "500000.00", "99999999.99"])
def test_the_table_covers_every_amount(amount: str) -> None:
    assert _schedule().covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("53463.00", "0.00"),
        ("53463.01", "53463.00"),
        ("152750.00", "53463.00"),
        ("152750.01", "152750.00"),
        ("500000.00", "152750.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    column = _schedule().column_for(D(amount))

    assert column.lower == D(lower)

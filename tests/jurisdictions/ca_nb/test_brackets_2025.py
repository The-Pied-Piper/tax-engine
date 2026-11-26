"""2025 `ca-nb/brackets`, checked against Form NB428 (CRA 5004-c, 2025), Part A.

Form text (read 2026-11-26, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt):
"Column 1: Line 1 is $51,306 or less", "Line 3: 0.00", "Line 5: Rate 9.4%", "Line 7: 0.00";
"Column 2: more than $51,306 but not more than $102,614", "Line 3: 51,306.00", "Line 5: 14%",
"Line 7: 4,822.76"; "Column 3: more than $102,614 but not more than $190,060", "Line 3:
102,614.00", "Line 5: 16%", "Line 7: 12,005.88"; "Column 4: more than $190,060", "Line 3:
190,060.00", "Line 5: 19.5%", "Line 7: 25,997.24".

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
tax at its start (line 7), carried as printed. The dataset has no rounding rule. Column 4 has no
upper boundary, so the schedule has no `up_to` and covers every amount.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(new_brunswick_packages().roots(), new_brunswick_parameter_parsers())
FAMILY = "ca-nb/brackets"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_four_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.094"), D("0.00")),
        (D("51306.00"), D("0.14"), D("4822.76")),
        (D("102614.00"), D("0.16"), D("12005.88")),
        (D("190060.00"), D("0.195"), D("25997.24")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_nb428() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2025_brackets_have_no_upper_boundary() -> None:
    schedule = _schedule()

    assert schedule.up_to is None
    assert not schedule.has_range


@pytest.mark.parametrize("amount", ["0.00", "190060.00", "190060.01", "500000.00", "99999999.99"])
def test_the_table_covers_every_amount(amount: str) -> None:
    assert _schedule().covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("51306.00", "0.00"),
        ("51306.01", "51306.00"),
        ("102614.00", "51306.00"),
        ("102614.01", "102614.00"),
        ("190060.00", "102614.00"),
        ("190060.01", "190060.00"),
        ("500000.00", "190060.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    column = _schedule().column_for(D(amount))

    assert column.lower == D(lower)

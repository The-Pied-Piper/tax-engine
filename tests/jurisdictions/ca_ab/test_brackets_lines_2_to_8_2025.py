"""2025 `ca-ab/brackets_lines_2_to_8`, checked against Form AB428 (5009-C, 2025), Part A.

Form text (cra-docs/docs/cra-forms-2025/5009-c-25e.txt): "Column 1: Line 1 is $60,000 or less",
"Line 3:
0.00", "Rate 8%", "Line 7: 0.00"; "Column 2: Line 1 is more than $60,000 but not more than
$151,234", "Line 3: 60,000.00", "Rate 10%", "Line 7: 4,800.00"; "Column 3: Line 1 is more than
$151,234 but not more than $181,481", "Line 3: 151,234.00", "Rate 12%", "Line 7: 13,923.40".

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
tax at its start (line 7), carried as printed. The dataset has no rounding rule (the form's
dollars-and-cents boxes are rounded by the steps that compute them). The table covers line 1 of
181,481.00 or less: its `up_to` is the form's printed boundary, 181,481.00.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/brackets_lines_2_to_8"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_three_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.08"), D("0.00")),
        (D("60000.00"), D("0.10"), D("4800.00")),
        (D("151234.00"), D("0.12"), D("13923.40")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_ab428() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2025_brackets_stop_at_181481() -> None:
    assert _schedule().up_to == D("181481.00")


def test_the_table_covers_181481_and_not_a_cent_more() -> None:
    schedule = _schedule()

    assert schedule.covers(D("181481.00"))
    assert not schedule.covers(D("181481.01"))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("60000.00", "0.00"),
        ("60000.01", "60000.00"),
        ("151234.00", "60000.00"),
        ("151234.01", "151234.00"),
        ("181481.00", "151234.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    column = _schedule().column_for(D(amount))

    assert column.lower == D(lower)

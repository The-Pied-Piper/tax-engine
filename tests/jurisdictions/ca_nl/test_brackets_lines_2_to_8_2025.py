"""2025 `ca-nl/brackets_lines_2_to_8`, checked against Form NL428 (5001-C, 2025), Part A.

Form text: "Column 1: Line 1 is $44,192 or less", "Line 3: 0.00", "Rate 8.7%", "Line 7: 0.00";
"Column 2: Line 1 is more than $44,192 but not more than $88,382", "Line 3: 44,192.00", "Rate
14.5%", "Line 7: 3,844.70"; "Column 3: Line 1 is more than $88,382 but not more than $157,792",
"Line 3: 88,382.00", "Rate 15.8%", "Line 7: 10,252.25"; "Column 4: Line 1 is more than $157,792 but
not more than $220,910", "Line 3: 157,792.00", "Rate 17.8%", "Line 7: 21,219.03".

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
tax at its start (line 7), carried as printed. The dataset has no rounding rule (the form states
none). The table covers line 1 of 220,910.00 or less: its `up_to` is the form's printed boundary,
220,910.00. The printed constants chain: each column's line 7 is the previous column's line 7 plus
its rate on the width of the previous column, exactly.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
# Newfoundland and Labrador is not in `registrations.JURISDICTIONS` yet, so the source is built
# over its own packages.
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/brackets_lines_2_to_8"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_four_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.087"), D("0.00")),
        (D("44192.00"), D("0.145"), D("3844.70")),
        (D("88382.00"), D("0.158"), D("10252.25")),
        (D("157792.00"), D("0.178"), D("21219.03")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_nl428() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2025_brackets_stop_at_220910() -> None:
    assert _schedule().up_to == D("220910.00")


def test_the_table_covers_220910_and_not_a_cent_more() -> None:
    schedule = _schedule()

    assert schedule.covers(D("220910.00"))
    assert not schedule.covers(D("220910.01"))


def test_the_printed_constants_chain_exactly() -> None:
    brackets = _schedule().brackets

    assert brackets[2].tax_at_start + (D("157792") - D("88382")) * D("0.158") == D("21219.03")
    assert brackets[3].tax_at_start + (D("220910") - D("157792")) * D("0.178") == D("32454.04")


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("44192.00", "0.00"),
        ("44192.01", "44192.00"),
        ("88382.00", "44192.00"),
        ("88382.01", "88382.00"),
        ("157792.00", "88382.00"),
        ("157792.01", "157792.00"),
        ("220910.00", "157792.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    column = _schedule().column_for(D(amount))

    assert column.lower == D(lower)

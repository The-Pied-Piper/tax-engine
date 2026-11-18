"""2026 `ca-sk/brackets`, from T4127 (Jan 2026) Table 8.1 (Saskatchewan), provisional.

The 2026 Form SK428 (CRA 5008-c) text is not yet published, so the dataset cites T4127 and its
header says so. The thresholds (54,532 and 155,805) and rates (10.5%, 12.5%, 14.5%) are the
T4127 figures; `tax_at_start` is derived as the 2025 form does, because the 2026 line 7
constants are not yet published.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_sk.support import saskatchewan_packages, saskatchewan_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(saskatchewan_packages().roots(), saskatchewan_parameter_parsers())
FAMILY = "ca-sk/brackets"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds 54,532 and 155,805 and rates 10.5%, 12.5%, 14.5% as printed in "
    "T4127 (Jan 2026) Table 8.1; tax_at_start derived as the 2025 form does (54,532 x 10.5% = "
    "5,725.86; plus (155,805 - 54,532) x 12.5% = 18,384.985, rounded half-up to 18,384.99) "
    "because the 2026 line 7 constants are not yet published."
)
COLUMNS = [
    (D("0.00"), D("0.105"), D("0.00")),
    (D("54532.00"), D("0.125"), D("5725.86")),
    (D("155805.00"), D("0.145"), D("18384.99")),
]


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2026, BRACKETS).values


def test_2026_brackets_are_the_three_columns_from_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == COLUMNS


def test_2026_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2026_brackets_cite_t4127_only() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).sources == (T4127_URL,)


def test_2026_brackets_are_for_tax_year_2026() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).tax_year == 2026


def test_2026_brackets_have_no_upper_boundary() -> None:
    schedule = _schedule()

    assert schedule.up_to is None
    assert not schedule.has_range


def test_2025_brackets_are_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.105"), D("0.00")),
        (D("53463.00"), D("0.125"), D("5613.62")),
        (D("152750.00"), D("0.145"), D("18024.49")),
    ]
    assert data.sources != (T4127_URL,)


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("54532.00", "0.00"),
        ("54532.01", "54532.00"),
        ("155805.00", "54532.00"),
        ("155805.01", "155805.00"),
        ("1000000.00", "155805.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = saskatchewan_packages().roots()[Namespace("ca-sk")]
    lines = (root / "parameters" / "brackets" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER

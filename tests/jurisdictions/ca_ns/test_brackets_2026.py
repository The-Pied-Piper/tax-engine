"""The 2026 `ca-ns/brackets` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_packages,
    nova_scotia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(nova_scotia_packages().roots(), nova_scotia_parameter_parsers())
FAMILY = "ca-ns/brackets"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form "
    "text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds 30,995 / 61,991 / 97,417 / 157,124 and rates 8.79% / 14.95%"
    " / 16.67% / 17.5% / 21% as printed in T4127 (Jan 2026) Table 8.1, Nova Scotia row, "
    "and in T4127 (Jul 2026) Table 8.1 (no change for Nova Scotia on July 1, 2026); "
    "tax_at_start calculated as the cumulative tax on the earlier brackets, exact, then "
    "rounded half-up to the cent, the way the 2025 printed constants come out (30,995 x "
    "8.79% = 2,724.4605, 2,724.46; plus 30,996 x 14.95% = 4,633.902, cumulative "
    "7,358.3625, 7,358.36; plus 35,426 x 16.67% = 5,905.5142, cumulative 13,263.8767, "
    "13,263.88; plus 59,707 x 17.5% = 10,448.725, cumulative 23,712.6017, 23,712.60), "
    "because the 2026 line 7 constants are not yet published. T4127 prints the payroll "
    "constants KP 0 / 1,909 / 2,976 / 3,784 / 9,283, which are a different quantity (the "
    "constants of the payroll formula) and are not used here."
)


def test_2026_brackets_are_the_t4127_thresholds_and_rates() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.0879"), D("0.00")),
        (D("30995.00"), D("0.1495"), D("2724.46")),
        (D("61991.00"), D("0.1667"), D("7358.36")),
        (D("97417.00"), D("0.175"), D("13263.88")),
        (D("157124.00"), D("0.21"), D("23712.60")),
    ]
    assert data.values.up_to is None


def test_2026_brackets_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("30995.00", "0.00"),
        ("30995.01", "30995.00"),
        ("61991.00", "30995.00"),
        ("61991.01", "61991.00"),
        ("97417.00", "61991.00"),
        ("97417.01", "97417.00"),
        ("157124.00", "97417.00"),
        ("157124.01", "157124.00"),
        ("1000000.00", "157124.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    column = SOURCE.get(FAMILY, 2026, BRACKETS).values.column_for(D(amount))

    assert column.lower == D(lower)


@pytest.mark.parametrize(
    ("lower", "tax"),
    [
        ("30995", "2724.4605"),
        ("61991", "7358.3625"),
        ("97417", "13263.8767"),
        ("157124", "23712.6017"),
    ],
)
def test_each_constant_is_the_cumulative_tax_at_its_lower_bound_to_the_cent(
    lower: str, tax: str
) -> None:
    brackets = SOURCE.get(FAMILY, 2026, BRACKETS).values.brackets
    cumulative = D(0)
    for earlier, later in zip(brackets, brackets[1:], strict=False):
        cumulative += (later.lower - earlier.lower) * earlier.rate
        if later.lower == D(lower):
            break

    assert cumulative == D(tax)
    assert later.tax_at_start == cumulative.quantize(D("0.01"), rounding="ROUND_HALF_UP")


def test_2026_brackets_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.sources == SOURCES


def test_2026_brackets_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = nova_scotia_packages().roots()[Namespace("ca-ns")]
    path = root / "parameters" / "brackets" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_brackets_are_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.0879"), D("0.00")),
        (D("30507.00"), D("0.1495"), D("2681.57")),
        (D("61015.00"), D("0.1667"), D("7242.51")),
        (D("95883.00"), D("0.175"), D("13055.01")),
        (D("154650.00"), D("0.21"), D("23339.23")),
    ]
    assert data.sources != SOURCES

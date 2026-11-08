"""2026 federal and Ontario bracket data, taken from T4127 (122nd edition, January 2026).

T4127 Table 8.1 prints each bracket's lower bound and rate, plus a different, whole-dollar "K"
(federal) or "KP" (Ontario) constant. The 2026 T1 and ON428 are not yet published, so the forms'
"tax at start" constants (T1 line 75, ON428 line 7) are calculated: the cumulative tax on earlier
brackets, summed unrounded, then rounded half-up to the cent. The same method reproduces all eight
non-zero 2025 printed constants. Both files are provisional and say how the constants were made.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog import FEDERAL_BASIC_TAX, TAXABLE_INCOME
from tax_engine.jurisdictions.core.capabilities.progressive_tax import ProgressiveTax

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds and rates as printed in T4127 Table 8.1; tax_at_start calculated "
    "as the cumulative tax on the earlier brackets, rounded half-up to the cent (reproduces the "
    "2025 printed constants)."
)

# T4127 Table 8.1 as printed: A (lower bound), R or V (rate), K or KP (whole-dollar constant).
FEDERAL_A = ["0", "58523", "117045", "181440", "258482"]
FEDERAL_R = ["0.14", "0.205", "0.26", "0.29", "0.33"]
FEDERAL_K = ["0", "3804", "10241", "15685", "26024"]
ONTARIO_A = ["0", "53891", "107785", "150000", "220000"]
ONTARIO_V = ["0.0505", "0.0915", "0.1116", "0.1216", "0.1316"]
ONTARIO_KP = ["0", "2210", "4376", "5876", "8076"]

FEDERAL_TAX_AT_START = ["0.00", "8193.22", "20190.23", "36932.93", "59275.11"]
ONTARIO_TAX_AT_START = ["0.00", "2721.50", "7652.80", "12363.99", "20875.99"]


def schedule(family: str) -> BracketSchedule:
    return SOURCE.get(family, 2026, BRACKETS).values


def tax_at_starts(family: str) -> list[Decimal]:
    starts = [b.tax_at_start for b in schedule(family).brackets]
    assert None not in starts
    return [start for start in starts if start is not None]


def cumulative_tax(lowers: list[str], rates: list[str]) -> list[Decimal]:
    total = D(0)
    starts = []
    for i, (lower, rate) in enumerate(zip(lowers, rates, strict=True)):
        starts.append(total.quantize(D("0.01"), ROUND_HALF_UP))
        if i + 1 < len(lowers):
            total += D(rate) * (D(lowers[i + 1]) - D(lower))
    return starts


def test_federal_2026_brackets() -> None:
    data = SOURCE.get("ca/brackets", 2026, BRACKETS)

    assert [(b.lower, b.rate) for b in data.values.brackets] == [
        (D(a), D(r)) for a, r in zip(FEDERAL_A, FEDERAL_R, strict=True)
    ]
    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING
    assert data.sources == (T4127_URL,)


def test_ontario_2026_brackets() -> None:
    data = SOURCE.get("ca-on/brackets", 2026, BRACKETS)

    assert [(b.lower, b.rate) for b in data.values.brackets] == [
        (D(a), D(v)) for a, v in zip(ONTARIO_A, ONTARIO_V, strict=True)
    ]
    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING
    assert data.sources == (T4127_URL,)


def test_the_2026_federal_lowest_rate_is_the_full_year_14_percent() -> None:
    assert schedule("ca/brackets").brackets[0].rate == D("0.14")


@pytest.mark.parametrize(
    ("family", "expected"),
    [("ca/brackets", FEDERAL_TAX_AT_START), ("ca-on/brackets", ONTARIO_TAX_AT_START)],
)
def test_the_2026_tax_at_each_start_is_the_calculated_cumulative_tax(
    family: str, expected: list[str]
) -> None:
    assert tax_at_starts(family) == [D(x) for x in expected]
    assert all(start.as_tuple().exponent == -2 for start in tax_at_starts(family))


@pytest.mark.parametrize(
    ("family", "lowers", "rates"),
    [
        ("ca/brackets", FEDERAL_A, FEDERAL_R),
        ("ca-on/brackets", ONTARIO_A, ONTARIO_V),
    ],
)
def test_the_2026_tax_at_start_follows_the_documented_method(
    family: str, lowers: list[str], rates: list[str]
) -> None:
    assert tax_at_starts(family) == cumulative_tax(lowers, rates)


@pytest.mark.parametrize(
    ("lowers", "rates", "printed"),
    [
        # The method reproduces the 2025 printed constants (T1 line 75; ON428 line 7).
        (
            ["0", "57375", "114750", "177882", "253414"],
            ["0.145", "0.205", "0.26", "0.29", "0.33"],
            ["0.00", "8319.38", "20081.25", "36495.57", "58399.85"],
        ),
        (
            ["0", "52886", "105775", "150000", "220000"],
            ["0.0505", "0.0915", "0.1116", "0.1216", "0.1316"],
            ["0.00", "2670.74", "7510.09", "12445.60", "20957.60"],
        ),
    ],
)
def test_the_method_reproduces_the_2025_printed_constants(
    lowers: list[str], rates: list[str], printed: list[str]
) -> None:
    assert cumulative_tax(lowers, rates) == [D(x) for x in printed]


@pytest.mark.parametrize(
    ("family", "lowers", "rates", "constants"),
    [
        ("ca/brackets", FEDERAL_A, FEDERAL_R, FEDERAL_K),
        ("ca-on/brackets", ONTARIO_A, ONTARIO_V, ONTARIO_KP),
    ],
)
def test_the_2026_tax_at_start_agrees_with_the_t4127_constant_within_a_dollar(
    family: str, lowers: list[str], rates: list[str], constants: list[str]
) -> None:
    # T4127's K is the tax overcharged by applying the bracket's rate to the whole income:
    # K = rate x lower - tax_at_start.
    for start, lower, rate, k in zip(tax_at_starts(family), lowers, rates, constants, strict=True):
        assert abs(D(rate) * D(lower) - start - D(k)) < D(1)


@pytest.mark.parametrize(
    ("family", "income"),
    [
        ("ca/brackets", "58523"),
        ("ca/brackets", "117045"),
        ("ca/brackets", "181440"),
        ("ca/brackets", "258482"),
        ("ca-on/brackets", "53891"),
        ("ca-on/brackets", "107785"),
        ("ca-on/brackets", "150000"),
        ("ca-on/brackets", "220000"),
    ],
)
def test_the_tax_is_continuous_across_each_2026_threshold(family: str, income: str) -> None:
    # The tax at a bound, from the column below, equals the next column's tax at its start,
    # to within the half-cent the constant is rounded by.
    brackets = schedule(family)
    at_bound = brackets.tax_on(D(income))
    next_start = brackets.column_for(D(income) + D("0.01")).tax_at_start

    assert abs(at_bound - next_start) <= D("0.005")


def test_federal_tax_on_a_taxable_income_of_69335() -> None:
    # A taxable income of 69,335.00: 8,193.22 + 0.205 x (69,335 - 58,523) = 10,409.68.
    capability = ProgressiveTax(
        TAXABLE_INCOME, FEDERAL_BASIC_TAX, SOURCE.get("ca/brackets", 2026, BRACKETS)
    )

    result = capability.compute((Artifact(TAXABLE_INCOME, D("69335.00")),))

    assert result.outputs == (Artifact(FEDERAL_BASIC_TAX, D("10409.68")),)


@pytest.mark.parametrize(
    ("family", "income", "tax"),
    [
        ("ca/brackets", "58523.01", "8193.22205"),  # 0.205 x 0.01 + 8,193.22
        ("ca/brackets", "117045.01", "20190.2326"),  # 0.26 x 0.01 + 20,190.23
        ("ca-on/brackets", "53891.01", "2721.500915"),  # 0.0915 x 0.01 + 2,721.50
        ("ca-on/brackets", "220000.01", "20875.991316"),  # 0.1316 x 0.01 + 20,875.99
    ],
)
def test_an_income_just_above_a_2026_threshold_starts_from_the_next_columns_tax_at_start(
    family: str, income: str, tax: str
) -> None:
    assert schedule(family).tax_on(D(income)) == D(tax)


@pytest.mark.parametrize(("package", "folder"), [("ca", "brackets"), ("ca-on", "brackets")])
def test_the_2026_files_are_provisional_and_state_their_derivation(
    package: str, folder: str
) -> None:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace(package)]
    lines = (root / "parameters" / folder / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_brackets_are_unchanged() -> None:
    assert SOURCE.get("ca/brackets", 2025, BRACKETS).values.brackets[1].tax_at_start == D("8319.38")
    assert SOURCE.get("ca-on/brackets", 2025, BRACKETS).values.brackets[1].tax_at_start == D(
        "2670.74"
    )

"""The `ca` datasets behind the federal part of the take-home marginal rate, for 2025 and 2026.

Each band dataset gives the rate (per extra dollar) of the band a base falls in, through
`core/amount_by_band_rate`; the figures are the forms' own, taken as printed (the 2026 files carry
the 2026 figures of T4127, the 2025 forms' layout):

- `marginal_cpp_base_rate_rows`, `marginal_cpp_first_additional_rate_rows`: Schedule 8 (form
  5000-S8) Part 3 lines 11 "multiplied by 4.95%" and 12 "multiplied by 1%", from the basic
  exemption (Part 2 line E, $3,500) up to the maximum pensionable earnings (line B, $71,300).
- `marginal_cpp_second_additional_rate_rows`: line 22 "multiplied by 4%", from line B up to the
  additional maximum pensionable earnings (line D, $81,200).
- `marginal_ei_rate_rows`: Form T2204 line 16 "Enter whichever amount is the least: line 7, line 9
  or line 12": 0 up to the $2,000 of line 7, then 1 for 1 (line 7) up to the $2,033 of note (3),
  then line 10's 1.64%, up to the maximum $65,700 of line 3.
- `marginal_federal_bpa_rows`: T1 line 77, "If the amount on line 23600 is $177,882 or less ...
  $253,414 or more": the band of net income in which the basic personal amount falls.
- `marginal_federal_credit_rate`: T1 line 114 "Federal non-refundable tax credit rate 14.5%",
  applied to the CPP base and EI contributions (T1 lines 30800 and 31200).
- `federal_bpa_phase_down_fraction`: Federal Worksheet (5000-D1) lines 2 and 8 "1,591.00" over
  line 6 "75,532.00".
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
from tax_engine.domain.parameters.fraction import FRACTION
from tax_engine.domain.parameters.rate import RATE

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)


def _rate(family: str, year: int, base: str) -> Decimal:
    band = SOURCE.get(family, year, AMOUNT_BY_BAND).values.band_for(D(base))
    return band.rate.value if band.rate is not None else D("0")


@pytest.mark.parametrize(
    ("family", "year", "base", "rate"),
    [
        # CPP base, 2025: no rate up to the $3,500 exemption, 4.95% to $71,300, none above.
        ("ca/marginal_cpp_base_rate_rows", 2025, "3500", "0"),
        ("ca/marginal_cpp_base_rate_rows", 2025, "3500.01", "0.0495"),
        ("ca/marginal_cpp_base_rate_rows", 2025, "71300", "0.0495"),
        ("ca/marginal_cpp_base_rate_rows", 2025, "71300.01", "0"),
        ("ca/marginal_cpp_base_rate_rows", 2026, "74600", "0.0495"),
        ("ca/marginal_cpp_base_rate_rows", 2026, "74600.01", "0"),
        ("ca/marginal_cpp_first_additional_rate_rows", 2025, "3500", "0"),
        ("ca/marginal_cpp_first_additional_rate_rows", 2025, "50000", "0.01"),
        ("ca/marginal_cpp_first_additional_rate_rows", 2025, "71300.01", "0"),
        ("ca/marginal_cpp_first_additional_rate_rows", 2026, "74600.01", "0"),
        # CPP2, 2025: 4% from $71,300 to $81,200.
        ("ca/marginal_cpp_second_additional_rate_rows", 2025, "71300", "0"),
        ("ca/marginal_cpp_second_additional_rate_rows", 2025, "75000", "0.04"),
        ("ca/marginal_cpp_second_additional_rate_rows", 2025, "81200.01", "0"),
        ("ca/marginal_cpp_second_additional_rate_rows", 2026, "74600", "0"),
        ("ca/marginal_cpp_second_additional_rate_rows", 2026, "85000", "0.04"),
        ("ca/marginal_cpp_second_additional_rate_rows", 2026, "85000.01", "0"),
        # EI, T2204 line 16: 0, then 1, then 1.64% (1.63% in 2026) to the maximum.
        ("ca/marginal_ei_rate_rows", 2025, "2000", "0"),
        ("ca/marginal_ei_rate_rows", 2025, "2000.01", "1"),
        ("ca/marginal_ei_rate_rows", 2025, "2033", "1"),
        ("ca/marginal_ei_rate_rows", 2025, "2033.01", "1"),
        ("ca/marginal_ei_rate_rows", 2025, "2033.35", "0.0164"),
        ("ca/marginal_ei_rate_rows", 2025, "65700", "0.0164"),
        ("ca/marginal_ei_rate_rows", 2025, "65700.01", "0"),
        ("ca/marginal_ei_rate_rows", 2026, "2033.01", "1"),
        ("ca/marginal_ei_rate_rows", 2026, "2033.15", "0.0163"),
        ("ca/marginal_ei_rate_rows", 2026, "68900", "0.0163"),
        ("ca/marginal_ei_rate_rows", 2026, "68900.01", "0"),
        # Federal basic personal amount: the phase-down band of net income.
        ("ca/marginal_federal_bpa_rows", 2025, "177882", "0"),
        ("ca/marginal_federal_bpa_rows", 2025, "177882.01", "1"),
        ("ca/marginal_federal_bpa_rows", 2025, "253414", "1"),
        ("ca/marginal_federal_bpa_rows", 2025, "253414.01", "0"),
        ("ca/marginal_federal_bpa_rows", 2026, "181440", "0"),
        ("ca/marginal_federal_bpa_rows", 2026, "181440.01", "1"),
        ("ca/marginal_federal_bpa_rows", 2026, "258482", "1"),
        ("ca/marginal_federal_bpa_rows", 2026, "258482.01", "0"),
    ],
)
def test_the_band_dataset_gives_the_rate_of_the_band_the_base_is_in(
    family: str, year: int, base: str, rate: str
) -> None:
    assert _rate(family, year, base) == D(rate)


@pytest.mark.parametrize(
    ("year", "rate"),
    [(2025, "0.145"), (2026, "0.14")],
)
def test_the_federal_credit_rate_dataset_holds_the_printed_rate_and_rounds_nothing(
    year: int, rate: str
) -> None:
    dataset = SOURCE.get("ca/marginal_federal_credit_rate", year, RATE)

    assert dataset.values.value == D(rate)
    assert dataset.rounding.apply(D("0.123456789")) == D("0.123456789")


@pytest.mark.parametrize(
    ("year", "numerator", "denominator"),
    [(2025, 1591, 75532), (2026, 1623, 77042)],
)
def test_the_basic_personal_amount_fraction_is_the_supplement_over_the_range(
    year: int, numerator: int, denominator: int
) -> None:
    dataset = SOURCE.get("ca/federal_bpa_phase_down_fraction", year, FRACTION)

    assert (dataset.values.numerator, dataset.values.denominator) == (numerator, denominator)
    assert dataset.rounding.apply(D("0.02106394")) == D("0.0210639")

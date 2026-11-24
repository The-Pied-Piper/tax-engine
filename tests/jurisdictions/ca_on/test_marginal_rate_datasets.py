"""The `ca-on` datasets behind the Ontario marginal rate, for 2025 and 2026.

Each band dataset gives the rate (per extra dollar) of the band a base falls in, through
`core/amount_by_band_rate`; the figures are the forms' own, taken as printed (the 2026 files carry
the 2026 figures of T4127, the 2025 forms' layout):

- `marginal_lift_reduction_rows`: ON428-A line 19 (line 17 times line 18 "Applicable rate 5%")
  over the credit's $875 maximum (lines 5 and 14).
- `marginal_ontario_credit_rate`: ON428 line 45's 5.05%, applied to the CPP base and EI
  contributions (ON428 lines 19 and 21).

The federal datasets (CPP, EI, the basic personal amount, the federal credit rate) are the `ca`
package's, tested in `tests/jurisdictions/ca/test_marginal_rate_datasets.py`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount_by_band import AMOUNT_BY_BAND
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
        # LIFT: the reduction rate while the reduction is above 0.00 and not over the $875 credit.
        ("ca-on/marginal_lift_reduction_rows", 2025, "0.00", "0"),
        ("ca-on/marginal_lift_reduction_rows", 2025, "0.01", "0.05"),
        ("ca-on/marginal_lift_reduction_rows", 2025, "875", "0.05"),
        ("ca-on/marginal_lift_reduction_rows", 2025, "875.01", "0"),
        ("ca-on/marginal_lift_reduction_rows", 2026, "0.00", "0"),
        ("ca-on/marginal_lift_reduction_rows", 2026, "875", "0.05"),
        ("ca-on/marginal_lift_reduction_rows", 2026, "875.01", "0"),
    ],
)
def test_the_band_dataset_gives_the_rate_of_the_band_the_base_is_in(
    family: str, year: int, base: str, rate: str
) -> None:
    assert _rate(family, year, base) == D(rate)


@pytest.mark.parametrize(
    ("family", "year", "rate"),
    [
        ("ca-on/marginal_ontario_credit_rate", 2025, "0.0505"),
        ("ca-on/marginal_ontario_credit_rate", 2026, "0.0505"),
    ],
)
def test_the_credit_rate_dataset_holds_the_printed_rate_and_rounds_nothing(
    family: str, year: int, rate: str
) -> None:
    dataset = SOURCE.get(family, year, RATE)

    assert dataset.values.value == D(rate)
    assert dataset.rounding.apply(D("0.123456789")) == D("0.123456789")

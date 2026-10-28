"""Unit tests for Taper: a base plus a supplement that tapers away, the `taper` kind's values.

A taper holds the four figures a form prints: the `base` amount, the `supplement` added to it, the
`threshold` above which the supplement is reduced and the `range` over which it is reduced to
nothing, all exact. Like `Rate` and `ContributionTier`, the value object checks itself: figures
that are not finite, a negative base, supplement or threshold, or a range that is not above zero,
are an `InvalidTaperError`. Values are made up.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import Any, cast

import pytest

from tax_calculator.domain.errors import DomainError, InvalidTaperError
from tax_calculator.domain.parameters.kind import ParameterKind
from tax_calculator.domain.parameters.taper import TAPER, Taper

D = Decimal


def taper(
    base: str = "1000", supplement: str = "500", threshold: str = "20000", range: str = "10000"
) -> Taper:
    return Taper(base=D(base), supplement=D(supplement), threshold=D(threshold), range=D(range))


def test_holds_its_base_supplement_threshold_and_range() -> None:
    held = taper()

    assert held.base == D("1000")
    assert held.supplement == D("500")
    assert held.threshold == D("20000")
    assert held.range == D("10000")


def test_holds_its_fields_in_order() -> None:
    assert [field.name for field in fields(Taper)] == ["base", "supplement", "threshold", "range"]


def test_is_built_positionally_in_field_order() -> None:
    assert Taper(D("1000"), D("500"), D("20000"), D("10000")) == taper()


def test_holds_no_maximum_of_its_own() -> None:
    # The full amount is base + supplement; the taper stores only the four figures.
    assert "maximum" not in [field.name for field in fields(Taper)]


def test_equal_values_are_equal_tapers() -> None:
    assert taper("1000", "500", "20000", "10000") == taper("1000.00", "500.0", "20000", "1E+4")


def test_tapers_differ_by_any_field() -> None:
    assert taper() != taper(base="900")
    assert taper() != taper(supplement="400")
    assert taper() != taper(threshold="25000")
    assert taper() != taper(range="5000")


def test_is_frozen() -> None:
    with pytest.raises(FrozenInstanceError):
        cast(Any, taper()).supplement = D("1")


def test_is_hashable() -> None:
    assert hash(taper()) == hash(taper())


def test_keeps_its_figures_exactly_as_given() -> None:
    held = taper(base="1000.50", supplement="500.00", threshold="20000.10", range="10000.0")

    # No rounding, no normalising.
    assert (str(held.base), str(held.supplement), str(held.threshold), str(held.range)) == (
        "1000.50",
        "500.00",
        "20000.10",
        "10000.0",
    )


def test_accepts_a_zero_base() -> None:
    assert taper(base="0").base == D("0")


def test_accepts_a_zero_supplement() -> None:
    assert taper(supplement="0").supplement == D("0")


def test_accepts_a_zero_threshold() -> None:
    assert taper(threshold="0").threshold == D("0")


def test_accepts_a_narrow_range() -> None:
    assert taper(range="0.01").range == D("0.01")


@pytest.mark.parametrize(
    ("base", "supplement", "threshold", "range", "message"),
    [
        pytest.param("-1", "500", "20000", "10000", "base must not be negative", id="base-neg"),
        pytest.param(
            "-0.01", "500", "20000", "10000", "base must not be negative", id="base-slightly-neg"
        ),
        pytest.param(
            "1000", "-1", "20000", "10000", "supplement must not be negative", id="supp-neg"
        ),
        pytest.param(
            "1000", "-0.01", "20000", "10000", "supplement must not be negative", id="supp-below-0"
        ),
        pytest.param(
            "1000", "500", "-1", "10000", "threshold must not be negative", id="threshold-neg"
        ),
        pytest.param("1000", "500", "20000", "0", "range must be positive", id="range-zero"),
        pytest.param("1000", "500", "20000", "-0", "range must be positive", id="range-neg-zero"),
        pytest.param("1000", "500", "20000", "-1", "range must be positive", id="range-neg"),
        pytest.param("Infinity", "500", "20000", "10000", "base must be finite", id="base-inf"),
        pytest.param("NaN", "500", "20000", "10000", "base must be finite", id="base-nan"),
        pytest.param(
            "1000", "Infinity", "20000", "10000", "supplement must be finite", id="supp-inf"
        ),
        pytest.param("1000", "NaN", "20000", "10000", "supplement must be finite", id="supp-nan"),
        pytest.param(
            "1000", "500", "Infinity", "10000", "threshold must be finite", id="threshold-inf"
        ),
        pytest.param("1000", "500", "NaN", "10000", "threshold must be finite", id="threshold-nan"),
        pytest.param("1000", "500", "20000", "Infinity", "range must be finite", id="range-inf"),
        pytest.param("1000", "500", "20000", "NaN", "range must be finite", id="range-nan"),
    ],
)
def test_rejects_invalid_tapers(
    base: str, supplement: str, threshold: str, range: str, message: str
) -> None:
    with pytest.raises(InvalidTaperError, match=message):
        taper(base=base, supplement=supplement, threshold=threshold, range=range)


@pytest.mark.parametrize("field", ["base", "supplement", "threshold", "range"])
@pytest.mark.parametrize("value", [1000, 0.5, "1000"])
def test_rejects_non_decimal_figures(field: str, value: object) -> None:
    figures: dict[str, object] = {
        "base": D("1000"),
        "supplement": D("500"),
        "threshold": D("20000"),
        "range": D("10000"),
    }
    figures[field] = value

    with pytest.raises(TypeError, match=f"{field} must be a Decimal"):
        Taper(**figures)  # type: ignore[arg-type]


def test_taper_kind() -> None:
    assert TAPER == ParameterKind("taper", Taper)
    assert TAPER.name == "taper"
    assert TAPER.value_type is Taper


def test_invalid_taper_is_a_domain_error() -> None:
    assert issubclass(InvalidTaperError, DomainError)

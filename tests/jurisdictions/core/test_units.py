"""Unit tests for the units the core package declares and their English text.

Core declares the generic units: `core/months`, `core/years` and `core/percent`. Their English text
is read from the shared registry, which the application fills when the packages are imported.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.inbound.trace_english import EnglishNames
from tax_engine.adapters.inbound.trace_english.unit_text import EnglishUnitTextRegistry
from tax_engine.adapters.inbound.unit_text import Placement
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.unit import Unit, UnitRegistry
from tax_engine.domain.worksheet import Worksheet

D = Decimal


def write(identifier: str, shown: str, value: Decimal | int) -> str:
    return EnglishUnitTextRegistry.shared().for_unit(Unit(identifier)).write(shown, value)


def test_core_declares_months_years_and_percent() -> None:
    registry = UnitRegistry()
    tax_engine.registrations.JURISDICTIONS.register_units(registry)

    declared = {u.identifier for u in registry.units if u.identifier.startswith("core/")}

    assert declared == {"core/months", "core/years", "core/percent"}


@pytest.mark.parametrize(
    ("identifier", "singular", "plural", "placement", "spaced"),
    [
        ("core/months", "month", "months", Placement.AFTER, True),
        ("core/years", "year", "years", Placement.AFTER, True),
        ("core/percent", "%", "%", Placement.AFTER, False),
    ],
)
def test_the_english_text_of_each_core_unit(
    identifier: str, singular: str, plural: str, placement: Placement, spaced: bool
) -> None:
    text = EnglishUnitTextRegistry.shared().for_unit(Unit(identifier))

    assert (text.singular, text.plural, text.placement, text.spaced) == (
        singular,
        plural,
        placement,
        spaced,
    )


def test_months_are_written_after_the_number_singular_for_one() -> None:
    assert write("core/months", "1", 1) == "1 month"
    assert write("core/months", "12", 12) == "12 months"
    assert write("core/months", "0", 0) == "0 months"


def test_years_are_written_after_the_number_singular_for_one() -> None:
    assert write("core/years", "1", 1) == "1 year"
    assert write("core/years", "2", 2) == "2 years"


def test_percent_is_written_against_the_number_for_one_and_for_any_other() -> None:
    assert write("core/percent", "12", 12) == "12%"
    assert write("core/percent", "1", 1) == "1%"
    assert write("core/percent", "5.05", D("5.05")) == "5.05%"


@pytest.mark.parametrize(
    ("identifier", "as_percentage"),
    [("core/months", False), ("core/years", False), ("core/percent", True)],
)
def test_only_core_percent_is_written_as_a_percentage(identifier: str, as_percentage: bool) -> None:
    text = EnglishUnitTextRegistry.shared().for_unit(Unit(identifier))

    assert text.as_percentage is as_percentage


def test_a_core_percent_figure_prints_as_the_percentage() -> None:
    names = EnglishNames(
        Worksheet(figure_units={"rate": Unit("core/percent")}, figure_references={}),
        EnglishUnitTextRegistry.shared(),
    )

    assert names.figure(AmountKind("ex/rate"), D("0.2965")) == "rate (29.65%)"

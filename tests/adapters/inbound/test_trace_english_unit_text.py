"""Unit tests for the English text of units: `EnglishUnitText`, its registry and `english_unit`.

A unit is only its identifier; each language supplies the text. `EnglishUnitText` writes a figure
with its unit: before the number ("EX$3500.00") or after it ("12 moons"), with a space between only
when `spaced`, the singular text for a value of exactly 1 and the plural for any other, and after
the minus sign of a negative figure. An `EnglishUnitTextRegistry` holds one text per unit and says
which units have none; `english_unit` registers on the shared one. Units and texts are made up and
use fresh registries, except where the shared one is the point.
"""

from __future__ import annotations

import dataclasses
from decimal import Decimal

import pytest

from tax_engine.adapters.inbound.trace_english.unit_text import (
    EnglishUnitText,
    EnglishUnitTextRegistry,
    Placement,
    UnitText,
    english_unit,
)
from tax_engine.domain.errors import (
    DuplicateRegistrationError,
    UnknownRegistrationError,
)
from tax_engine.domain.registry import Namespace, SharedRegistry
from tax_engine.domain.unit import Unit, UnitCatalog, UnitRegistry

D = Decimal
CROWNS = EnglishUnitText("ex/crowns", "EX$", "EX$", Placement.BEFORE, spaced=False)
MOONS = EnglishUnitText("ex/moons", "moon", "moons", Placement.AFTER, spaced=True)


def test_a_unit_text_is_a_frozen_value_with_the_identifier_it_is_for() -> None:
    assert CROWNS.identifier == "ex/crowns"
    assert [f.name for f in dataclasses.fields(EnglishUnitText)] == [
        "identifier",
        "singular",
        "plural",
        "placement",
        "spaced",
    ]
    assert EnglishUnitText("ex/moons", "moon", "moons", Placement.AFTER, spaced=True) == MOONS
    with pytest.raises(dataclasses.FrozenInstanceError):
        MOONS.identifier = "ex/suns"  # type: ignore[misc]
    assert {p.value for p in Placement} == {"before", "after"}


def test_an_english_unit_text_is_a_unit_text() -> None:
    text: UnitText = MOONS

    assert text.identifier == "ex/moons"


def test_spaced_is_keyword_only_and_has_no_default() -> None:
    with pytest.raises(TypeError, match="spaced"):
        EnglishUnitText("ex/crowns", "EX$", "EX$", Placement.BEFORE)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        EnglishUnitText("ex/crowns", "EX$", "EX$", Placement.BEFORE, False)  # type: ignore[call-arg]


def test_a_unit_before_the_number_is_written_against_it() -> None:
    assert CROWNS.write("3500.00", D("3500.00")) == "EX$3500.00"
    assert CROWNS.write("0.00", D("0.00")) == "EX$0.00"


def test_a_unit_after_the_number_is_written_after_it() -> None:
    assert MOONS.write("12", 12) == "12 moons"


def test_the_singular_is_for_exactly_one_and_the_plural_for_any_other() -> None:
    assert MOONS.write("1", 1) == "1 moon"
    assert MOONS.write("1.00", D("1.00")) == "1.00 moon"
    assert MOONS.write("2", 2) == "2 moons"
    assert MOONS.write("0", 0) == "0 moons"
    assert MOONS.write("1.50", D("1.50")) == "1.50 moons"
    assert MOONS.write("-1", -1) == "-1 moons"


def test_a_symbol_is_the_same_singular_and_plural() -> None:
    assert CROWNS.write("1", 1) == "EX$1"
    assert CROWNS.write("2", 2) == "EX$2"


def test_spaced_decides_the_gap_before_or_after() -> None:
    before_tight = CROWNS
    before_spaced = EnglishUnitText("ex/crowns", "EX$", "EX$", Placement.BEFORE, spaced=True)
    after_spaced = MOONS
    after_tight = EnglishUnitText("ex/percent", "%", "%", Placement.AFTER, spaced=False)

    assert before_tight.write("3500.00", D("3500.00")) == "EX$3500.00"
    assert before_spaced.write("3500.00", D("3500.00")) == "EX$ 3500.00"
    assert after_spaced.write("12", 12) == "12 moons"
    assert after_tight.write("12", 12) == "12%"


def test_the_singular_and_plural_text_is_written_as_given() -> None:
    marks = EnglishUnitText("ex/marks", "one mark ", "marks ", Placement.BEFORE, spaced=False)
    tight_after = EnglishUnitText("ex/ratios", "pt", "pts", Placement.AFTER, spaced=False)

    assert marks.write("1", 1) == "one mark 1"
    assert marks.write("3", 3) == "marks 3"
    assert tight_after.write("1", 1) == "1pt"
    assert tight_after.write("1.50", D("1.50")) == "1.50pts"


def test_a_negative_figure_has_its_sign_first_when_the_unit_goes_before() -> None:
    spaced = EnglishUnitText("ex/crowns", "EX$", "EX$", Placement.BEFORE, spaced=True)

    assert CROWNS.write("-1.00", D("-1.00")) == "-EX$1.00"
    assert CROWNS.write("-1", -1) == "-EX$1"
    assert CROWNS.write("-3500.50", D("-3500.50")) == "-EX$3500.50"
    assert spaced.write("-1.00", D("-1.00")) == "-EX$ 1.00"


def test_a_negative_figure_keeps_its_sign_first_when_the_unit_goes_after() -> None:
    assert MOONS.write("-3", -3) == "-3 moons"


# --- the registry ---------------------------------------------------------------------------------


def test_the_registry_is_a_shared_registry_like_the_renderers() -> None:
    assert issubclass(EnglishUnitTextRegistry, SharedRegistry)
    assert EnglishUnitTextRegistry.shared() is EnglishUnitTextRegistry.shared()
    assert EnglishUnitTextRegistry() is not EnglishUnitTextRegistry.shared()


def test_the_text_of_a_unit_is_found_by_the_unit() -> None:
    registry = EnglishUnitTextRegistry()
    registry.register_text(CROWNS)
    registry.register_text(MOONS)

    assert registry.for_unit(Unit("ex/crowns")) is CROWNS
    assert registry.for_unit(Unit("ex/moons")) is MOONS


def test_a_unit_with_no_english_text_is_refused_naming_it() -> None:
    registry = EnglishUnitTextRegistry()
    registry.register_text(CROWNS)

    with pytest.raises(UnknownRegistrationError, match="ex/furlongs"):
        registry.for_unit(Unit("ex/furlongs"))


def test_a_second_text_for_one_unit_is_refused_naming_it() -> None:
    registry = EnglishUnitTextRegistry()
    registry.register_text(MOONS)

    with pytest.raises(DuplicateRegistrationError, match="ex/moons"):
        registry.register_text(
            EnglishUnitText("ex/moons", "lune", "lunes", Placement.AFTER, spaced=True)
        )
    assert registry.for_unit(Unit("ex/moons")) is MOONS


def test_the_same_local_id_in_two_namespaces_has_two_texts() -> None:
    registry = EnglishUnitTextRegistry()
    other = EnglishUnitText("ex-on/crowns", "ON$", "ON$", Placement.BEFORE, spaced=False)
    registry.register_text(CROWNS)
    registry.register_text(other)

    assert registry.for_unit(Unit("ex/crowns")) is CROWNS
    assert registry.for_unit(Unit("ex-on/crowns")) is other


def test_require_accepts_units_that_all_have_text() -> None:
    registry = EnglishUnitTextRegistry()
    registry.register_text(CROWNS)
    registry.register_text(MOONS)

    registry.require([Unit("ex/crowns"), Unit("ex/moons")])
    registry.require([])


def test_require_names_every_unit_with_no_text_in_one_error() -> None:
    registry = EnglishUnitTextRegistry()
    registry.register_text(CROWNS)

    with pytest.raises(UnknownRegistrationError) as caught:
        registry.require(
            [Unit("ex/crowns"), Unit("ex/furlongs"), Unit("ex/moons"), Unit("ex-on/ducats")]
        )

    message = str(caught.value)
    assert "ex/furlongs" in message
    assert "ex/moons" in message
    assert "ex-on/ducats" in message
    assert "ex/crowns" not in message


def test_the_startup_check_refuses_a_registered_unit_with_no_text() -> None:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns")
    catalog.declare("moons")
    units = UnitRegistry()
    units.register_catalog(catalog)
    texts = EnglishUnitTextRegistry()
    texts.register_text(CROWNS)

    with pytest.raises(UnknownRegistrationError, match="ex/moons"):
        texts.require(units.units)

    texts.register_text(MOONS)
    texts.require(units.units)


def test_english_unit_registers_the_text_on_the_shared_registry() -> None:
    english_unit("ex/test_652_lunes", "lune", "lunes", Placement.AFTER, spaced=True)

    found = EnglishUnitTextRegistry.shared().for_unit(Unit("ex/test_652_lunes"))
    assert found.write("2", 2) == "2 lunes"
    assert found.write("1", 1) == "1 lune"
    assert found.identifier == "ex/test_652_lunes"


def test_english_unit_takes_spaced_by_keyword_only() -> None:
    with pytest.raises(TypeError):
        english_unit("ex/test_652_bad", "a", "b", Placement.AFTER, True)  # type: ignore[call-arg]
    with pytest.raises(TypeError, match="spaced"):
        english_unit("ex/test_652_bad", "a", "b", Placement.AFTER)  # type: ignore[call-arg]

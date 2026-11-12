"""Unit tests for the unit the federal Canada package declares and its English text.

`ca` declares the Canadian dollar, `ca/cad`, written "CA$" against the number, so it never reads
the same as another currency.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions
import tax_engine.registrations
from tax_engine.adapters.inbound.trace_english.unit_text import EnglishUnitTextRegistry
from tax_engine.adapters.inbound.unit_text import Placement
from tax_engine.domain.unit import Unit, UnitRegistry

D = Decimal


def test_ca_declares_the_canadian_dollar_and_nothing_else() -> None:
    registry = UnitRegistry()
    tax_engine.registrations.JURISDICTIONS.register_units(registry)

    declared = {u.identifier for u in registry.units if u.identifier.startswith("ca/")}

    assert declared == {"ca/cad"}


def test_the_english_text_of_the_canadian_dollar() -> None:
    text = EnglishUnitTextRegistry.shared().for_unit(Unit("ca/cad"))

    assert (text.singular, text.plural, text.placement, text.spaced) == (
        "CA$",
        "CA$",
        Placement.BEFORE,
        False,
    )


def test_the_canadian_dollar_is_written_before_the_number_for_any_value() -> None:
    text = EnglishUnitTextRegistry.shared().for_unit(Unit("ca/cad"))

    assert text.write("3500.00", D("3500.00")) == "CA$3500.00"
    assert text.write("1.00", D("1.00")) == "CA$1.00"
    assert text.write("0.00", D("0.00")) == "CA$0.00"


def test_a_negative_canadian_dollar_amount_has_its_sign_first() -> None:
    text = EnglishUnitTextRegistry.shared().for_unit(Unit("ca/cad"))

    assert text.write("-1.00", D("-1.00")) == "-CA$1.00"


def test_every_registered_unit_has_english_text() -> None:
    units = tax_engine.registrations.units().units

    assert len(units) == 4
    EnglishUnitTextRegistry.shared().require(units)


def test_every_bundled_amount_dataset_is_measured_in_the_canadian_dollar() -> None:
    root = Path(tax_engine.jurisdictions.__file__).parent
    amounts = [
        path
        for package in ("ca", "ca_on")
        for path in (root / package / "parameters").rglob("*.yaml")
        if "\nkind: amount\n" in path.read_text()
    ]

    assert amounts
    assert [p for p in amounts if "\nunit: ca/cad\n" not in p.read_text()] == []

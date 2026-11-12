"""Unit tests for the units of the Ontario package: it declares none of its own."""

from __future__ import annotations

import tax_engine.registrations
from tax_engine.domain.unit import UnitRegistry


def test_ontario_declares_no_units_and_uses_the_federal_and_core_ones() -> None:
    registry = UnitRegistry()
    tax_engine.registrations.JURISDICTIONS.register_units(registry)

    declared = {u.identifier for u in registry.units}

    assert not {i for i in declared if i.startswith("ca-on/")}
    assert {"ca/cad", "core/months"} <= declared

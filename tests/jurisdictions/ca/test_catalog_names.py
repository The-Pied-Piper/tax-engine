"""Every kind in the federal catalog is registered under the name its constant spells.

A constant such as `ZONE_A_DAYS_LIVED` is declared with its own local id, `"zone_a_days_lived"`,
and the engine adds the namespace, giving `ca/zone_a_days_lived`. Nothing in the engine ties the
two together, so a constant declared with another line's id would read a caller's figure for the
wrong line. This test walks every catalog module, so a new kind is checked without editing it.
"""

from __future__ import annotations

import importlib
import pkgutil

import tax_engine.jurisdictions.ca.catalog as catalog_package
from tax_engine.domain.artifact import ArtifactKind


def test_every_catalog_kind_is_registered_under_its_constants_name() -> None:
    mismatched: list[str] = []
    checked = 0
    for module_info in pkgutil.iter_modules(catalog_package.__path__):
        module = importlib.import_module(f"{catalog_package.__name__}.{module_info.name}")
        for name, value in vars(module).items():
            if not isinstance(value, ArtifactKind):
                continue
            checked += 1
            if value.identifier != f"ca/{name.lower()}":
                mismatched.append(f"{module_info.name}.{name} -> {value.identifier}")
    assert checked > 0
    assert mismatched == []

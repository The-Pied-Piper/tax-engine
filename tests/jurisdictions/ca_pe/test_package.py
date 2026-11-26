"""The Prince Edward Island package: its namespace, its capabilities subpackage, its catalog and its
place in the Prince Edward Island package list. Importing it registers nothing in the bundled
package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_pe
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_capabilities,
    prince_edward_island_kinds,
    prince_edward_island_packages,
)


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_pe.NAMESPACE == "ca-pe"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_pe.capabilities"]

    assert tax_engine.jurisdictions.ca_pe.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-pe"


def test_the_catalog_is_in_the_prince_edward_island_namespace() -> None:
    from tax_engine.jurisdictions.ca_pe.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-pe")


def test_the_prince_edward_island_package_list_registers_without_a_clash() -> None:
    assert prince_edward_island_kinds().identifiers()
    assert prince_edward_island_capabilities() is not None


def test_the_roots_map_the_prince_edward_island_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_pe.__file__).parent

    assert prince_edward_island_packages().roots()[Namespace("ca-pe")] == directory


def test_importing_the_package_imports_its_trace_and_trace_english_packages() -> None:
    trace = sys.modules["tax_engine.jurisdictions.ca_pe.trace"]
    trace_english = sys.modules["tax_engine.jurisdictions.ca_pe.trace_english"]

    assert tax_engine.jurisdictions.ca_pe.trace is trace
    assert tax_engine.jurisdictions.ca_pe.trace_english is trace_english
    assert {"trace", "trace_english"} <= set(tax_engine.jurisdictions.ca_pe.__all__)


def test_importing_the_package_registers_nothing_in_the_bundled_package_list() -> None:
    from tax_engine.registrations import CORE_PACKAGES

    assert tax_engine.jurisdictions.ca_pe not in CORE_PACKAGES

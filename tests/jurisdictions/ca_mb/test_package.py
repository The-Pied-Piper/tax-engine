"""The Manitoba package: its namespace, its capabilities subpackage, its catalog and its place in
the Manitoba package list. Importing it registers nothing in the bundled package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_mb
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
)


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_mb.NAMESPACE == "ca-mb"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_mb.capabilities"]

    assert tax_engine.jurisdictions.ca_mb.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-mb"


def test_the_catalog_is_in_the_manitoba_namespace() -> None:
    from tax_engine.jurisdictions.ca_mb.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-mb")


def test_the_manitoba_package_list_registers_without_a_clash() -> None:
    assert manitoba_kinds().identifiers()
    assert manitoba_capabilities() is not None


def test_the_roots_map_the_manitoba_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_mb.__file__).parent

    assert manitoba_packages().roots()[Namespace("ca-mb")] == directory


def test_importing_the_package_imports_its_trace_and_trace_english_packages() -> None:
    trace = sys.modules["tax_engine.jurisdictions.ca_mb.trace"]
    trace_english = sys.modules["tax_engine.jurisdictions.ca_mb.trace_english"]

    assert tax_engine.jurisdictions.ca_mb.trace is trace
    assert tax_engine.jurisdictions.ca_mb.trace_english is trace_english
    assert {"trace", "trace_english"} <= set(tax_engine.jurisdictions.ca_mb.__all__)


def test_importing_the_package_registers_nothing_in_the_bundled_package_list() -> None:
    from tax_engine.registrations import CORE_PACKAGES

    assert tax_engine.jurisdictions.ca_mb not in CORE_PACKAGES

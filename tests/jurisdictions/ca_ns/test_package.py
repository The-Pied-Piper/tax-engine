"""The Nova Scotia package: its namespace, its capabilities subpackage, its catalog
and its place in the Nova Scotia package list. Importing it registers nothing in the
bundled package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_ns
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ns.support import (
    nova_scotia_capabilities,
    nova_scotia_kinds,
    nova_scotia_packages,
)


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_ns.NAMESPACE == "ca-ns"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_ns.capabilities"]

    assert tax_engine.jurisdictions.ca_ns.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-ns"


def test_the_catalog_is_in_the_nova_scotia_namespace() -> None:
    from tax_engine.jurisdictions.ca_ns.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-ns")


def test_the_nova_scotia_package_list_registers_without_a_clash() -> None:
    assert nova_scotia_kinds().identifiers()
    assert nova_scotia_capabilities() is not None


def test_the_roots_map_the_nova_scotia_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_ns.__file__).parent

    assert nova_scotia_packages().roots()[Namespace("ca-ns")] == directory


def test_importing_the_package_imports_its_trace_and_trace_english_packages() -> None:
    trace = sys.modules["tax_engine.jurisdictions.ca_ns.trace"]
    trace_english = sys.modules["tax_engine.jurisdictions.ca_ns.trace_english"]

    assert tax_engine.jurisdictions.ca_ns.trace is trace
    assert tax_engine.jurisdictions.ca_ns.trace_english is trace_english
    assert {"trace", "trace_english"} <= set(tax_engine.jurisdictions.ca_ns.__all__)


def test_importing_the_package_registers_nothing_in_the_bundled_package_list() -> None:
    from tax_engine.registrations import CORE_PACKAGES

    assert tax_engine.jurisdictions.ca_ns not in CORE_PACKAGES

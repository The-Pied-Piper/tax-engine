"""The Quebec package: its namespace, its capabilities subpackage, its catalog
and its place in the Quebec package list. Importing it registers nothing in the
bundled package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_qc
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_qc.support import (
    quebec_capabilities,
    quebec_kinds,
    quebec_packages,
)


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_qc.NAMESPACE == "ca-qc"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_qc.capabilities"]

    assert tax_engine.jurisdictions.ca_qc.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-qc"


def test_the_catalog_is_in_the_quebec_namespace() -> None:
    from tax_engine.jurisdictions.ca_qc.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-qc")


def test_the_quebec_package_list_registers_without_a_clash() -> None:
    assert quebec_kinds().identifiers()
    assert quebec_capabilities() is not None


def test_the_roots_map_the_quebec_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_qc.__file__).parent

    assert quebec_packages().roots()[Namespace("ca-qc")] == directory


def test_importing_the_package_imports_its_trace_and_trace_english_packages() -> None:
    trace = sys.modules["tax_engine.jurisdictions.ca_qc.trace"]
    trace_english = sys.modules["tax_engine.jurisdictions.ca_qc.trace_english"]

    assert tax_engine.jurisdictions.ca_qc.trace is trace
    assert tax_engine.jurisdictions.ca_qc.trace_english is trace_english
    assert {"trace", "trace_english"} <= set(tax_engine.jurisdictions.ca_qc.__all__)


def test_importing_the_package_registers_nothing_in_the_bundled_package_list() -> None:
    from tax_engine.registrations import CORE_PACKAGES

    assert tax_engine.jurisdictions.ca_qc not in CORE_PACKAGES

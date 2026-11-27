"""The New Brunswick package: its namespace, its capabilities subpackage, its catalog and its place
in the New Brunswick package list. Importing it registers nothing in the bundled package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_nb
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_capabilities,
    new_brunswick_kinds,
    new_brunswick_packages,
)


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_nb.NAMESPACE == "ca-nb"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_nb.capabilities"]

    assert tax_engine.jurisdictions.ca_nb.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-nb"


def test_the_catalog_is_in_the_new_brunswick_namespace() -> None:
    from tax_engine.jurisdictions.ca_nb.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-nb")


def test_the_new_brunswick_package_list_registers_without_a_clash() -> None:
    assert new_brunswick_kinds().identifiers()
    assert new_brunswick_capabilities() is not None


def test_the_roots_map_the_new_brunswick_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_nb.__file__).parent

    assert new_brunswick_packages().roots()[Namespace("ca-nb")] == directory


def test_importing_the_package_imports_its_trace_and_trace_english_packages() -> None:
    trace = sys.modules["tax_engine.jurisdictions.ca_nb.trace"]
    trace_english = sys.modules["tax_engine.jurisdictions.ca_nb.trace_english"]

    assert tax_engine.jurisdictions.ca_nb.trace is trace
    assert tax_engine.jurisdictions.ca_nb.trace_english is trace_english
    assert {"trace", "trace_english"} <= set(tax_engine.jurisdictions.ca_nb.__all__)


def test_importing_the_package_registers_nothing_in_the_bundled_package_list() -> None:
    from tax_engine.registrations import CORE_PACKAGES

    assert tax_engine.jurisdictions.ca_nb not in CORE_PACKAGES

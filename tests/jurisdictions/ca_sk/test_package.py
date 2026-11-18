"""The Saskatchewan package: its namespace, its capabilities subpackage, its catalog and its place
in the Saskatchewan package list. Importing it registers nothing in the bundled package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_sk
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
)


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_sk.NAMESPACE == "ca-sk"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_sk.capabilities"]

    assert tax_engine.jurisdictions.ca_sk.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-sk"


def test_the_catalog_is_in_the_saskatchewan_namespace() -> None:
    from tax_engine.jurisdictions.ca_sk.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-sk")


def test_the_saskatchewan_package_list_registers_without_a_clash() -> None:
    assert saskatchewan_kinds().identifiers()
    assert saskatchewan_capabilities() is not None


def test_the_roots_map_the_saskatchewan_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_sk.__file__).parent

    assert saskatchewan_packages().roots()[Namespace("ca-sk")] == directory


def test_importing_the_package_imports_its_trace_and_trace_english_packages() -> None:
    trace = sys.modules["tax_engine.jurisdictions.ca_sk.trace"]
    trace_english = sys.modules["tax_engine.jurisdictions.ca_sk.trace_english"]

    assert tax_engine.jurisdictions.ca_sk.trace is trace
    assert tax_engine.jurisdictions.ca_sk.trace_english is trace_english
    assert {"trace", "trace_english"} <= set(tax_engine.jurisdictions.ca_sk.__all__)


def test_importing_the_package_registers_nothing_in_the_bundled_package_list() -> None:
    from tax_engine.registrations import CORE_PACKAGES

    assert tax_engine.jurisdictions.ca_sk not in CORE_PACKAGES

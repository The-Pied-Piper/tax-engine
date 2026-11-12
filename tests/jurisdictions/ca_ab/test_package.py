"""The Alberta package: its namespace, its capabilities subpackage, its catalog and its place in
the Alberta package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_ab
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_ab.NAMESPACE == "ca-ab"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_ab.capabilities"]

    assert tax_engine.jurisdictions.ca_ab.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-ab"


def test_the_catalog_is_in_the_alberta_namespace() -> None:
    from tax_engine.jurisdictions.ca_ab.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-ab")


def test_the_alberta_package_list_registers_every_catalog_without_a_clash() -> None:
    kinds = alberta_kinds()

    assert kinds.identifiers()


def test_the_roots_map_the_alberta_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_ab.__file__).parent

    assert alberta_packages().roots()[Namespace("ca-ab")] == directory

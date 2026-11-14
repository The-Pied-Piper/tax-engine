"""The British Columbia package: its namespace, its capabilities subpackage, its catalog and its
place in the British Columbia package list."""

from __future__ import annotations

import sys
from pathlib import Path

import tax_engine.jurisdictions.ca_bc
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
)


def test_declares_its_namespace() -> None:
    assert tax_engine.jurisdictions.ca_bc.NAMESPACE == "ca-bc"


def test_importing_the_package_imports_its_capabilities() -> None:
    capabilities = sys.modules["tax_engine.jurisdictions.ca_bc.capabilities"]

    assert tax_engine.jurisdictions.ca_bc.capabilities is capabilities
    assert capabilities.NAMESPACE == "ca-bc"


def test_the_catalog_is_in_the_british_columbia_namespace() -> None:
    from tax_engine.jurisdictions.ca_bc.catalog import CATALOG

    assert CATALOG.namespace == Namespace("ca-bc")


def test_the_british_columbia_package_list_registers_every_catalog_without_a_clash() -> None:
    kinds = british_columbia_kinds()

    assert kinds.identifiers()


def test_the_roots_map_the_british_columbia_namespace_to_its_directory() -> None:
    directory = Path(tax_engine.jurisdictions.ca_bc.__file__).parent

    assert british_columbia_packages().roots()[Namespace("ca-bc")] == directory

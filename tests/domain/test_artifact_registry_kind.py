"""Unit tests for `ArtifactRegistry.kind`: the artifact kind registered under an identifier.

The registry stores items as `object` (`ArtifactKind` is invariant), so `kind` is the one place
that checks an entry is an `ArtifactKind`: an unknown identifier is the registry's
`UnknownRegistrationError`, anything else registered is an `InvalidRegistrationError` naming the
identifier. Every registry here is a private one and every name is made up.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, assert_type

import pytest

from tax_calculator.domain.artifact import ArtifactCatalog, ArtifactKind, ArtifactRegistry
from tax_calculator.domain.errors import InvalidRegistrationError, UnknownRegistrationError
from tax_calculator.domain.registry import Namespace

BASE = ArtifactKind("ex/taxable_base", Decimal)
COUNT = ArtifactKind("ex/count", int)


def registry(**items: object) -> ArtifactRegistry:
    """A private registry holding BASE, COUNT and `items` (identifier with `/` given as `__`)."""
    artifacts = ArtifactRegistry()
    for kind in (BASE, COUNT):
        artifacts.register(kind.identifier, kind)
    for key, item in items.items():
        artifacts.register(key.replace("__", "/"), item)
    return artifacts


def test_kind_is_the_kind_registered_under_the_identifier() -> None:
    artifacts = registry()

    found = artifacts.kind("ex/taxable_base")

    assert_type(found, ArtifactKind[Any])
    assert found is BASE
    assert artifacts.kind("ex/count") is COUNT


def test_kind_returns_the_registered_object_not_an_equal_one() -> None:
    own = ArtifactKind("ex/own_base", Decimal)
    artifacts = ArtifactRegistry()
    artifacts.register("ex/own_base", own)

    assert artifacts.kind("ex/own_base") is own


def test_kind_finds_kinds_registered_from_a_catalog() -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    declared = catalog.declare("refund", Decimal)
    artifacts = ArtifactRegistry()
    artifacts.register_catalog(catalog)

    assert artifacts.kind("ex/refund") is declared


def test_an_unknown_identifier_is_an_unknown_registration() -> None:
    with pytest.raises(UnknownRegistrationError, match="'ex/nowhere'"):
        registry().kind("ex/nowhere")


@pytest.mark.parametrize(
    "item",
    [
        pytest.param(object(), id="object"),
        pytest.param("ex/taxable_base", id="string"),
        pytest.param(Decimal, id="value-type"),
    ],
)
def test_an_entry_that_is_not_an_artifact_kind_is_an_invalid_registration(item: object) -> None:
    artifacts = registry(ex__stray=item)

    with pytest.raises(
        InvalidRegistrationError,
        match=r"'ex/stray' is registered as .*, not as an artifact kind",
    ):
        artifacts.kind("ex/stray")


def test_kind_looks_in_that_registry_only() -> None:
    artifacts = registry()

    assert "ex/taxable_base" not in ArtifactRegistry.shared().identifiers()
    assert artifacts.kind("ex/taxable_base") is BASE
    with pytest.raises(UnknownRegistrationError):
        ArtifactRegistry().kind("ex/taxable_base")


def test_kind_rejects_an_entry_registered_under_another_identifier_than_its_own() -> None:
    artifacts = registry(ex__alias=ArtifactKind("ex/elsewhere", Decimal))

    with pytest.raises(
        InvalidRegistrationError, match=r"'ex/alias' is registered as .*'ex/elsewhere'"
    ):
        artifacts.kind("ex/alias")
